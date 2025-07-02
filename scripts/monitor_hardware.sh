#!/bin/bash

# Script per monitorare l'hardware durante l'utilizzo di Ollama
# Uso: ./monitor_hardware.sh [intervallo_secondi]

INTERVAL=${1:-30}  # Default 30 secondi
LOG_FILE="hardware_monitor.log"

echo "🔍 Monitoraggio Hardware Avviato"
echo "⏱️  Intervallo: ${INTERVAL} secondi"
echo "📝 Log: ${LOG_FILE}"
echo "💡 Premi Ctrl+C per fermare"
echo ""

# Funzione per ottenere temperatura CPU
get_cpu_temp() {
    if command -v sensors > /dev/null; then
        sensors | grep -E "(Package|Core|temp1)" | head -1 | awk '{print $2}' | sed 's/+//' | sed 's/°C//'
    else
        echo "N/A"
    fi
}

# Funzione per ottenere utilizzo CPU di Ollama
get_ollama_cpu() {
    ps aux | grep ollama | grep -v grep | awk '{print $3}' | head -1
}

# Funzione per ottenere memoria utilizzata da Ollama
get_ollama_memory() {
    ps aux | grep ollama | grep -v grep | awk '{print $6}' | head -1
}

# Funzione per valutare il rischio
assess_risk() {
    local cpu_usage=$1
    local temp=$2
    local duration=$3
    
    local risk_level="LOW"
    local risk_message="✅ Sistema OK"
    
    # Valutazione CPU
    if (( $(echo "$cpu_usage > 800" | bc -l 2>/dev/null || echo "0") )); then
        risk_level="HIGH"
        risk_message="🚨 CPU usage troppo alto: ${cpu_usage}%"
    elif (( $(echo "$cpu_usage > 500" | bc -l 2>/dev/null || echo "0") )); then
        risk_level="MEDIUM"
        risk_message="⚠️ CPU usage elevato: ${cpu_usage}%"
    fi
    
    # Valutazione temperatura
    if [[ "$temp" != "N/A" ]] && (( $(echo "$temp > 80" | bc -l 2>/dev/null || echo "0") )); then
        risk_level="HIGH"
        risk_message="🔥 Temperatura critica: ${temp}°C"
    elif [[ "$temp" != "N/A" ]] && (( $(echo "$temp > 70" | bc -l 2>/dev/null || echo "0") )); then
        if [[ "$risk_level" == "LOW" ]]; then
            risk_level="MEDIUM"
            risk_message="⚠️ Temperatura elevata: ${temp}°C"
        fi
    fi
    
    # Valutazione durata
    if (( duration > 1800 )); then  # 30 minuti
        if [[ "$risk_level" == "LOW" ]]; then
            risk_level="MEDIUM"
            risk_message="⏰ Esecuzione prolungata: ${duration}s"
        fi
    fi
    
    echo "$risk_level|$risk_message"
}

# Funzione per log
log_message() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $message" | tee -a "$LOG_FILE"
}

# Controlla se Ollama è in esecuzione
check_ollama_running() {
    if ! ps aux | grep ollama | grep -v grep > /dev/null; then
        echo "❌ Ollama non è in esecuzione"
        return 1
    fi
    return 0
}

# Ottieni informazioni del processo Ollama
get_ollama_info() {
    local ollama_process=$(ps aux | grep ollama | grep -v grep | head -1)
    if [[ -n "$ollama_process" ]]; then
        local pid=$(echo "$ollama_process" | awk '{print $2}')
        local cpu=$(echo "$ollama_process" | awk '{print $3}')
        local mem=$(echo "$ollama_process" | awk '{print $6}')
        local time_str=$(echo "$ollama_process" | awk '{print $10}')
        local model=$(echo "$ollama_process" | grep -o '--model [^ ]*' | awk '{print $2}' | sed 's/.*\///' | sed 's/-.*//')
        
        echo "$pid|$cpu|$mem|$time_str|$model"
    else
        echo ""
    fi
}

# Converti tempo in secondi
time_to_seconds() {
    local time_str="$1"
    if [[ "$time_str" =~ ^([0-9]+):([0-9]+)$ ]]; then
        local minutes=${BASH_REMATCH[1]}
        local seconds=${BASH_REMATCH[2]}
        echo $((minutes * 60 + seconds))
    elif [[ "$time_str" =~ ^([0-9]+):([0-9]+):([0-9]+)$ ]]; then
        local hours=${BASH_REMATCH[1]}
        local minutes=${BASH_REMATCH[2]}
        local seconds=${BASH_REMATCH[3]}
        echo $((hours * 3600 + minutes * 60 + seconds))
    else
        echo "0"
    fi
}

