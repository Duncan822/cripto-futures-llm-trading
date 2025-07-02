#!/bin/bash

# Script per gestire il monitoraggio dei backtest
# Comandi: start, stop, status, logs, monitor

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PID_FILE="backtest_monitor.pid"
MONITOR_NAME="Backtest Monitor"

show_help() {
    echo -e "${BLUE}🔧 Gestione Backtest Monitor${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandi disponibili:"
    echo -e "  ${GREEN}start${NC}     - Avvia il monitor"
    echo -e "  ${RED}stop${NC}      - Ferma il monitor"
    echo -e "  ${YELLOW}restart${NC}   - Riavvia il monitor"
    echo -e "  ${CYAN}status${NC}    - Mostra lo stato del monitor"
    echo -e "  ${BLUE}logs${NC}      - Mostra i log in tempo reale"
    echo -e "  ${BLUE}monitor${NC}   - Monitora backtest attivi"
    echo -e "  ${BLUE}help${NC}      - Mostra questo aiuto"
    echo ""
    echo "Esempi:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 monitor"
}

check_pid() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    else
        return 1
    fi
}

start_monitor() {
    echo -e "${BLUE}🚀 Avvio $MONITOR_NAME...${NC}"
    
    if check_pid; then
        echo -e "${YELLOW}⚠️ $MONITOR_NAME è già in esecuzione (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    # Attiva l'ambiente virtuale se esiste
    if [ -d "venv" ]; then
        echo -e "${YELLOW}🔧 Attivazione ambiente virtuale...${NC}"
        source venv/bin/activate
    fi
    
    # Crea directory per i log se non esiste
    mkdir -p logs/backtests
    
    # Avvia il monitor in background
    nohup python backtest_monitor.py > logs/backtest_monitor_$(date +%Y%m%d_%H%M%S).log 2>&1 &
    
    # Salva il PID
    echo $! > backtest_monitor.pid
    
    # Aspetta un momento e controlla se è partito
    sleep 2
    if check_pid; then
        echo -e "${GREEN}✅ $MONITOR_NAME avviato con successo (PID: $(cat $PID_FILE))${NC}"
    else
        echo -e "${RED}❌ Errore nell'avvio di $MONITOR_NAME${NC}"
        return 1
    fi
}

stop_monitor() {
    echo -e "${YELLOW}🛑 Arresto $MONITOR_NAME...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            echo -e "${GREEN}✅ Segnale di arresto inviato a PID $PID${NC}"
            
            # Aspetta l'arresto
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ $MONITOR_NAME arrestato${NC}"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Forza l'arresto se necessario
            echo -e "${YELLOW}⚠️ Forzatura arresto...${NC}"
            kill -9 "$PID" 2>/dev/null || true
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ $MONITOR_NAME arrestato forzatamente${NC}"
        else
            echo -e "${YELLOW}⚠️ $MONITOR_NAME non era in esecuzione${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️ File PID non trovato, $MONITOR_NAME non era in esecuzione${NC}"
    fi
}

restart_monitor() {
    echo -e "${BLUE}🔄 Riavvio $MONITOR_NAME...${NC}"
    stop_monitor
    sleep 2
    start_monitor
}

show_status() {
    echo -e "${BLUE}📊 Stato $MONITOR_NAME${NC}"
    echo ""
    
    if check_pid; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✅ $MONITOR_NAME è in esecuzione${NC}"
        echo -e "   PID: $PID"
        echo -e "   Uptime: $(ps -o etime= -p $PID)"
        echo -e "   Memoria: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
    else
        echo -e "${RED}❌ $MONITOR_NAME non è in esecuzione${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📁 File di sistema:${NC}"
    if [ -d "logs/backtests" ]; then
        BACKTEST_LOG_COUNT=$(ls logs/backtests/*.log 2>/dev/null | wc -l)
        echo -e "   📝 Log backtest: $BACKTEST_LOG_COUNT"
    else
        echo -e "   ❌ Directory log backtest: mancante"
    fi
    
    if [ -d "backtest_results" ]; then
        RESULT_COUNT=$(ls backtest_results/*.json 2>/dev/null | wc -l)
        echo -e "   📊 Risultati backtest: $RESULT_COUNT"
    else
        echo -e "   ❌ Directory risultati: mancante"
    fi
    
    echo ""
    echo -e "${BLUE}🔧 Comandi utili:${NC}"
    echo -e "   $0 logs     - Visualizza log in tempo reale"
    echo -e "   $0 monitor  - Monitora backtest attivi"
    echo -e "   $0 restart  - Riavvia il monitor"
}

show_logs() {
    echo -e "${BLUE}📋 Log $MONITOR_NAME${NC}"
    echo ""
    
    # Trova il file di log più recente
    LATEST_LOG=$(ls -t logs/backtest_monitor_*.log 2>/dev/null | head -1)
    
    if [ -n "$LATEST_LOG" ]; then
        echo -e "${GREEN}📄 File di log: $LATEST_LOG${NC}"
        echo -e "${YELLOW}💡 Premi Ctrl+C per uscire${NC}"
        echo ""
        tail -f "$LATEST_LOG"
    else
        echo -e "${YELLOW}⚠️ Nessun file di log trovato${NC}"
        echo "Il monitor potrebbe non essere mai stato avviato"
    fi
}

monitor_backtests() {
    echo -e "${BLUE}📊 Monitoraggio Backtest Attivi${NC}"
    echo ""
    
    if ! check_pid; then
        echo -e "${RED}❌ $MONITOR_NAME non è in esecuzione${NC}"
        echo "Avvia prima il monitor con: $0 start"
        return 1
    fi
    
    echo -e "${YELLOW}💡 Monitoraggio in tempo reale. Premi Ctrl+C per uscire${NC}"
    echo ""
    
    # Monitora continuamente i backtest attivi
    while true; do
        clear
        echo -e "${BLUE}📊 Stato Backtest - $(date)${NC}"
        echo ""
        
        # Conta i log di backtest attivi
        if [ -d "logs/backtests" ]; then
            ACTIVE_LOGS=$(find logs/backtests -name "*.log" -mmin -10 2>/dev/null | wc -l)
            echo -e "🔄 Backtest attivi (ultimi 10 min): $ACTIVE_LOGS"
            
            # Mostra i log più recenti
            if [ $ACTIVE_LOGS -gt 0 ]; then
                echo ""
                echo -e "${GREEN}📋 Log recenti:${NC}"
                find logs/backtests -name "*.log" -mmin -10 2>/dev/null | head -5 | while read log; do
                    echo -e "   📄 $(basename $log) - $(stat -c %y $log | cut -d' ' -f2 | cut -d'.' -f1)"
                done
            fi
        fi
        
        # Conta i risultati completati
        if [ -d "backtest_results" ]; then
            COMPLETED_RESULTS=$(ls backtest_results/*.json 2>/dev/null | wc -l)
            echo -e "✅ Backtest completati: $COMPLETED_RESULTS"
        fi
        
        echo ""
        echo -e "${YELLOW}Aggiornamento ogni 5 secondi...${NC}"
        sleep 5
    done
}

# Gestione comandi
case "${1:-help}" in
    start)
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    restart)
        restart_monitor
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    monitor)
        monitor_backtests
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando sconosciuto: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac 