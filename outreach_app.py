"""
LinkedIn Outreach App — Klik Energy
CSV de empresas → busca decisores → genera mensajes → envía conexiones.
Puerto: 8766
"""
import asyncio, csv, io, json, uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agents.linkedin_agent import LinkedInAgent
from agents.outreach_templates import select_template, personalize
from linkedin_sender import LinkedInSender

BASE_DIR    = Path(__file__).parent
COOKIES_FILE = BASE_DIR / "linkedin_cookies.json"
QUEUE_DIR   = BASE_DIR / "outreach"
QUEUE_DIR.mkdir(exist_ok=True)

app = FastAPI(title="LinkedIn Outreach App")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

sessions: dict = {}


@app.get("/")
async def root():
    return FileResponse(str(BASE_DIR / "ui" / "outreach.html"))

@app.get("/health")
async def health():
    return {"status": "ok", "linkedin_auth": COOKIES_FILE.exists()}


@app.get("/docs/{filename}")
async def download_doc(filename: str):
    allowed = {
        "klik_whatsapp_asesor_energetico.md",
        "klik_llamada_asesor_energetico.md",
        "klik_procesos_whatsapp_llamada.html",
    }
    if filename not in allowed:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    return FileResponse(str(BASE_DIR / "docs" / filename), filename=filename)


@app.websocket("/ws/{session_id}")
async def ws_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()

    async def emit(event: dict):
        try: await ws.send_json(event)
        except Exception: pass

    linkedin = LinkedInAgent(emit_fn=emit)
    sessions[session_id] = {"ws": ws, "linkedin": linkedin, "contacts": [], "stop": False}

    await ws.send_json({
        "type": "connected",
        "linkedin_auth": COOKIES_FILE.exists(),
        "timestamp": datetime.now().isoformat(),
    })

    try:
        while True:
            data = await ws.receive_json()
            t = data.get("type")

            # ── Parsear CSV ─────────────────────────────────────────────────
            if t == "parse_csv":
                companies = _parse_csv(data.get("content", ""))
                sessions[session_id]["companies"] = companies
                await ws.send_json({"type": "csv_parsed", "companies": companies, "total": len(companies)})

            # ── Buscar decisores en LinkedIn ─────────────────────────────────
            elif t == "search_linkedin":
                companies = sessions[session_id].get("companies", [])
                sessions[session_id]["stop"] = False
                contacts: list[dict] = []
                total = len(companies)

                await ws.send_json({"type": "search_start", "total": total})

                for i, company in enumerate(companies):
                    if sessions[session_id]["stop"]:
                        break

                    await ws.send_json({
                        "type": "search_progress",
                        "current": i + 1, "total": total,
                        "company": company["name"],
                    })

                    found = await linkedin.find_decision_makers(
                        [{"name": company["name"], "nit": company.get("nit",""), "city":""}],
                        max_per_company=2,
                    )

                    for person in found:
                        c = {
                            "id":              str(uuid.uuid4())[:8],
                            "name":    person.get("name",""),
                            "title":   person.get("title",""),
                            "company": company["name"],
                            "nit":     company.get("nit",""),
                            "linkedin_url":    person.get("linkedin_url",""),
                            "status":          "queued",
                        }
                        c["message"] = _gen_message(c)
                        contacts.append(c)
                        await ws.send_json({"type": "contact_found", "contact": c})

                    await asyncio.sleep(2.5)

                sessions[session_id]["contacts"] = contacts
                await ws.send_json({"type": "search_complete", "total": len(contacts)})

            # ── Editar mensaje ───────────────────────────────────────────────
            elif t == "update_message":
                cid, msg = data.get("id"), data.get("message","")[:300]
                for c in sessions[session_id].get("contacts",[]):
                    if c["id"] == cid:
                        c["message"] = msg
                        break

            # ── Iniciar envío ────────────────────────────────────────────────
            elif t == "start_send":
                contacts = data.get("contacts") or sessions[session_id].get("contacts",[])
                limit    = min(int(data.get("limit", 15)), 20)
                sessions[session_id]["stop"] = False

                if not COOKIES_FILE.exists():
                    await ws.send_json({
                        "type": "error",
                        "message": "Sin sesión LinkedIn — ejecuta: python setup_linkedin_auth.py"
                    })
                    continue

                queue_file = QUEUE_DIR / f"queue_{session_id}.json"
                queue_file.write_text(json.dumps(_build_queue(contacts, session_id), indent=2))

                await ws.send_json({"type": "send_start", "total": len(contacts), "limit": limit})

                def make_emit(wsi):
                    def e(ev): asyncio.create_task(wsi.send_json(ev))
                    return e

                sender = LinkedInSender(queue_file=queue_file, emit_fn=make_emit(ws), headless=True)
                sessions[session_id]["sender"] = sender
                asyncio.create_task(sender.run(stage="connection", max_per_day=limit))

            # ── Detener ──────────────────────────────────────────────────────
            elif t == "stop":
                sessions[session_id]["stop"] = True
                sessions[session_id]["linkedin"].stop()
                if s := sessions[session_id].get("sender"):
                    s.stop()
                await ws.send_json({"type": "stopped"})

    except WebSocketDisconnect:
        sessions.pop(session_id, None)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_csv(content: str) -> list[dict]:
    try:
        reader = csv.DictReader(io.StringIO(content))
        result = []
        for row in reader:
            n = {k.lower().strip(): (v or "").strip() for k, v in row.items()}
            name = n.get("nombre_empresa") or n.get("name") or n.get("empresa") or n.get("razon_social") or ""
            nit  = n.get("nit") or n.get("tax_id") or ""
            if name and len(name) > 3:
                result.append({"name": name, "nit": nit})
        return result
    except Exception:
        return []


def _gen_message(contact: dict) -> str:
    tpl = select_template({"title": contact.get("title", "Director General")}, "connection", 0)
    if tpl:
        return personalize(tpl, {
            "name":        contact["name"],
            "title":       contact.get("title",""),
            "company_name":contact["company"],
            "company_city":contact.get("city","Colombia"),
        })[:300]
    n = contact["name"].split()[0] if contact.get("name") else "estimado/a"
    return f"Hola {n}, trabajo con directores industriales para optimizar costos energéticos con Klik Energy en el mercado no regulado. ¿Conectamos?"[:300]


def _build_queue(contacts: list, session_id: str) -> dict:
    return {
        "campaign_id": f"outreach_{session_id}",
        "created_at":  datetime.now().isoformat(),
        "stats": {"total": len(contacts), "sent_today": 0, "last_reset": datetime.now().date().isoformat()},
        "queue": [{
            "contact_id":   c["id"],
            "name":         c.get("name",""),
            "title":        c.get("title",""),
            "company_name": c.get("company",""),
            "company_city": c.get("city",""),
            "linkedin_url": c.get("linkedin_url",""),
            "sequence": {"connection": {"message": c.get("message","")[:300], "status":"queued", "sent_at":None}},
        } for c in contacts],
    }


if __name__ == "__main__":
    print("\n  💬 LinkedIn Outreach App · Klik Energy")
    print("  🌐 http://localhost:8766\n")
    uvicorn.run("outreach_app:app", host="0.0.0.0", port=8766, reload=False, log_level="warning")
