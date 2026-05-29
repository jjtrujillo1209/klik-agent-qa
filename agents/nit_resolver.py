"""
Agent 2: NIT Resolver — RUES API real
Valida NITs contra el Registro Único Empresarial (RUES) de Colombia.

Usa el endpoint real de RUES:
  POST https://elasticprd.rues.org.co/api/ConsultasRUES/BusquedaAvanzadaRM
El request se encripta con CryptoJS dentro del browser (Playwright),
la respuesta es JSON plano.
"""

import asyncio
import re
import unicodedata
from typing import Callable, Optional
from datetime import datetime
from pathlib import Path

RUES_ADV_URL  = "https://www.rues.org.co/busqueda-avanzada"
RUES_API_BASE = "https://elasticprd.rues.org.co"


class NitResolver:

    def __init__(self, emit_fn: Optional[Callable] = None):
        self.emit        = emit_fn or (lambda x: None)
        self._stop       = False
        self._page       = None
        self._browser    = None
        self._pw_ctx     = None
        self._query_count = 0    # evita goto completo para queries 2+

    def stop(self):
        self._stop = True

    async def _emit_log(self, msg: str, level: str = "info"):
        await self.emit({
            "type": "agent_log", "agent": "nit_resolver",
            "level": level, "message": msg,
            "timestamp": datetime.now().isoformat()
        })

    def clean_nit(self, nit: str) -> str:
        nit_clean = re.sub(r"[^0-9]", "", str(nit))
        return nit_clean[:9] if len(nit_clean) >= 9 else nit_clean

    @staticmethod
    def _strip_accents(text: str) -> str:
        return "".join(
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

    # ── Setup / teardown del browser compartido ───────────────────────────────
    async def _open_browser(self):
        from playwright.async_api import async_playwright
        self._pw_ctx = async_playwright()
        pw = await self._pw_ctx.__aenter__()
        self._browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-web-security", "--no-sandbox"],
        )
        ctx = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        self._page = await ctx.new_page()
        self._query_count = 0
        await self._emit_log("🌐 Browser RUES listo")

    async def _close_browser(self):
        try:
            if self._browser:
                await self._browser.close()
            if self._pw_ctx:
                await self._pw_ctx.__aexit__(None, None, None)
        except Exception:
            pass
        self._page = self._browser = self._pw_ctx = None

    # ── Consulta individual vía API del browser ───────────────────────────────
    # Stopwords corporativas que quitamos del término de búsqueda por nombre.
    _CORP_STOPWORDS = frozenset({"S.A.", "S.A.S.", "LTDA", "S.A", "SA", "SAS"})

    async def _reset_search_page(self):
        """Navega al formulario limpio en cada query — garantiza estado React limpio."""
        await self._page.goto(RUES_ADV_URL, timeout=60000, wait_until="domcontentloaded")
        await asyncio.sleep(1.5)
        await self._page.evaluate("document.querySelector('.swal2-container')?.remove()")
        await asyncio.sleep(0.3)

    async def _click_tab_js(self, tab_text: str) -> bool:
        """Click en un tab via JS — argumento pasado como parámetro (sin interpolación)."""
        return await self._page.evaluate(
            """(text) => {
                for (const btn of document.querySelectorAll('button')) {
                    if (btn.textContent.trim().startsWith(text)) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }""",
            tab_text,
        )

    async def _fill_input_js(self, selector: str, value: str) -> bool:
        """Rellena un input vía JS nativo (bypassa React, evita timeouts de visibilidad)."""
        return await self._page.evaluate(
            """({selector, value}) => {
                const el = document.querySelector(selector);
                if (!el) return false;
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                setter.call(el, value);
                el.dispatchEvent(new Event('input',  {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
                return true;
            }""",
            {"selector": selector, "value": value},
        )

    async def _wait_for_input_js(self, selector: str, timeout_ms: int = 8000) -> bool:
        """Espera hasta que el input exista en el DOM (sin requerir visibilidad)."""
        try:
            await self._page.wait_for_function(
                "selector => !!document.querySelector(selector)",
                arg=selector,
                timeout=timeout_ms,
            )
            return True
        except Exception:
            return False

    async def _click_buscar_js(self):
        """Click en el botón Buscar visible vía JS."""
        await self._page.evaluate(
            """() => document.querySelectorAll('button.btn-busqueda')
                .forEach(b => { if (b.offsetParent) b.click(); })"""
        )

    def _build_name_search_term(self, name: str) -> str:
        """Construye el término de búsqueda por nombre: sin tildes, en mayúsculas, sin sufijos corporativos."""
        clean_name = self._strip_accents(name[:40]).upper()
        words = [w for w in clean_name.split() if w not in self._CORP_STOPWORDS]
        return " ".join(words[:2]) if words else clean_name

    async def _query_rues(self, nit: str = "", name: str = "") -> Optional[dict]:
        """
        Busca en RUES y parsea los resultados directamente del DOM (div.card-result).
        Toda interacción (tabs, inputs, botón) se hace vía JS puro — sin locators de Playwright.
        """
        if not self._page:
            return None
        try:
            await self._reset_search_page()
            self._query_count += 1

            if nit:
                await self._click_tab_js("Identificacion")
                await asyncio.sleep(0.8)
                if not await self._wait_for_input_js('[name="Nit"]'):
                    await self._emit_log("Input Nit no encontrado", "warn")
                    return None
                await self._fill_input_js('[name="Nit"]', nit)
            else:
                await self._click_tab_js("Nombre")
                await asyncio.sleep(0.8)
                if not await self._wait_for_input_js('[name="Razon"]'):
                    await self._emit_log(f"Input Razon no encontrado para '{name}'", "warn")
                    return None
                await self._fill_input_js('[name="Razon"]', self._build_name_search_term(name))

            await self._click_buscar_js()
            # Limpiar cualquier popup que aparezca tras la búsqueda
            await self._page.evaluate(
                "document.querySelectorAll('.swal2-container, [role=\"dialog\"]').forEach(el => el.remove())"
            )

            # Esperar resultados vía JS (inmune a popups superpuestos)
            try:
                await self._page.wait_for_function(
                    "() => document.querySelector('.card-result') !== null",
                    timeout=10000,
                )
            except Exception:
                return None  # Sin resultados

            # Parsear resultados desde el DOM
            records = await self._page.evaluate("""
                () => {
                    const cards = document.querySelectorAll('.card-result');
                    const results = [];
                    cards.forEach(card => {
                        const text = card.innerText;
                        const lines = text.split('\\n').map(l => l.trim()).filter(l => l);
                        const obj = { razon_social: lines[0] || '' };
                        for (let i = 0; i < lines.length - 1; i++) {
                            const key = lines[i].toLowerCase();
                            const val = lines[i+1];
                            if (key.includes('identificaci')) obj.nit = val;
                            if (key.includes('estado'))       obj.estado_matricula = val;
                            if (key.includes('cámara') || key.includes('camara')) obj.nom_camara = val;
                            if (key.includes('matrícula') || key.includes('matricula')) obj.matricula = val;
                            if (key.includes('categor'))      obj.categoria = val;
                        }
                        results.push(obj);
                    });
                    return results;
                }
            """)

            if records:
                return self._parse_registros(records, nit, expected_name=name)

        except Exception as e:
            await self._emit_log(f"RUES query error: {e}", "warn")
        return None

    def _parse_registros(self, registros: list, nit_clean: str, expected_name: str = "") -> Optional[dict]:
        if not registros:
            return None

        # Preferir resultado VIGENTE; si hay varios, el que más se parece al nombre buscado
        def score(rec):
            estado = rec.get("estado_matricula", "").upper()
            vigente_bonus = 100 if any(v in estado for v in ("VIGENTE", "ACTIV", "INSCRIT")) else 0
            name_match = 0
            if expected_name:
                exp = self._strip_accents(expected_name).upper()
                got = self._strip_accents(rec.get("razon_social", "")).upper()
                # Contar palabras del nombre esperado que aparecen en el resultado
                words = [w for w in exp.split() if len(w) > 3]
                name_match = sum(1 for w in words if w in got) * 10
            return vigente_bonus + name_match

        rec = max(registros, key=score)
        estado_raw = rec.get("estado_matricula", "").upper()

        if "VIGENTE" in estado_raw or "ACTIV" in estado_raw or "INSCRIT" in estado_raw:
            estado = "VIGENTE"
        elif "CANCEL" in estado_raw:
            estado = "CANCELADO"
        elif "INACTIV" in estado_raw or "LIQUIDAD" in estado_raw:
            estado = "INACTIVO"
        else:
            estado = estado_raw or "DESCONOCIDO"

        return {
            "rues_status":        estado,
            "rues_name":          rec.get("razon_social", "").strip(),
            "nit":                nit_clean or rec.get("nit", ""),
            "city":               rec.get("nom_camara", "").strip(),
            "matricula":          rec.get("matricula", ""),
            "organizacion":       rec.get("organizacion_juridica", ""),
            "ultimo_renovado":    rec.get("ultimo_ano_renovado", ""),
            "rues_checked":       datetime.now().isoformat(),
        }

    # ── Validación individual ──────────────────────────────────────────────────
    async def validate_single(self, company: dict) -> dict:
        result = dict(company)
        nit  = self.clean_nit(company.get("nit", ""))
        name = company.get("name", "")

        data = await self._query_rues(nit=nit, name="" if nit else name[:40])

        if data:
            result.update(data)
        else:
            result["rues_status"]  = "NO_ENCONTRADO"
            result["rues_checked"] = datetime.now().isoformat()
        return result

    # ── Validación en lote (abre browser UNA vez para todo el lote) ────────────
    async def validate_batch(
        self,
        companies: list[dict],
        progress_cb: Optional[Callable] = None,
        delay: float = 2.0,
    ) -> list[dict]:
        self._stop = False
        validated  = []
        total      = len(companies)
        delay      = 1.0          # reducido de 2.0s

        await self._emit_log(f"🌐 Iniciando browser RUES para validar {total} empresas...")
        try:
            await self._open_browser()
        except Exception as e:
            await self._emit_log(f"❌ No se pudo abrir browser RUES: {e}", "error")
            # Fallback: marcar todas como NO_ENCONTRADO
            for company in companies:
                r = dict(company)
                r["rues_status"]  = "NO_ENCONTRADO"
                r["rues_checked"] = datetime.now().isoformat()
                validated.append(r)
            return validated

        try:
            for i, company in enumerate(companies):
                if self._stop:
                    break
                if progress_cb:
                    await progress_cb(i + 1, total, company.get("name", ""))

                result = await self.validate_single(company)
                validated.append(result)

                icon = "✅" if result.get("rues_status") == "VIGENTE" else "❌"
                await self._emit_log(
                    f"{icon} [{i+1}/{total}] {company.get('name','N/A')} "
                    f"→ {result.get('rues_status','?')} "
                    f"({result.get('rues_name','')})"
                )

                if i < total - 1:
                    await asyncio.sleep(delay)
        finally:
            await self._close_browser()

        vigentes = sum(1 for c in validated if c.get("rues_status") == "VIGENTE")
        await self._emit_log(f"✅ Validación completa: {vigentes}/{total} VIGENTES")
        return validated

    # ── Validación directa desde el chat ──────────────────────────────────────
    async def validate_nit_direct(self, nit: str) -> dict:
        nit_clean = self.clean_nit(nit)
        await self._emit_log(f"Consultando NIT {nit_clean} en RUES...")
        try:
            await self._open_browser()
            result = await self._query_rues(nit=nit_clean)
            await self._close_browser()
            if result:
                return result
        except Exception as e:
            await self._emit_log(f"Error: {e}", "warn")
            await self._close_browser()
        return {
            "nit":          nit_clean,
            "rues_status":  "NO_ENCONTRADO",
            "rues_checked": datetime.now().isoformat(),
            "message":      f"NIT {nit} no encontrado en RUES.",
        }
