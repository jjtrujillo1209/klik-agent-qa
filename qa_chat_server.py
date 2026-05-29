"""
KLIK Agent QA Chat Server — puerto 8767
Demo y QA del agente WhatsApp y Llamada.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"

app = FastAPI(title="KLIK Agent QA")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "ui")), name="static")


@app.get("/")
async def root():
    return FileResponse(str(BASE_DIR / "ui" / "qa_chat.html"))


def load_guide(mode: str) -> str:
    fname = (
        "klik_whatsapp_asesor_energetico.md"
        if mode == "whatsapp"
        else "klik_llamada_asesor_energetico.md"
    )
    return (DOCS_DIR / fname).read_text(encoding="utf-8")


SYSTEM_TPL = """\
Eres el asesor energético de KLIK. Sigue estrictamente la siguiente guía:

{guide}

---
INSTRUCCIONES DE SISTEMA (no las menciones al prospecto):
- Actúa de forma natural y conversacional, sin sonar robótico.
- Si el mensaje del usuario es "__START_INBOUND__", genera la apertura inbound exacta de la guía.
- Si el mensaje del usuario es "__START_OUTBOUND__", genera la apertura outbound exacta de la guía.
- Al final de CADA respuesta agrega un bloque CRM con los datos recopilados hasta ese momento.
  Usa EXACTAMENTE este formato (sin alterar las claves):

```crm
{{"empresa":null,"ciudad":null,"consumo":null,"nombre":null,"cargo":null,"correo":null,"interes":null,"estado":"por_calificar","tipo":null}}
```

  Valores de "estado": por_calificar | calificado | reunion_propuesta | reunion_agendada | no_aplica
  Valores de "tipo": inbound | outbound | pqrs | comercial | soporte | null
  Solo actualiza campos con información real de la conversación.
"""


class ChatRequest(BaseModel):
    message: str
    history: list[dict]
    mode: str  # whatsapp | llamada


@app.post("/chat")
async def chat(req: ChatRequest):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    system = SYSTEM_TPL.format(guide=load_guide(req.mode))
    messages = req.history + [{"role": "user", "content": req.message}]

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system,
            messages=messages,
        )
    except anthropic.BadRequestError as e:
        msg = str(e)
        if "credit balance is too low" in msg:
            raise HTTPException(status_code=402, detail="Sin créditos en la API key. Ve a console.anthropic.com/billing para recargar.")
        raise HTTPException(status_code=400, detail=msg)
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="API key inválida. Revisa el archivo .env")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    full = resp.content[0].text

    crm: dict = {}
    m = re.search(r"```crm\s*(\{.*?\})\s*```", full, re.DOTALL)
    if m:
        try:
            crm = json.loads(m.group(1))
        except Exception:
            pass

    text = re.sub(r"\s*```crm[\s\S]*?```", "", full).strip()

    return {
        "text": text,
        "crm": crm,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
    }


@app.get("/health")
async def health():
    return {"status": "ok", "api_key": bool(os.getenv("ANTHROPIC_API_KEY"))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("qa_chat_server:app", host="0.0.0.0", port=8767, reload=True)
