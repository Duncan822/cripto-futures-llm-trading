#!/bin/bash

# Script per avviare il monitor LLM
# Fornisce un'interfaccia semplice per gestire il monitoraggio

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurazione
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=${1:-8080}
LOG_FILE="$SCRIPT_DIR/llm_monitor.log"
PID_FILE="$SCRIPT_DIR/llm_monitor.pid"

# Funzioni di utilità
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Controlla se il monitor è già in esecuzione
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# Avvia il monitor
start_monitor() {
    log_info "Avvio del monitor LLM..."
    
    if check_running; then
        log_warn "Il monitor è già in esecuzione (PID: $(cat $PID_FILE))"
        return 1
    fi
    
    # Attiva l'ambiente virtuale se presente
    if [ -d "venv" ]; then
        log_debug "Attivazione ambiente virtuale..."
        source venv/bin/activate
    fi
    
    # Installa dipendenze se necessario
    if ! python -c "import flask, psutil" 2>/dev/null; then
        log_info "Installazione dipendenze..."
        pip install flask psutil
    fi
    
    # Avvia il monitor in background
    log_debug "Avvio processo monitor..."
    nohup python llm_monitor.py > "$LOG_FILE" 2>&1 &
    MONITOR_PID=$!
    
    # Salva PID
    echo $MONITOR_PID > "$PID_FILE"
    
    # Attendi che il monitor si avvii
    log_info "Attesa avvio monitor..."
    sleep 3
    
    # Controlla se è avviato
    if check_running; then
        log_info "✅ Monitor LLM avviato con successo!"
        log_info "🌐 Dashboard: http://localhost:$PORT"
        log_info "📊 Log: $LOG_FILE"
        log_info "🆔 PID: $MONITOR_PID"
        
        # Apri browser se possibile
        if command -v xdg-open > /dev/null 2>&1; then
            xdg-open "http://localhost:$PORT" &
        elif command -v open > /dev/null 2>&1; then
            open "http://localhost:$PORT" &
        fi
        
        return 0
    else
        log_error "❌ Errore nell'avvio del monitor"
        return 1
    fi
}

# Ferma il monitor
stop_monitor() {
    log_info "Arresto del monitor LLM..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_debug "Terminazione processo $PID..."
            kill "$PID"
            
            # Attendi terminazione
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Forza terminazione se necessario
            if ps -p "$PID" > /dev/null 2>&1; then
                log_warn "Forzatura terminazione processo..."
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            log_info "✅ Monitor fermato"
            return 0
        else
            log_warn "Processo non trovato, rimozione PID file"
            rm -f "$PID_FILE"
        fi
    else
        log_warn "Nessun PID file trovato"
    fi
    
    return 0
}

# Mostra stato
show_status() {
    log_info "Stato del monitor LLM:"
    
    if check_running; then
        PID=$(cat "$PID_FILE")
        log_info "✅ Monitor in esecuzione (PID: $PID)"
        log_info "🌐 Dashboard: http://localhost:$PORT"
        
        # Mostra ultime righe del log
        if [ -f "$LOG_FILE" ]; then
            log_info "📊 Ultime righe del log:"
            tail -n 5 "$LOG_FILE" | sed 's/^/  /'
        fi
        
        # Controlla se la porta è in ascolto
        if netstat -tlnp 2>/dev/null | grep ":$PORT " > /dev/null; then
            log_info "✅ Porta $PORT in ascolto"
        else
            log_warn "⚠️  Porta $PORT non in ascolto"
        fi
        
    else
        log_info "❌ Monitor non in esecuzione"
    fi
}

# Mostra log in tempo reale
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        log_info "Visualizzazione log in tempo reale (Ctrl+C per uscire):"
        tail -f "$LOG_FILE"
    else
        log_error "File di log non trovato"
        return 1
    fi
}

# Test del monitor
test_monitor() {
    log_info "Test del monitor LLM..."
    
    # Avvia monitor se non è già in esecuzione
    if ! check_running; then
        start_monitor
        if [ $? -ne 0 ]; then
            log_error "Impossibile avviare il monitor per il test"
            return 1
        fi
        sleep 5
    fi
    
    # Test API
    log_info "Test delle API del monitor..."
    
    if curl -s "http://localhost:$PORT/api/status" > /dev/null; then
        log_info "✅ API status funzionante"
    else
        log_error "❌ API status non funzionante"
        return 1
    fi
    
    if curl -s "http://localhost:$PORT/api/models" > /dev/null; then
        log_info "✅ API models funzionante"
    else
        log_error "❌ API models non funzionante"
        return 1
    fi
    
    log_info "✅ Tutti i test superati!"
    return 0
}

# Pulisci file temporanei
cleanup() {
    log_info "Pulizia file temporanei..."
    rm -f "$PID_FILE"
    log_info "✅ Pulizia completata"
}

# Menu principale
show_help() {
    echo "Usage: $0 [COMMAND] [PORT]"
    echo ""
    echo "Commands:"
    echo "  start [PORT]     Avvia il monitor (default: 8080)"
    echo "  stop             Ferma il monitor"
    echo "  restart [PORT]   Riavvia il monitor"
    echo "  status           Mostra lo stato del monitor"
    echo "  logs             Mostra i log in tempo reale"
    echo "  test             Testa il monitor"
    echo "  cleanup          Pulisce i file temporanei"
    echo "  help             Mostra questo aiuto"
    echo ""
    echo "Examples:"
    echo "  $0 start         # Avvia su porta 8080"
    echo "  $0 start 9090    # Avvia su porta 9090"
    echo "  $0 status        # Mostra stato"
    echo "  $0 logs          # Mostra log"
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
        stop_monitor
        sleep 2
        start_monitor
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        test_monitor
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Comando sconosciuto: $1"
        show_help
        exit 1
        ;;
esac 