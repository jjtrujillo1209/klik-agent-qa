"""
Scrappling Adapter
==================
Integra Scrappling como fuente de datos para el pipeline de leads.

Scrappling puede ser usado de dos formas:
  1. OUTPUT WATCHER: Lee CSVs/JSONs que Scrappling exporta a una carpeta
  2. HTTP API: Si Scrappling expone un endpoint local (modo servidor)

Cómo usar Scrappling con este sistema:
---------------------------------------
  a) Configura Scrappling para exportar resultados a:
       /06-INFRAESTRUCTURA/lead-genai-system/scrappling_input/
  b) O configura Scrappling en modo API en http://localhost:3333

El adapter detecta automáticamente qué modo usar.
"""

import asyncio
import csv
import json
import os
from pathlib import Path
from typing import Callable, Optional, AsyncGenerator
from datetime import datetime
import httpx


# Directorio donde Scrappling puede depositar sus outputs
SCRAPPLING_INPUT_DIR = Path(__file__).parent.parent / "scrappling_input"
SCRAPPLING_INPUT_DIR.mkdir(exist_ok=True)

# Puerto por defecto si Scrappling corre como servidor HTTP local
SCRAPPLING_API_PORT = int(os.getenv("SCRAPPLING_API_PORT", "3333"))
SCRAPPLING_API_URL = f"http://localhost:{SCRAPPLING_API_PORT}"

# Archivos ya procesados (evitar duplicados)
PROCESSED_FILE = Path(__file__).parent.parent / "checkpoints" / "scrappling_processed.json"


