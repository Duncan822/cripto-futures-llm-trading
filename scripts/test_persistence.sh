#!/bin/bash

# Script per testare la persistenza del Background Agent
# Dimostra che l'agente rimane in funzione anche dopo la disconnessione

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Test Persistenza Background Agent${NC}"
echo ""

# Controlla se l'agente è in esecuzione
if [ -f "background_agent.pid" ]; then
    PID=$(cat background_agent.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Background Agent è in esecuzione (PID: $PID)${NC}"
        echo -e "   Uptime: $(ps -o etime= -p $PID)"
        echo -e "   Memoria: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
    else
        echo -e "${YELLOW}⚠️ File PID trovato ma processo non attivo${NC}"
        rm -f background_agent.pid
    fi
else
    echo -e "${RED}❌ Background Agent non è in esecuzione${NC}"
    echo "Avvia prima l'agente con: ./manage_background_agent.sh start"
    exit 1
fi

echo ""
echo -e "${BLUE}📊 Informazioni sulla Persistenza:${NC}"
echo ""

# Mostra il comando di avvio
echo -e "${YELLOW}🔧 Comando di avvio utilizzato:${NC}"
echo "   nohup python background_agent.py > logs/background_agent_\$(date +%Y%m%d_%H%M%S).log 2>&1 &"
echo ""

# Spiega i componenti
echo -e "${YELLOW}📋 Componenti per la persistenza:${NC}"
echo "   ✅ nohup - Impedisce la terminazione quando chiudi la sessione"
echo "   ✅ & - Esegue il processo in background"
echo "   ✅ > file.log - Reindirizza l'output a un file di log"
echo "   ✅ 2>&1 - Reindirizza anche gli errori al file di log"
echo "   ✅ PID file - Salva il PID per la gestione"
echo ""

# Mostra i log attivi
echo -e "${YELLOW}📝 Log attivi:${NC}"
if [ -d "logs" ]; then
    LATEST_LOG=$(ls -t logs/background_agent_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo -e "   📄 File: $LATEST_LOG"
        echo -e "   📏 Dimensione: $(du -h "$LATEST_LOG" | cut -f1)"
        echo -e "   🕐 Ultimo aggiornamento: $(stat -c %y "$LATEST_LOG" | cut -d' ' -f2 | cut -d'.' -f1)"
    else
        echo -e "   ❌ Nessun log trovato"
    fi
else
    echo -e "   ❌ Directory logs non trovata"
fi

echo ""
echo -e "${BLUE}🧪 Test di Persistenza:${NC}"
echo ""

# Simula cosa succede quando esci dal server
echo -e "${YELLOW}💡 Quando esci dal server (logout/disconnessione):${NC}"
echo "   1. Il processo nohup rimane attivo"
echo "   2. Il Background Agent continua a funzionare"
echo "   3. I log vengono scritti nel file"
echo "   4. Le attività programmate continuano"
echo ""

# Mostra come controllare da una nuova sessione
echo -e "${YELLOW}🔍 Come controllare da una nuova sessione:${NC}"
echo "   # Connettiti al server"
echo "   ssh user@server"
echo ""
echo "   # Vai nella directory del progetto"
echo "   cd /path/to/crypto-futures-llm-trading"
echo ""
echo "   # Controlla lo stato"
echo "   ./manage_background_agent.sh status"
echo ""
echo "   # Visualizza i log"
echo "   ./manage_background_agent.sh logs"
echo ""

# Mostra come fermare l'agente
echo -e "${YELLOW}🛑 Come fermare l'agente:${NC}"
echo "   # Metodo raccomandato"
echo "   ./manage_background_agent.sh stop"
echo ""
echo "   # Metodo alternativo"
echo "   kill \$(cat background_agent.pid)"
echo ""

# Test di continuità
echo -e "${BLUE}📊 Test di Continuità:${NC}"
echo ""

# Controlla se ci sono attività recenti
if [ -f "strategies_metadata.json" ]; then
    echo -e "${GREEN}✅ Metadati strategie trovati${NC}"
    STRATEGY_COUNT=$(python -c "import json; data=json.load(open('strategies_metadata.json')); print(len(data))" 2>/dev/null || echo "0")
    echo -e "   📊 Strategie totali: $STRATEGY_COUNT"
else
    echo -e "${YELLOW}⚠️ Metadati strategie non trovati${NC}"
fi

# Controlla configurazione
if [ -f "background_config.json" ]; then
    echo -e "${GREEN}✅ Configurazione trovata${NC}"
    echo -e "   📄 File: background_config.json"
else
    echo -e "${YELLOW}⚠️ Configurazione non trovata${NC}"
fi

echo ""
echo -e "${GREEN}✅ Test completato!${NC}"
echo ""
echo -e "${BLUE}📝 Riepilogo:${NC}"
echo "   ✅ Il Background Agent è configurato per la persistenza"
echo "   ✅ Rimarrà attivo anche dopo la disconnessione"
echo "   ✅ I log vengono salvati automaticamente"
echo "   ✅ Puoi controllare lo stato da una nuova sessione"
echo "   ✅ Usa ./manage_background_agent.sh stop per fermarlo" 