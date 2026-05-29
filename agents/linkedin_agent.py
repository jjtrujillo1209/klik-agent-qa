"""
Agent 3: LinkedIn Decision Maker Finder
Busca directores/gerentes usando LinkedIn regular (búsqueda de personas).
Enriquece email con Apollo people/match y teléfono con Lusha v2.
"""

import asyncio
import json
import os
import re
import unicodedata
import urllib.parse
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

BASE_DIR     = Path(__file__).parent.parent
COOKIES_FILE = BASE_DIR / "linkedin_cookies.json"

DEFAULT_TARGET_TITLES = [
    "Director de Mantenimiento", "Gerente de Mantenimiento",
    "Director de Planta",        "Gerente de Planta",
    "Director de Operaciones",   "Director General",
    "Gerente General",           "COO",
    "Director de Producción",    "Gerente de Producción",
]


class LinkedInAgent:

    def __init__(self, emit_fn: Optional[Callable] = None):
        self.emit     = emit_fn or (lambda x: None)
        self._stop    = False
        self._browser = None
        self._pw_ctx  = None
        self._page    = None
        self._ctx     = None

    def stop(self):
        self._stop = True

    async def _emit_log(self, msg: str, level: str = "info"):
        await self.emit({
            "type": "agent_log", "agent": "linkedin_agent",
            "level": level, "message": msg,
            "timestamp": datetime.now().isoformat()
        })

    # ── Browser ────────────────────────────────────────────────────────────────

    async def _open_browser(self):
        from playwright.async_api import async_playwright
        self._pw_ctx = async_playwright()
        pw = await self._pw_ctx.__aenter__()
        self._browser = await pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        self._ctx = await self._browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        if COOKIES_FILE.exists():
            cookies = json.loads(COOKIES_FILE.read_text())
            await self._ctx.add_cookies(cookies)
        self._page = await self._ctx.new_page()
        await self._emit_log("🔒 Browser LinkedIn listo")

    async def _close_browser(self):
        try:
            if self._ctx:
                cookies = await self._ctx.cookies()
                COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
            if self._browser:
                await self._browser.close()
            if self._pw_ctx:
                await self._pw_ctx.__aexit__(None, None, None)
        except Exception:
            pass
        self._page = self._browser = self._pw_ctx = self._ctx = None

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        nfd = unicodedata.normalize("NFD", text.lower())
        return "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Palabras genéricas que NO sirven como identificador único de empresa
    _GENERIC_WORDS = {
        "de","del","la","el","los","las","y","en","sa","sas","ltda","spa",
        "colombia","grupo","corp","inc","co","empresa","industria","industrias",
        "compania","nacional","servicios","productos","comercial","internacional",
        "transporte","logistica","energia","soluciones","tecnologia","alimentos",
        "petroleo","gas","mineria","construccion","salud","finanzas","inversiones",
    }

    def _company_matches(self, company: str, card_text: str) -> bool:
        """
        Exige que al menos UNA palabra específica de la empresa (no genérica)
        aparezca en el texto de la tarjeta. Esto evita falsos positivos donde
        palabras comunes como 'transporte' o 'logistica' matchean perfiles
        de empresas completamente distintas.
        """
        all_words = [w for w in re.split(r'\W+', self._normalize(company)) if len(w) > 3]
        # Palabras específicas: las que NO son genéricas
        specific = [w for w in all_words if w not in self._GENERIC_WORDS]
        # Si no hay palabras específicas, usar todas las que tengamos
        keywords = specific if specific else all_words
        if not keywords:
            return True

        ct = self._normalize(card_text)
        # Debe aparecer al menos UNA palabra específica en la tarjeta
        return any(w in ct for w in keywords)

    def _relevant_title(self, title: str) -> bool:
        kws = ["director","gerente","jefe","coo","mantenimiento","planta",
               "operaciones","produccion","general","cfo","financiero","compras"]
        return any(k in self._normalize(title) for k in kws)

    # ── Búsqueda LinkedIn regular ──────────────────────────────────────────────

    # Sufijos/formas legales colombianas + internacionales
    _LEGAL_RE = re.compile(
        r'(?<!\w)'                                      # no precedido de letra
        r'(S\.?\s*A\.?\s*S\.?|S\.?\s*C\.?\s*A\.?|'    # S.A.S / S.C.A
        r'S\.?\s*A\.?|SAS|SA|'                          # S.A / SAS / SA
        r'LTDA\.?|LLC|CORP\.?|INC\.?|GMBH|AG|LTD\.?|' # formas internacionales
        r'CORPORACION|COOPERATIVA|'
        r'SUCURSAL\s+COLOMBIA|SUCURSAL|'
        r'E\.?\s*S\.?\s*P\.?|BIC|'                     # E.S.P. / BIC
        r'LIMITED|COMPANY|COMPANIA|'
        r'&\s*CIA\.?|CIA\.?|'                           # & CIA / CIA
        r'HERMANOS)'
        r'(?!\w)',                                       # no seguido de letra
        re.IGNORECASE,
    )
    # Palabras genéricas a eliminar si quedan sueltas tras limpiar sufijos
    _GENERIC_RE = re.compile(
        r'\b(DE|DEL|LA|EL|LOS|LAS|Y|EN|&)\b',
        re.IGNORECASE,
    )

    def _name_variants(self, company: str) -> list[str]:
        """Devuelve hasta 3 variantes progresivamente más cortas del nombre."""
        # 1) Quitar sufijos legales
        cleaned = self._LEGAL_RE.sub(' ', company)
        # 2) Quitar puntuación y guiones sueltos
        cleaned = re.sub(r'[\.\,\-]+', ' ', cleaned)
        # 3) Colapsar espacios y strip
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # 4) Quitar palabras de 1-2 letras que quedaron sueltas
        words = [w for w in cleaned.split() if len(w) > 2]
        cleaned = ' '.join(words)

        variants: list[str] = []

        # Variante 1: nombre completo limpio
        if cleaned and cleaned.upper() != company.strip().upper():
            variants.append(cleaned)

        # Variante 2: primeras 3 palabras significativas
        short = ' '.join(words[:3]) if len(words) > 3 else cleaned
        if short and short not in variants:
            variants.append(short)

        # Variante 3: primera palabra (marca raíz, mínimo 4 chars)
        first = words[0] if words else ''
        if len(first) >= 4 and first not in variants:
            variants.append(first)

        # Fallback si no logramos extraer nada
        if not variants:
            variants.append(company.split()[0] if company.split() else company)

        return [v for v in variants if v][:3]

    def _search_url(self, name_variant: str) -> str:
        # Query simple sin comillas ni OR encadenados (LinkedIn lo maneja mejor)
        query = f'{name_variant} director gerente mantenimiento planta operaciones'
        return (
            "https://www.linkedin.com/search/results/people/"
            f"?keywords={urllib.parse.quote(query)}&origin=GLOBAL_SEARCH_HEADER"
        )

    async def _get_cards(self) -> list[dict]:
        """Extrae tarjetas de la página de resultados usando JS sobre atributos estables."""
        # Scroll para cargar resultados lazy
        for _ in range(3):
            await self._page.evaluate("window.scrollBy(0, 700)")
            await asyncio.sleep(0.6)

        return await self._page.evaluate("""
            () => {
                const seen = new Set();
                const results = [];
                for (const a of document.querySelectorAll('a[href*="/in/"]')) {
                    const url = a.href.split('?')[0];
                    if (!url.includes('linkedin.com/in/') || seen.has(url)) continue;
                    seen.add(url);

                    const container = a.closest('li') || a.closest('[data-view-name]') || a;
                    const cardText  = container.innerText || '';
                    const lines     = cardText.split('\\n').map(l => l.trim()).filter(Boolean);

                    const name = lines[0] || '';
                    if (name.length < 3 || name.toLowerCase().includes('linkedin')) continue;

                    // Headline: primera línea que no sea nombre ni grado ("• 2nd")
                    let title = '';
                    for (let i = 1; i < lines.length; i++) {
                        if (!lines[i].startsWith('•') && lines[i].length > 3) {
                            title = lines[i];
                            break;
                        }
                    }

                    results.push({ name, title, cardText, url });
                    if (results.length >= 20) break;
                }
                return results;
            }
        """)

    async def _get_current_company(self, profile_url: str) -> str:
        """Visita el perfil y extrae la empresa actual (header o primera experiencia)."""
        try:
            await self._page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            result = await self._page.evaluate("""
                () => {
                    // 1. Empresa mostrada en el panel derecho del header (UI nueva)
                    const headerCompany = document.querySelector(
                        '.pv-text-details__right-panel .hoverable-link-text, ' +
                        '.pv-text-details__right-panel .inline-show-more-text, ' +
                        '.top-card-layout__company'
                    );
                    if (headerCompany && headerCompany.innerText.trim())
                        return headerCompany.innerText.trim();

                    // 2. Link de empresa en el header
                    const headerLink = document.querySelector(
                        '.pv-text-details__right-panel a[href*="/company/"], ' +
                        '.top-card__subline-item a[href*="/company/"]'
                    );
                    if (headerLink && headerLink.innerText.trim())
                        return headerLink.innerText.trim();

                    // 3. Primera entrada en Experiencia
                    const expSection = document.querySelector(
                        '#experience ~ .pvs-list__outer-container, ' +
                        'section:has(#experience) .pvs-list__outer-container'
                    );
                    if (expSection) {
                        const firstItem = expSection.querySelector('.pvs-entity');
                        if (firstItem) {
                            // Nombre de empresa en negrita dentro del item
                            const bold = firstItem.querySelector('.t-bold span[aria-hidden="true"]');
                            if (bold && bold.innerText.trim()) return bold.innerText.trim();
                            // Fallback: link a empresa
                            const link = firstItem.querySelector('a[href*="/company/"]');
                            if (link && link.innerText.trim()) return link.innerText.trim();
                        }
                    }

                    // 4. Cualquier link /company/ visible en la mitad superior
                    const allCompLinks = document.querySelectorAll('a[href*="/company/"]');
                    for (const cl of allCompLinks) {
                        const txt = cl.innerText.trim();
                        if (txt.length > 2) return txt;
                    }
                    return '';
                }
            """)
            return (result or "").strip()
        except Exception:
            return ""

    # ── Enriquecimiento ────────────────────────────────────────────────────────

    @staticmethod
    def _apollo_email(name: str, company: str) -> Optional[str]:
        key = os.getenv("APOLLO_API_KEY")
        if not key:
            return None
        parts = name.split()
        try:
            import requests as req
            r = req.post(
                "https://api.apollo.io/v1/people/match",
                json={
                    "api_key": key,
                    "first_name": parts[0] if parts else name,
                    "last_name":  parts[-1] if len(parts) > 1 else "",
                    "organization_name": company,
                    "reveal_personal_emails": True,
                },
                timeout=12,
            )
            if r.ok:
                return (r.json().get("person") or {}).get("email")
        except Exception:
            pass
        return None

    @staticmethod
    def _lusha_phone(name: str, company: str) -> dict:
        key = os.getenv("LUSHA_API_KEY")
        out = {"phone": None, "phone_verified": False, "email": None}
        if not key:
            return out
        parts = name.split()
        domain = re.sub(r"[^a-z0-9]", "", company.lower().split()[0]) + ".com"
        try:
            import requests as req
            r = req.get(
                "https://api.lusha.com/v2/person",
                params={
                    "firstName": parts[0] if parts else name,
                    "lastName":  parts[-1] if len(parts) > 1 else "",
                    "companyDomain": domain,
                },
                headers={"api_key": key},
                timeout=10,
            )
            if r.ok:
                d = r.json()
                ph = d.get("phoneNumbers", [])
                em = d.get("emailAddresses", [])
                if ph:
                    out["phone"]          = ph[0].get("internationalNumber")
                    out["phone_verified"] = ph[0].get("isVerified", False)
                if em:
                    out["email"] = em[0].get("validatedEmail")
        except Exception:
            pass
        return out

    # ── Punto de entrada ───────────────────────────────────────────────────────

    async def find_decision_makers(
        self,
        companies: list[dict],
        titles: list[str] = None,
        progress_cb: Optional[Callable] = None,
        max_per_company: int = 3,
    ) -> list[dict]:
        self._stop   = False
        contacts     = []
        seen_urls: set[str] = set()   # deduplicación global por URL LinkedIn
        total        = len(companies)

        if not COOKIES_FILE.exists():
            await self._emit_log(
                "⚠️ Sin cookies LinkedIn — ejecuta setup_linkedin_auth.py para autenticar.", "warn"
            )
            return []

        try:
            await self._open_browser()
        except Exception as e:
            await self._emit_log(f"❌ No se pudo abrir browser LinkedIn: {e}", "error")
            return []

        await self._emit_log("🔒 Modo autenticado (cookies LinkedIn)")

        # Warm-up: visitar el feed antes de hacer búsquedas
        try:
            await self._page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3)
            if "linkedin.com/login" in self._page.url or "authwall" in self._page.url:
                await self._emit_log("⚠️ Sesión expirada. Ejecuta setup_linkedin_auth.py", "error")
                await self._close_browser()
                return []
            await self._emit_log("✅ Sesión LinkedIn verificada")
        except Exception as e:
            await self._emit_log(f"⚠️ Warm-up timeout ({e}) — continuando igual", "warn")

        try:
            for i, company in enumerate(companies):
                if self._stop:
                    break
                if progress_cb:
                    await progress_cb(i + 1, total, company.get("name", ""))

                name = company.get("name", "").strip()
                if not name:
                    continue

                found = await self._search(name, max_per_company)
                added = 0
                for c in found:
                    url = c.get("linkedin_url", "")
                    if url and url in seen_urls:
                        await self._emit_log(f"↩ Duplicado omitido: {c.get('name','')} ({url})", "warn")
                        continue
                    if url:
                        seen_urls.add(url)
                    c["company_name"] = name
                    c["company_nit"]  = company.get("nit", "")
                    c["company_city"] = company.get("city", "")
                    contacts.append(c)
                    added += 1

                await self._emit_log(f"[{i+1}/{total}] {name}: {added} contacto(s)")
                await asyncio.sleep(2.5)

        finally:
            await self._close_browser()

        await self._emit_log(f"✅ Total: {len(contacts)} decision makers")
        return contacts

    async def _ensure_logged_in(self) -> bool:
        """Verifica que la sesión LinkedIn esté activa; retorna False si expiró."""
        try:
            current = self._page.url
            if "linkedin.com/login" in current or "linkedin.com/authwall" in current:
                await self._emit_log("⚠️ Sesión LinkedIn expirada — re-autenticar con setup_linkedin_auth.py", "warn")
                return False
        except Exception:
            pass
        return True

    async def _search(self, company: str, max_res: int) -> list[dict]:
        """Prueba variantes del nombre progresivamente hasta encontrar resultados."""
        variants = self._name_variants(company)
        await self._emit_log(f"🔍 Variantes: {variants}")

        for variant in variants:
            contacts = await self._search_variant(company, variant, max_res)
            if contacts:
                return contacts
            # Pequeña pausa entre variantes
            await asyncio.sleep(2)

        return []

    async def _search_variant(self, company: str, variant: str, max_res: int) -> list[dict]:
        contacts = []
        try:
            url = self._search_url(variant)

            # Navegación con un retry
            for attempt in range(2):
                try:
                    await self._page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    break
                except Exception as e:
                    if attempt == 0:
                        await self._emit_log(f"Reintentando '{variant}'…", "warn")
                        await asyncio.sleep(5)
                    else:
                        raise e

            await asyncio.sleep(3)

            if not await self._ensure_logged_in():
                return []

            # Esperar a que aparezca algún resultado
            try:
                await self._page.wait_for_function(
                    "() => document.querySelector('a[href*=\"/in/\"]') !== null",
                    timeout=15000,
                )
            except Exception:
                pass

            cards = await self._get_cards()

            if not cards:
                await self._emit_log(f"Sin resultados con '{variant}' — probando siguiente variante")
                return []

            for card in cards:
                if len(contacts) >= max_res:
                    break

                name     = card.get("name", "")
                title    = card.get("title", "")
                li_url   = card.get("url", "")
                card_txt = card.get("cardText", "")

                if not name or len(name) < 3:
                    continue
                if not self._relevant_title(title):
                    continue
                if not self._company_matches(company, card_txt):
                    continue

                contacts.append({
                    "name":         name,
                    "title":        title,
                    "linkedin_url": li_url,
                    "email":        "",
                    "phone":        "",
                    "source":       "LinkedIn",
                })

        except Exception as e:
            await self._emit_log(f"Error buscando '{variant}': {e}", "warn")

        return contacts

    # ── Setup auth ────────────────────────────────────────────────────────────

    async def setup_auth_interactive(self):
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            await self._emit_log("Instala playwright: pip install playwright && playwright install chromium", "error")
            return
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=False)
            ctx     = await browser.new_context()
            page    = await ctx.new_page()
            await page.goto("https://www.linkedin.com/login")
            await self._emit_log("🌐 Browser abierto — inicia sesión en LinkedIn (60s)")
            try:
                await page.wait_for_url("**/feed/**", timeout=60000)
                cookies = await ctx.cookies()
                COOKIES_FILE.write_text(json.dumps(cookies, indent=2))
                await self._emit_log(f"✅ {len(cookies)} cookies guardadas")
            except Exception:
                await self._emit_log("⚠️ Timeout en login", "warn")
            finally:
                await browser.close()
