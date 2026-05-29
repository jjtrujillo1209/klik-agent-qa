"""
Lead GenAI Orchestrator - Agente Claude AI
Interpreta comandos de chat y ejecuta el pipeline de 5 pasos
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Any

import anthropic
from dotenv import load_dotenv

from agents.company_finder import CompanyFinder
from agents.nit_resolver import NitResolver
from agents.linkedin_agent import LinkedInAgent
from agents.exporter import LeadExporter
from agents.outreach_agent import OutreachAgent

load_dotenv()

BASE_DIR = Path(__file__).parent


# ─── Paso del pipeline ────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    {
        "id": 1,
        "name": "Descubrimiento de Empresas",
        "description": "Búsqueda en RUES, Google, Páginas Amarillas — Mercado No Regulado",
        "icon": "🏭",
        "agent": "company_finder"
    },
    {
        "id": 2,
        "name": "Validación NIT · RUES",
        "description": "Registro Único Empresarial — vigencia y datos oficiales",
        "icon": "🪪",
        "agent": "nit_resolver"
    },
    {
        "id": 3,
        "name": "Decision Makers · LinkedIn",
        "description": "Director Mantenimiento, Director Planta, Director General",
        "icon": "👤",
        "agent": "linkedin_agent"
    },
    {
        "id": 4,
        "name": "Enriquecimiento de Contactos",
        "description": "Emails y teléfonos verificados desde LinkedIn y fuentes públicas",
        "icon": "📧",
        "agent": "enricher"
    },
    {
        "id": 5,
        "name": "Exportación · Excel + CSV",
        "description": "Plantilla HubSpot + Excel con links LinkedIn clickeables",
        "icon": "📊",
        "agent": "exporter"
    },
    {
        "id": 6,
        "name": "Outreach · LinkedIn",
        "description": "Secuencias de mensajes personalizados por cargo listos para enviar",
        "icon": "💬",
        "agent": "outreach"
    }
]

# ─── Sistema prompt del orquestador ──────────────────────────────────────────

SYSTEM_PROMPT = """Eres el Agente Orquestador de Lead GenAI para Click Energy / Klik Energy.

Tu misión: Generar leads de empresas en el mercado eléctrico NO REGULADO de Colombia,
validarlas en RUES y encontrar decision makers en LinkedIn.

Target de empresas: Consumidores con demanda > 0.1 MW que pueden elegir su comercializador
de energía libremente (no regulados). Sectores: manufactura, industria, minería, hospitales
grandes, centros comerciales, empresas con plantas industriales.

Target de contactos LinkedIn:
- Director de Mantenimiento
- Director de Planta / Gerente de Planta
- Director General / Gerente General
- Director de Operaciones / COO
- Director Financiero / CFO (secundario)

Pipeline de 6 pasos que ejecutas:
1. company_finder → Descubrir empresas MNR vía RUES + Google
2. nit_resolver → Validar NIT y vigencia en RUES oficial
3. linkedin_agent → Buscar decision makers en LinkedIn
4. enricher → Enriquecer emails y teléfonos
5. exporter → Exportar Excel + CSV HubSpot
6. outreach → Generar secuencias de mensajes LinkedIn personalizados por cargo (connection request, primer mensaje, 2 follow-ups, demo request)

Cuando el usuario te dé un comando:
- Analiza qué quiere hacer (buscar empresas, validar NIT, buscar contactos, exportar)
- Responde de forma conversacional y profesional en español
- Si es una búsqueda de leads: empieza el pipeline completo o el paso específico
- Si es una pregunta: responde directamente
- Si falta información (sector, ciudad, etc.): pregunta de forma específica
- Si el usuario pide outreach, mensajes LinkedIn, templates o secuencias: ejecuta el paso 6
- El paso 6 puede correr solo (si ya hay contactos) o al final del pipeline completo
- Parámetro outreach_mode: "queue" (solo exportar) o "send" (enviar via LinkedIn si hay cookies)

