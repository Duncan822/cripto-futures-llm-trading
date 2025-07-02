#!/bin/bash

# Script per avviare il Background Agent
# Gestisce automaticamente la generazione, validazione e backtest delle strategie

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Avvio Background Agent per Crypto Futures LLM Trading${NC}"

# Controlla se siamo nella directory corretta
if [ ! -f "background_agent.py" ]; then
    echo -e "${RED}❌ Errore: background_agent.py non trovato${NC}"
    echo "Assicurati di essere nella directory del progetto"
    exit 1
fi

# Attiva l'ambiente virtuale se esiste
if [ -d "venv" ]; then
    echo -e "${YELLOW}🔧 Attivazione ambiente virtuale...${NC}"
    source venv/bin/activate
fi

# Controlla dipendenze
echo -e "${YELLOW}🔍 Controllo dipendenze...${NC}"
python -c "import schedule" 2>/dev/null || {
    echo -e "${YELLOW}📦 Installazione dipendenza 'schedule'...${NC}"
    pip install schedule
}

# Controlla configurazione
if [ ! -f "background_config.json" ]; then
    echo -e "${YELLOW}⚙️ Creazione configurazione di default...${NC}"
    python -c "
import json
config = {
    'auto_validation': True,
    'auto_backtest': True,
    'max_strategies': 50,
    'generation_interval': 3600,
    'backtest_interval': 7200,
    'cleanup_old_strategies': True,
    'strategy_types': ['volatility', 'scalping', 'breakout', 'momentum'],
    'models': ['phi3', 'llama2', 'mistral'],
    'min_backtest_score': 0.1,
    'max_concurrent_tasks': 3
}
with open('background_config.json', 'w') as f:
    json.dump(config, f, indent=2)
"
fi

# Controlla se Ollama è in esecuzione
echo -e "${YELLOW}🔍 Controllo Ollama...${NC}"
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}⚠️ Ollama non sembra essere in esecuzione${NC}"
    echo "Avvia Ollama con: ollama serve"
    echo "Poi installa i modelli necessari:"
    echo "  ollama pull phi3"
    echo "  ollama pull llama2"
    echo "  ollama pull mistral"
fi

# Crea directory per i log se non esiste
mkdir -p logs

# Avvia l'agente
echo -e "${GREEN}✅ Avvio Background Agent...${NC}"
echo -e "${BLUE}📝 Log disponibili in: background_agent.log${NC}"
echo -e "${BLUE}📊 Configurazione: background_config.json${NC}"
echo -e "${YELLOW}💡 Per fermare l'agente: Ctrl+C${NC}"
echo ""

# Avvia l'agente in background con nohup
nohup python background_agent.py > logs/background_agent_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Salva il PID
echo $! > background_agent.pid

echo -e "${GREEN}✅ Background Agent avviato con PID: $(cat background_agent.pid)${NC}"
echo -e "${BLUE}📋 Per controllare lo stato: tail -f logs/background_agent_*.log${NC}"
echo -e "${BLUE}🛑 Per fermare: kill $(cat background_agent.pid)${NC}" 