#!/bin/bash

# Script di test per dimostrare la gestione di Ctrl+C
# Simula il comportamento quando si guardano i log in tempo reale

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Test gestione Ctrl+C per Background Agent${NC}"
echo ""

# Controlla se l'agente è in esecuzione
if [ -f "background_agent.pid" ]; then
    PID=$(cat background_agent.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Background Agent è in esecuzione (PID: $PID)${NC}"
    else
        echo -e "${YELLOW}⚠️ Background Agent non è in esecuzione, avviandolo...${NC}"
        ./manage_background_agent.sh start
        sleep 2
    fi
else
    echo -e "${YELLOW}⚠️ Background Agent non è in esecuzione, avviandolo...${NC}"
    ./manage_background_agent.sh start
    sleep 2
fi

echo ""
echo -e "${BLUE}📋 Simulazione visualizzazione log in tempo reale${NC}"
echo -e "${YELLOW}💡 Questo comando mostrerà i log per 10 secondi, poi si fermerà automaticamente${NC}"
echo -e "${YELLOW}💡 In un caso reale, premeresti Ctrl+C per uscire${NC}"
echo ""

# Simula la visualizzazione dei log per 10 secondi
timeout 10 ./manage_background_agent.sh logs

echo ""
echo -e "${GREEN}✅ Test completato!${NC}"
echo ""
echo -e "${BLUE}📝 Spiegazione del comportamento:${NC}"
echo "1. Quando premi Ctrl+C durante 'tail -f logs/...':"
echo "   - Il comando 'tail -f' si ferma"
echo "   - L'agente continua a funzionare in background"
echo ""
echo "2. Per fermare completamente l'agente:"
echo "   - Usa: ./manage_background_agent.sh stop"
echo "   - Oppure: kill \$(cat background_agent.pid)"
echo ""
echo "3. L'agente gestisce correttamente i segnali SIGINT e SIGTERM"
echo "   - Salva i metadati prima di terminare"
echo "   - Chiude pulitamente tutti i thread"
echo "   - Registra l'arresto nei log" 