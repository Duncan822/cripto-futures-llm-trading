#!/bin/bash

# Script per verificare e gestire sessioni multiple del Background Agent
# Controlla quante istanze sono attive e fornisce opzioni di gestione

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Verifica Sessioni Multiple Background Agent${NC}"
echo ""

# Funzione per contare i processi attivi
count_active_processes() {
    ps aux | grep "python background_agent.py" | grep -v grep | wc -l
}

# Funzione per ottenere tutti i PID attivi
get_active_pids() {
    ps aux | grep "python background_agent.py" | grep -v grep | awk '{print $2}'
}

# Funzione per ottenere informazioni dettagliate
get_process_info() {
    local pid=$1
    if [ -n "$pid" ]; then
        echo -e "   🆔 PID: $pid"
        echo -e "   ⏱️  Uptime: $(ps -o etime= -p $pid 2>/dev/null || echo 'N/A')"
        echo -e "   💾 Memoria: $(ps -o rss= -p $pid 2>/dev/null | awk '{print $1/1024 " MB"}' || echo 'N/A')"
        echo -e "   📊 CPU: $(ps -o %cpu= -p $pid 2>/dev/null || echo 'N/A')%"
    fi
}

# Controlla se esiste il file PID
if [ -f "background_agent.pid" ]; then
    STORED_PID=$(cat background_agent.pid)
    echo -e "${YELLOW}📄 File PID trovato: $STORED_PID${NC}"
    
    # Verifica se il PID memorizzato è ancora attivo
    if ps -p "$STORED_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PID memorizzato è attivo${NC}"
    else
        echo -e "${RED}❌ PID memorizzato non è più attivo${NC}"
        echo -e "${YELLOW}💡 Rimuovendo file PID obsoleto...${NC}"
        rm -f background_agent.pid
    fi
else
    echo -e "${YELLOW}⚠️ Nessun file PID trovato${NC}"
fi

echo ""

# Conta processi attivi
ACTIVE_COUNT=$(count_active_processes)
echo -e "${BLUE}📊 Processi Background Agent Attivi: $ACTIVE_COUNT${NC}"

