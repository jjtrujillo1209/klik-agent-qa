"""
Fuente web: búsqueda de empresas MNR Colombia via Claude + web_search tool.
Estrategia: múltiples búsquedas exhaustivas en directorios industriales, informes
de sostenibilidad y bases de datos públicas colombianas.

Criterio MNR: consumo eléctrico > 50.000 KWH/mes → mercado no regulado.
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Callable, Optional

SEARCH_MODEL = "claude-sonnet-4-6"

SECTOR_QUERIES: dict[str, list[str]] = {
    "cemento": [
        'empresas cementeras Colombia lista directorio "S.A." OR "S.A.S."',
        'planta cemento Colombia manufactura gran consumidor energía eléctrica KWH',
        'empresa cementera Colombia "consumo energético" KWH informe sostenibilidad',
        'CEMENTOS Colombia directorio industrial empresa manufactura',
        'site:paginasamarillas.com.co cementos concretos Colombia',
    ],
    "alimentos": [
        'empresas industria alimentos Colombia directorio "S.A." OR "S.A.S." manufactura',
        'industria alimentos bebidas Colombia "consumo de energía eléctrica" KWH reporte',
        'empresa alimentos Colombia planta industrial gran consumidor energía',
        'site:paginasamarillas.com.co industria alimentos Colombia empresa',
        'directorio empresas alimentos procesados Colombia manufactura industrial',
    ],
    "quimica": [
        'empresa química farmacéutica Colombia directorio industrial "S.A."',
        'empresa química Colombia "consumo energético" KWH informe ambiental',
        'industria química Colombia gran consumidor energía eléctrica planta',
        'site:paginasamarillas.com.co química farmacéutica Colombia empresa',
    ],
    "plasticos": [
        'empresa plásticos polímeros Colombia directorio industrial gran consumidor',
        'empresa plásticos Colombia consumo energía eléctrica industrial KWH',
        'site:paginasamarillas.com.co plásticos polímeros Colombia manufactura',
        'industria plástica Colombia empresa manufactura planta industrial',
    ],
    "textil": [
        'empresa textil confecciones Colombia directorio industrial "S.A."',
        'industria textil Colombia "consumo energético" KWH informe sostenibilidad',
        'site:paginasamarillas.com.co textil confecciones Colombia empresa',
        'empresa textil Colombia manufactura planta industrial gran consumidor',
    ],
    "mineria": [
        'empresa minera Colombia directorio "S.A." OR "S.A.S." gran consumidor energía',
        'empresa minera Colombia consumo energía eléctrica KWH reporte sostenibilidad',
        'minería carbón Colombia empresa industrial planta consumidor energía',
        'site:paginasamarillas.com.co minería empresa Colombia',
    ],
    "papel": [
        'empresa papel cartón Colombia directorio industrial gran consumidor energía',
        'empresa papel cartón Colombia "consumo de energía" KWH planta industrial',
        'industria papelera Colombia manufactura empresa "S.A."',
        'site:paginasamarillas.com.co papel cartón empaque Colombia empresa',
    ],
    "ceramica": [
        'empresa cerámica vidrio Colombia directorio industrial gran consumidor',
        'empresa cerámica vidrio Colombia consumo energético KWH informe',
        'site:paginasamarillas.com.co cerámica vidrio Colombia manufactura',
    ],
    "metal": [
        'empresa siderúrgica aceros metalúrgica Colombia directorio industrial',
        'empresa metalúrgica Colombia consumo energía KWH manufactura planta',
        'aceros metalmecánica Colombia empresa "S.A." gran consumidor energía',
        'site:paginasamarillas.com.co metalmecánica aceros Colombia empresa',
    ],
    "hospitales_grandes": [
        'clínicas hospitales Colombia gran consumidor energía eléctrica KWH directorio',
        'hospital clínica Colombia mayor consumo energía eléctrica',
        'directorio clínicas hospitales privados Colombia gran consumidor',
        'site:paginasamarillas.com.co clínicas hospitales Colombia',
    ],
    "centros_comerciales": [
        'centro comercial mall Colombia gran consumidor energía eléctrica directorio',
        'centros comerciales Colombia consumo energía KWH lista',
        'mall centro comercial Colombia empresa administradora "S.A."',
    ],
    "all": [
        'grandes consumidores energía eléctrica Colombia empresa manufactura industrial mercado no regulado lista',
        'empresa industrial Colombia "consumo energético" KWH informe sostenibilidad gran consumidor directorio',
        'directorio empresas industriales Colombia manufactura planta mayor consumidor energía',
        'site:paginasamarillas.com.co industria manufactura Colombia empresa planta industrial',
        '"mercado no regulado" empresa Colombia gran consumidor energía eléctrica lista directorio',
        'empresas Colombia consumo mayor 50000 KWH mes energía eléctrica manufactura industrial',
        'kompass.com empresas industriales Colombia manufactura directorio',
        'informe sostenibilidad Colombia empresa manufactura "consumo de energía" KWH 2023 OR 2024',
        'UPME Colombia grandes consumidores energía eléctrica empresa industrial lista',
    ],
}


class WebEnergySearch:

    def __init__(self, emit_fn: Optional[Callable] = None):
        self.emit = emit_fn or (lambda x: None)

    async def _emit_log(self, msg: str, level: str = "info"):
        await self.emit({
            "type": "agent_log", "agent": "web_energy_search",
            "level": level, "message": msg,
            "timestamp": datetime.now().isoformat(),
        })

    def _build_prompt(self, sector: str, cities: list[str], search_limit: int) -> str:
        city_str    = ", ".join(cities) if cities else "Colombia (todas las ciudades)"
        queries     = SECTOR_QUERIES.get(sector, SECTOR_QUERIES["all"])
        queries_str = "\n".join(f'- {q}' for q in queries)

        return f"""Encuentra empresas industriales en Colombia con consumo > 50.000 KWH/mes (Mercado No Regulado).

