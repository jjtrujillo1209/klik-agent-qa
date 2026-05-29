# ⚡ KLIK ENERGY — Sistema Completo de Generación de Leads

Sistema de IA para descubrir, calificar y contactar empresas del mercado no regulado de energía en Colombia. Construido sobre Claude AI (Anthropic) con automatización LinkedIn y Playwright.

---

## Inicio rápido

```bash
# 1. Configurar API key
cp .env.example .env
# Edita .env → agrega ANTHROPIC_API_KEY

# 2. Iniciar (menú interactivo)
chmod +x INICIAR.sh
./INICIAR.sh
```

---

## Arquitectura del sistema

```
KLIK-COMPLETO/
│
├── server.py              ← Servidor principal WebSocket (puerto 8765)
├── orchestrator.py        ← Orquestador multi-ronda Claude AI
├── outreach_app.py        ← App LinkedIn + Email Outreach (puerto 8766)
├── prospector_server.py   ← Pipeline multi-fuente (puerto 8767)
├── linkedin_sender.py     ← Envío automático LinkedIn (Playwright)
├── setup_linkedin_auth.py ← Autenticación LinkedIn (correr 1 vez)
│
├── agents/
│   ├── web_energy_search.py   ← Descubre empresas >50K KWH (Claude + web)
│   ├── company_finder.py      ← Busca empresas (CSV / RUES / MNR)
│   ├── nit_resolver.py        ← Valida NITs vía RUES (Playwright)
│   ├── linkedin_agent.py      ← Encuentra decisores en LinkedIn
│   ├── outreach_agent.py      ← Agente de contacto
│   ├── outreach_templates.py  ← 75+ templates por cargo/industria
│   ├── exporter.py            ← Exporta Excel + HubSpot CSV
│   └── scrappling_adapter.py  ← Adaptador Scrapling
│
├── ui/
│   ├── index.html         ← UI Orquestador (WebSocket live)
│   └── outreach.html      ← UI LinkedIn + Compositor de Email
│
├── data/
│   ├── empresas_colombia_alto_consumo_energia.csv   ← Base de datos fuente
│   └── outputs/           ← Leads generados (Excel + HubSpot CSV)
│
└── docs/                  ← Presentaciones y documentos comerciales
    ├── klik-propuesta-1pager.html
    ├── klik-energy-deck.pptx
    ├── klik-propuesta-comercial.pptx
    └── Click_Energy_Documento_Sistema.docx
```

---

## Módulos principales

### 1. Orquestador de Leads — `http://localhost:8765`
Pipeline completo de generación:
- **Paso 1:** `web_energy_search` busca empresas colombianas con >50K KWH/mes
- **Paso 2:** `company_finder` valida contra RUES (solo empresas VIGENTES)
- **Paso 3:** `nit_resolver` confirma NIT oficial
- **Paso 4:** `linkedin_agent` encuentra CEO / Director de Operaciones / etc.
- **Paso 5:** `exporter` genera Excel + CSV listo para HubSpot

### 2. LinkedIn + Email Outreach — `http://localhost:8766`
- Carga CSV de empresas → busca decisores automáticamente
- Genera mensajes de conexión personalizados por cargo (75+ templates)
- Envía conexiones automáticamente (máx 20/día, límite seguro)
- **Compositor de Email** con dos templates:
  - *Sin conexión LinkedIn* — cold outreach
  - *Con conexión LinkedIn* — follow-up cálido
- Copiar asunto o cuerpo con un clic

### 3. Prospector Multi-fuente — `http://localhost:8767`
Pipeline integrado: web → CSV → RUES → exportación.

---

## Variables de entorno (`.env`)

| Variable | Descripción | Requerida |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude AI | ✅ Sí |
| `APOLLO_API_KEY` | Enriquecimiento emails | Opcional |
| `HUBSPOT_API_KEY` | Deduplicación automática | Opcional |
| `BETTERCONTACT_API_KEY` | Emails verificados | Opcional |

---

## Flujo de trabajo recomendado

```
1. ./INICIAR.sh → opción 4 (autenticar LinkedIn — solo 1 vez)

2. ./INICIAR.sh → opción 1 (Orquestador)
   → Genera leads → exporta Excel + HubSpot CSV

3. ./INICIAR.sh → opción 2 (LinkedIn Outreach)
   → Carga el CSV → busca decisores → envía conexiones
   → Usa el compositor de email para follow-up por correo

4. Importa data/outputs/hubspot_import_*.csv en HubSpot
```

---

## Templates de email incluidos

Ubicados en `agents/outreach_templates.py` — 75+ mensajes organizados por:
- **Cargo:** CEO, Director de Operaciones, Gerente Financiero, Jefe de Planta, etc.
- **Industria:** manufactura, agroindustria, minería, retail, etc.
- **Etapa:** conexión, seguimiento, propuesta

---

## Outputs generados

Cada ejecución genera archivos con timestamp en `data/outputs/`:

| Archivo | Contenido |
|---|---|
| `leads_MNR_YYYYMMDD.xlsx` | Leads completos con contactos |
| `hubspot_import_YYYYMMDD.csv` | Listo para importar en HubSpot |
| `outreach_linkedin_YYYYMMDD.csv` | Queue de conexiones enviadas |

---

## Documentos comerciales (`docs/`)

| Archivo | Descripción |
|---|---|
| `klik-propuesta-1pager.html` | One-pager propuesta Klik |
| `klik-energy-deck.pptx` | Presentación ejecutiva |
| `klik-propuesta-comercial.pptx` | Propuesta comercial completa |
| `Click_Energy_Documento_Sistema.docx` | Documento técnico del sistema |
| `Click_Energy_Sistema_Leads.xlsx` | Tracking de leads |

---

## Stack tecnológico

- **IA:** Claude Sonnet (Anthropic) — búsqueda, clasificación, redacción
- **Backend:** FastAPI + WebSockets (Python 3.10+)
- **Browser automation:** Playwright (LinkedIn, RUES)
- **Scraping:** Scrapling
- **Frontend:** HTML/CSS/JS vanilla (sin dependencias)
- **Export:** openpyxl (Excel), CSV nativo

---

*Sistema desarrollado para Klik Energy — Mercado No Regulado Colombia*
