#!/bin/bash

# Session Manager per Background Agent
# Gestisce sessioni multiple e fornisce un'interfaccia unificata

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PID_FILE="background_agent.pid"
LOCK_FILE="session.lock"
SESSION_LOG="session_manager.log"

# Funzione per log
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$SESSION_LOG"
    echo -e "$message"
}

# Funzione per contare i processi attivi
count_active_processes() {
    ps aux | grep "python background_agent.py" | grep -v grep | wc -l
}

# Funzione per ottenere tutti i PID attivi
get_active_pids() {
    ps aux | grep "python background_agent.py" | grep -v grep | awk '{print $2}'
}

# Funzione per ottenere informazioni sessione
get_session_info() {
    local pid=$1
    if [ -n "$pid" ]; then
        local tty=$(ps -o tty= -p "$pid" 2>/dev/null || echo "N/A")
        local user=$(ps -o user= -p "$pid" 2>/dev/null || echo "N/A")
        local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null || echo "N/A")
        echo "TTY: $tty, User: $user, Start: $start_time"
    fi
}

# Funzione per creare lock
create_lock() {
    local session_id="$1"
    echo "$session_id" > "$LOCK_FILE"
    log_message "${GREEN}🔒 Lock creato per sessione: $session_id${NC}"
}

# Funzione per rimuovere lock
remove_lock() {
    if [ -f "$LOCK_FILE" ]; then
        rm -f "$LOCK_FILE"
        log_message "${YELLOW}🔓 Lock rimosso${NC}"
    fi
}

# Funzione per controllare lock
check_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_session=$(cat "$LOCK_FILE")
        echo "$lock_session"
    else
        echo ""
    fi
}

# Funzione per mostrare stato sessioni
show_session_status() {
    echo -e "${BLUE}🔍 Stato Sessioni Background Agent${NC}"
    echo ""
    
    # Controlla lock
    local lock_session=$(check_lock)
    if [ -n "$lock_session" ]; then
        echo -e "${YELLOW}🔒 Sessione attiva: $lock_session${NC}"
    else
        echo -e "${GREEN}🔓 Nessuna sessione attiva${NC}"
    fi
    
    echo ""
    
    # Conta processi attivi
    local active_count=$(count_active_processes)
    echo -e "${BLUE}📊 Processi Background Agent Attivi: $active_count${NC}"
    
    if [ "$active_count" -eq 0 ]; then
        echo -e "${YELLOW}💡 Nessun Background Agent in esecuzione${NC}"
        return 0
    fi
    
    echo ""
    echo -e "${PURPLE}📋 Dettagli Processi:${NC}"
    echo ""
    
    local counter=1
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            echo -e "${BLUE}🔄 Processo #$counter:${NC}"
            echo -e "   🆔 PID: $pid"
            echo -e "   ⏱️  Uptime: $(ps -o etime= -p $pid 2>/dev/null || echo 'N/A')"
            echo -e "   💾 Memoria: $(ps -o rss= -p $pid 2>/dev/null | awk '{print $1/1024 " MB"}' || echo 'N/A')"
            echo -e "   📊 CPU: $(ps -o %cpu= -p $pid 2>/dev/null || echo 'N/A')%"
            
            # Informazioni sessione
            local session_info=$(get_session_info "$pid")
            echo -e "   🔗 Sessione: $session_info"
            
            # Controlla se è il PID memorizzato
            if [ -f "$PID_FILE" ] && [ "$pid" = "$(cat $PID_FILE)" ]; then
                echo -e "   📌 PID Memorizzato: Sì"
            else
                echo -e "   📌 PID Memorizzato: No"
            fi
            
            echo ""
            counter=$((counter + 1))
        fi
    done < <(get_active_pids)
    
    # Controlla operazioni attive
    echo -e "${PURPLE}🔍 Operazioni Attive:${NC}"
    echo ""
    
    local backtest_count=$(ps aux | grep "freqtrade backtesting" | grep -v grep | wc -l)
    local strategy_gen_count=$(ps aux | grep "strategy_generator" | grep -v grep | wc -l)
    local validation_count=$(ps aux | grep "strategy_validator" | grep -v grep | wc -l)
    local optimization_count=$(ps aux | grep "optimizer_agent" | grep -v grep | wc -l)
    
    echo -e "   📊 Backtest attivi: $backtest_count"
    echo -e "   🎯 Generazione strategie: $strategy_gen_count"
    echo -e "   ✅ Validazione strategie: $validation_count"
    echo -e "   🔧 Ottimizzazione strategie: $optimization_count"
}

# Funzione per avviare sessione controllata
start_controlled_session() {
    local session_id="$1"
    
    echo -e "${BLUE}🚀 Avvio Sessione Controllata${NC}"
    echo ""
    
    # Controlla se c'è già un lock
    local existing_lock=$(check_lock)
    if [ -n "$existing_lock" ]; then
        echo -e "${RED}❌ Sessione già attiva: $existing_lock${NC}"
        echo -e "${YELLOW}💡 Usa 'join' per unirti alla sessione esistente${NC}"
        return 1
    fi
    
    # Controlla se c'è già un processo attivo
    local active_count=$(count_active_processes)
    if [ "$active_count" -gt 0 ]; then
        echo -e "${YELLOW}⚠️ Processi già attivi ($active_count)${NC}"
        echo -e "${YELLOW}💡 Usa 'cleanup' per pulire prima di avviare${NC}"
        return 1
    fi
    
    # Crea lock
    create_lock "$session_id"
    
    # Avvia l'agente
    echo -e "${YELLOW}🔄 Avviando Background Agent...${NC}"
    ./manage_background_agent.sh start
    
    if [ $? -eq 0 ]; then
        log_message "${GREEN}✅ Sessione avviata con successo${NC}"
        echo -e "${GREEN}✅ Sessione controllata avviata${NC}"
    else
        remove_lock
        log_message "${RED}❌ Errore nell'avvio della sessione${NC}"
        echo -e "${RED}❌ Errore nell'avvio della sessione${NC}"
        return 1
    fi
}

