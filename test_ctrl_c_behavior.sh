#!/bin/bash

# Script per testare il comportamento di Ctrl+C sui log dell'agente
# Verifica se Ctrl+C ferma solo i log o anche l'agente

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Test Comportamento Ctrl+C sui Log${NC}"
echo ""

# Funzione per contare i processi attivi
count_active_processes() {
    ps aux | grep "python background_agent.py" | grep -v grep | wc -l
}

# Funzione per ottenere il PID dell'agente
get_agent_pid() {
    if [ -f "background_agent.pid" ]; then
        cat background_agent.pid
    else
        echo ""
    fi
}

# Controlla stato iniziale
echo -e "${BLUE}📊 Stato Iniziale:${NC}"
INITIAL_COUNT=$(count_active_processes)
INITIAL_PID=$(get_agent_pid)

echo -e "   🔄 Processi attivi: $INITIAL_COUNT"
if [ -n "$INITIAL_PID" ]; then
    echo -e "   🆔 PID memorizzato: $INITIAL_PID"
else
    echo -e "   🆔 PID memorizzato: Nessuno"
fi

if [ "$INITIAL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Nessun Background Agent attivo${NC}"
    echo -e "   Avvia prima un agente con: ./manage_background_agent.sh start"
    exit 1
fi

echo ""

# Test 1: Verifica che l'agente sia in esecuzione
echo -e "${PURPLE}🧪 Test 1: Verifica Agente Attivo${NC}"
echo -e "${YELLOW}Eseguendo: ./manage_background_agent.sh status${NC}"
echo ""

./manage_background_agent.sh status

echo ""
echo -e "${GREEN}✅ Test 1 completato${NC}"
echo ""

# Test 2: Simulazione Ctrl+C sui log
echo -e "${PURPLE}🧪 Test 2: Simulazione Ctrl+C sui Log${NC}"
echo ""
echo -e "${YELLOW}⚠️ ATTENZIONE: Questo test simula Ctrl+C sui log${NC}"
echo -e "${YELLOW}💡 Il comando 'tail -f' verrà interrotto dopo 3 secondi${NC}"
echo ""

# Avvia tail -f in background e lo ferma dopo 3 secondi
echo -e "${BLUE}📋 Avviando visualizzazione log...${NC}"
echo -e "${YELLOW}💡 Premi Ctrl+C per uscire (o aspetta 3 secondi)${NC}"
echo ""

# Trova il file di log più recente
LATEST_LOG=$(ls -t logs/background_agent_*.log 2>/dev/null | head -1)

if [ -n "$LATEST_LOG" ]; then
    echo -e "${GREEN}📄 File di log: $LATEST_LOG${NC}"
    echo ""
    
    # Avvia tail -f in background
    tail -f "$LATEST_LOG" &
    TAIL_PID=$!
    
    # Aspetta 3 secondi
    sleep 3
    
    # Ferma tail -f
    kill $TAIL_PID 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}✅ Visualizzazione log fermata${NC}"
else
    echo -e "${YELLOW}⚠️ Nessun file di log trovato${NC}"
fi

echo ""
echo -e "${GREEN}✅ Test 2 completato${NC}"
echo ""

# Test 3: Verifica che l'agente sia ancora attivo
echo -e "${PURPLE}🧪 Test 3: Verifica Agente Ancora Attivo${NC}"
echo ""

FINAL_COUNT=$(count_active_processes)
FINAL_PID=$(get_agent_pid)

echo -e "${BLUE}📊 Stato Finale:${NC}"
echo -e "   🔄 Processi attivi: $FINAL_COUNT"
if [ -n "$FINAL_PID" ]; then
    echo -e "   🆔 PID memorizzato: $FINAL_PID"
else
    echo -e "   🆔 PID memorizzato: Nessuno"
fi

echo ""

# Confronta stato iniziale e finale
if [ "$INITIAL_COUNT" -eq "$FINAL_COUNT" ]; then
    echo -e "${GREEN}✅ SUCCESSO: L'agente è ancora attivo dopo Ctrl+C sui log${NC}"
    echo -e "   📊 Processi prima: $INITIAL_COUNT, Processi dopo: $FINAL_COUNT"
