"""
Lead GenAI Orchestrator - FastAPI Server
Chat + WebSocket en tiempo real para el pipeline de leads
"""

import asyncio
import json
import uuid
import warnings
from datetime import datetime
from pathlib import Path

import logging
warnings.filterwarnings("ignore", message=".*deprecated.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*deprecated.*", category=DeprecationWarning)
logging.getLogger("scrapling").setLevel(logging.ERROR)
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from orchestrator import LeadOrchestrator
from linkedin_sender import LinkedInSender

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Lead GenAI Orchestrator API",
    description="Orquestador de leads con Claude AI para mercado no regulado Colombia",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio base
BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Sesiones activas de WebSocket
active_sessions: dict[str, dict] = {}


# ─── WebSocket Manager ────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.orchestrators: dict[str, LeadOrchestrator] = {}
        self.senders: dict[str, LinkedInSender] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.connections[session_id] = ws
        self.orchestrators[session_id] = LeadOrchestrator(
            session_id=session_id,
            emit_fn=self._make_emitter(session_id)
        )
        await self.send(session_id, {
            "type": "connected",
            "session_id": session_id,
            "message": "🤖 Agente OrquestADOR conectado. Estoy listo para buscar leads.",
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, session_id: str):
        self.connections.pop(session_id, None)
        self.orchestrators.pop(session_id, None)
        self.senders.pop(session_id, None)

    async def send(self, session_id: str, data: dict):
        ws = self.connections.get(session_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                pass

    def _make_emitter(self, session_id: str):
        async def emit(event: dict):
            await self.send(session_id, event)
        return emit


manager = ConnectionManager()


# ─── WebSocket Endpoint ───────────────────────────────────────────────────────

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(ws: WebSocket, session_id: str):
    await manager.connect(session_id, ws)
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type", "chat")

            if msg_type == "chat":
                user_message = data.get("message", "").strip()
                if not user_message:
                    continue

                orchestrator = manager.orchestrators.get(session_id)
                if orchestrator:
                    # Eco del mensaje del usuario
                    await manager.send(session_id, {
                        "type": "user_message",
                        "message": user_message,
                        "timestamp": datetime.now().isoformat()
                    })
                    # Ejecutar en background para no bloquear el WS
                    asyncio.create_task(
                        orchestrator.process_command(user_message)
                    )

            elif msg_type == "stop":
                orchestrator = manager.orchestrators.get(session_id)
                if orchestrator:
                    orchestrator.stop()
                    await manager.send(session_id, {
                        "type": "system",
                        "message": "⏹️ Pipeline detenido.",
                        "timestamp": datetime.now().isoformat()
                    })

            elif msg_type == "send_outreach":
                stage     = data.get("stage", "connection")
                limit     = min(int(data.get("limit", 15)), 20)
                queue_file = BASE_DIR / "outreach" / "campaign_queue.json"

                if not queue_file.exists():
                    await manager.send(session_id, {
                        "type": "system",
                        "message": "⚠️ No hay cola de outreach generada. Ejecuta el pipeline completo primero.",
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    await manager.send(session_id, {
                        "type": "outreach_sending_start",
                        "stage": stage,
                        "limit": limit,
                        "message": f"📤 Iniciando envío — etapa: {stage} · límite: {limit}/día",
                        "timestamp": datetime.now().isoformat()
                    })

                    def make_sender_emit(sid: str):
                        async def emit(event: dict):
                            await manager.send(sid, event)
                        def sync_emit(event: dict):
                            asyncio.create_task(emit(event))
                        return sync_emit

                    sender = LinkedInSender(
                        queue_file=queue_file,
                        emit_fn=make_sender_emit(session_id),
                        headless=True,
                    )
                    manager.senders[session_id] = sender
                    asyncio.create_task(sender.run(stage=stage, max_per_day=limit))

            elif msg_type == "stop_outreach":
                sender = manager.senders.get(session_id)
                if sender:
                    sender.stop()
                    await manager.send(session_id, {
                        "type": "system",
                        "message": "⏹️ Envío detenido.",
                        "timestamp": datetime.now().isoformat()
                    })

            elif msg_type == "reset":
                manager.orchestrators[session_id] = LeadOrchestrator(
                    session_id=session_id,
                    emit_fn=manager._make_emitter(session_id)
                )
                await manager.send(session_id, {
                    "type": "reset",
                    "message": "🔄 Sesión reiniciada. Lista para nueva búsqueda.",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send(session_id, {
            "type": "error",
            "message": f"Error de conexión: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        manager.disconnect(session_id)


# ─── REST Endpoints ───────────────────────────────────────────────────────────

@app.get("/")
async def root():
    ui_file = BASE_DIR / "ui" / "index.html"
    if ui_file.exists():
        return FileResponse(str(ui_file))
    return JSONResponse({"status": "Lead GenAI Orchestrator running", "version": "2.0.0"})


@app.get("/health")
async def health():
    return {"status": "ok", "sessions": len(manager.connections), "timestamp": datetime.now().isoformat()}


@app.get("/outputs")
async def list_outputs():
    """Lista archivos generados en la carpeta outputs"""
    files = []
    for f in OUTPUTS_DIR.glob("*"):
        if f.is_file():
            files.append({
                "name": f.name,
                "size": f.stat().st_size,
                "created": datetime.fromtimestamp(f.stat().st_ctime).isoformat(),
                "url": f"/outputs/{f.name}"
            })
    return {"files": sorted(files, key=lambda x: x["created"], reverse=True)}


@app.get("/outputs/{filename}")
async def download_output(filename: str):
    """Descarga un archivo de output"""
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(str(file_path), filename=filename)


@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Info de una sesión activa"""
    orchestrator = manager.orchestrators.get(session_id)
    if not orchestrator:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    return {
        "session_id": session_id,
        "state": orchestrator.state,
        "companies_found": len(orchestrator.companies),
        "contacts_found": len(orchestrator.contacts),
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 Lead GenAI Orchestrator v2.0")
    print("  📡 WebSocket: ws://localhost:8765/ws/{session_id}")
    print("  🌐 UI: http://localhost:8765")
    print("  📁 Outputs: http://localhost:8765/outputs")
    print("=" * 60)
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8765,
        reload=False,
        log_level="info"
    )
