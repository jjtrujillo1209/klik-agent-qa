"""
LinkedIn Sender — Klik Energy
Envía connection requests y mensajes directos con Playwright.

Límites seguros:
  - Connection requests: máx 15/día (LinkedIn bloquea a partir de ~20)
  - Mensajes directos: máx 25/día
  - Delay entre acciones: 60-120s (aleatorio, simula comportamiento humano)

Uso directo:
    python linkedin_sender.py --queue outreach/campaign_queue.json --limit 10
    python linkedin_sender.py --queue outreach/campaign_queue.json --stage connection --limit 15
    python linkedin_sender.py --queue outreach/campaign_queue.json --stage messages --limit 20
"""

import argparse
import asyncio
import json
import random
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Callable, Optional

BASE_DIR = Path(__file__).parent
COOKIES_FILE = BASE_DIR / "linkedin_cookies.json"


class LinkedInSender:
    """
    Envía connection requests y mensajes LinkedIn de forma automatizada
    usando Playwright con cookies de sesión real.
    """

    def __init__(
        self,
        queue_file: Path,
        emit_fn: Optional[Callable] = None,
        headless: bool = True,
    ):
        self.queue_file = Path(queue_file)
        self.emit = emit_fn or self._default_emit
        self.headless = headless
        self._stop = False
        self._browser = None
        self._context = None

    def stop(self):
        self._stop = True

    def _default_emit(self, event: dict):
        ts = datetime.now().strftime("%H:%M:%S")
        lvl = event.get("level", "info").upper()
        msg = event.get("message", "")
        print(f"[{ts}] [{lvl}] {msg}")

    async def _log(self, msg: str, level: str = "info"):
        await asyncio.to_thread(self.emit, {
            "type": "agent_log",
            "agent": "linkedin_sender",
            "level": level,
            "message": msg,
            "timestamp": datetime.now().isoformat(),
        })

    async def _emit_progress(self, sent: int, total: int, name: str, result: str):
        await asyncio.to_thread(self.emit, {
            "type": "outreach_progress",
            "sent": sent,
            "total": total,
            "current_name": name,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })

    # ── Cola ──────────────────────────────────────────────────────────────────

    def load_queue(self) -> dict:
        if not self.queue_file.exists():
            raise FileNotFoundError(f"Cola no encontrada: {self.queue_file}")
        return json.loads(self.queue_file.read_text())

    def save_queue(self, queue: dict):
        self.queue_file.write_text(json.dumps(queue, indent=2, default=str))

    def _reset_daily_if_needed(self, queue: dict):
        today = date.today().isoformat()
        stats = queue.setdefault("stats", {})
        if stats.get("last_reset") != today:
            stats["sent_today"] = 0
            stats["messages_today"] = 0
            stats["last_reset"] = today
        return queue

    def _get_queued(self, queue: dict, stage: str, limit: int) -> list[dict]:
        """Retorna contactos con ese stage en estado 'queued', hasta el límite diario."""
        stats = queue.get("stats", {})
        sent_today = stats.get("sent_today", 0) if stage == "connection" else stats.get("messages_today", 0)
        remaining = limit - sent_today

        result = []
        for contact in queue.get("queue", []):
            if len(result) >= remaining:
                break
            seq = contact.get("sequence", {})
            step = seq.get(stage, {})
            if step.get("status") == "queued" and contact.get("linkedin_url"):
                result.append(contact)
        return result

    # ── Runner principal ──────────────────────────────────────────────────────

    async def run(
        self,
        stage: str = "connection",
        max_per_day: int = 15,
    ) -> dict:
        """
        Punto de entrada principal.
        stage: 'connection' | 'messages' (primer_mensaje a conectados)
        """
        self._stop = False

        if not COOKIES_FILE.exists():
            await self._log(
                "❌ No hay cookies LinkedIn. Ejecuta: python setup_linkedin_auth.py",
                "error"
            )
            return {"sent": 0, "failed": 0, "error": "No cookies"}

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            await self._log("❌ Playwright no instalado: pip install playwright", "error")
            return {"sent": 0, "failed": 0, "error": "No playwright"}

        queue = self.load_queue()
        queue = self._reset_daily_if_needed(queue)
        targets = self._get_queued(queue, stage, max_per_day)

        if not targets:
            await self._log(
                f"ℹ️ No hay contactos pendientes en cola para '{stage}' "
                f"(límite diario: {max_per_day})"
            )
            return {"sent": 0, "failed": 0, "skipped": 0}

        await self._log(
            f"🚀 Iniciando envío — {len(targets)} contactos · "
            f"etapa: {stage} · límite: {max_per_day}/día"
        )

        cookies = json.loads(COOKIES_FILE.read_text())
        sent = failed = skipped = 0
        total = len(targets)

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(
                headless=self.headless,
                args=["--window-size=1280,900", "--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 900},
                locale="es-CO",
            )
            await context.add_cookies(cookies)
            page = await context.new_page()

            # Warm-up: ir al feed primero para validar sesión
            await self._log("🔐 Validando sesión LinkedIn...")
            try:
                await page.goto("https://www.linkedin.com/feed/", timeout=20000)
                await page.wait_for_timeout(random.randint(2000, 3500))

                if "login" in page.url or "authwall" in page.url:
                    await self._log(
                        "❌ Sesión expirada. Ejecuta: python setup_linkedin_auth.py",
                        "error"
                    )
                    await browser.close()
                    return {"sent": 0, "failed": 0, "error": "Session expired"}

                await self._log("✅ Sesión válida. Comenzando envíos...")
            except Exception as e:
                await self._log(f"❌ No se pudo conectar a LinkedIn: {e}", "error")
                await browser.close()
                return {"sent": 0, "failed": 0, "error": str(e)}

            for i, contact in enumerate(targets):
                if self._stop:
                    await self._log("⏹️ Envío detenido por el usuario.")
                    break

                name = contact.get("name", "?")
                company = contact.get("company_name", "")
                url = contact.get("linkedin_url", "")
                msg_text = contact.get("sequence", {}).get(stage, {}).get("message", "")

                await self._log(f"[{i+1}/{total}] {name} — {company}")

                if stage == "connection":
                    result = await self._send_connection(page, url, msg_text[:300])
                else:
                    result = await self._send_message(page, url, msg_text)

                # Actualizar cola
                seq_step = contact.setdefault("sequence", {}).setdefault(stage, {})
                seq_step["sent_at"] = datetime.now().isoformat()

                if result["success"]:
                    seq_step["status"] = "sent"
                    sent += 1
                    if stage == "connection":
                        queue["stats"]["sent_today"] = queue["stats"].get("sent_today", 0) + 1
                    else:
                        queue["stats"]["messages_today"] = queue["stats"].get("messages_today", 0) + 1
                    await self._log(f"  ✅ {result['detail']}")
                elif result.get("skip"):
                    seq_step["status"] = "skipped"
                    seq_step["skip_reason"] = result.get("detail", "")
                    skipped += 1
                    await self._log(f"  ⏭️ Saltado: {result['detail']}", "warn")
                else:
                    seq_step["status"] = "failed"
                    seq_step["error"] = result.get("detail", "")
                    failed += 1
                    await self._log(f"  ❌ Error: {result['detail']}", "warn")

                self.save_queue(queue)
                await self._emit_progress(sent, total, name, seq_step["status"])

                # Delay humano entre envíos (último no necesita delay)
                if i < total - 1 and not self._stop:
                    delay = random.uniform(60, 120)
                    await self._log(f"  ⏳ Esperando {int(delay)}s...")
                    await asyncio.sleep(delay)

            await browser.close()

        summary = {
            "sent": sent, "failed": failed, "skipped": skipped,
            "total": total, "stage": stage,
        }
        await self._log(
            f"📊 Resumen: {sent} enviados · {skipped} saltados · {failed} fallidos"
        )
        await asyncio.to_thread(self.emit, {
            "type": "outreach_complete",
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        })
        return summary

    # ── Envío de connection request ───────────────────────────────────────────

    async def _send_connection(self, page, url: str, message: str) -> dict:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(random.randint(1800, 3200))

            # Detectar estado actual de la conexión
            state = await self._detect_connection_state(page)

            if state == "connected":
                return {"success": False, "skip": True, "detail": "Ya conectado — usa 'messages'"}
            if state == "pending":
                return {"success": False, "skip": True, "detail": "Solicitud pendiente"}
            if state == "follow_only":
                return {"success": False, "skip": True, "detail": "Solo se puede seguir (InMail)"}

            # Intentar hacer clic en Connect
            clicked = await self._click_connect_button(page)
            if not clicked:
                return {"success": False, "detail": "Botón Connect no encontrado"}

            await page.wait_for_timeout(random.randint(800, 1500))

            # Intentar agregar nota personalizada
            noted = await self._add_note(page, message)
            if not noted:
                # Sin nota → enviar de todas formas (sin mensaje personalizado)
                sent = await self._click_send(page)
                detail = "Enviado sin nota (modal sin campo de texto)"
            else:
                sent = await self._click_send(page)
                detail = f"Enviado con nota ({len(message)} chars)"

            if sent:
                return {"success": True, "detail": detail}
            return {"success": False, "detail": "No se encontró botón de envío"}

        except Exception as e:
            return {"success": False, "detail": str(e)[:120]}

    async def _detect_connection_state(self, page) -> str:
        """Detecta si ya está conectado, pendiente, o puede conectar."""
        try:
            await page.wait_for_selector("main", timeout=10000)

            checks = [
                ("connected",    "button[aria-label*='Message'], button[aria-label*='Mensaje']"),
                ("pending",      "button[aria-label*='Pending'], button[aria-label*='Pendiente']"),
                ("connect",      "button[aria-label*='Invite'], button[aria-label*='Connect'], button[aria-label*='Conectar']"),
                ("follow_only",  "button[aria-label*='Follow'], button[aria-label*='Seguir']"),
            ]

            for state, selector in checks:
                el = await page.query_selector(selector)
                if el:
                    return state

            # Buscar en dropdown "More"
            more = await page.query_selector("button[aria-label='More actions'], button[aria-label='Más acciones']")
            if more:
                await more.click()
                await page.wait_for_timeout(500)
                connect_in_menu = await page.query_selector(
                    "[role='menu'] button[aria-label*='Connect'], [role='menu'] button[aria-label*='Conectar']"
                )
                if connect_in_menu:
                    return "connect_in_menu"
                await page.keyboard.press("Escape")
        except Exception:
            pass
        return "unknown"

    async def _click_connect_button(self, page) -> bool:
        selectors = [
            "button[aria-label*='Invite'][aria-label*='connect']",
            "button[aria-label*='Invite'][aria-label*='Connect']",
            "button[aria-label*='Conectar']",
            "button[aria-label='Connect']",
            ".pvs-profile-actions button[aria-label*='Connect']",
            ".pvs-profile-actions button[aria-label*='Invite']",
        ]
        for sel in selectors:
            btn = await page.query_selector(sel)
            if btn:
                await btn.scroll_into_view_if_needed()
                await page.wait_for_timeout(random.randint(300, 700))
                await btn.click()
                return True

        # Buscar en menú "More"
        more = await page.query_selector(
            "button[aria-label='More actions'], button[aria-label='Más acciones']"
        )
        if more:
            await more.click()
            await page.wait_for_timeout(600)
            menu_connect = await page.query_selector(
                "[role='menu'] button[aria-label*='Connect'], [role='menu'] button[aria-label*='Conectar']"
            )
            if menu_connect:
                await menu_connect.click()
                return True
        return False

    async def _add_note(self, page, message: str) -> bool:
        try:
            note_btn = await page.wait_for_selector(
                "button[aria-label*='Add a note'], button[aria-label*='Agregar una nota']",
                timeout=4000
            )
            await note_btn.click()
            await page.wait_for_timeout(random.randint(400, 800))

            textarea = await page.wait_for_selector(
                "textarea[name='message'], #custom-message, textarea.connect-button-send-invite__custom-message",
                timeout=4000
            )
            # Escribir con delays (simula tipeo humano)
            await textarea.click()
            await page.wait_for_timeout(random.randint(200, 500))
            await textarea.fill(message)
            await page.wait_for_timeout(random.randint(300, 700))
            return True
        except Exception:
            return False

    async def _click_send(self, page) -> bool:
        send_selectors = [
            "button[aria-label='Send invitation']",
            "button[aria-label='Send now']",
            "button[aria-label='Enviar invitación']",
            "button[aria-label='Enviar ahora']",
            ".artdeco-modal button.artdeco-button--primary",
        ]
        for sel in send_selectors:
            btn = await page.query_selector(sel)
            if btn:
                await page.wait_for_timeout(random.randint(500, 1000))
                await btn.click()
                await page.wait_for_timeout(random.randint(1000, 2000))
                return True
        return False

    # ── Envío de mensaje directo (contactos ya conectados) ────────────────────

    async def _send_message(self, page, url: str, message: str) -> dict:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(random.randint(1800, 3000))

            msg_btn = await page.query_selector(
                "button[aria-label*='Message'], button[aria-label*='Mensaje']"
            )
            if not msg_btn:
                return {"success": False, "skip": True, "detail": "No está conectado — envía connection request primero"}

            await msg_btn.click()
            await page.wait_for_timeout(random.randint(1000, 2000))

            # Textarea del chat
            textarea = await page.wait_for_selector(
                ".msg-form__contenteditable, div[contenteditable='true'][role='textbox'], "
                "div[data-artdeco-is-focused] div[contenteditable='true']",
                timeout=8000
            )
            await textarea.click()
            await page.wait_for_timeout(random.randint(300, 600))
            await textarea.fill(message)
            await page.wait_for_timeout(random.randint(500, 1000))

            # Send
            send_btn = await page.query_selector(
                "button.msg-form__send-button, button[type='submit'][aria-label*='Send'], "
                "button[aria-label*='Enviar']"
            )
            if send_btn:
                await send_btn.click()
            else:
                await textarea.press("Control+Enter")

            await page.wait_for_timeout(random.randint(800, 1500))
            return {"success": True, "detail": f"Mensaje enviado ({len(message)} chars)"}

        except Exception as e:
            return {"success": False, "detail": str(e)[:120]}


# ── Runner por consola ─────────────────────────────────────────────────────────

async def _run_cli(args):
    queue_file = Path(args.queue)
    sender = LinkedInSender(
        queue_file=queue_file,
        headless=not args.visible,
    )
    result = await sender.run(stage=args.stage, max_per_day=args.limit)
    print(f"\n✅ Resultado: {result}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Sender — Klik Energy")
    parser.add_argument(
        "--queue", default="outreach/campaign_queue.json",
        help="Ruta al archivo JSON de la cola de outreach"
    )
    parser.add_argument(
        "--stage", default="connection",
        choices=["connection", "messages"],
        help="Etapa a enviar: 'connection' (solicitudes) o 'messages' (DMs a conectados)"
    )
    parser.add_argument(
        "--limit", type=int, default=15,
        help="Máximo de envíos por día (default: 15)"
    )
    parser.add_argument(
        "--visible", action="store_true",
        help="Mostrar el browser (útil para debug)"
    )
    args = parser.parse_args()
    asyncio.run(_run_cli(args))