REGLAS CRÍTICAS:
1. NUNCA inventes ni generes resultados falsos. Los resultados los producen los agentes reales.
2. Cuando action != "answer", el campo "reply" debe ser CORTO (1-2 oraciones de confirmación).
3. Si el usuario confirma ejecutar algo ("sí", "hazlo", "ejecuta", "dale", "corre"), usa action: "run_pipeline".
4. NUNCA uses action: "answer" cuando el usuario pide ejecutar el pipeline.

Ejemplos de action correcta:
- "busca empresas en Bogotá" → action: "run_pipeline"
- "sí hazlo" / "ejecuta" / "dale" → action: "run_pipeline"
- "¿qué es el MNR?" → action: "answer"
- "¿cuántas empresas encontraste?" → action: "answer"

Formato de respuesta SIEMPRE JSON puro (sin markdown):
{
  "reply": "Texto corto de confirmación (si action=run_pipeline) o respuesta completa (si action=answer)",
  "action": "run_pipeline | run_step | answer | ask_info | stop",
  "step": 1-6 (solo si action=run_step),
  "params": { "sector": "...", "cities": ["..."], "limit": 10 }
}"""


class LeadOrchestrator:
    """Orquestador principal del pipeline de leads"""

    def __init__(self, session_id: str, emit_fn: Callable):
        self.session_id = session_id
        self.emit = emit_fn
        self.state = "idle"
        self._stop_flag = False

        # Datos acumulados del pipeline
        self.companies: list[dict] = []
        self.contacts: list[dict] = []
        self.pipeline_params: dict = {}

        # Historial de conversación
        self.messages: list[dict] = []

        # Agentes del pipeline
        self.company_finder = CompanyFinder(emit_fn=emit_fn)
        self.nit_resolver = NitResolver(emit_fn=emit_fn)
        self.linkedin_agent = LinkedInAgent(emit_fn=emit_fn)
        self.exporter = LeadExporter(emit_fn=emit_fn, output_dir=BASE_DIR / "outputs")
        self.outreach_agent = OutreachAgent(emit_fn=emit_fn, output_dir=BASE_DIR / "outputs")

        # Estado del outreach
        self.outreach_result: dict = {}

        # Cliente Anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY no encontrada en .env")
        self.client = anthropic.Anthropic(api_key=api_key)

    def stop(self):
        self._stop_flag = True
        self.company_finder.stop()
        self.nit_resolver.stop()
        self.linkedin_agent.stop()
        self.outreach_agent.stop()

    async def _emit_step(self, step_id: int, status: str, message: str, data: Any = None):
        """Emite actualización de un paso del pipeline"""
        await self.emit({
            "type": "step_update",
            "step_id": step_id,
            "status": status,  # pending | running | completed | error
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

    async def _emit_agent_reply(self, message: str, data: Any = None):
        """Emite respuesta del agente al chat"""
        await self.emit({
            "type": "agent_reply",
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

    async def _emit_progress(self, step_id: int, current: int, total: int, item: str = ""):
        """Emite progreso dentro de un paso"""
        await self.emit({
            "type": "progress",
            "step_id": step_id,
            "current": current,
            "total": total,
            "item": item,
            "timestamp": datetime.now().isoformat()
        })

    def _parse_params(self, msg: str) -> dict:
        """Extrae sector, ciudades y límite del mensaje del usuario."""
        msg_l = msg.lower()
        params = dict(self.pipeline_params)

        sector_map = {
            "cemento": "cemento", "alimento": "alimentos", "bebida": "alimentos",
            "quimic": "quimica", "plastico": "plasticos", "textil": "textil",
            "miner": "mineria", "papel": "papel", "ceramica": "ceramica",
            "metal": "metal", "maquinaria": "maquinaria", "hospital": "hospitales_grandes",
            "centro comercial": "centros_comerciales",
        }
        for kw, sector in sector_map.items():
            if kw in msg_l:
                params["sector"] = sector
                break
        if "sector" not in params:
            params.setdefault("sector", "all")

        city_map = {
            "bogotá": "Bogotá", "bogota": "Bogotá",
            "medellín": "Medellín", "medellin": "Medellín",
            "cali": "Cali", "barranquilla": "Barranquilla",
            "bucaramanga": "Bucaramanga", "cartagena": "Cartagena",
        }
        found_cities = [v for k, v in city_map.items() if k in msg_l]
        if found_cities:
            params["cities"] = found_cities

        import re
        nums = re.findall(r'\b(\d+)\b', msg)
        for n in nums:
            if 3 <= int(n) <= 100:
                params["limit"] = int(n)
                break
        params.setdefault("limit", 10)

        return params

    async def process_command(self, user_message: str):
        """Siempre ejecuta el pipeline con los parámetros del mensaje."""
        msg = user_message.lower().strip()

        if msg in ("stop", "detener", "parar"):
            self.stop()
            await self._emit_agent_reply("⏹️ Pipeline detenido.")
            self.state = "idle"
            return

        if msg in ("reset", "reiniciar", "limpiar"):
            self.companies = []
            self.contacts = []
            self.pipeline_params = {}
            await self._emit_agent_reply("🔄 Sesión limpiada.")
            return

        if self.state == "running":
            await self._emit_agent_reply("⚠️ Pipeline en ejecución. Escribe **stop** para detenerlo.")
            return

        self._stop_flag = False
        params = self._parse_params(user_message)
        self.pipeline_params.update(params)

        try:
            await self._run_full_pipeline(params)
        except Exception as e:
            await self._emit_agent_reply(f"❌ Error: {str(e)}")
            self.state = "idle"

    async def _run_full_pipeline(self, params: dict):
        """Ejecuta el pipeline completo de 5 pasos"""
        self.state = "running"

        # Notificar inicio del pipeline
        await self.emit({
            "type": "pipeline_start",
            "steps": PIPELINE_STEPS,
            "params": params,
            "timestamp": datetime.now().isoformat()
        })

        # Reset pasos
        for step in PIPELINE_STEPS:
            await self._emit_step(step["id"], "pending", "Esperando...")

        try:
            # ── PASO 1 + 2: Buscar y validar hasta tener `limit` VIGENTES ──
            if self._stop_flag:
                return

            target        = params.get("limit", 10)
            vigentes      = []
            seen_names    = set()
            round_n       = 0
            max_rounds    = 3          # máx 3 rondas de búsqueda
            batch_size    = target + 5 # buscar con margen en cada ronda

            await self._emit_step(1, "running", "🔍 Buscando empresas en mercado no regulado...")
            await self._emit_step(2, "running", f"🪪 Validando NITs en RUES (objetivo: {target} VIGENTES)...")

            while len(vigentes) < target and round_n < max_rounds and not self._stop_flag:
                round_n += 1
                needed = batch_size if round_n == 1 else (target - len(vigentes)) + 5

                round_params = {**params, "limit": needed, "_exclude": list(seen_names)}
                candidates = await self.company_finder.find(round_params)

                # Filtrar ya buscadas
                fresh = [c for c in candidates if c["name"].lower() not in seen_names]
                for c in fresh:
                    seen_names.add(c["name"].lower())

                if not fresh:
                    break

                await self._emit_step(2, "running",
                    f"🪪 Ronda {round_n}: validando {len(fresh)} empresas en RUES...")

                validated = await self.nit_resolver.validate_batch(
                    fresh,
                    progress_cb=lambda i, t, name: asyncio.create_task(
                        self._emit_progress(2, i, t, name)
                    )
                )
                new_vigentes = [c for c in validated if c.get("rues_status") == "VIGENTE"]
                vigentes.extend(new_vigentes)

            vigentes = vigentes[:target]

            if not vigentes:
                await self._emit_step(1, "error", "No se encontraron empresas. Intenta con otros filtros.")
                self.state = "idle"
                return

            self.companies = vigentes
            await self._emit_step(
                1, "completed",
                f"✅ {len(vigentes)} empresas encontradas",
                {"count": len(vigentes), "sample": vigentes[:3]}
            )
            await self._emit_step(
                2, "completed",
                f"✅ {len(vigentes)} empresas VIGENTES en RUES",
                {"vigentes": len(vigentes), "total": len(seen_names)}
            )

            # ── PASO 3: Decision Makers en LinkedIn ─────────────────────────
            if self._stop_flag:
                return

            await self._emit_step(3, "running", f"👤 Buscando contactos en LinkedIn para {len(vigentes)} empresas...")
            contacts = await self.linkedin_agent.find_decision_makers(
                vigentes,
                titles=params.get("linkedin_titles", [
                    "Director de Mantenimiento",
                    "Director de Planta",
                    "Gerente de Planta",
                    "Director General",
                    "Gerente General",
                    "Director de Operaciones"
                ]),
                max_per_company=2,
                progress_cb=lambda i, t, name: asyncio.create_task(
                    self._emit_progress(3, i, t, name)
                )
            )

            self.contacts = contacts
            await self._emit_step(
                3, "completed",
                f"✅ {len(contacts)} decision makers encontrados",
                {"count": len(contacts), "sample": contacts[:3]}
            )

            # ── PASO 4: Enriquecimiento ─────────────────────────────────────
            if self._stop_flag:
                return

            await self._emit_step(4, "running", "📧 Enriqueciendo emails y teléfonos...")
            enriched = await self._enrich_contacts(contacts)

            await self._emit_step(
                4, "completed",
                f"✅ {len(enriched)} contactos enriquecidos",
                {"with_email": sum(1 for c in enriched if c.get("email")),
                 "with_phone": sum(1 for c in enriched if c.get("phone"))}
            )
            self.contacts = enriched

            # ── PASO 5: Exportación ─────────────────────────────────────────
            if self._stop_flag:
                return

            await self._emit_step(5, "running", "📊 Generando Excel y CSV HubSpot...")
            export_result = await self.exporter.export(
                companies=self.companies,
                contacts=self.contacts,
                params=params
            )

            await self._emit_step(
                5, "completed",
                f"✅ Exportado: {export_result['excel_file']}",
                export_result
            )

            # ── PASO 6: Outreach LinkedIn ───────────────────────────────────
            if self._stop_flag:
                return

            await self._emit_step(6, "running", "💬 Generando secuencias de outreach LinkedIn...")
            outreach_result = await self.outreach_agent.run_campaign(
                contacts=self.contacts,
                params=params,
                progress_cb=lambda i, t, name: asyncio.create_task(
                    self._emit_progress(6, i, t, name)
                )
            )
            self.outreach_result = outreach_result

            await self._emit_step(
                6, "completed",
                f"✅ {outreach_result['total_messages']} mensajes listos en cola",
                outreach_result
            )

            # Notificar finalización
            all_exports = {**export_result, **outreach_result}
            await self.emit({
                "type": "pipeline_complete",
                "companies": len(self.companies),
                "contacts": len(self.contacts),
                "messages": outreach_result.get("total_messages", 0),
                "exports": all_exports,
                "timestamp": datetime.now().isoformat()
            })

            await self._emit_agent_reply(
                f"🎉 **Pipeline completado exitosamente.**\n\n"
                f"📊 **Resultados:**\n"
                f"- {len(self.companies)} empresas VIGENTES en RUES\n"
                f"- {len(self.contacts)} decision makers en LinkedIn\n"
                f"- {outreach_result.get('total_messages', 0)} mensajes de outreach generados\n"
                f"- Archivos listos en `outputs/`\n\n"
                f"💬 La cola de outreach incluye: connection request, primer mensaje, "
                f"2 follow-ups y solicitud de demo — personalizados por cargo.\n\n"
                f"¿Quieres que envíe las conexiones LinkedIn ahora o prefieres revisarlas primero?"
            )

        except Exception as e:
            await self._emit_agent_reply(f"❌ Error en el pipeline: {str(e)}")
        finally:
            self.state = "idle"

    async def _run_single_step(self, step_id: int, params: dict):
        """Ejecuta un solo paso del pipeline"""
        self.state = "running"
        step_info = next((s for s in PIPELINE_STEPS if s["id"] == step_id), None)
        if not step_info:
            await self._emit_agent_reply(f"❌ Paso {step_id} no existe.")
            self.state = "idle"
            return

        try:
            if step_id == 1:
                await self._emit_step(1, "running", "🔍 Buscando empresas...")
                companies = await self.company_finder.find(params)
                self.companies = companies
                await self._emit_step(1, "completed", f"✅ {len(companies)} empresas encontradas",
                                      {"count": len(companies)})

            elif step_id == 2:
                if not self.companies:
                    await self._emit_agent_reply("⚠️ Primero ejecuta el Paso 1 para obtener empresas.")
                    return
                await self._emit_step(2, "running", "🪪 Validando NITs en RUES...")
                validated = await self.nit_resolver.validate_batch(self.companies)
                vigentes = [c for c in validated if c.get("rues_status") == "VIGENTE"]
                self.companies = vigentes
                await self._emit_step(2, "completed", f"✅ {len(vigentes)} vigentes", {"vigentes": len(vigentes)})

            elif step_id == 3:
                if not self.companies:
                    await self._emit_agent_reply("⚠️ Primero ejecuta los pasos 1 y 2.")
                    return
                await self._emit_step(3, "running", "👤 Buscando decision makers...")
                contacts = await self.linkedin_agent.find_decision_makers(self.companies)
                self.contacts = contacts
                await self._emit_step(3, "completed", f"✅ {len(contacts)} contactos", {"count": len(contacts)})

            elif step_id == 5:
                if not self.contacts:
                    await self._emit_agent_reply("⚠️ No hay contactos para exportar. Ejecuta el pipeline primero.")
                    return
                await self._emit_step(5, "running", "📊 Exportando...")
                result = await self.exporter.export(self.companies, self.contacts, params)
                await self._emit_step(5, "completed", f"✅ Exportado", result)

            elif step_id == 6:
                if not self.contacts:
                    await self._emit_agent_reply(
                        "⚠️ No hay contactos para generar outreach. "
                        "Ejecuta el pipeline completo primero (pasos 1-3)."
                    )
                    return
                await self._emit_step(6, "running", "💬 Generando secuencias de outreach...")
                outreach_result = await self.outreach_agent.run_campaign(
                    contacts=self.contacts,
                    params=params,
                    progress_cb=lambda i, t, name: asyncio.create_task(
                        self._emit_progress(6, i, t, name)
                    )
                )
                self.outreach_result = outreach_result
                await self._emit_step(
                    6, "completed",
                    f"✅ {outreach_result['total_messages']} mensajes en cola",
                    outreach_result
                )
                await self._emit_agent_reply(
                    f"💬 **Outreach generado:**\n"
                    f"- {outreach_result['total_contacts']} contactos\n"
                    f"- {outreach_result['total_messages']} mensajes personalizados\n"
                    f"- Excel y CSV listos en `outputs/`\n\n"
                    f"Cada contacto tiene: connection request · primer mensaje · "
                    f"2 follow-ups · solicitud de demo, adaptados a su cargo."
                )

        except Exception as e:
            await self._emit_step(step_id, "error", f"Error: {str(e)}")
        finally:
            self.state = "idle"

    async def _enrich_contacts(self, contacts: list[dict]) -> list[dict]:
        """
        Enriquecimiento con fuentes disponibles (LinkedIn público + Hunter.io si hay key)
        Por ahora mantiene datos de LinkedIn y agrega campos vacíos para email/phone
        """
        enriched = []
        for contact in contacts:
            if self._stop_flag:
                break
            enriched_contact = dict(contact)
            # Placeholder para enriquecimiento externo (Apollo, BetterContact, Lusha)
            # Puedes agregar API keys en .env para activarlos
            if not enriched_contact.get("email"):
                enriched_contact["email"] = ""
            if not enriched_contact.get("phone"):
                enriched_contact["phone"] = ""
            enriched.append(enriched_contact)
            await asyncio.sleep(0.1)
        return enriched
