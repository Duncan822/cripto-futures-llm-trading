#!/bin/bash

# Background Agent Cooperativo: Usa cooperazione tra i migliori LLM per generare strategie
# Mantiene tutte le funzioni originali ma migliora la generazione tramite LLM multipli
# Versione alternativa al sistema standard

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

PID_FILE="background_agent_cooperative.pid"
AGENT_NAME="Background Agent Cooperativo"

# Configurazione LLM cooperativi
LLM_STRATEGY_GENERATORS=("cogito:8b" "mistral:7b" "phi3:14b" "llama3.1:8b")
LLM_VALIDATORS=("cogito:8b" "mistral:7b")
LLM_OPTIMIZERS=("cogito:8b" "llama3.1:8b")

# Configurazione hardware
MAX_CPU_USAGE=70          # Massimo utilizzo CPU per operazioni cooperative (%)
MAX_TEMPERATURE=75        # Temperatura massima CPU (°C)
MIN_FREE_MEMORY=2         # Memoria minima libera richiesta (GB)
MAX_PARALLEL_LLMS=4       # Massimo LLM paralleli (adattabile dinamicamente)
HARDWARE_CHECK_INTERVAL=30 # Intervallo controllo hardware (secondi)

show_help() {
    echo -e "${BLUE}🤖 Background Agent Cooperativo - Generazione Strategie Multi-LLM${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo -e "${PURPLE}=== SISTEMA COOPERATIVO ============================${NC}"
    echo -e "  ${GREEN}cooperative-generate${NC} - Genera strategia con cooperazione LLM"
    echo -e "  ${GREEN}llm-contest${NC}        - Contest tra LLM per migliore strategia"
    echo -e "  ${GREEN}consensus-strategy${NC}  - Strategia basata su consenso LLM"
    echo -e "  ${GREEN}validate-cooperative${NC} - Validazione incrociata tra LLM"
    echo ""
    echo -e "${BLUE}=== COMANDI STANDARD ============================${NC}"
    echo -e "  ${GREEN}start${NC}     - Avvia l'agente cooperativo"
    echo -e "  ${RED}stop${NC}      - Ferma l'agente"
    echo -e "  ${YELLOW}restart${NC}   - Riavvia l'agente"
    echo -e "  ${CYAN}status${NC}    - Mostra lo stato dell'agente"
    echo -e "  ${BLUE}logs${NC}      - Mostra i log in tempo reale"
    echo -e "  ${BLUE}config${NC}    - Modifica la configurazione cooperativa"
    echo -e "  ${BLUE}help${NC}      - Mostra questo aiuto"
    echo ""
    echo "Esempi:"
    echo "  $0 cooperative-generate volatility"
    echo "  $0 llm-contest scalping"
    echo "  $0 consensus-strategy momentum"
    echo "  $0 start"
}

# ===== FUNZIONI DI CONTROLLO HARDWARE =====

get_cpu_usage() {
    # Ottiene l'utilizzo CPU totale
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' | sed 's/,//' || echo "0"
}

get_cpu_temperature() {
    # Ottiene la temperatura CPU
    if command -v sensors > /dev/null; then
        sensors | grep -E "(Package|Core|temp1)" | head -1 | awk '{print $2}' | sed 's/+//' | sed 's/°C//' || echo "0"
    else
        echo "0"
    fi
}

get_free_memory_gb() {
    # Ottiene la memoria libera in GB
    free -g | grep "Mem:" | awk '{print $7}' || echo "0"
}

get_system_load() {
    # Ottiene il carico del sistema (load average 1 min)
    uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//' || echo "0"
}