Zona: {city_str} | Sector: {sector} | Meta: {search_limit} empresas

Realiza estas búsquedas una por una:
{queries_str}

Devuelve SOLO este JSON (sin markdown):
{{"empresas":[{{"name":"Nombre Legal S.A.","city":"Ciudad","evidence":"fuente"}}]}}

Reglas: nombre legal real, máx {search_limit} empresas, incluye medianas y regionales."""

    def _run_claude_search(self, prompt: str) -> str:
        import anthropic

        client   = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        tools    = [{"type": "web_search_20250305", "name": "web_search"}]
        messages = [{"role": "user", "content": prompt}]
        last_content = []

        for _ in range(12):  # máx 12 rondas
            response = client.messages.create(
                model=SEARCH_MODEL,
                max_tokens=4096,
                tools=tools,
                messages=messages,
            )
            last_content = response.content
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "tool_use":
                tool_results = [
                    {"type": "tool_result", "tool_use_id": b.id, "content": ""}
                    for b in response.content
                    if getattr(b, "type", None) == "tool_use"
                ]
                if tool_results:
                    messages.append({"role": "user", "content": tool_results})
            else:
                break

        return "".join(b.text for b in last_content if hasattr(b, "text"))

    _BAD_PREFIXES = (
        "reference", "here are", "the following", "i found", "based on",
        "according", "search", "result", "empresa", "companies", "note:",
        "below", "list", "these are", "algunas", "entre las", "incluyen",
    )

    def _is_valid_name(self, name: str) -> bool:
        if not name or len(name) < 4 or len(name) > 90:
            return False
        low = name.lower()
        if any(low.startswith(p) for p in self._BAD_PREFIXES):
            return False
        if name.count(",") > 4:
            return False
        if re.search(r'\([^)]{40,}\)', name):
            return False
        return True

    def _parse_response(self, text: str, sector: str, cities: list[str]) -> list[dict]:
        default_city = cities[0] if cities else ""

        def make_entry(name: str, city: str = "", evidence: str = "") -> dict:
            return {
                "name":        name.strip(),
                "nit":         "",
                "source":      "web_energy_search",
                "city":        (city or default_city).strip(),
                "sector":      sector,
                "evidence":    evidence,
                "rues_status": "PENDIENTE",
            }

        text_clean = re.sub(r"```(?:json)?", "", text).strip()

        # Buscar cualquier bloque JSON con "empresas"
        json_match = re.search(r'\{[\s\S]*?"empresas"[\s\S]*\}', text_clean)
        if json_match:
            try:
                data = json.loads(json_match.group())
                raw  = data.get("empresas", [])
                result = [
                    make_entry(c.get("name", ""), c.get("city", ""), c.get("evidence", ""))
                    for c in raw
                    if self._is_valid_name(c.get("name", ""))
                ]
                if result:
                    return result
            except json.JSONDecodeError:
                pass

        # Fallback: líneas con sufijo legal
        companies = []
        legal = ("S.A.", "S.A.S.", "Ltda.", "LTDA", "Cooperativa", "Corp.", "S.A.S", "E.S.P.")
        for line in text_clean.splitlines():
            line = line.strip()
            if not any(s in line for s in legal):
                continue
            name = re.sub(r'^[\-\*\d\.\)\#]+\s*', "", line).split("—")[0].split(":")[0].strip()
            name = re.sub(r'\s*\([^)]{30,}\)\s*$', "", name).strip()
            if self._is_valid_name(name):
                companies.append(make_entry(name))
        return companies

    async def search(self, sector: str, cities: list[str], limit: int) -> list[dict]:
        city_label   = ", ".join(cities) if cities else "Colombia"
        # Pedir 2x internamente para tener candidatos suficientes tras el filtro RUES
        search_limit = min(limit * 2, 30)

        await self._emit_log(
            f"🌐 Buscando {search_limit} empresas MNR via web — sector: {sector}, zona: {city_label}"
        )

        prompt = self._build_prompt(sector, cities, search_limit)

        try:
            loop     = asyncio.get_event_loop()
            raw_text = await loop.run_in_executor(None, self._run_claude_search, prompt)
        except Exception as e:
            await self._emit_log(f"❌ Error en búsqueda web: {e}", "error")
            return []

        companies = self._parse_response(raw_text, sector, cities)

        seen, unique = set(), []
        for c in companies:
            key = c["name"].lower()
            if key not in seen:
                seen.add(key)
                unique.append(c)

        await self._emit_log(
            f"🌐 Web search: {len(unique)} empresas encontradas"
            + (f" ({sum(1 for c in unique if c['evidence'])} con evidencia KWH)" if unique else "")
        )
        # Devolver todos (sin cortar por limit) — el orchestrator filtra por VIGENTES
        return unique
