"""
Prospector Flow — servidor independiente (sin orquestador Claude)
Corre solo el CompanyFinder y exporta CSV.
Puerto: 8766
"""

import asyncio
import csv
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

from agents.company_finder import CompanyFinder

BASE_DIR = Path(__file__).parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Prospector Flow")

# ─── HTML inline ──────────────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prospector Flow · Klik Energy</title>
<style>
  :root {
    --bg:#0f172a;--surface:#1e293b;--surface2:#263550;--border:#334155;
    --blue:#3b82f6;--green:#10b981;--orange:#f59e0b;--red:#ef4444;
    --text:#f1f5f9;--dim:#94a3b8;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;}
  .header{background:linear-gradient(135deg,#1F4E78 0%,#2563eb 100%);padding:16px 28px;display:flex;align-items:center;gap:14px;border-bottom:1px solid rgba(255,255,255,.1);}
  .header h1{font-size:20px;font-weight:700;}
  .header p{font-size:12px;opacity:.7;margin-top:2px;}
  .dot{width:10px;height:10px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green);animation:pulse 2s infinite;}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
  .main{max-width:1100px;margin:0 auto;padding:28px 20px;display:grid;grid-template-columns:300px 1fr;gap:20px;}
  .panel{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:22px;height:fit-content;}
  .panel h2{font-size:14px;font-weight:600;color:var(--dim);letter-spacing:.05em;text-transform:uppercase;margin-bottom:18px;}
  label{display:block;font-size:13px;color:var(--dim);margin-bottom:6px;margin-top:14px;}
  label:first-of-type{margin-top:0;}
  select,input[type=text],input[type=number]{width:100%;padding:9px 12px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:14px;outline:none;transition:border .2s;}
  select:focus,input:focus{border-color:var(--blue);}
  .btn{margin-top:20px;width:100%;padding:12px;border:none;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer;transition:all .2s;}
  .btn-run{background:var(--blue);color:#fff;}
  .btn-run:hover{background:#2563eb;}
  .btn-stop{background:var(--red);color:#fff;margin-top:8px;}
  .btn-stop:hover{background:#dc2626;}
  .btn-csv{background:var(--green);color:#fff;margin-top:8px;}
  .btn-csv:hover{background:#059669;}
  .btn:disabled{opacity:.4;cursor:not-allowed;}
  .count-badge{margin-top:16px;text-align:center;font-size:13px;color:var(--dim);}
  .count-badge span{font-size:28px;font-weight:700;color:var(--green);display:block;}
  .right{display:flex;flex-direction:column;gap:16px;}
  .log-box,.results-box{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:16px;}
  .log-box h3,.results-box h3{font-size:13px;color:var(--dim);text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px;}
  .log-scroll{height:180px;overflow-y:auto;font-family:monospace;font-size:12px;display:flex;flex-direction:column;gap:3px;}
  .log-scroll::-webkit-scrollbar{width:4px;}
  .log-scroll::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px;}
  .log-line{padding:2px 0;}
  .log-info{color:#93c5fd;}
  .log-warn{color:var(--orange);}
  .log-error{color:var(--red);}
  .table-wrap{overflow-x:auto;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  thead th{background:var(--surface2);padding:10px 12px;text-align:left;color:var(--dim);font-weight:600;border-bottom:1px solid var(--border);white-space:nowrap;}
  tbody tr{border-bottom:1px solid var(--border);transition:background .15s;}
  tbody tr:hover{background:var(--surface2);}
  tbody td{padding:9px 12px;vertical-align:middle;}
  .chip{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:600;}
  .chip-rues{background:#1d4ed8;color:#93c5fd;}
  .chip-csv{background:#065f46;color:#6ee7b7;}
  .chip-web{background:#7c3aed;color:#c4b5fd;}
  .chip-seed{background:#92400e;color:#fcd34d;}
  .empty-state{text-align:center;padding:40px 0;color:var(--dim);font-size:14px;}
</style>
</head>
<body>

<div class="header">
  <div class="dot"></div>
  <div>
    <h1>&#9889; Prospector Flow</h1>
    <p>Klik Energy &middot; Mercado No Regulado &middot; Descubrimiento de Empresas</p>
  </div>
</div>

<div class="main">
  <div class="panel">
    <h2>Par&aacute;metros</h2>
    <label>Sector industrial</label>
    <select id="sector">
      <option value="all">Todos los sectores</option>
      <option value="cemento">Cemento</option>
      <option value="alimentos">Alimentos &amp; Bebidas</option>
      <option value="quimica">Qu&iacute;mica &amp; Farmac&eacute;utica</option>
      <option value="plasticos">Pl&aacute;sticos &amp; Pol&iacute;meros</option>
      <option value="textil">Textil &amp; Confecciones</option>
      <option value="mineria">Miner&iacute;a &amp; Carb&oacute;n</option>
      <option value="papel">Papel &amp; Cart&oacute;n</option>
      <option value="ceramica">Cer&aacute;mica &amp; Vidrio</option>
      <option value="metal">Metal &amp; Aceros</option>
      <option value="maquinaria">Maquinaria &amp; Equipos</option>
      <option value="hospitales_grandes">Hospitales &amp; Cl&iacute;nicas</option>
      <option value="centros_comerciales">Centros Comerciales</option>
    </select>
    <label>Ciudades (separadas por coma)</label>
    <input type="text" id="cities" placeholder="Medell&iacute;n, Bogot&aacute;, Cali&hellip;">
    <label>L&iacute;mite de empresas</label>
    <input type="number" id="limit" value="15" min="1" max="100">
    <button class="btn btn-run" id="btnRun" onclick="runProspector()">&#128269; Buscar empresas</button>
    <button class="btn btn-stop" id="btnStop" onclick="stopProspector()" disabled>&#9209; Detener</button>
    <button class="btn btn-csv" id="btnCsv" onclick="downloadCsv()" disabled>&#11015; Exportar CSV</button>
    <div class="count-badge">
      <span id="countNum">0</span>
      empresas encontradas
    </div>
  </div>

  <div class="right">
    <div class="log-box">
      <h3>&#128187; Logs en tiempo real</h3>
      <div class="log-scroll" id="logBox"></div>
    </div>
    <div class="results-box">
      <h3>&#128203; Resultados</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th><th>Empresa</th><th>NIT</th><th>Ciudad</th><th>Sector</th><th>Fuente</th>
            </tr>
          </thead>
          <tbody id="resultsBody"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
  var ws = null;
  var results = [];
  var sessionId = Math.random().toString(36).slice(2);

  function connect() {
    ws = new WebSocket('ws://' + location.host + '/ws/' + sessionId);
    ws.onmessage = function(e) { handleMessage(JSON.parse(e.data)); };
    ws.onclose   = function() { setBusy(false); addLog('Desconectado del servidor', 'warn'); };
    ws.onerror   = function() { addLog('Error de conexion WebSocket', 'error'); };
  }

  function handleMessage(msg) {
    if (msg.type === 'log') {
      addLog(msg.message, msg.level || 'info');
    } else if (msg.type === 'results') {
      results = msg.companies || [];
      renderResults(results);
      document.getElementById('countNum').textContent = results.length;
      document.getElementById('btnCsv').disabled = results.length === 0;
      addLog('Listo: ' + results.length + ' empresas encontradas', 'info');
      setBusy(false);
    } else if (msg.type === 'error') {
      addLog('Error: ' + msg.message, 'error');
      setBusy(false);
    } else if (msg.type === 'stopped') {
      addLog('Busqueda detenida', 'warn');
      setBusy(false);
    }
  }

  function runProspector() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      connect();
      setTimeout(runProspector, 400);
      return;
    }
    results = [];
    clearResults();
    document.getElementById('countNum').textContent = '0';
    document.getElementById('btnCsv').disabled = true;
    document.getElementById('logBox').textContent = '';

    var sector = document.getElementById('sector').value;
    var citiesRaw = document.getElementById('cities').value;
    var cities = citiesRaw ? citiesRaw.split(',').map(function(c){ return c.trim(); }).filter(Boolean) : [];
    var limit = parseInt(document.getElementById('limit').value) || 15;

    setBusy(true);
    ws.send(JSON.stringify({ type: 'search', sector: sector, cities: cities, limit: limit }));
    addLog('Iniciando busqueda — sector: ' + sector + ', ciudades: ' + (cities.length ? cities.join(', ') : 'todas') + ', limite: ' + limit);
  }

  function stopProspector() {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'stop' }));
    }
  }

  function downloadCsv() {
    if (!results.length) return;
    var rows = [['#','Empresa','NIT','Ciudad','Sector','Fuente']];
    results.forEach(function(c, i) {
      rows.push([i+1, c.name||'', c.nit||'', c.city||'', c.sector||'', c.source||'']);
    });
    var csv = rows.map(function(r) {
      return r.map(function(v){ return '"' + String(v).replace(/"/g,'""') + '"'; }).join(',');
    }).join('\n');
    var blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'prospector_' + new Date().toISOString().slice(0,10) + '.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  function clearResults() {
    var tbody = document.getElementById('resultsBody');
    while (tbody.firstChild) { tbody.removeChild(tbody.firstChild); }
  }

  function renderResults(data) {
    var tbody = document.getElementById('resultsBody');
    while (tbody.firstChild) { tbody.removeChild(tbody.firstChild); }
    if (!data.length) {
      var tr = document.createElement('tr');
      var td = document.createElement('td');
      td.setAttribute('colspan', '6');
      td.className = 'empty-state';
      td.textContent = 'Sin resultados';
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }
    data.forEach(function(c, i) {
      var tr = document.createElement('tr');

      var tdNum = document.createElement('td');
      tdNum.style.color = 'var(--dim)';
      tdNum.textContent = i + 1;
      tr.appendChild(tdNum);

      var tdName = document.createElement('td');
      tdName.style.fontWeight = '600';
      tdName.textContent = c.name || '';
      tr.appendChild(tdName);

      var tdNit = document.createElement('td');
      tdNit.style.fontFamily = 'monospace';
      tdNit.style.color = 'var(--dim)';
      tdNit.textContent = c.nit || '—';
      tr.appendChild(tdNit);

      var tdCity = document.createElement('td');
      tdCity.textContent = c.city || '—';
      tr.appendChild(tdCity);

      var tdSector = document.createElement('td');
      tdSector.textContent = c.sector || '—';
      tr.appendChild(tdSector);

      var tdSrc = document.createElement('td');
      var chip = document.createElement('span');
      chip.className = 'chip ' + sourceClass(c.source || '');
      chip.textContent = sourceLabel(c.source || '');
      tdSrc.appendChild(chip);
      tr.appendChild(tdSrc);

      tbody.appendChild(tr);
    });
  }

  function sourceClass(src) {
    var s = src.toUpperCase();
    if (s.indexOf('RUES') !== -1) return 'chip-rues';
    if (s.indexOf('WEB') !== -1)  return 'chip-web';
    if (s.indexOf('CSV') !== -1 || s.indexOf('JSON') !== -1) return 'chip-csv';
    return 'chip-seed';
  }

  function sourceLabel(src) {
    var s = src.toUpperCase();
    if (s.indexOf('RUES') !== -1) return 'RUES';
    if (s.indexOf('WEB') !== -1)  return 'WEB';
    if (s.indexOf('CSV') !== -1 || s.indexOf('JSON') !== -1) return 'CSV';
    return src || 'SEED';
  }

  function addLog(msg, level) {
    var box = document.getElementById('logBox');
    var ts  = new Date().toLocaleTimeString('es-CO', { hour12: false });
    var div = document.createElement('div');
    div.className = 'log-line log-' + (level || 'info');
    div.textContent = '[' + ts + '] ' + msg;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }

  function setBusy(busy) {
    document.getElementById('btnRun').disabled  = busy;
    document.getElementById('btnStop').disabled = !busy;
  }

  connect();
</script>
</body>
</html>"""


# ─── WebSocket handler ────────────────────────────────────────────────────────

active: dict = {}


@app.get("/")
async def root():
    return HTMLResponse(HTML)


@app.websocket("/ws/{session_id}")
async def ws_endpoint(ws: WebSocket, session_id: str):
    await ws.accept()

    async def emit(ev: dict):
        try:
            await ws.send_json(ev)
        except Exception:
            pass

    finder = CompanyFinder(emit_fn=emit)
    active[session_id] = finder

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            if msg_type == "search":
                finder._stop = False
                params = {
                    "sector": data.get("sector", "all"),
                    "cities": data.get("cities", []),
                    "limit":  int(data.get("limit", 15)),
                }

                async def run_search(p=params):
                    try:
                        companies = await finder.find(p)
                        await emit({"type": "results", "companies": companies})
                        if companies:
                            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                            out = OUTPUTS_DIR / f"prospector_{ts}.csv"
                            with open(out, "w", newline="", encoding="utf-8-sig") as f:
                                fields = ["name", "nit", "city", "sector", "source", "rues_status"]
                                writer = csv.DictWriter(f, fieldnames=fields)
                                writer.writeheader()
                                for c in companies:
                                    writer.writerow({k: c.get(k, "") for k in fields})
                            await emit({"type": "log", "level": "info", "message": f"CSV guardado: {out.name}"})
                    except Exception as e:
                        await emit({"type": "error", "message": str(e)})

                asyncio.create_task(run_search())

            elif msg_type == "stop":
                finder.stop()
                await emit({"type": "stopped"})

    except WebSocketDisconnect:
        pass
    finally:
        active.pop(session_id, None)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  Prospector Flow - Klik Energy")
    print("  UI: http://localhost:8766")
    print("=" * 55)
    uvicorn.run("prospector_server:app", host="0.0.0.0", port=8766, reload=False, log_level="warning")