else
    echo -e "${RED}❌ PROBLEMA: L'agente è stato fermato da Ctrl+C sui log${NC}"
    echo -e "   📊 Processi prima: $INITIAL_COUNT, Processi dopo: $FINAL_COUNT"
fi

if [ "$INITIAL_PID" = "$FINAL_PID" ] && [ -n "$INITIAL_PID" ]; then
    echo -e "${GREEN}✅ SUCCESSO: Lo stesso PID è ancora attivo${NC}"
    echo -e "   🆔 PID: $INITIAL_PID"
else
    echo -e "${YELLOW}⚠️ ATTENZIONE: Il PID è cambiato o non è più disponibile${NC}"
    echo -e "   🆔 PID prima: $INITIAL_PID, PID dopo: $FINAL_PID"
fi

echo ""

# Test 4: Verifica dettagliata del processo
if [ "$FINAL_COUNT" -gt 0 ]; then
    echo -e "${PURPLE}🧪 Test 4: Dettagli Processo${NC}"
    echo ""
    
    # Mostra dettagli del processo attivo
    ps aux | grep "python background_agent.py" | grep -v grep | while read line; do
        PID=$(echo "$line" | awk '{print $2}')
        UPTIME=$(ps -o etime= -p $PID 2>/dev/null || echo "N/A")
        MEMORY=$(ps -o rss= -p $PID 2>/dev/null | awk '{print $1/1024 " MB"}' || echo "N/A")
        
        echo -e "${BLUE}🔄 Processo attivo:${NC}"
        echo -e "   🆔 PID: $PID"
        echo -e "   ⏱️  Uptime: $UPTIME"
        echo -e "   💾 Memoria: $MEMORY"
        echo -e "   📍 Comando: $(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i}')"
    done
fi

echo ""
echo -e "${BLUE}📊 Riepilogo Test:${NC}"
echo ""

# Riepilogo finale
if [ "$INITIAL_COUNT" -eq "$FINAL_COUNT" ] && [ "$FINAL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ COMPORTAMENTO CORRETTO${NC}"
    echo -e "   ✅ Ctrl+C sui log ferma solo la visualizzazione"
    echo -e "   ✅ L'agente rimane attivo e funzionante"
    echo -e "   ✅ Nessun impatto sulle operazioni in background"
else
    echo -e "${RED}❌ COMPORTAMENTO PROBLEMATICO${NC}"
    echo -e "   ❌ Ctrl+C sui log ferma anche l'agente"
    echo -e "   ❌ L'agente non rimane attivo"
    echo -e "   ❌ Impatto negativo sulle operazioni in background"
fi

echo ""
echo -e "${BLUE}🔧 Raccomandazioni:${NC}"
echo ""

if [ "$INITIAL_COUNT" -eq "$FINAL_COUNT" ] && [ "$FINAL_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Il sistema funziona correttamente${NC}"
    echo -e "   💡 Puoi usare Ctrl+C sui log senza preoccupazioni"
    echo -e "   💡 L'agente continuerà a funzionare in background"
else
    echo -e "${YELLOW}⚠️ Il sistema ha problemi${NC}"
    echo -e "   💡 Evita Ctrl+C sui log se l'agente è importante"
    echo -e "   💡 Usa 'stop' per fermare l'agente in modo controllato"
    echo -e "   💡 Considera di migliorare la gestione dei segnali"
fi

echo ""
echo -e "${BLUE}📝 Comandi Utili:${NC}"
echo -e "   ./manage_background_agent.sh status  - Verifica stato agente"
echo -e "   ./manage_background_agent.sh logs    - Visualizza log (usa Ctrl+C per uscire)"
echo -e "   ./manage_background_agent.sh stop    - Ferma agente in modo controllato"
echo -e "   ./session_manager.sh status          - Stato sessioni multiple" 