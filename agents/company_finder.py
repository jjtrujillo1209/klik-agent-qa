"""
Agent 1: Company Finder
Fuentes en orden de prioridad:
  1. scrappling_input/ — archivos CSV/JSON que el usuario coloca manualmente
  2. RUES Playwright  — búsqueda por keyword (comparte browser con nit_resolver si está disponible)
  3. Seed conocidas   — lista curada de grandes consumidores MNR colombianos;
                        toda empresa de aquí se valida en tiempo real en RUES (paso 2)
                        y sus decision makers se buscan en LinkedIn (paso 3).
Sin datos inventados: las seeds son empresas reales, el estado RUES y contactos
son siempre consultados en vivo.
"""

import asyncio
import re
from typing import Callable, Optional
from datetime import datetime

try:
    from agents.scrappling_adapter import ScrapplingAdapter
    SCRAPPLING_AVAILABLE = True
except ImportError:
    SCRAPPLING_AVAILABLE = False

try:
    from agents.web_energy_search import WebEnergySearch
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False

RUES_ADV_URL = "https://www.rues.org.co/busqueda-avanzada"

INACTIVE_KEYWORDS = {
    "EN LIQUIDACION", "LIQUIDACION", "DISUELTO", "DISUELTA",
    "CANCELADO", "CANCELADA", "EXTINGUIDA", "EXTINGUIDO",
    "EN EJECUCION", "INTERVENIDA",
}


SECTOR_KEYWORDS = {
    "cemento":             ["CEMENTOS", "CONCRETOS"],
    "alimentos":           ["ALIMENTOS", "LACTEOS", "BEBIDAS"],
    "quimica":             ["QUIMICA", "QUIMICOS", "FARMACEUTICA"],
    "plasticos":           ["PLASTICOS", "POLIMEROS"],
    "textil":              ["TEXTIL", "CONFECCIONES"],
    "mineria":             ["MINERA", "CARBON"],
    "papel":               ["PAPEL", "CARTON"],
    "ceramica":            ["CERAMICA", "VIDRIO"],
    "metal":               ["ACEROS", "METALURGICA"],
    "maquinaria":          ["MAQUINARIA", "EQUIPOS"],
    "hospitales_grandes":  ["CLINICA", "HOSPITAL"],
    "centros_comerciales": ["CENTRO COMERCIAL", "MALL"],
    "all":                 ["INDUSTRIA", "MANUFACTURA", "PLANTA"],
}

# Grandes consumidores MNR Colombia — validados en tiempo real en paso 2
MNR_SEED: list[dict] = [
    {"name": "Cementos Argos S.A.",        "sector": "cemento",    "city": "Medellín"},
    {"name": "Holcim Colombia S.A.",        "sector": "cemento",    "city": "Bogotá"},
    {"name": "Cementos San Marcos S.A.",    "sector": "cemento",    "city": "Bogotá"},
    {"name": "Grupo Nutresa S.A.",          "sector": "alimentos",  "city": "Medellín"},
    {"name": "Postobón S.A.",               "sector": "alimentos",  "city": "Medellín"},
    {"name": "Alpina S.A.",                 "sector": "alimentos",  "city": "Bogotá"},
    {"name": "Familia S.A.",                "sector": "papel",      "city": "Medellín"},
    {"name": "Cartón de Colombia S.A.",     "sector": "papel",      "city": "Cali"},
    {"name": "Tecnoquímicas S.A.",          "sector": "quimica",    "city": "Cali"},
    {"name": "Bayer S.A.",                  "sector": "quimica",    "city": "Bogotá"},
    {"name": "Colcerámica S.A.",            "sector": "ceramica",   "city": "Bogotá"},
    {"name": "Pavco S.A.",                  "sector": "plasticos",  "city": "Bogotá"},
    {"name": "Acerías Paz del Río S.A.",    "sector": "metal",      "city": "Boyacá"},
    {"name": "Eternit Colombia S.A.",       "sector": "ceramica",   "city": "Bogotá"},
    {"name": "Colanta Cooperativa",         "sector": "alimentos",  "city": "Medellín"},
    {"name": "Alimentos Polar Colombia",    "sector": "alimentos",  "city": "Bogotá"},
    {"name": "Vidrio Andino S.A.",          "sector": "ceramica",   "city": "Bogotá"},
    {"name": "Indufrial S.A.",              "sector": "metal",      "city": "Bogotá"},
    {"name": "Cervecería del Valle S.A.",   "sector": "alimentos",  "city": "Cali"},
    {"name": "Alicorp Colombia S.A.",       "sector": "alimentos",  "city": "Bogotá"},
]


