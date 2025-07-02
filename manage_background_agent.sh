#!/bin/bash

# Script per gestire il Background Agent
# Comandi: start, stop, status, logs, restart, config, sessions, stop-others, stop-all, logs-all

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

PID_FILE="background_agent.pid"
AGENT_NAME="Background Agent"

show_help() {
    echo -e "${BLUE}🔧 Gestione Background Agent${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandi disponibili:"
    echo -e "  ${GREEN}start${NC}     - Avvia l'agente"
    echo -e "  ${RED}stop${NC}      - Ferma l'agente"
    echo -e "  ${YELLOW}restart${NC}   - Riavvia l'agente"
    echo -e "  ${CYAN}status${NC}    - Mostra lo stato dell'agente"
    echo -e "  ${BLUE}logs${NC}      - Mostra i log in tempo reale"
    echo -e "  ${BLUE}config${NC}    - Modifica la configurazione"
    echo -e "  ${BLUE}backtest${NC}  - Monitora backtest attivi"
    echo -e "  ${BLUE}backtest-logs${NC} - Log backtest in tempo reale"
    echo -e "  ${BLUE}optimization${NC} - Monitora ottimizzazioni"
    echo -e "  ${BLUE}dry-run${NC}      - Monitora dry run"
    echo -e "  ${BLUE}live-strategies${NC} - Gestisci strategie live"
    echo -e "  ${BLUE}cleanup-analysis${NC} - Analizza pulizia strategie"
    echo ""
    echo -e "${PURPLE}Gestione Sessioni Multiple:${NC}"
    echo -e "  ${PURPLE}sessions${NC}   - Verifica sessioni multiple"
    echo -e "  ${PURPLE}stop-others${NC} - Ferma istanze non memorizzate"
    echo -e "  ${PURPLE}stop-all${NC}   - Ferma tutte le istanze"
    echo -e "  ${PURPLE}logs-all${NC}   - Mostra log di tutte le istanze"
    echo ""
    echo -e "  ${BLUE}help${NC}      - Mostra questo aiuto"
    echo ""
    echo "Esempi:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 sessions"
    echo "  $0 logs"
    echo "  $0 backtest"
    echo "  $0 cleanup-analysis"
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

start_agent() {
    echo -e "${BLUE}🚀 Avvio $AGENT_NAME...${NC}"
    
    if check_pid; then
        echo -e "${YELLOW}⚠️ $AGENT_NAME è già in esecuzione (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    # Usa lo script di avvio
    ./start_background_agent.sh
    
    # Aspetta un momento e controlla se è partito
    sleep 2
    if check_pid; then
        echo -e "${GREEN}✅ $AGENT_NAME avviato con successo (PID: $(cat $PID_FILE))${NC}"
    else
        echo -e "${RED}❌ Errore nell'avvio di $AGENT_NAME${NC}"
        return 1
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

restart_agent() {
    echo -e "${BLUE}🔄 Riavvio $AGENT_NAME...${NC}"
    stop_agent
    sleep 2
    start_agent
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
    echo -e "${BLUE}📁 File di sistema:${NC}"
    if [ -f "background_config.json" ]; then
        echo -e "   ✅ Configurazione: background_config.json"
    else
        echo -e "   ❌ Configurazione: mancante"
    fi
    
    if [ -f "strategies_metadata.json" ]; then
        echo -e "   ✅ Metadati strategie: strategies_metadata.json"
        # Conta le strategie
        STRATEGY_COUNT=$(python3 -c "import json; data=json.load(open('strategies_metadata.json')); print(len(data))" 2>/dev/null || echo "0")
        echo -e "   📊 Strategie totali: $STRATEGY_COUNT"
    else
        echo -e "   ❌ Metadati strategie: mancante"
    fi
    
    # Conta i file di log
    if [ -d "logs" ]; then
        LOG_COUNT=$(ls logs/background_agent_*.log 2>/dev/null | wc -l)
        echo -e "   📝 File di log: $LOG_COUNT"
    fi
    
    # Informazioni sui backtest
    echo ""
    echo -e "${BLUE}📊 Stato Backtest:${NC}"
    if [ -d "logs/backtests" ]; then
        ACTIVE_BACKTESTS=$(find logs/backtests -name "*.log" -mmin -10 2>/dev/null | wc -l)
        TOTAL_BACKTESTS=$(ls logs/backtests/*.log 2>/dev/null | wc -l)
        echo -e "   🔄 Backtest attivi: $ACTIVE_BACKTESTS"
        echo -e "   📝 Log backtest totali: $TOTAL_BACKTESTS"
    else
        echo -e "   ❌ Directory log backtest: mancante"
    fi
    
    if [ -d "backtest_results" ]; then
        COMPLETED_BACKTESTS=$(ls backtest_results/*.json 2>/dev/null | wc -l)
        echo -e "   ✅ Backtest completati: $COMPLETED_BACKTESTS"
    else
        echo -e "   ❌ Directory risultati: mancante"
    fi
    
    echo ""
    echo -e "${BLUE}🔧 Comandi utili:${NC}"
    echo -e "   $0 logs         - Visualizza log in tempo reale"
    echo -e "   $0 backtest     - Monitora backtest attivi"
    echo -e "   $0 backtest-logs - Log backtest in tempo reale"
    echo -e "   $0 live-strategies - Gestisci strategie live"
    echo -e "   $0 config       - Modifica configurazione"
    echo -e "   $0 restart      - Riavvia l'agente"
}

show_logs() {
    echo -e "${BLUE}📋 Log $AGENT_NAME${NC}"
    echo ""
    
    # Trova il file di log più recente
    LATEST_LOG=$(ls -t logs/background_agent_*.log 2>/dev/null | head -1)
    
    if [ -n "$LATEST_LOG" ]; then
        echo -e "${GREEN}📄 File di log: $LATEST_LOG${NC}"
        echo -e "${YELLOW}💡 Premi Ctrl+C per uscire${NC}"
        echo ""
        tail -f "$LATEST_LOG"
    else
        echo -e "${YELLOW}⚠️ Nessun file di log trovato${NC}"
        echo "L'agente potrebbe non essere mai stato avviato"
    fi
}

edit_config() {
    echo -e "${BLUE}⚙️ Modifica configurazione $AGENT_NAME${NC}"
    echo ""
    
    if [ -f "background_config.json" ]; then
        echo -e "${GREEN}📄 Apertura configurazione...${NC}"
        
        # Controlla se è disponibile un editor
        if command -v nano > /dev/null; then
            nano background_config.json
        elif command -v vim > /dev/null; then
            vim background_config.json
        elif command -v vi > /dev/null; then
            vi background_config.json
        else
            echo -e "${YELLOW}⚠️ Nessun editor trovato, mostro il contenuto:${NC}"
            cat background_config.json
            echo ""
            echo -e "${YELLOW}💡 Modifica manualmente il file background_config.json${NC}"
        fi
        
        echo -e "${GREEN}✅ Configurazione salvata${NC}"
        echo -e "${YELLOW}💡 Riavvia l'agente per applicare le modifiche: $0 restart${NC}"
    else
        echo -e "${RED}❌ File di configurazione non trovato${NC}"
        echo "Avvia prima l'agente per creare la configurazione di default"
    fi
}

show_backtest_status() {
    echo -e "${BLUE}📊 Monitoraggio Backtest Attivi${NC}"
    echo ""
    
    if ! check_pid; then
        echo -e "${RED}❌ Background Agent non è in esecuzione${NC}"
        echo "Avvia prima l'agente con: $0 start"
        return 1
    fi
    
    # Controlla se ci sono log di backtest
    if [ -d "logs/backtests" ]; then
        ACTIVE_LOGS=$(find logs/backtests -name "*.log" -mmin -10 2>/dev/null | wc -l)
        echo -e "🔄 Backtest attivi (ultimi 10 min): $ACTIVE_LOGS"
        
        if [ $ACTIVE_LOGS -gt 0 ]; then
            echo ""
            echo -e "${GREEN}📋 Backtest recenti:${NC}"
            find logs/backtests -name "*.log" -mmin -10 2>/dev/null | head -5 | while read log; do
                LOG_NAME=$(basename "$log" .log)
                LOG_TIME=$(stat -c %y "$log" | cut -d' ' -f2 | cut -d'.' -f1)
                echo -e "   📄 $LOG_NAME - $LOG_TIME"
            done
        fi
    else
        echo -e "${YELLOW}⚠️ Nessun log di backtest trovato${NC}"
    fi
    
    # Controlla risultati completati
    if [ -d "backtest_results" ]; then
        COMPLETED_RESULTS=$(ls backtest_results/*.json 2>/dev/null | wc -l)
        echo -e "✅ Backtest completati: $COMPLETED_RESULTS"
    fi
    
    echo ""
    echo -e "${BLUE}🔧 Comandi utili:${NC}"
    echo -e "   $0 backtest-logs  - Visualizza log backtest in tempo reale"
    echo -e "   $0 status         - Stato completo dell'agente"
}

show_backtest_logs() {
    echo -e "${BLUE}📋 Log Backtest in Tempo Reale${NC}"
    echo ""
    
    if ! check_pid; then
        echo -e "${RED}❌ Background Agent non è in esecuzione${NC}"
        echo "Avvia prima l'agente con: $0 start"
        return 1
    fi
    
    # Trova il file di log di backtest più recente
    LATEST_BACKTEST_LOG=$(find logs/backtests -name "*.log" 2>/dev/null | xargs ls -t 2>/dev/null | head -1)
    
    if [ -n "$LATEST_BACKTEST_LOG" ]; then
        echo -e "${GREEN}📄 File di log: $LATEST_BACKTEST_LOG${NC}"
        echo -e "${YELLOW}💡 Premi Ctrl+C per uscire${NC}"
        echo ""
        tail -f "$LATEST_BACKTEST_LOG"
    else
        echo -e "${YELLOW}⚠️ Nessun log di backtest trovato${NC}"
        echo "I backtest potrebbero non essere mai stati avviati"
        
        # Mostra tutti i log disponibili
        if [ -d "logs/backtests" ]; then
            echo ""
            echo -e "${BLUE}📁 Log disponibili:${NC}"
            ls -la logs/backtests/ 2>/dev/null || echo "   Nessun file trovato"
        fi
    fi
}

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

check_sessions() {
    echo -e "${BLUE}🔍 Verifica Sessioni Multiple Background Agent${NC}"
    echo ""
    
    # Controlla se esiste il file PID
    if [ -f "$PID_FILE" ]; then
        STORED_PID=$(cat "$PID_FILE")
        echo -e "${YELLOW}📄 File PID trovato: $STORED_PID${NC}"
        
        # Verifica se il PID memorizzato è ancora attivo
        if ps -p "$STORED_PID" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ PID memorizzato è attivo${NC}"
        else
            echo -e "${RED}❌ PID memorizzato non è più attivo${NC}"
            echo -e "${YELLOW}💡 Rimuovendo file PID obsoleto...${NC}"
            rm -f "$PID_FILE"
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
        echo -e "   Per avviarne uno: $0 start"
        return 0
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
    OPTIMIZATION_COUNT=$(ps aux | grep "optimizer_agent\|optimize_strategy" | grep -v grep | wc -l)
    echo -e "   🔧 Ottimizzazione strategie: $OPTIMIZATION_COUNT"
    
    echo ""
    echo -e "${BLUE}📊 Riepilogo Finale:${NC}"
    echo -e "   🔄 Processi attivi: $(count_active_processes)"
    echo -e "   📊 Backtest attivi: $BACKTEST_COUNT"
    echo -e "   🎯 Generazione strategie: $STRATEGY_GEN_COUNT"
    echo -e "   ✅ Validazione strategie: $VALIDATION_COUNT"
    echo -e "   🔧 Ottimizzazione strategie: $OPTIMIZATION_COUNT"
}

stop_others() {
    echo -e "${YELLOW}🛑 Fermando istanze non memorizzate...${NC}"
    
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${RED}❌ Nessun file PID trovato${NC}"
        return 1
    fi
    
    STORED_PID=$(cat "$PID_FILE")
    STOPPED_COUNT=0
    
    while IFS= read -r pid; do
        if [ -n "$pid" ] && [ "$pid" != "$STORED_PID" ]; then
            echo -e "   Fermando PID: $pid"
            if kill "$pid" 2>/dev/null; then
                echo -e "   ✅ PID $pid fermato"
                STOPPED_COUNT=$((STOPPED_COUNT + 1))
            else
                echo -e "   ❌ Errore nel fermare PID: $pid"
            fi
        fi
    done < <(get_active_pids)
    
    if [ $STOPPED_COUNT -eq 0 ]; then
        echo -e "${GREEN}✅ Nessuna istanza aggiuntiva da fermare${NC}"
    else
        echo -e "${GREEN}✅ $STOPPED_COUNT istanze fermate${NC}"
    fi
}

stop_all() {
    echo -e "${YELLOW}🛑 Fermando tutte le istanze...${NC}"
    
    STOPPED_COUNT=0
    
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            echo -e "   Fermando PID: $pid"
            if kill "$pid" 2>/dev/null; then
                echo -e "   ✅ PID $pid fermato"
                STOPPED_COUNT=$((STOPPED_COUNT + 1))
            else
                echo -e "   ❌ Errore nel fermare PID: $pid"
            fi
        fi
    done < <(get_active_pids)
    
    # Rimuovi il file PID
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
        echo -e "   📄 File PID rimosso"
    fi
    
    if [ $STOPPED_COUNT -eq 0 ]; then
        echo -e "${GREEN}✅ Nessuna istanza da fermare${NC}"
    else
        echo -e "${GREEN}✅ $STOPPED_COUNT istanze fermate${NC}"
    fi
}

show_all_logs() {
    echo -e "${BLUE}📝 Log di Tutte le Istanze${NC}"
    echo ""
    
    # Trova tutti i log disponibili
    if [ -d "logs" ]; then
        LOG_FILES=$(ls -t logs/background_agent_*.log 2>/dev/null)
        
        if [ -n "$LOG_FILES" ]; then
            echo -e "${GREEN}📁 Log disponibili:${NC}"
            echo ""
            
            for log in $LOG_FILES; do
                if [ -f "$log" ]; then
                    LOG_NAME=$(basename "$log")
                    LOG_SIZE=$(du -h "$log" | cut -f1)
                    LOG_TIME=$(stat -c %y "$log" | cut -d' ' -f2 | cut -d'.' -f1)
                    
                    echo -e "${YELLOW}📄 $LOG_NAME${NC}"
                    echo -e "   📏 Dimensione: $LOG_SIZE"
                    echo -e "   🕐 Ultimo aggiornamento: $LOG_TIME"
                    echo -e "   📋 Ultime 3 righe:"
                    tail -3 "$log" | sed 's/^/      /'
                    echo ""
                fi
            done
        else
            echo -e "${YELLOW}⚠️ Nessun log trovato${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Directory logs non trovata${NC}"
    fi
}

show_cleanup_analysis() {
    echo -e "${BLUE}🧹 Analisi Pulizia Strategie${NC}"
    echo ""
    
    if [ -f "analyze_cleanup.py" ]; then
        echo -e "${GREEN}📊 Esecuzione analisi...${NC}"
        echo ""
        python analyze_cleanup.py
    else
        echo -e "${RED}❌ Script di analisi non trovato${NC}"
        echo "Esegui: python analyze_cleanup.py"
    fi
}

show_optimization_status() {
    echo -e "${BLUE}🔧 Stato Ottimizzazione Strategie${NC}"
    echo ""
    
    # Controlla se l'ottimizzazione è abilitata nella configurazione
    if [ -f "background_config.json" ]; then
        OPTIMIZATION_ENABLED=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('optimization', {}).get('enable_hyperopt', False))" 2>/dev/null || echo "False")
        
        if [ "$OPTIMIZATION_ENABLED" = "True" ]; then
            echo -e "${GREEN}✅ Ottimizzazione automatica ABILITATA${NC}"
        else
            echo -e "${RED}❌ Ottimizzazione automatica DISABILITATA${NC}"
        fi
        
        # Mostra configurazione ottimizzazione
        OPTIMIZATION_INTERVAL=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('optimization', {}).get('optimization_interval', 0))" 2>/dev/null || echo "0")
        if [ "$OPTIMIZATION_INTERVAL" -gt 0 ]; then
            HOURS=$((OPTIMIZATION_INTERVAL / 3600))
            echo -e "   ⏰ Intervallo ottimizzazione: $HOURS ore"
        fi
    else
        echo -e "${RED}❌ File di configurazione non trovato${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Strategie Ottimizzate:${NC}"
    
    # Conta strategie ottimizzate
    if [ -f "strategies_metadata.json" ]; then
        OPTIMIZED_COUNT=$(python3 -c "import json; data=json.load(open('strategies_metadata.json')); print(sum(1 for s in data.values() if s.get('validation_status') == 'optimized'))" 2>/dev/null || echo "0")
        echo -e "   🔧 Strategie ottimizzate: $OPTIMIZED_COUNT"
        
        # Mostra strategie che necessitano ottimizzazione
        LOW_SCORE_COUNT=$(python3 -c "import json; data=json.load(open('strategies_metadata.json')); min_score=0.1; print(sum(1 for s in data.values() if s.get('backtest_score', 0) < min_score and s.get('validation_status') == 'validated'))" 2>/dev/null || echo "0")
        echo -e "   ⚠️ Strategie che necessitano ottimizzazione: $LOW_SCORE_COUNT"
        
        if [ "$LOW_SCORE_COUNT" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}📋 Strategie con punteggio basso:${NC}"
            python3 -c "
import json
data = json.load(open('strategies_metadata.json'))
min_score = 0.1
low_score_strategies = [(name, s) for name, s in data.items() if s.get('backtest_score', 0) < min_score and s.get('validation_status') == 'validated']
low_score_strategies.sort(key=lambda x: x[1].get('backtest_score', 0))
for name, strategy in low_score_strategies[:5]:
    score = strategy.get('backtest_score', 0)
    print(f'   - {name}: {score:.3f}')
" 2>/dev/null || echo "   Errore nel caricamento dati"
        fi
    else
        echo -e "${RED}❌ File metadati strategie non trovato${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🔍 Processi di Ottimizzazione:${NC}"
    
    # Conta processi di ottimizzazione attivi
    OPTIMIZATION_PROCESSES=$(ps aux | grep -E "optimizer_agent|optimize_strategy|test_auto_optimization" | grep -v grep | wc -l)
    echo -e "   🔧 Processi ottimizzazione attivi: $OPTIMIZATION_PROCESSES"
    
    if [ "$OPTIMIZATION_PROCESSES" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}📋 Processi attivi:${NC}"
        ps aux | grep -E "optimizer_agent|optimize_strategy|test_auto_optimization" | grep -v grep | while read line; do
            echo -e "   $line"
        done
    fi
    
    echo ""
    echo -e "${BLUE}📝 Log Ottimizzazione:${NC}"
    
    # Cerca log di ottimizzazione
    if [ -d "logs" ]; then
        OPTIMIZATION_LOGS=$(find logs -name "*optimization*" -o -name "*optimizer*" 2>/dev/null | head -5)
        if [ -n "$OPTIMIZATION_LOGS" ]; then
            for log in $OPTIMIZATION_LOGS; do
                if [ -f "$log" ]; then
                    LOG_NAME=$(basename "$log")
                    LOG_SIZE=$(du -h "$log" | cut -f1)
                    echo -e "   📄 $LOG_NAME ($LOG_SIZE)"
                fi
            done
        else
            echo -e "   ℹ️ Nessun log di ottimizzazione trovato"
        fi
    fi
}

show_dry_run_status() {
    echo -e "${BLUE}🚀 Stato Dry Run Strategie${NC}"
    echo ""
    
    # Controlla se il dry run automatico è abilitato
    if [ -f "background_config.json" ]; then
        DRY_RUN_ENABLED=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('dry_run', {}).get('auto_dry_run', False))" 2>/dev/null || echo "False")
        
        if [ "$DRY_RUN_ENABLED" = "True" ]; then
            echo -e "${GREEN}✅ Dry run automatico ABILITATO${NC}"
        else
            echo -e "${RED}❌ Dry run automatico DISABILITATO${NC}"
        fi
        
        # Mostra configurazione dry run
        DRY_RUN_INTERVAL=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('dry_run', {}).get('dry_run_interval', 0))" 2>/dev/null || echo "0")
        if [ "$DRY_RUN_INTERVAL" -gt 0 ]; then
            HOURS=$((DRY_RUN_INTERVAL / 3600))
            echo -e "   ⏰ Intervallo dry run: $HOURS ore"
        fi
        
        MAX_DRY_RUNS=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('dry_run', {}).get('max_dry_runs', 0))" 2>/dev/null || echo "0")
        echo -e "   🔢 Max dry run contemporanei: $MAX_DRY_RUNS"
    else
        echo -e "${RED}❌ File di configurazione non trovato${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Dry Run Attivi:${NC}"
    
    # Conta dry run attivi
    ACTIVE_DRY_RUNS=$(ps aux | grep "freqtrade.*trade" | grep -v grep | wc -l)
    echo -e "   🚀 Dry run attivi: $ACTIVE_DRY_RUNS"
    
    if [ "$ACTIVE_DRY_RUNS" -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}📋 Processi dry run attivi:${NC}"
        ps aux | grep "freqtrade.*trade" | grep -v grep | while read line; do
            echo -e "   $line"
        done
    fi
    
    echo ""
    echo -e "${BLUE}📊 Strategie Candidate per Dry Run:${NC}"
    
    # Trova strategie candidate
    if [ -f "strategies_metadata.json" ]; then
        CANDIDATE_COUNT=$(python3 -c "
import json
from datetime import datetime, timedelta
data = json.load(open('strategies_metadata.json'))
now = datetime.now()
week_ago = now - timedelta(days=7)
candidates = []
for name, strategy in data.items():
    if strategy.get('validation_status') == 'validated':
        gen_time = strategy.get('generation_time', '')
        if gen_time:
            try:
                gen_dt = datetime.fromisoformat(gen_time.replace('Z', '+00:00'))
                if gen_dt >= week_ago:
                    candidates.append(name)
            except:
                pass
print(len(candidates))
" 2>/dev/null || echo "0")
        
        echo -e "   🎯 Strategie candidate (validate, <7 giorni): $CANDIDATE_COUNT"
        
        if [ "$CANDIDATE_COUNT" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}📋 Top 5 strategie candidate:${NC}"
            python3 -c "
import json
from datetime import datetime, timedelta
data = json.load(open('strategies_metadata.json'))
now = datetime.now()
week_ago = now - timedelta(days=7)
candidates = []
for name, strategy in data.items():
    if strategy.get('validation_status') == 'validated':
        gen_time = strategy.get('generation_time', '')
        if gen_time:
            try:
                gen_dt = datetime.fromisoformat(gen_time.replace('Z', '+00:00'))
                if gen_dt >= week_ago:
                    priority = 0
                    model = strategy.get('model_used', '')
                    if 'cogito:8b' in model:
                        priority += 10
                    elif 'cogito:3b' in model:
                        priority += 5
                    elif 'mistral' in model:
                        priority += 3
                    candidates.append((priority, name, strategy))
            except:
                pass
candidates.sort(reverse=True)
for priority, name, strategy in candidates[:5]:
    model = strategy.get('model_used', 'unknown')
    strategy_type = strategy.get('strategy_type', 'unknown')
    print(f'   - {name} ({model}, {strategy_type})')
" 2>/dev/null || echo "   Errore nel caricamento dati"
        fi
    else
        echo -e "${RED}❌ File metadati strategie non trovato${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📝 Log Dry Run:${NC}"
    
    # Cerca log di dry run
    if [ -d "logs" ]; then
        DRY_RUN_LOGS=$(find logs -name "dry_run_*.log" 2>/dev/null | head -5)
        if [ -n "$DRY_RUN_LOGS" ]; then
            for log in $DRY_RUN_LOGS; do
                if [ -f "$log" ]; then
                    LOG_NAME=$(basename "$log")
                    LOG_SIZE=$(du -h "$log" | cut -f1)
                    echo -e "   📄 $LOG_NAME ($LOG_SIZE)"
                fi
            done
        else
            echo -e "   ℹ️ Nessun log di dry run trovato"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}💾 Database Dry Run:${NC}"
    
    # Cerca database dry run
    shopt -s nullglob
    for db in dry_run_*.db; do
        if [ -f "$db" ]; then
            DB_NAME=$(basename "$db")
            DB_SIZE=$(du -h "$db" | cut -f1)
            echo -e "   📊 $DB_NAME ($DB_SIZE)"
        fi
    done
    shopt -u nullglob
}

show_live_strategies() {
    echo -e "${BLUE}🚀 Gestione Strategie Live Trading${NC}"
    echo ""
    
    # Controlla se l'esportatore live è disponibile
    if [ -f "live_strategies_exporter.py" ]; then
        echo -e "${GREEN}✅ Live Strategies Exporter disponibile${NC}"
    else
        echo -e "${RED}❌ Live Strategies Exporter non trovato${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}📊 Stato Esportazione Live:${NC}"
    
    # Controlla configurazione live export
    if [ -f "background_config.json" ]; then
        LIVE_EXPORT_ENABLED=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('live_export', {}).get('export_interval', 0) > 0)" 2>/dev/null || echo "False")
        
        if [ "$LIVE_EXPORT_ENABLED" = "True" ]; then
            echo -e "${GREEN}✅ Esportazione automatica ABILITATA${NC}"
            
            LIVE_EXPORT_INTERVAL=$(python3 -c "import json; config=json.load(open('background_config.json')); print(config.get('live_export', {}).get('export_interval', 0))" 2>/dev/null || echo "0")
            if [ "$LIVE_EXPORT_INTERVAL" -gt 0 ]; then
                HOURS=$((LIVE_EXPORT_INTERVAL / 3600))
                echo -e "   ⏰ Intervallo esportazione: $HOURS ore"
            fi
        else
            echo -e "${RED}❌ Esportazione automatica DISABILITATA${NC}"
        fi
    else
        echo -e "${RED}❌ File di configurazione non trovato${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📁 Directory Strategie Live:${NC}"
    
    # Controlla directory strategie live
    if [ -d "live_strategies" ]; then
        LIVE_STRATEGIES_COUNT=$(ls live_strategies/*.py 2>/dev/null | wc -l)
        echo -e "   📊 Strategie live esportate: $LIVE_STRATEGIES_COUNT"
        
        if [ "$LIVE_STRATEGIES_COUNT" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}📋 Strategie live disponibili:${NC}"
            ls live_strategies/*.py 2>/dev/null | while read file; do
                STRATEGY_NAME=$(basename "$file" .py)
                FILE_SIZE=$(du -h "$file" | cut -f1)
                MOD_TIME=$(stat -c %y "$file" | cut -d' ' -f1)
                echo -e "   📄 $STRATEGY_NAME ($FILE_SIZE, $MOD_TIME)"
            done
        fi
        
        # Controlla metadati live
        if [ -f "live_strategies/live_strategies_metadata.json" ]; then
            echo ""
            echo -e "${BLUE}📊 Metadati Strategie Live:${NC}"
            
            # Conta strategie attive
            ACTIVE_COUNT=$(python3 -c "import json; data=json.load(open('live_strategies/live_strategies_metadata.json')); print(sum(1 for s in data.values() if s.get('status') == 'active'))" 2>/dev/null || echo "0")
            echo -e "   ✅ Strategie attive: $ACTIVE_COUNT"
            
            # Mostra top strategie per punteggio
            echo ""
            echo -e "${YELLOW}🏆 Top 3 strategie per punteggio:${NC}"
            python3 -c "
import json
from datetime import datetime
try:
    data = json.load(open('live_strategies/live_strategies_metadata.json'))
    strategies = []
    for name, metadata in data.items():
        score = metadata.get('evaluation_score', 0)
        export_time = metadata.get('export_time', '')
        strategies.append((score, name, metadata))
    
    strategies.sort(reverse=True)
    for score, name, metadata in strategies[:3]:
        export_date = metadata.get('export_time', '')[:10] if metadata.get('export_time') else 'N/A'
        print(f'   🥇 {name} (Score: {score:.3f}, Export: {export_date})')
except Exception as e:
    print(f'   ❌ Errore: {e}')
" 2>/dev/null || echo "   ❌ Errore nel caricamento metadati"
        fi
    else
        echo -e "${RED}❌ Directory strategie live non trovata${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Strategie Candidate per Live:${NC}"
    
    # Trova strategie candidate per live trading
    if [ -f "strategies_metadata.json" ]; then
        CANDIDATE_COUNT=$(python3 -c "
import json
from datetime import datetime
data = json.load(open('strategies_metadata.json'))
candidates = []
for name, strategy in data.items():
    backtest_score = strategy.get('backtest_score', 0)
    validation_status = strategy.get('validation_status', '')
    model_used = strategy.get('model_used', '')
    
    # Criteri per live trading
    if (backtest_score and backtest_score >= 0.1 and 
        validation_status in ['validated', 'optimized'] and
        ('cogito:8b' in model_used or 'cogito:3b' in model_used or 'mistral' in model_used)):
        candidates.append((backtest_score, name, strategy))
candidates.sort(reverse=True)
print(len(candidates))
" 2>/dev/null || echo "0")
        
        echo -e "   🎯 Strategie candidate per live: $CANDIDATE_COUNT"
        
        if [ "$CANDIDATE_COUNT" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}📋 Top 5 strategie candidate:${NC}"
            python3 -c "
import json
from datetime import datetime
data = json.load(open('strategies_metadata.json'))
candidates = []
for name, strategy in data.items():
    backtest_score = strategy.get('backtest_score', 0)
    validation_status = strategy.get('validation_status', '')
    model_used = strategy.get('model_used', '')
    
    if (backtest_score and backtest_score >= 0.1 and 
        validation_status in ['validated', 'optimized'] and
        ('cogito:8b' in model_used or 'cogito:3b' in model_used or 'mistral' in model_used)):
        candidates.append((backtest_score, name, strategy))
candidates.sort(reverse=True)
for score, name, strategy in candidates[:5]:
    model = strategy.get('model_used', 'unknown')
    strategy_type = strategy.get('strategy_type', 'unknown')
    print(f'   - {name} (Score: {score:.3f}, {model}, {strategy_type})')
" 2>/dev/null || echo "   Errore nel caricamento dati"
        fi
    else
        echo -e "${RED}❌ File metadati strategie non trovato${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🔧 Comandi Utili:${NC}"
    echo -e "   python3 live_strategies_exporter.py - Test esportatore"
    echo -e "   ls live_strategies/ - Lista strategie esportate"
    echo -e "   cat live_strategies/live_strategies_metadata.json - Metadati live"
    echo ""
    echo -e "${BLUE}💡 Per utilizzare le strategie live:${NC}"
    echo -e "   1. Copia i file da live_strategies/ in user_data/strategies/"
    echo -e "   2. Configura Freqtrade per il live trading"
    echo -e "   3. Avvia il bot con le strategie selezionate"
}

# Gestione comandi
case "${1:-help}" in
    start)
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    restart)
        restart_agent
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    config)
        edit_config
        ;;
    backtest)
        show_backtest_status
        ;;
    backtest-logs)
        show_backtest_logs
        ;;
    optimization)
        show_optimization_status
        ;;
    dry-run)
        show_dry_run_status
        ;;
    live-strategies)
        show_live_strategies
        ;;
    cleanup-analysis)
        show_cleanup_analysis
        ;;
    sessions)
        check_sessions
        ;;
    stop-others)
        stop_others
        ;;
    stop-all)
        stop_all
        ;;
    logs-all)
        show_all_logs
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