check_hardware_resources() {
    echo -e "${BLUE}🔍 Controllo risorse hardware...${NC}"
    
    local cpu_usage=$(get_cpu_usage)
    local cpu_temp=$(get_cpu_temperature)
    local free_mem=$(get_free_memory_gb)
    local load_avg=$(get_system_load)
    
    echo -e "   💻 CPU: ${cpu_usage}% - 🌡️ Temp: ${cpu_temp}°C"
    echo -e "   💾 RAM libera: ${free_mem}GB - ⚖️ Load: ${load_avg}"
    
    # Verifica limiti di sicurezza
    local hardware_ok=true
    local warnings=()
    
    # Controllo CPU
    if (( $(echo "$cpu_usage > $MAX_CPU_USAGE" | bc -l 2>/dev/null || echo "0") )); then
        hardware_ok=false
        warnings+=("🚨 CPU troppo utilizzata: ${cpu_usage}% > ${MAX_CPU_USAGE}%")
    fi
    
    # Controllo temperatura
    if [[ "$cpu_temp" != "0" ]] && (( $(echo "$cpu_temp > $MAX_TEMPERATURE" | bc -l 2>/dev/null || echo "0") )); then
        hardware_ok=false
        warnings+=("🔥 Temperatura troppo alta: ${cpu_temp}°C > ${MAX_TEMPERATURE}°C")
    fi
    
    # Controllo memoria
    if (( free_mem < MIN_FREE_MEMORY )); then
        hardware_ok=false
        warnings+=("💾 Memoria insufficiente: ${free_mem}GB < ${MIN_FREE_MEMORY}GB")
    fi
    
    # Controllo carico sistema
    if (( $(echo "$load_avg > 8.0" | bc -l 2>/dev/null || echo "0") )); then
        hardware_ok=false
        warnings+=("⚖️ Sistema sovraccarico: load ${load_avg}")
    fi
    
    if [ "$hardware_ok" = true ]; then
        echo -e "${GREEN}✅ Risorse hardware OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Risorse hardware insufficienti:${NC}"
        for warning in "${warnings[@]}"; do
            echo -e "   $warning"
        done
        return 1
    fi
}

calculate_optimal_parallel_llms() {
    local cpu_usage=$(get_cpu_usage)
    local free_mem=$(get_free_memory_gb)
    local load_avg=$(get_system_load)
    
    # Calcolo dinamico del numero ottimale di LLM paralleli
    local optimal_llms=$MAX_PARALLEL_LLMS
    
    # Riduci in base al carico CPU
    if (( $(echo "$cpu_usage > 50" | bc -l 2>/dev/null || echo "0") )); then
        optimal_llms=$((optimal_llms - 1))
    fi
    if (( $(echo "$cpu_usage > 60" | bc -l 2>/dev/null || echo "0") )); then
        optimal_llms=$((optimal_llms - 1))
    fi
    
    # Riduci in base alla memoria
    if (( free_mem < 4 )); then
        optimal_llms=$((optimal_llms - 1))
    fi
    if (( free_mem < 3 )); then
        optimal_llms=$((optimal_llms - 1))
    fi
    
    # Riduci in base al load average
    if (( $(echo "$load_avg > 4.0" | bc -l 2>/dev/null || echo "0") )); then
        optimal_llms=$((optimal_llms - 1))
    fi
    
    # Minimo 1 LLM
    if (( optimal_llms < 1 )); then
        optimal_llms=1
    fi
    
    echo $optimal_llms
}

monitor_hardware_during_execution() {
    local operation_name="$1"
    local max_duration=${2:-1800}  # Default 30 minuti
    
    echo -e "${YELLOW}🔍 Monitoraggio hardware durante: $operation_name${NC}"
    
    local start_time=$(date +%s)
    local warning_count=0
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        # Timeout operazione
        if (( elapsed > max_duration )); then
            echo -e "${RED}⏰ Timeout operazione: ${operation_name} (${elapsed}s)${NC}"
            return 2
        fi
        
        # Controllo risorse
        local cpu_usage=$(get_cpu_usage)
        local cpu_temp=$(get_cpu_temperature)
        local free_mem=$(get_free_memory_gb)
        
        # Controlli critici
        local critical_issue=false
        
        if (( $(echo "$cpu_usage > 90" | bc -l 2>/dev/null || echo "0") )); then
            echo -e "${RED}🚨 CPU critica: ${cpu_usage}%${NC}"
            critical_issue=true
        fi
        
        if [[ "$cpu_temp" != "0" ]] && (( $(echo "$cpu_temp > 85" | bc -l 2>/dev/null || echo "0") )); then
            echo -e "${RED}🔥 Temperatura critica: ${cpu_temp}°C${NC}"
            critical_issue=true
        fi
        
        if (( free_mem < 1 )); then
            echo -e "${RED}💾 Memoria critica: ${free_mem}GB${NC}"
            critical_issue=true
        fi
        
        if [ "$critical_issue" = true ]; then
            ((warning_count++))
            if (( warning_count >= 3 )); then
                echo -e "${RED}🛑 Interruzione operazione per sicurezza sistema${NC}"
                return 1
            fi
        else
            warning_count=0
        fi
        
        sleep $HARDWARE_CHECK_INTERVAL
    done
}