# Funzione per unirsi a una sessione esistente
join_session() {
    local session_id="$1"
    
    echo -e "${BLUE}🤝 Unione a Sessione Esistente${NC}"
    echo ""
    
    # Controlla se c'è un lock
    local existing_lock=$(check_lock)
    if [ -z "$existing_lock" ]; then
        echo -e "${YELLOW}⚠️ Nessuna sessione attiva da cui unirsi${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Unito alla sessione: $existing_lock${NC}"
    echo -e "${YELLOW}💡 Usa 'status' per vedere lo stato${NC}"
    echo -e "${YELLOW}💡 Usa 'logs' per vedere i log${NC}"
    
    log_message "${GREEN}✅ Nuovo utente unito alla sessione: $existing_lock${NC}"
}

# Funzione per fermare sessione
stop_session() {
    local session_id="$1"
    
    echo -e "${YELLOW}🛑 Arresto Sessione Controllata${NC}"
    echo ""
    
    # Controlla se c'è un lock
    local existing_lock=$(check_lock)
    if [ -z "$existing_lock" ]; then
        echo -e "${YELLOW}⚠️ Nessuna sessione attiva da fermare${NC}"
        return 1
    fi
    
    # Controlla se è la sessione corretta
    if [ "$session_id" != "$existing_lock" ]; then
        echo -e "${RED}❌ Sessione non corrisponde: attesa $session_id, trovata $existing_lock${NC}"
        return 1
    fi
    
    # Ferma l'agente
    echo -e "${YELLOW}🔄 Fermando Background Agent...${NC}"
    ./manage_background_agent.sh stop
    
    # Rimuovi lock
    remove_lock
    
    log_message "${GREEN}✅ Sessione fermata con successo${NC}"
    echo -e "${GREEN}✅ Sessione controllata fermata${NC}"
}

# Funzione per pulizia
cleanup_session() {
    echo -e "${YELLOW}🧹 Pulizia Sessioni${NC}"
    echo ""
    
    # Ferma tutti i processi
    local active_count=$(count_active_processes)
    if [ "$active_count" -gt 0 ]; then
        echo -e "${YELLOW}🛑 Fermando $active_count processi...${NC}"
        ./manage_background_agent.sh stop-all
    fi
    
    # Rimuovi lock
    remove_lock
    
    log_message "${GREEN}✅ Pulizia completata${NC}"
    echo -e "${GREEN}✅ Pulizia completata${NC}"
}

# Funzione per mostrare aiuto
show_help() {
    echo -e "${BLUE}🔧 Session Manager per Background Agent${NC}"
    echo ""
    echo "Uso: $0 [comando] [session_id]"
    echo ""
    echo "Comandi disponibili:"
    echo -e "  ${GREEN}start [id]${NC}   - Avvia sessione controllata"
    echo -e "  ${YELLOW}join [id]${NC}    - Unisciti a sessione esistente"
    echo -e "  ${RED}stop [id]${NC}     - Ferma sessione controllata"
    echo -e "  ${PURPLE}status${NC}     - Mostra stato sessioni"
    echo -e "  ${CYAN}cleanup${NC}     - Pulizia completa"
    echo -e "  ${BLUE}logs${NC}        - Mostra log sessione"
    echo -e "  ${BLUE}help${NC}        - Mostra questo aiuto"
    echo ""
    echo "Esempi:"
    echo "  $0 start my_session"
    echo "  $0 join my_session"
    echo "  $0 status"
    echo "  $0 stop my_session"
    echo ""
    echo "Note:"
    echo "  - Una sola sessione controllata alla volta"
    echo "  - Usa 'join' per unirti a sessioni esistenti"
    echo "  - Usa 'cleanup' per pulizia completa"
}

# Funzione per mostrare log
show_logs() {
    echo -e "${BLUE}📋 Log Session Manager${NC}"
    echo ""
    
    if [ -f "$SESSION_LOG" ]; then
        echo -e "${GREEN}📄 File di log: $SESSION_LOG${NC}"
        echo -e "${YELLOW}💡 Ultime 20 righe:${NC}"
        echo ""
        tail -20 "$SESSION_LOG"
    else
        echo -e "${YELLOW}⚠️ Nessun log trovato${NC}"
    fi
}

# Gestione comandi
case "${1:-help}" in
    start)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Specifica un ID sessione${NC}"
            echo "Uso: $0 start [session_id]"
            exit 1
        fi
        start_controlled_session "$2"
        ;;
    join)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Specifica un ID sessione${NC}"
            echo "Uso: $0 join [session_id]"
            exit 1
        fi
        join_session "$2"
        ;;
    stop)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Specifica un ID sessione${NC}"
            echo "Uso: $0 stop [session_id]"
            exit 1
        fi
        stop_session "$2"
        ;;
    status)
        show_session_status
        ;;
    cleanup)
        cleanup_session
        ;;
    logs)
        show_logs
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