if [ "$ACTIVE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}💡 Nessun Background Agent in esecuzione${NC}"
    echo -e "   Per avviarne uno: ./manage_background_agent.sh start"
    exit 0
elif [ "$ACTIVE_COUNT" -eq 1 ]; then
    echo -e "${GREEN}✅ Situazione normale: 1 istanza attiva${NC}"
else
    echo -e "${RED}⚠️ ATTENZIONE: $ACTIVE_COUNT istanze attive!${NC}"
    echo -e "${YELLOW}💡 Questo può causare conflitti e duplicazione di operazioni${NC}"
fi

echo ""

# Mostra dettagli di tutti i processi
if [ "$ACTIVE_COUNT" -gt 0 ]; then
    echo -e "${PURPLE}📋 Dettagli Processi Attivi:${NC}"
    echo ""
    
    COUNTER=1
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            echo -e "${BLUE}🔄 Istanza #$COUNTER:${NC}"
            get_process_info "$pid"
            
            # Controlla se è il PID memorizzato
            if [ "$pid" = "$STORED_PID" ]; then
                echo -e "   📌 PID Memorizzato: Sì"
            else
                echo -e "   📌 PID Memorizzato: No"
            fi
            
            echo ""
            COUNTER=$((COUNTER + 1))
        fi
    done < <(get_active_pids)
fi

# Controlla operazioni attive
echo -e "${PURPLE}🔍 Operazioni Attive:${NC}"
echo ""

# Controlla backtest attivi
BACKTEST_COUNT=$(ps aux | grep "freqtrade backtesting" | grep -v grep | wc -l)
echo -e "   📊 Backtest attivi: $BACKTEST_COUNT"

# Controlla generazione strategie
STRATEGY_GEN_COUNT=$(ps aux | grep "strategy_generator" | grep -v grep | wc -l)
echo -e "   🎯 Generazione strategie: $STRATEGY_GEN_COUNT"

# Controlla validazione strategie
VALIDATION_COUNT=$(ps aux | grep "strategy_validator" | grep -v grep | wc -l)
echo -e "   ✅ Validazione strategie: $VALIDATION_COUNT"

# Controlla ottimizzazione strategie
OPTIMIZATION_COUNT=$(ps aux | grep "optimizer_agent" | grep -v grep | wc -l)
echo -e "   🔧 Ottimizzazione strategie: $OPTIMIZATION_COUNT"

echo ""

# Se ci sono multiple istanze, mostra opzioni
if [ "$ACTIVE_COUNT" -gt 1 ]; then
    echo -e "${RED}🚨 GESTIONE SESSIONI MULTIPLE${NC}"
    echo ""
    echo -e "${YELLOW}Opzioni disponibili:${NC}"
    echo ""
    echo -e "1️⃣  ${GREEN}Mantieni solo il PID memorizzato${NC}"
    echo -e "   ./manage_background_agent.sh stop-others"
    echo ""
    echo -e "2️⃣  ${GREEN}Ferma tutte le istanze${NC}"
    echo -e "   ./manage_background_agent.sh stop-all"
    echo ""
    echo -e "3️⃣  ${GREEN}Riavvia tutto pulito${NC}"
    echo -e "   ./manage_background_agent.sh restart"
    echo ""
    echo -e "4️⃣  ${GREEN}Mostra log di tutte le istanze${NC}"
    echo -e "   ./manage_background_agent.sh logs-all"
    echo ""
    
    # Chiedi all'utente cosa fare
    echo -e "${BLUE}💭 Cosa vuoi fare? (1-4 o 'q' per uscire):${NC}"
    read -r choice
    
    case $choice in
        1)
            echo -e "${YELLOW}🛑 Fermando istanze non memorizzate...${NC}"
            for pid in $(get_active_pids); do
                if [ "$pid" != "$STORED_PID" ]; then
                    echo -e "   Fermando PID: $pid"
                    kill "$pid" 2>/dev/null || echo "   ❌ Errore nel fermare PID: $pid"
                fi
            done
            echo -e "${GREEN}✅ Operazione completata${NC}"
            ;;
        2)
            echo -e "${YELLOW}🛑 Fermando tutte le istanze...${NC}"
            ./manage_background_agent.sh stop
            echo -e "${GREEN}✅ Tutte le istanze fermate${NC}"
            ;;
        3)
            echo -e "${YELLOW}🔄 Riavvio pulito...${NC}"
            ./manage_background_agent.sh restart
            echo -e "${GREEN}✅ Riavvio completato${NC}"
            ;;
        4)
            echo -e "${YELLOW}📝 Mostrando log di tutte le istanze...${NC}"
            echo -e "${BLUE}Log disponibili:${NC}"
            ls -la logs/background_agent_*.log 2>/dev/null || echo "   Nessun log trovato"
            echo ""
            echo -e "${BLUE}Ultime righe di ogni log:${NC}"
            for log in logs/background_agent_*.log 2>/dev/null; do
                if [ -f "$log" ]; then
                    echo -e "${YELLOW}📄 $log:${NC}"
                    tail -5 "$log" | sed 's/^/   /'
                    echo ""
                fi
            done
            ;;
        q|Q)
            echo -e "${BLUE}👋 Uscita${NC}"
            ;;
        *)
            echo -e "${RED}❌ Scelta non valida${NC}"
            ;;
    esac
fi

echo ""
echo -e "${BLUE}📊 Riepilogo Finale:${NC}"
echo -e "   🔄 Processi attivi: $(count_active_processes)"
echo -e "   📊 Backtest attivi: $(ps aux | grep "freqtrade backtesting" | grep -v grep | wc -l)"
echo -e "   🎯 Generazione strategie: $(ps aux | grep "strategy_generator" | grep -v grep | wc -l)"
echo -e "   ✅ Validazione strategie: $(ps aux | grep "strategy_validator" | grep -v grep | wc -l)"
echo -e "   🔧 Ottimizzazione strategie: $(ps aux | grep "optimizer_agent" | grep -v grep | wc -l)" 