get_hardware_optimized_models() {
    local cpu_usage=$(get_cpu_usage)
    local free_mem=$(get_free_memory_gb)
    
    # Selezione modelli ottimizzata per hardware
    local optimized_models=()
    
    if (( free_mem >= 8 && $(echo "$cpu_usage < 40" | bc -l 2>/dev/null || echo "0") )); then
        # Sistema potente: usa tutti i modelli
        optimized_models=("${LLM_STRATEGY_GENERATORS[@]}")
    elif (( free_mem >= 4 && $(echo "$cpu_usage < 60" | bc -l 2>/dev/null || echo "0") )); then
        # Sistema medio: usa modelli efficienti
        optimized_models=("phi3:14b" "mistral:7b" "cogito:8b")
    else
        # Sistema limitato: usa solo modelli veloci
        optimized_models=("phi3:14b" "mistral:7b")
    fi
    
    echo "${optimized_models[@]}"
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

check_llm_availability() {
    echo -e "${BLUE}🔍 Verifica disponibilità LLM cooperativi...${NC}"
    
    # Verifica Ollama
    if ! pgrep -x "ollama" > /dev/null; then
        echo -e "${RED}❌ Ollama non in esecuzione${NC}"
        return 1
    fi
    
    # Verifica modelli disponibili
    AVAILABLE_MODELS=()
    for model in "${LLM_STRATEGY_GENERATORS[@]}"; do
        if ollama list | grep -q "$model"; then
            AVAILABLE_MODELS+=("$model")
            echo -e "${GREEN}✅ $model disponibile${NC}"
        else
            echo -e "${YELLOW}⚠️ $model non disponibile${NC}"
        fi
    done
    
    if [ ${#AVAILABLE_MODELS[@]} -lt 2 ]; then
        echo -e "${RED}❌ Servono almeno 2 LLM per la cooperazione${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ ${#AVAILABLE_MODELS[@]} LLM disponibili per cooperazione${NC}"
    return 0
}

cooperative_generate_strategy() {
    local strategy_type=${1:-"volatility"}
    echo -e "${PURPLE}🤖 Generazione Cooperativa: $strategy_type${NC}"
    echo ""
    
    if ! check_llm_availability; then
        echo -e "${RED}❌ LLM non disponibili per cooperazione${NC}"
        return 1
    fi
    
    # Crea directory per i risultati cooperativi
    mkdir -p "cooperative_results/$(date +%Y%m%d_%H%M%S)"
    RESULT_DIR="cooperative_results/$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}📁 Directory risultati: $RESULT_DIR${NC}"
    
    # Fase 1: Generazione parallela con LLM multipli
    echo -e "${YELLOW}🔄 Fase 1: Generazione parallela con ${#AVAILABLE_MODELS[@]} LLM...${NC}"
    
    local strategy_files=()
    local pids=()
    
    for i in "${!AVAILABLE_MODELS[@]}"; do
        local model="${AVAILABLE_MODELS[$i]}"
        local output_file="$RESULT_DIR/strategy_${model//[:\/]/_}_$strategy_type.py"
        
        echo -e "   🚀 Avvio generazione con $model..."
        
        # Avvia generazione in parallelo
        python3 -c "
import sys
sys.path.append('.')
from agents.generator import GeneratorAgent

try:
    generator = GeneratorAgent(default_model='$model')
    strategy_name = '${strategy_type^}Strategy${model//[:\/]/_}'
    strategy_code = generator.generate_futures_strategy(
        strategy_type='$strategy_type',
        use_hybrid=True,
        strategy_name=strategy_name
    )
    
    with open('$output_file', 'w') as f:
        f.write(strategy_code)
        
    print(f'✅ Strategia generata con $model: $output_file')
    
except Exception as e:
    print(f'❌ Errore con $model: {e}')
    with open('$output_file.error', 'w') as f:
        f.write(str(e))
" &
        
        pids+=($!)
        strategy_files+=("$output_file")
        sleep 2  # Pausa per evitare sovraccarico
    done
    
    # Aspetta completamento di tutte le generazioni
    echo -e "${YELLOW}⏳ Attesa completamento generazioni...${NC}"
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    # Fase 2: Validazione incrociata
    echo -e "${YELLOW}🔄 Fase 2: Validazione incrociata...${NC}"
    cooperative_validate_strategies "$RESULT_DIR" "${strategy_files[@]}"
    
    # Fase 3: Selezione della migliore strategia
    echo -e "${YELLOW}🔄 Fase 3: Selezione strategia ottimale...${NC}"
    select_best_cooperative_strategy "$RESULT_DIR" "${strategy_files[@]}"
    
    echo -e "${GREEN}✅ Generazione cooperativa completata${NC}"
    echo -e "${BLUE}📊 Risultati in: $RESULT_DIR${NC}"
}

cooperative_validate_strategies() {
    local result_dir="$1"
    shift
    local strategy_files=("$@")
    
    echo -e "${BLUE}🔍 Validazione incrociata delle strategie...${NC}"
    
    local validation_file="$result_dir/validation_results.json"
    echo "{" > "$validation_file"
    echo '  "validations": [' >> "$validation_file"
    
    local first=true
    for strategy_file in "${strategy_files[@]}"; do
        if [ -f "$strategy_file" ]; then
            echo -e "   🔎 Validando $(basename "$strategy_file")..."
            
            if [ "$first" = false ]; then
                echo "    ," >> "$validation_file"
            fi
            first=false
            
            # Validazione con più LLM
            local validation_score=0
            local validations_count=0
            
            for validator in "${LLM_VALIDATORS[@]}"; do
                if ollama list | grep -q "$validator"; then
                    echo -e "     🤖 Validazione con $validator..."
                    
                    local score=$(python3 -c "
import sys
sys.path.append('.')
from agents.strategy_converter import StrategyConverter

try:
    converter = StrategyConverter()
    with open('$strategy_file', 'r') as f:
        code = f.read()
    
    # Validazione semplificata
    if 'class' in code and 'IStrategy' in code and 'populate_' in code:
        print('8')  # Punteggio alto per codice valido
    else:
        print('3')  # Punteggio basso
except:
    print('0')
")
                    validation_score=$((validation_score + score))
                    validations_count=$((validations_count + 1))
                fi
            done
            
            if [ $validations_count -gt 0 ]; then
                local avg_score=$((validation_score / validations_count))
                echo "    {" >> "$validation_file"
                echo "      \"file\": \"$(basename "$strategy_file")\"," >> "$validation_file"
                echo "      \"avg_score\": $avg_score," >> "$validation_file"
                echo "      \"validations_count\": $validations_count" >> "$validation_file"
                echo "    }" >> "$validation_file"
            fi
        fi
    done
    
    echo '  ]' >> "$validation_file"
    echo '}' >> "$validation_file"
    
    echo -e "${GREEN}✅ Validazione incrociata completata${NC}"
}

select_best_cooperative_strategy() {
    local result_dir="$1"
    shift
    local strategy_files=("$@")
    
    echo -e "${BLUE}🏆 Selezione della strategia migliore...${NC}"
    
    local best_file=""
    local best_score=0
    
    # Analizza i risultati di validazione
    if [ -f "$result_dir/validation_results.json" ]; then
        for strategy_file in "${strategy_files[@]}"; do
            if [ -f "$strategy_file" ]; then
                local filename=$(basename "$strategy_file")
                local score=$(python3 -c "
import json
try:
    with open('$result_dir/validation_results.json', 'r') as f:
        data = json.load(f)
    
    for validation in data['validations']:
        if validation['file'] == '$filename':
            print(validation['avg_score'])
            break
    else:
        print('0')
except:
    print('0')
")
                
                echo -e "   📊 $filename: punteggio $score"
                
                if [ "$score" -gt "$best_score" ]; then
                    best_score="$score"
                    best_file="$strategy_file"
                fi
            fi
        done
    fi
    
    if [ -n "$best_file" ] && [ -f "$best_file" ]; then
        echo -e "${GREEN}🏆 Strategia migliore: $(basename "$best_file") (punteggio: $best_score)${NC}"
        
        # Copia la strategia migliore nella directory delle strategie
        local final_name="CooperativeStrategy_$(date +%Y%m%d_%H%M%S).py"
        cp "$best_file" "user_data/strategies/$final_name"
        
        echo -e "${GREEN}✅ Strategia cooperativa salvata come: $final_name${NC}"
        echo "$final_name" > "$result_dir/best_strategy.txt"
    else
        echo -e "${YELLOW}⚠️ Nessuna strategia valida trovata${NC}"
    fi
}

llm_contest_strategy() {
    local strategy_type=${1:-"scalping"}
    echo -e "${PURPLE}🏁 Contest LLM per strategia $strategy_type${NC}"
    echo ""
    
    if ! check_llm_availability; then
        echo -e "${RED}❌ LLM non disponibili per contest${NC}"
        return 1
    fi
    
    # Crea directory per il contest
    mkdir -p "llm_contest/$(date +%Y%m%d_%H%M%S)"
    CONTEST_DIR="llm_contest/$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}🏁 Contest in: $CONTEST_DIR${NC}"
    
    # Genera prompt di sfida
    local challenge_prompt="Crea la migliore strategia Freqtrade per $strategy_type trading su futures crypto volatili. Devi battere gli altri LLM!"
    
    # Avvia contest tra LLM
    echo -e "${YELLOW}🚀 Avvio contest tra ${#AVAILABLE_MODELS[@]} LLM...${NC}"
    
    local contest_results=()
    for model in "${AVAILABLE_MODELS[@]}"; do
        echo -e "   🤖 $model sta partecipando al contest..."
        
        local strategy_file="$CONTEST_DIR/contest_${model//[:\/]/_}_$strategy_type.py"
        
        python3 -c "
import sys
sys.path.append('.')
from agents.generator import GeneratorAgent

try:
    generator = GeneratorAgent(default_model='$model')
    strategy_name = 'Contest${strategy_type^}${model//[:\/]/_}'
    strategy_code = generator.generate_futures_strategy(
        strategy_type='$strategy_type',
        use_hybrid=True,
        strategy_name=strategy_name
    )
    
    with open('$strategy_file', 'w') as f:
        f.write(strategy_code)
        
    print(f'🏁 $model ha completato il contest')
    
except Exception as e:
    print(f'❌ $model ha fallito: {e}')
" &
    done
    
    wait  # Aspetta tutti i contest
    
    echo -e "${GREEN}🏆 Contest completato! Analisi risultati...${NC}"
    
    # Valuta i risultati del contest
    evaluate_contest_results "$CONTEST_DIR"
}

evaluate_contest_results() {
    local contest_dir="$1"
    echo -e "${BLUE}📊 Valutazione risultati contest...${NC}"
    
    # Criterli di valutazione
    local criteria=("complessità_codice" "uso_indicatori" "gestione_rischio" "originalità")
    
    echo -e "${YELLOW}🔍 Criteri di valutazione: ${criteria[*]}${NC}"
    
    # Crea report contest
    local report_file="$contest_dir/contest_report.md"
    echo "# Contest LLM - Risultati" > "$report_file"
    echo "" >> "$report_file"
    echo "Data: $(date)" >> "$report_file"
    echo "" >> "$report_file"
    
    # Analizza ogni strategia del contest
    for strategy_file in "$contest_dir"/contest_*.py; do
        if [ -f "$strategy_file" ]; then
            local model_name=$(basename "$strategy_file" | sed 's/contest_\(.*\)_.*\.py/\1/')
            echo -e "   📊 Analizzando strategia di $model_name..."
            
            # Conteggi per la valutazione
            local indicators_count=$(grep -c "ta\." "$strategy_file" 2>/dev/null || echo "0")
            local conditions_count=$(grep -c "dataframe.loc" "$strategy_file" 2>/dev/null || echo "0")
            local lines_count=$(wc -l < "$strategy_file" 2>/dev/null || echo "0")
            
            echo "## $model_name" >> "$report_file"
            echo "- Indicatori tecnici: $indicators_count" >> "$report_file"
            echo "- Condizioni di trading: $conditions_count" >> "$report_file"
            echo "- Righe di codice: $lines_count" >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
    
    echo -e "${GREEN}✅ Report contest salvato in: $report_file${NC}"
}

consensus_strategy() {
    local strategy_type=${1:-"momentum"}
    echo -e "${PURPLE}🤝 Strategia basata su consenso LLM: $strategy_type${NC}"
    echo ""
    
    if ! check_llm_availability; then
        echo -e "${RED}❌ LLM non disponibili per consenso${NC}"
        return 1
    fi
    
    # Crea directory per consenso
    mkdir -p "consensus_strategies/$(date +%Y%m%d_%H%M%S)"
    CONSENSUS_DIR="consensus_strategies/$(date +%Y%m%d_%H%M%S)"
    
    echo -e "${BLUE}🤝 Consenso in: $CONSENSUS_DIR${NC}"
    
    # Fase 1: Raccolta idee da tutti i LLM
    echo -e "${YELLOW}🧠 Fase 1: Raccolta idee strategiche...${NC}"
    collect_llm_ideas "$CONSENSUS_DIR" "$strategy_type"
    
    # Fase 2: Sintesi delle idee
    echo -e "${YELLOW}🔄 Fase 2: Sintesi consensuale...${NC}"
    synthesize_consensus "$CONSENSUS_DIR" "$strategy_type"
    
    # Fase 3: Implementazione finale
    echo -e "${YELLOW}⚙️ Fase 3: Implementazione strategia consensuale...${NC}"
    implement_consensus_strategy "$CONSENSUS_DIR" "$strategy_type"
    
    echo -e "${GREEN}✅ Strategia consensuale completata${NC}"
}

collect_llm_ideas() {
    local consensus_dir="$1"
    local strategy_type="$2"
    
    echo -e "${BLUE}💡 Raccolta idee da ${#AVAILABLE_MODELS[@]} LLM...${NC}"
    
    for model in "${AVAILABLE_MODELS[@]}"; do
        echo -e "   🤖 Raccogliendo idee da $model..."
        
        local ideas_file="$consensus_dir/ideas_${model//[:\/]/_}.txt"
        
        python3 -c "
import sys
sys.path.append('.')
from llm_utils import query_ollama_fast

prompt = '''Descrivi 3 idee chiave per una strategia di trading $strategy_type su futures crypto:
1. Indicatori tecnici da usare
2. Condizioni di entrata/uscita 
3. Gestione del rischio

Rispondi in modo conciso e pratico.'''

try:
    response = query_ollama_fast(prompt, '$model', timeout=300)
    with open('$ideas_file', 'w') as f:
        f.write(f'=== Idee da $model ===\n')
        f.write(response)
        f.write('\n\n')
    print(f'💡 Idee raccolte da $model')
except Exception as e:
    print(f'❌ Errore con $model: {e}')
"
    done
    
    echo -e "${GREEN}✅ Idee raccolte da tutti i LLM${NC}"
}

synthesize_consensus() {
    local consensus_dir="$1"
    local strategy_type="$2"
    
    echo -e "${BLUE}🔗 Sintesi delle idee...${NC}"
    
    # Combina tutte le idee
    local all_ideas_file="$consensus_dir/all_ideas.txt"
    cat "$consensus_dir"/ideas_*.txt > "$all_ideas_file" 2>/dev/null || true
    
    # Crea sintesi consensuale
    local synthesis_file="$consensus_dir/consensus_synthesis.txt"
    
    if [ -f "$all_ideas_file" ] && [ -s "$all_ideas_file" ]; then
        echo -e "   🧠 Creando sintesi consensuale..."
        
        # Usa il LLM più potente per la sintesi
        local synthesis_model="${AVAILABLE_MODELS[0]}"
        
        python3 -c "
import sys
sys.path.append('.')
from llm_utils import query_ollama

with open('$all_ideas_file', 'r') as f:
    all_ideas = f.read()

synthesis_prompt = f'''Analizza queste idee da diversi LLM per una strategia $strategy_type:

{all_ideas}

Crea una sintesi consensuale che combini le migliori idee:
1. Indicatori tecnici più votati
2. Condizioni di trading condivise
3. Approcci di gestione rischio comuni
4. Parametri ottimali suggeriti

Rispondi con una strategia unificata e coerente.'''

try:
    synthesis = query_ollama(synthesis_prompt, '$synthesis_model', timeout=600)
    with open('$synthesis_file', 'w') as f:
        f.write(synthesis)
    print('🔗 Sintesi consensuale creata')
except Exception as e:
    print(f'❌ Errore nella sintesi: {e}')
"
    else
        echo -e "${YELLOW}⚠️ Nessuna idea raccolta per la sintesi${NC}"
    fi
}

implement_consensus_strategy() {
    local consensus_dir="$1"
    local strategy_type="$2"
    
    echo -e "${BLUE}⚙️ Implementazione strategia consensuale...${NC}"
    
    local synthesis_file="$consensus_dir/consensus_synthesis.txt"
    local strategy_file="$consensus_dir/consensus_strategy.py"
    
    if [ -f "$synthesis_file" ]; then
        # Implementa la strategia basata sulla sintesi
        python3 -c "
import sys
sys.path.append('.')
from agents.strategy_converter import StrategyConverter

try:
    converter = StrategyConverter()
    
    with open('$synthesis_file', 'r') as f:
        synthesis = f.read()
    
    strategy_name = 'Consensus${strategy_type^}Strategy'
    strategy_code = converter.convert_text_to_strategy(synthesis, strategy_name)
    
    with open('$strategy_file', 'w') as f:
        f.write(strategy_code)
    
    print('⚙️ Strategia consensuale implementata')
    
except Exception as e:
    print(f'❌ Errore implementazione: {e}')
"
        
        # Copia nella directory delle strategie se valida
        if [ -f "$strategy_file" ]; then
            local final_name="ConsensusStrategy_$(date +%Y%m%d_%H%M%S).py"
            cp "$strategy_file" "user_data/strategies/$final_name"
            echo -e "${GREEN}✅ Strategia consensuale salvata: $final_name${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Sintesi non disponibile per implementazione${NC}"
    fi
}

start_agent() {
    echo -e "${BLUE}🚀 Avvio $AGENT_NAME...${NC}"
    
    if check_pid; then
        echo -e "${YELLOW}⚠️ $AGENT_NAME è già in esecuzione (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    if ! check_llm_availability; then
        echo -e "${RED}❌ LLM non disponibili, impossibile avviare agente cooperativo${NC}"
        return 1
    fi
    
    # Crea configurazione cooperativa se non esiste
    create_cooperative_config
    
    # Avvia l'agente cooperativo
    nohup python3 -c "
import sys
sys.path.append('.')
from background_agent import BackgroundAgent

# Usa configurazione cooperativa
agent = BackgroundAgent('background_config_cooperative.json')
print('🤖 Background Agent Cooperativo avviato')
agent.start()

import time
try:
    while agent.is_running:
        time.sleep(1)
except KeyboardInterrupt:
    print('🛑 Arresto agente cooperativo')
    agent.stop()
" > "logs/background_agent_cooperative_$(date +%Y%m%d_%H%M%S).log" 2>&1 &
    
    # Salva il PID
    echo $! > "$PID_FILE"
    
    sleep 2
    if check_pid; then
        echo -e "${GREEN}✅ $AGENT_NAME avviato con successo (PID: $(cat $PID_FILE))${NC}"
        echo -e "${BLUE}📋 Log: logs/background_agent_cooperative_*.log${NC}"
    else
        echo -e "${RED}❌ Errore nell'avvio di $AGENT_NAME${NC}"
        return 1
    fi
}

create_cooperative_config() {
    if [ ! -f "background_config_cooperative.json" ]; then
        echo -e "${YELLOW}⚙️ Creazione configurazione cooperativa...${NC}"
        
        cat > "background_config_cooperative.json" << 'EOF'
{
  "auto_validation": true,
  "auto_backtest": true,
  "max_strategies": 75,
  "generation_interval": 2700,
  "backtest_interval": 5400,
  "cleanup_old_strategies": true,
  "strategy_types": ["volatility", "scalping", "breakout", "momentum", "adaptive"],
  "models": ["cogito:8b", "mistral:7b", "phi3:14b", "llama3.1:8b"],
  "min_backtest_score": 0.15,
  "max_concurrent_tasks": 4,
  "cooperative_mode": {
    "enable_cooperation": true,
    "cooperative_generation_interval": 10800,
    "llm_consensus_threshold": 0.7,
    "use_llm_voting": true,
    "parallel_generation_count": 3,
    "enable_contest_mode": true,
    "contest_interval": 21600
  },
  "model_selection": {
    "generation": ["cogito:8b", "mistral:7b", "phi3:14b"],
    "validation": ["cogito:8b", "mistral:7b"],
    "optimization": "cogito:8b"
  }
}
EOF
        echo -e "${GREEN}✅ Configurazione cooperativa creata${NC}"
    fi
}

stop_agent() {
    echo -e "${YELLOW}🛑 Arresto $AGENT_NAME...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            echo -e "${GREEN}✅ Segnale di arresto inviato a PID $PID${NC}"
            
            # Aspetta l'arresto
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ $AGENT_NAME arrestato${NC}"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Forza l'arresto se necessario
            echo -e "${YELLOW}⚠️ Forzatura arresto...${NC}"
            kill -9 "$PID" 2>/dev/null || true
            rm -f "$PID_FILE"
            echo -e "${GREEN}✅ $AGENT_NAME arrestato forzatamente${NC}"
        else
            echo -e "${YELLOW}⚠️ $AGENT_NAME non era in esecuzione${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠️ File PID non trovato, $AGENT_NAME non era in esecuzione${NC}"
    fi
}

show_status() {
    echo -e "${BLUE}📊 Stato $AGENT_NAME${NC}"
    echo ""
    
    if check_pid; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✅ $AGENT_NAME è in esecuzione${NC}"
        echo -e "   PID: $PID"
        echo -e "   Uptime: $(ps -o etime= -p $PID)"
        echo -e "   Memoria: $(ps -o rss= -p $PID | awk '{print $1/1024 " MB"}')"
    else
        echo -e "${RED}❌ $AGENT_NAME non è in esecuzione${NC}"
    fi
    
    echo ""
    echo -e "${PURPLE}🤖 LLM Cooperativi:${NC}"
    check_llm_availability
    
    echo ""
    echo -e "${BLUE}📁 Risultati Cooperativi:${NC}"
    if [ -d "cooperative_results" ]; then
        local coop_count=$(find cooperative_results -name "*.py" | wc -l)
        echo -e "   📊 Strategie cooperative generate: $coop_count"
    fi
    
    if [ -d "llm_contest" ]; then
        local contest_count=$(find llm_contest -name "contest_*.py" | wc -l)
        echo -e "   🏁 Contest LLM completati: $contest_count"
    fi
    
    if [ -d "consensus_strategies" ]; then
        local consensus_count=$(find consensus_strategies -name "consensus_*.py" | wc -l)
        echo -e "   🤝 Strategie consensuali: $consensus_count"
    fi
}

show_logs() {
    echo -e "${BLUE}📋 Log $AGENT_NAME${NC}"
    echo ""
    
    # Trova il file di log più recente
    LATEST_LOG=$(ls -t logs/background_agent_cooperative_*.log 2>/dev/null | head -1)
    
    if [ -n "$LATEST_LOG" ]; then
        echo -e "${GREEN}📄 File di log: $LATEST_LOG${NC}"
        echo -e "${YELLOW}💡 Premi Ctrl+C per uscire${NC}"
        echo ""
        tail -f "$LATEST_LOG"
    else
        echo -e "${YELLOW}⚠️ Nessun file di log trovato${NC}"
        echo "L'agente cooperativo potrebbe non essere mai stato avviato"
    fi
}

# Comando principale
case "${1:-help}" in
    "start")
        start_agent
        ;;
    "stop")
        stop_agent
        ;;
    "restart")
        stop_agent
        sleep 2
        start_agent
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "config")
        if command -v nano > /dev/null; then
            nano background_config_cooperative.json
        else
            echo -e "${YELLOW}📄 Configurazione cooperativa:${NC}"
            cat background_config_cooperative.json 2>/dev/null || echo "File non trovato"
        fi
        ;;
    "cooperative-generate")
        cooperative_generate_strategy "$2"
        ;;
    "llm-contest")
        llm_contest_strategy "$2"
        ;;
    "consensus-strategy")
        consensus_strategy "$2"
        ;;
    "validate-cooperative")
        echo -e "${BLUE}🔍 Validazione cooperativa...${NC}"
        check_llm_availability
        ;;
    "help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando non riconosciuto: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac