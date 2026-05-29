"""
Setup de autenticación de LinkedIn con Playwright.
Abre un browser visible para que inicies sesión manualmente.
Las cookies se guardan para uso futuro del pipeline.

Uso:
    python setup_linkedin_auth.py
"""

import asyncio
import json
from pathlib import Path

COOKIES_FILE = Path(__file__).parent / "linkedin_cookies.json"


async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright no instalado.")
        print("   Instala con: pip install playwright && playwright install chromium")
        return

    print("=" * 60)
    print("  🔐 LinkedIn Authentication Setup")
    print("  Se abrirá un browser. Inicia sesión en LinkedIn.")
    print("  Las cookies se guardarán automáticamente.")
    print("=" * 60)
    print()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=["--window-size=1200,800"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🌐 Abriendo LinkedIn...")
        await page.goto("https://www.linkedin.com/login?originalReferer=")
        print("👤 Por favor inicia sesión en el browser que se abrió.")
        print("⏳ Esperando hasta 120 segundos...")
        print()

        try:
            # Esperar a que llegue al feed
            await page.wait_for_url("**/feed/**", timeout=120000)
            print("✅ Login detectado exitosamente!")

            # Guardar cookies
            cookies = await context.cookies()
            with open(COOKIES_FILE, "w") as f:
                json.dump(cookies, f, indent=2)

            print(f"💾 Cookies guardadas en: {COOKIES_FILE}")
            print(f"   ({len(cookies)} cookies guardadas)")
            print()
            print("🚀 LinkedIn autenticado. Ya puedes ejecutar el pipeline.")

        except Exception:
            print("⚠️  Timeout — no se detectó el login a tiempo.")
            print("   Intenta de nuevo o revisa tus credenciales.")
        finally:
            await asyncio.sleep(2)
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