class ScrapplingAdapter:
    """
    Puente entre Scrappling y el pipeline de Lead GenAI.
    Detecta automáticamente el modo disponible (API o file watcher).
    """

    def __init__(self, emit_fn: Optional[Callable] = None):
        self.emit = emit_fn or (lambda x: None)
        self._stop = False
        self._processed = self._load_processed()
        self._mode = None  # 'api' | 'files' | None

    def stop(self):
        self._stop = True

    async def _emit_log(self, msg: str, level: str = "info"):
        await self.emit({
            "type": "agent_log",
            "agent": "scrappling",
            "level": level,
            "message": msg,
            "timestamp": datetime.now().isoformat()
        })

    def _load_processed(self) -> set:
        PROCESSED_FILE.parent.mkdir(exist_ok=True)
        if PROCESSED_FILE.exists():
            try:
                return set(json.loads(PROCESSED_FILE.read_text()))
            except Exception:
                return set()
        return set()

    def _save_processed(self):
        PROCESSED_FILE.write_text(json.dumps(list(self._processed)))

    async def detect_mode(self) -> str:
        """Detecta si Scrappling está disponible vía API o como exportador de archivos"""
        # Primero intentar API local
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                resp = await client.get(f"{SCRAPPLING_API_URL}/health")
                if resp.status_code == 200:
                    self._mode = "api"
                    await self._emit_log(f"✅ Scrappling API detectada en {SCRAPPLING_API_URL}")
                    return "api"
        except Exception:
            pass

        # Verificar si hay archivos en el directorio de entrada
        files = list(SCRAPPLING_INPUT_DIR.glob("*.csv")) + list(SCRAPPLING_INPUT_DIR.glob("*.json"))
        if files:
            self._mode = "files"
            await self._emit_log(f"📁 Scrappling: {len(files)} archivo(s) encontrados en {SCRAPPLING_INPUT_DIR.name}/")
            return "files"

        self._mode = None
        await self._emit_log(
            f"ℹ️ Scrappling no detectado. Coloca archivos CSV/JSON en: scrappling_input/",
            "info"
        )
        return "none"

    async def get_companies(self, params: dict = {}) -> list[dict]:
        """
        Obtiene empresas desde Scrappling.
        Returns lista vacía si Scrappling no está disponible.
        """
        mode = await self.detect_mode()

        if mode == "api":
            return await self._get_from_api(params)
        elif mode == "files":
            return await self._get_from_files()
        return []

    async def _get_from_api(self, params: dict) -> list[dict]:
        """Obtiene datos de la API de Scrappling"""
        companies = []
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Intentar endpoint de búsqueda de empresas
                payload = {
                    "query": params.get("keywords", "empresa industrial Colombia"),
                    "sector": params.get("sector", "manufactura"),
                    "limit": params.get("limit", 20)
                }

                for endpoint in ["/scrape/companies", "/search", "/companies"]:
                    try:
                        resp = await client.post(f"{SCRAPPLING_API_URL}{endpoint}", json=payload)
                        if resp.status_code == 200:
                            data = resp.json()
                            companies = self._normalize_companies(
                                data.get("results", data.get("companies", data if isinstance(data, list) else []))
                            )
                            await self._emit_log(f"✅ Scrappling API: {len(companies)} empresas obtenidas")
                            break
                    except Exception:
                        continue
        except Exception as e:
            await self._emit_log(f"Scrappling API error: {e}", "warn")
        return companies

    async def _get_from_files(self) -> list[dict]:
        """Lee archivos CSV/JSON exportados por Scrappling"""
        companies = []
        new_files = []

        all_files = (
            list(SCRAPPLING_INPUT_DIR.glob("*.csv")) +
            list(SCRAPPLING_INPUT_DIR.glob("*.json"))
        )

        for file_path in all_files:
            if str(file_path) in self._processed:
                continue  # Ya procesado
            new_files.append(file_path)

        if not new_files:
            await self._emit_log("ℹ️ No hay archivos nuevos en scrappling_input/")
            return []

        for file_path in new_files:
            if self._stop:
                break
            try:
                if file_path.suffix == ".csv":
                    parsed = self._parse_csv(file_path)
                elif file_path.suffix == ".json":
                    parsed = self._parse_json(file_path)
                else:
                    continue

                normalized = self._normalize_companies(parsed)
                companies.extend(normalized)
                self._processed.add(str(file_path))
                await self._emit_log(f"📄 {file_path.name}: {len(normalized)} empresas")

            except Exception as e:
                await self._emit_log(f"Error leyendo {file_path.name}: {e}", "warn")

        self._save_processed()
        await self._emit_log(f"✅ Scrappling: {len(companies)} empresas totales de {len(new_files)} archivo(s)")
        return companies

    def _parse_csv(self, path: Path) -> list[dict]:
        """Parsea CSV de Scrappling"""
        rows = []
        try:
            with open(path, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
        except UnicodeDecodeError:
            with open(path, encoding="latin-1") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(dict(row))
        return rows

    def _parse_json(self, path: Path) -> list[dict]:
        """Parsea JSON de Scrappling"""
        data = json.loads(path.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ["results", "companies", "data", "items"]:
                if key in data and isinstance(data[key], list):
                    return data[key]
        return [data] if isinstance(data, dict) else []

    def _normalize_companies(self, raw: list[dict]) -> list[dict]:
        """Normaliza datos al formato estándar del pipeline"""
        normalized = []
        for item in raw:
            if not item:
                continue

            # Detectar campos comunes de diferentes herramientas
            name = (
                item.get("razon_social") or
                item.get("company_name") or
                item.get("name") or
                item.get("nombre") or
                item.get("empresa") or
                item.get("Company") or
                item.get("Empresa") or ""
            )

            nit = (
                item.get("nit") or
                item.get("NIT") or
                item.get("tax_id") or
                item.get("rut") or ""
            )

            city = (
                item.get("city") or
                item.get("ciudad") or
                item.get("municipio") or
                item.get("City") or ""
            )

            if name and len(str(name)) > 2:
                normalized.append({
                    "name": str(name).strip(),
                    "nit": str(nit).strip(),
                    "city": str(city).strip(),
                    "source": "Scrappling",
                    "rues_status": "PENDIENTE",
                    # Preservar datos extras
                    "_raw": item
                })
        return normalized

    async def watch_for_new_files(
        self,
        callback: Callable,
        interval: float = 5.0
    ):
        """
        Observa la carpeta de Scrappling y llama callback cuando hay nuevos archivos.
        Útil para integración en tiempo real.
        """
        await self._emit_log(f"👁️ Observando: {SCRAPPLING_INPUT_DIR.name}/ (cada {interval}s)")
        while not self._stop:
            companies = await self._get_from_files()
            if companies:
                await callback(companies)
            await asyncio.sleep(interval)

    @staticmethod
    def get_input_dir() -> Path:
        """Retorna el directorio donde Scrappling debe depositar sus outputs"""
        return SCRAPPLING_INPUT_DIR

    @staticmethod
    def get_setup_instructions() -> str:
        return f"""
🔧 CONFIGURAR SCRAPPLING CON LEAD GENAI:

Opción A - Exportar archivos:
  1. En Scrappling, configura el directorio de export:
     {SCRAPPLING_INPUT_DIR}
  2. Scrappling puede exportar CSV o JSON
  3. El pipeline detectará automáticamente los nuevos archivos

Opción B - API local:
  1. Activa Scrappling en modo servidor (puerto {SCRAPPLING_API_PORT})
  2. Configura en .env: SCRAPPLING_API_PORT={SCRAPPLING_API_PORT}
  3. El pipeline consultará /search o /companies automáticamente

Columnas recomendadas en CSV:
  razon_social | nit | ciudad | ciiu | sector | url
"""