class CompanyFinder:

    def __init__(self, emit_fn: Optional[Callable] = None):
        self.emit  = emit_fn or (lambda x: None)
        self._stop = False

    def stop(self):
        self._stop = True

    async def _emit_log(self, message: str, level: str = "info"):
        await self.emit({
            "type": "agent_log", "agent": "company_finder",
            "level": level, "message": message,
            "timestamp": datetime.now().isoformat()
        })

    async def find(self, params: dict) -> list[dict]:
        self._stop = False
        limit   = params.get("limit", 10)
        sector  = params.get("sector", "all")
        cities  = params.get("cities", [])
        exclude = {n.lower() for n in params.get("_exclude", [])}

        await self._emit_log(f"🔍 Buscando empresas — sector: {sector}, ciudades: {cities or 'todas'}")

        companies: list[dict] = []

        # ── Fuente 1: Web search (Claude + web_search tool) ──────────────────────
        if not self._stop and WEB_SEARCH_AVAILABLE:
            web = WebEnergySearch(emit_fn=self.emit)
            web_results = await web.search(sector, cities, limit)
            if web_results:
                companies.extend(web_results)
                await self._emit_log(f"🌐 Web search: {len(web_results)} empresas")

        # ── Fuente 2: archivos CSV/JSON externos ─────────────────────────────────
        if not self._stop and len(companies) < limit and SCRAPPLING_AVAILABLE:
            adapter = ScrapplingAdapter(emit_fn=self.emit)
            ext = await adapter.get_companies(params)
            if ext:
                companies.extend(ext)
                await self._emit_log(f"📂 Archivos externos: {len(ext)} empresas")

        # ── Fuente 3: RUES Playwright ─────────────────────────────────────────────
        if not self._stop and len(companies) < limit:
            keywords = SECTOR_KEYWORDS.get(sector, SECTOR_KEYWORDS["all"])
            rues = await self._search_rues_playwright(keywords[:2], limit - len(companies))
            if rues:
                companies.extend(rues)
                await self._emit_log(f"📋 RUES búsqueda: {len(rues)} empresas")

        # ── Fuente 4: Seed MNR — desactivada temporalmente ───────────────────────
        # await self._emit_log("🌱 Seed MNR desactivado")

        if not companies:
            await self._emit_log("⚠️ Sin empresas encontradas. Coloca un CSV en scrappling_input/", "warn")
            return []

        # Filtrar inactivas
        before = len(companies)
        companies = [
            c for c in companies
            if not any(kw in c["name"].upper() for kw in INACTIVE_KEYWORDS)
        ]
        removed = before - len(companies)
        if removed:
            await self._emit_log(f"🚫 {removed} empresa(s) en liquidación/canceladas eliminadas")

        # Deduplicar y excluir ya procesadas en rondas anteriores
        seen, unique = set(), []
        for c in companies:
            key = c["name"].lower().strip()
            if key not in seen and key not in exclude:
                seen.add(key)
                unique.append(c)

        result = unique[:limit]
        await self._emit_log(f"✅ {len(result)} empresas listas para validar en RUES")
        return result

    # ── RUES Playwright ───────────────────────────────────────────────────────
    async def _search_rues_playwright(self, keywords: list[str], limit: int) -> list[dict]:
        companies: list[dict] = []
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return []

        try:
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-web-security"],
                )
                ctx = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1280, "height": 800},
                )
                page = await ctx.new_page()

                for kw in keywords:
                    if self._stop or len(companies) >= limit:
                        break
                    try:
                        await page.goto(RUES_ADV_URL, timeout=60000, wait_until="domcontentloaded")
                        await asyncio.sleep(3)
                        await page.evaluate("document.querySelector('.swal2-container')?.remove()")
                        await asyncio.sleep(0.5)

                        # Click tab Nombre vía JS
                        await page.evaluate(
                            "(text) => { for (const b of document.querySelectorAll('button')) "
                            "if (b.textContent.trim().startsWith(text)) { b.click(); return; } }",
                            "Nombre",
                        )
                        await asyncio.sleep(1)

                        # Esperar input con timeout activo
                        try:
                            await page.wait_for_function(
                                "() => !!document.querySelector('[name=\"Razon\"]')",
                                timeout=8000,
                            )
                        except Exception:
                            await self._emit_log(f"RUES: input no apareció para '{kw}'", "warn")
                            continue

                        # Rellenar vía native setter
                        await page.evaluate(
                            "({sel, val}) => { const el = document.querySelector(sel); "
                            "if (!el) return; "
                            "const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; "
                            "s.call(el, val); "
                            "el.dispatchEvent(new Event('input',  {bubbles:true})); "
                            "el.dispatchEvent(new Event('change', {bubbles:true})); }",
                            {"sel": '[name="Razon"]', "val": kw},
                        )

                        # Click Buscar
                        await page.evaluate(
                            "() => document.querySelectorAll('button.btn-busqueda')"
                            ".forEach(b => { if (b.offsetParent) b.click(); })"
                        )
                        await page.evaluate(
                            "document.querySelectorAll('.swal2-container, [role=\"dialog\"]')"
                            ".forEach(el => el.remove())"
                        )

                        # Esperar cards
                        try:
                            await page.wait_for_function(
                                "() => document.querySelector('.card-result') !== null",
                                timeout=10000,
                            )
                        except Exception:
                            continue

                        records = await page.evaluate("""
                            () => Array.from(document.querySelectorAll('.card-result')).map(card => {
                                const lines = card.innerText.split('\\n')
                                    .map(l => l.trim()).filter(Boolean);
                                const obj = { razon_social: lines[0] || '' };
                                for (let i = 0; i < lines.length - 1; i++) {
                                    const k = lines[i].toLowerCase();
                                    if (k.includes('identificaci')) obj.nit    = lines[i+1];
                                    if (k.includes('cámara') || k.includes('camara'))
                                        obj.ciudad = lines[i+1];
                                }
                                return obj;
                            })
                        """)

                        for r in records:
                            name = (r.get("razon_social") or "").strip()
                            if name and len(name) > 3:
                                companies.append({
                                    "name":        name,
                                    "nit":         (r.get("nit") or "").strip(),
                                    "source":      "RUES",
                                    "city":        (r.get("ciudad") or "").strip(),
                                    "rues_status": "PENDIENTE",
                                })

                        await self._emit_log(f"  RUES '{kw}': {len(records)} resultados")
                        await asyncio.sleep(2)

                    except Exception as e:
                        await self._emit_log(f"RUES '{kw}': {e}", "warn")

                await browser.close()

        except Exception as e:
            await self._emit_log(f"Browser RUES: {e}", "warn")

        return companies[:limit]

    # ── Seed MNR ──────────────────────────────────────────────────────────────
    def _get_seed(self, sector: str, cities: list, limit: int) -> list[dict]:
        """Empresas reales del MNR colombiano — estado RUES y contactos se consultan en vivo."""
        pool = MNR_SEED
        if sector != "all":
            filtered = [c for c in pool if c.get("sector") == sector]
            pool = filtered if filtered else pool
        if cities:
            cities_lower = [c.lower() for c in cities]
            filtered = [c for c in pool if any(city in c.get("city","").lower() for city in cities_lower)]
            pool = filtered if filtered else pool

        return [
            {
                "name":        c["name"],
                "nit":         "",
                "source":      "MNR_target",
                "city":        c.get("city", ""),
                "rues_status": "PENDIENTE",
            }
            for c in pool[:limit]
        ]
