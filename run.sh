#!/bin/bash
# ============================================================
# Lead GenAI Orchestrator - Script de arranque
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "⚡ ==========================================="
echo "   Lead GenAI Orchestrator · Klik Energy"
echo "   Mercado No Regulado · Claude AI"
echo "⚡ ==========================================="
echo ""

# Verificar .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Copiando .env.example → .env"
        cp .env.example .env
        echo ""
        echo "⚠️  IMPORTANTE: Edita .env y agrega tu ANTHROPIC_API_KEY"
        echo "   Abre el archivo: open .env"
        echo ""
        read -p "¿Quieres configurar el API key ahora? (s/n): " answer
        if [[ "$answer" == "s" || "$answer" == "S" ]]; then
            read -p "Ingresa tu ANTHROPIC_API_KEY: " api_key
            if [[ -n "$api_key" ]]; then
                sed -i '' "s/sk-ant-.../$api_key/" .env
                echo "✅ API key configurada"
            fi
        fi
    else
        echo "❌ No se encontró .env.example"
        exit 1
    fi
fi

# Verificar Python
PYTHON=$(which python3 || which python)
if [ -z "$PYTHON" ]; then
    echo "❌ Python no encontrado. Instala Python 3.10+"
    exit 1
fi

echo "🐍 Python: $($PYTHON --version)"

# Instalar dependencias si es necesario
if [ ! -f ".deps_installed" ]; then
    echo ""
    echo "📦 Instalando dependencias..."
    $PYTHON -m pip install -r requirements.txt -q
    $PYTHON -m playwright install chromium --with-deps 2>/dev/null || \
        $PYTHON -m playwright install chromium 2>/dev/null || \
        echo "⚠️  Playwright chromium no instalado (opcional para LinkedIn autenticado)"
    touch .deps_installed
    echo "✅ Dependencias instaladas"
fi

# Verificar API key
source .env 2>/dev/null || true
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; then
    echo ""
    echo "❌ ANTHROPIC_API_KEY no configurada en .env"
    echo "   Edita el archivo .env y agrega tu key"
    exit 1
fi

echo ""
echo "🚀 Iniciando servidor..."
echo ""
echo "   🌐 UI:      http://localhost:8765"
echo "   📡 WS:      ws://localhost:8765/ws/{session}"
echo "   📁 Outputs: http://localhost:8765/outputs"
echo ""
echo "   ▶ Para autenticar LinkedIn:  python setup_linkedin_auth.py"
echo "   ▶ Para detener:              Ctrl+C"
echo ""
echo "⚡ ==========================================="
echo ""

# Abrir UI en browser (después de 2 segundos)
(sleep 2 && open "http://localhost:8765") &

# Iniciar servidor
$PYTHON server.py