# Funzione principale di monitoraggio
monitor_loop() {
    local start_time=$(date +%s)
    local alert_count=0
    
    while true; do
        clear
        echo "🔍 Monitoraggio Hardware - $(date)"
        echo "⏱️  Intervallo: ${INTERVAL}s | 📝 Log: ${LOG_FILE}"
        echo "=" * 60
        echo ""
        
        # Controlla se Ollama è in esecuzione
        if ! check_ollama_running; then
            echo "💤 Ollama non è in esecuzione"
            echo ""
            echo "💡 Per avviare: ollama run phi3"
            echo "💡 Per fermare: pkill ollama"
            sleep $INTERVAL
            continue
        fi
        
        # Ottieni informazioni Ollama
        local ollama_info=$(get_ollama_info)
        if [[ -n "$ollama_info" ]]; then
            IFS='|' read -r pid cpu mem time_str model <<< "$ollama_info"
            local duration=$(time_to_seconds "$time_str")
            
            echo "🤖 Processo Ollama:"
            echo "   PID: $pid"
            echo "   Modello: $model"
            echo "   CPU: ${cpu}%"
            echo "   Memoria: ${mem} KB"
            echo "   Tempo: ${time_str} (${duration}s)"
            echo ""
        fi
        
        # Ottieni temperatura
        local temp=$(get_cpu_temp)
        echo "🌡️  Temperatura Sistema:"
        echo "   CPU: ${temp}°C"
        
        # Mostra tutte le temperature disponibili
        if command -v sensors > /dev/null; then
            echo "   Dettagli:"
            sensors | grep -E "(temp|Composite)" | sed 's/^/     /'
        fi
        echo ""
        
        # Ottieni informazioni sistema
        echo "💻 Risorse Sistema:"
        local total_mem=$(free -h | grep Mem | awk '{print $2}')
        local used_mem=$(free -h | grep Mem | awk '{print $3}')
        local available_mem=$(free -h | grep Mem | awk '{print $7}')
        echo "   Memoria: ${used_mem}/${total_mem} (${available_mem} disponibile)"
        
        local disk_usage=$(df -h / | tail -1 | awk '{print $5}')
        echo "   Disco: ${disk_usage} utilizzato"
        echo ""
        
        # Valuta rischio
        local risk_info=$(assess_risk "$cpu" "$temp" "$duration")
        IFS='|' read -r risk_level risk_message <<< "$risk_info"
        
        echo "⚠️  Valutazione Rischio:"
        case "$risk_level" in
            "HIGH")
                echo "   🚨 LIVELLO ALTO: $risk_message"
                ((alert_count++))
                log_message "ALERT: $risk_message"
                ;;
            "MEDIUM")
                echo "   ⚠️  LIVELLO MEDIO: $risk_message"
                ((alert_count++))
                log_message "WARNING: $risk_message"
                ;;
            "LOW")
                echo "   ✅ LIVELLO BASSO: $risk_message"
                ;;
        esac
        echo ""
        
        # Raccomandazioni
        echo "💡 Raccomandazioni:"
        if [[ "$risk_level" == "HIGH" ]]; then
            echo "   🛑 Ferma immediatamente: sudo kill $pid"
            echo "   🔧 Configura limitazioni per Ollama"
            echo "   🌡️  Controlla ventilazione sistema"
        elif [[ "$risk_level" == "MEDIUM" ]]; then
            echo "   ⏸️  Considera di fermare se continua"
            echo "   🔧 Usa modelli più veloci (phi3)"
            echo "   📊 Monitora temperatura"
        else
            echo "   ✅ Sistema OK, continua monitoraggio"
            echo "   🔧 Considera ottimizzazioni per efficienza"
        fi
        echo ""
        
        # Statistiche
        echo "📊 Statistiche:"
        echo "   Alert totali: $alert_count"
        echo "   Tempo monitoraggio: $(( $(date +%s) - start_time ))s"
        echo ""
        
        echo "🔄 Prossimo aggiornamento in ${INTERVAL}s..."
        sleep $INTERVAL
    done
}

# Gestione interruzione
trap 'echo ""; echo "🛑 Monitoraggio fermato"; exit 0' INT

# Avvia monitoraggio
monitor_loop 