#!/bin/bash
# ============================================================
#  KLIK ENERGY — Sistema Completo de Generación de Leads
#  Mercado No Regulado · Colombia
# ============================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'

echo ""
echo -e "${BLUE}⚡ =============================================${NC}"
echo -e "${BLUE}   KLIK ENERGY — Lead GenAI System${NC}"
echo -e "${BLUE}   Mercado No Regulado · Claude AI${NC}"
echo -e "${BLUE}⚡ =============================================${NC}"
echo ""

# ── .env ──────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${YELLOW}⚠️  Edita .env y agrega ANTHROPIC_API_KEY antes de continuar${NC}"
  echo ""
  read -p "¿Agregar API key ahora? (s/n): " ans
  if [[ "$ans" == "s" || "$ans" == "S" ]]; then
    read -p "ANTHROPIC_API_KEY: " key
    [[ -n "$key" ]] && sed -i '' "s/sk-ant-.../$key/" .env && echo -e "${GREEN}✅ API key guardada${NC}"
  fi
fi

source .env 2>/dev/null || true
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; then
  echo -e "${RED}❌ ANTHROPIC_API_KEY no configurada. Edita .env${NC}"
  exit 1
fi

# ── Python ────────────────────────────────────────────────────
PYTHON=$(which python3 2>/dev/null || which python 2>/dev/null)
[[ -z "$PYTHON" ]] && { echo -e "${RED}❌ Python no encontrado${NC}"; exit 1; }
echo -e "${GREEN}🐍 $($PYTHON --version)${NC}"

# ── Dependencias ──────────────────────────────────────────────
if [ ! -f ".deps_installed" ]; then
  echo "📦 Instalando dependencias (solo primera vez)..."
  $PYTHON -m pip install -r requirements.txt -q
  $PYTHON -m playwright install chromium 2>/dev/null || true
  touch .deps_installed
  echo -e "${GREEN}✅ Dependencias instaladas${NC}"
fi

# ── Menú ──────────────────────────────────────────────────────
echo ""
echo "¿Qué servidor quieres iniciar?"
echo ""
echo "  1) Orquestador principal     → http://localhost:8765  (busca leads + enriquece)"
echo "  2) LinkedIn Outreach         → http://localhost:8766  (envía conexiones + emails)"
echo "  3) Prospector                → http://localhost:8767  (pipeline multi-fuente)"
echo "  4) Autenticar LinkedIn       (ejecuta setup una sola vez)"
echo "  5) Todo a la vez             (3 servidores en background)"
echo ""
read -p "Opción [1-5]: " opt

case "$opt" in
  1)
    echo ""
    echo -e "${GREEN}🚀 Orquestador → http://localhost:8765${NC}"
    (sleep 2 && open "http://localhost:8765") &
    $PYTHON server.py
    ;;
  2)
    echo ""
    echo -e "${GREEN}🚀 LinkedIn Outreach → http://localhost:8766${NC}"
    (sleep 2 && open "http://localhost:8766") &
    $PYTHON outreach_app.py
    ;;
  3)
    echo ""
    echo -e "${GREEN}🚀 Prospector → http://localhost:8767${NC}"
    (sleep 2 && open "http://localhost:8767") &
    $PYTHON prospector_server.py
    ;;
  4)
    echo ""
    echo -e "${YELLOW}🔐 Autenticando LinkedIn (se abrirá un browser)...${NC}"
    $PYTHON setup_linkedin_auth.py
    ;;
  5)
    echo ""
    echo -e "${GREEN}🚀 Iniciando los 3 servidores...${NC}"
    $PYTHON server.py &
    PID1=$!
    sleep 1
    $PYTHON outreach_app.py &
    PID2=$!
    sleep 1
    $PYTHON prospector_server.py &
    PID3=$!
    echo ""
    echo "  🌐 Orquestador:    http://localhost:8765"
    echo "  🌐 LinkedIn:       http://localhost:8766"
    echo "  🌐 Prospector:     http://localhost:8767"
    echo ""
    echo "Ctrl+C para detener todo."
    sleep 2
    open "http://localhost:8765"
    wait $PID1 $PID2 $PID3
    ;;
  *)
    echo "Opción inválida. Ejecuta ./INICIAR.sh nuevamente."
    ;;
esac
