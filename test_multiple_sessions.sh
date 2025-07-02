#!/bin/bash

# Script per testare la gestione delle sessioni multiple
# Simula l'avvio di multiple istanze e testa i comandi di gestione

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Test Gestione Sessioni Multiple Background Agent${NC}"
echo ""

# Funzione per contare i processi attivi
count_active_processes() {
    ps aux | grep "python background_agent.py" | grep -v grep | wc -l
}

# Funzione per ottenere tutti i PID attivi
get_active_pids() {
    ps aux | grep "python background_agent.py" | grep -v grep | awk '{print $2}'
}

# Controlla stato iniziale
echo -e "${BLUE}📊 Stato Iniziale:${NC}"
INITIAL_COUNT=$(count_active_processes)
echo -e "   🔄 Processi attivi: $INITIAL_COUNT"

if [ "$INITIAL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Nessun Background Agent attivo${NC}"
    echo -e "   Avvia prima un agente con: ./manage_background_agent.sh start"
    exit 1
fi

echo ""

# Test 1: Verifica sessioni multiple
echo -e "${PURPLE}🧪 Test 1: Verifica Sessioni Multiple${NC}"
echo -e "${YELLOW}Eseguendo: ./manage_background_agent.sh sessions${NC}"
echo ""

./manage_background_agent.sh sessions

echo ""
echo -e "${GREEN}✅ Test 1 completato${NC}"
echo ""

# Test 2: Log di tutte le istanze
echo -e "${PURPLE}🧪 Test 2: Log di Tutte le Istanze${NC}"
echo -e "${YELLOW}Eseguendo: ./manage_background_agent.sh logs-all${NC}"
echo ""

./manage_background_agent.sh logs-all

echo ""
echo -e "${GREEN}✅ Test 2 completato${NC}"
echo ""

# Test 3: Simulazione sessioni multiple (se c'è solo 1 istanza)
if [ "$INITIAL_COUNT" -eq 1 ]; then
    echo -e "${PURPLE}🧪 Test 3: Simulazione Sessioni Multiple${NC}"
    echo -e "${YELLOW}⚠️ ATTENZIONE: Questo test creerà istanze multiple!${NC}"
    echo ""
    
    read -p "Vuoi procedere con la simulazione? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🔄 Creando istanze multiple...${NC}"
        
        # Avvia istanze aggiuntive in background
        for i in {1..2}; do
            echo -e "   Avviando istanza aggiuntiva #$i..."
            nohup python background_agent.py > logs/test_session_$i.log 2>&1 &
            sleep 1
        done
        
        echo ""
        echo -e "${GREEN}✅ Istanze multiple create${NC}"
        echo ""
        
        # Verifica il nuovo stato
        NEW_COUNT=$(count_active_processes)
        echo -e "${BLUE}📊 Nuovo Stato:${NC}"
        echo -e "   🔄 Processi attivi: $NEW_COUNT"
        echo ""
        
        # Testa la gestione
        echo -e "${YELLOW}🔄 Testando gestione sessioni multiple...${NC}"
        ./manage_background_agent.sh sessions
        
        echo ""
        echo -e "${YELLOW}💭 Opzioni disponibili:${NC}"
        echo "   1. ./manage_background_agent.sh stop-others"
        echo "   2. ./manage_background_agent.sh stop-all"
        echo "   3. ./manage_background_agent.sh restart"
        echo ""
        
        read -p "Vuoi fermare le istanze extra? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}🛑 Fermando istanze extra...${NC}"
            ./manage_background_agent.sh stop-others
            
            echo ""
            FINAL_COUNT=$(count_active_processes)
            echo -e "${GREEN}✅ Istanze extra fermate${NC}"
            echo -e "   🔄 Processi attivi: $FINAL_COUNT"
        else
            echo -e "${YELLOW}⚠️ Istanze multiple rimangono attive${NC}"
            echo -e "   Usa manualmente: ./manage_background_agent.sh stop-others"
        fi
    else
        echo -e "${BLUE}⏭️ Test 3 saltato${NC}"
    fi
else
    echo -e "${PURPLE}🧪 Test 3: Gestione Sessioni Multiple Esistenti${NC}"
    echo -e "${YELLOW}Rilevate $INITIAL_COUNT istanze attive${NC}"
    echo ""
    
    ./manage_background_agent.sh sessions
    
    echo ""
    echo -e "${YELLOW}💭 Opzioni disponibili:${NC}"
    echo "   1. ./manage_background_agent.sh stop-others"
    echo "   2. ./manage_background_agent.sh stop-all"
    echo "   3. ./manage_background_agent.sh restart"
    echo ""
    
    read -p "Vuoi gestire le istanze multiple? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}🛑 Fermando istanze extra...${NC}"
        ./manage_background_agent.sh stop-others
        
        echo ""
        FINAL_COUNT=$(count_active_processes)
        echo -e "${GREEN}✅ Gestione completata${NC}"
        echo -e "   🔄 Processi attivi: $FINAL_COUNT"
    else
        echo -e "${BLUE}⏭️ Gestione saltata${NC}"
    fi
fi

echo ""
echo -e "${BLUE}📊 Test Completati:${NC}"
echo ""

# Riepilogo finale
FINAL_COUNT=$(count_active_processes)
echo -e "${GREEN}✅ Test completati con successo${NC}"
echo -e "   🔄 Processi attivi finali: $FINAL_COUNT"
echo ""

# Mostra comandi utili
echo -e "${BLUE}🔧 Comandi Utili:${NC}"
echo -e "   ./manage_background_agent.sh sessions    - Verifica sessioni multiple"
echo -e "   ./manage_background_agent.sh stop-others - Ferma istanze extra"
echo -e "   ./manage_background_agent.sh stop-all    - Ferma tutte le istanze"
echo -e "   ./manage_background_agent.sh logs-all    - Log di tutte le istanze"
echo -e "   ./manage_background_agent.sh status      - Stato completo"
echo ""

echo -e "${GREEN}🎯 Raccomandazioni:${NC}"
echo -e "   ✅ Usa sempre 'sessions' prima di avviare"
echo -e "   ✅ Mantieni una sola istanza attiva"
echo -e "   ✅ Monitora regolarmente lo stato"
echo -e "   ✅ Usa 'stop-others' per gestire conflitti" 