#!/bin/bash

# Script per gestire il Dry Run delle strategie ottimizzate
# Comandi: start, stop, status, report, list, select

set -e

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

DRY_RUN_DB="dry_run.db"
MANAGER_SCRIPT="dry_run_manager.py"

show_help() {
    echo -e "${BLUE}🚀 Gestione Dry Run Strategie Ottimizzate${NC}"
    echo ""
    echo "Uso: $0 [comando] [opzioni]"
    echo ""
    echo "Comandi disponibili:"
    echo -e "  ${GREEN}list${NC}      - Lista strategie disponibili per dry run"
    echo -e "  ${GREEN}select${NC}    - Seleziona strategie per dry run"
    echo -e "  ${GREEN}start${NC}     - Avvia dry run per strategia"
    echo -e "  ${RED}stop${NC}      - Ferma dry run per strategia"
    echo -e "  ${YELLOW}status${NC}   - Mostra status dry run attivi"
    echo -e "  ${BLUE}report${NC}    - Genera report dry run completati"
    echo -e "  ${BLUE}monitor${NC}   - Monitora performance in tempo reale"
    echo -e "  ${BLUE}cleanup${NC}   - Pulisci dry run completati"
    echo ""
    echo -e "  ${BLUE}help${NC}      - Mostra questo aiuto"
    echo ""
    echo "Esempi:"
    echo "  $0 list"
    echo "  $0 select"
    echo "  $0 start VolatilityStrategy_cogito:8b_20250630_223230"
    echo "  $0 status"
    echo "  $0 report"
}

list_strategies() {
    echo -e "${BLUE}📋 Strategie Disponibili per Dry Run${NC}"
    echo ""
    
    if [ ! -f "strategies_metadata.json" ]; then
        echo -e "${RED}❌ File metadati strategie non trovato${NC}"
        return 1
    fi
    
    python3 -c "
import json
data = json.load(open('strategies_metadata.json'))
validated = [(name, s) for name, s in data.items() if s.get('validation_status') == 'validated']
validated.sort(key=lambda x: x[1].get('generation_time', ''), reverse=True)

print('Strategie validate (pronte per dry run):')
print('=' * 50)
for name, strategy in validated[:10]:
    strategy_type = strategy.get('strategy_type', 'unknown')
    model = strategy.get('model_used', 'unknown')
    print(f'📊 {name}')
    print(f'   Tipo: {strategy_type} | Modello: {model}')
    print()
" 2>/dev/null || echo "Errore nel caricamento strategie"
}

select_strategies() {
    echo -e "${BLUE}🎯 Selezione Strategie per Dry Run${NC}"
    echo ""
    
    # Mostra strategie disponibili
    list_strategies
    
    echo -e "${YELLOW}💡 Raccomandazioni per selezione:${NC}"
    echo "1. Inizia con strategie cogito:8b (più accurate)"
    echo "2. Diversifica per tipo (volatility, scalping, momentum)"
    echo "3. Scegli strategie recenti (< 7 giorni)"
    echo "4. Considera strategie con backtest score > 0.1"
    echo ""
    
    # Strategie raccomandate
    echo -e "${GREEN}✅ Strategie Raccomandate:${NC}"
    python3 -c "
import json
from datetime import datetime, timedelta

data = json.load(open('strategies_metadata.json'))
now = datetime.now()
week_ago = now - timedelta(days=7)

recommended = []
for name, strategy in data.items():
    if strategy.get('validation_status') != 'validated':
        continue
        
    # Controlla età
    gen_time = strategy.get('generation_time', '')
    if gen_time:
        try:
            gen_dt = datetime.fromisoformat(gen_time.replace('Z', '+00:00'))
            if gen_dt < week_ago:
                continue
        except:
            continue
    
    # Priorità per modello
    model = strategy.get('model_used', '')
    priority = 0
    if 'cogito:8b' in model:
        priority = 3
    elif 'cogito:3b' in model:
        priority = 2
    elif 'mistral' in model:
        priority = 1
    
    recommended.append((priority, name, strategy))

recommended.sort(reverse=True)

print('Top 5 strategie raccomandate:')
for i, (priority, name, strategy) in enumerate(recommended[:5], 1):
    model = strategy.get('model_used', 'unknown')
    strategy_type = strategy.get('strategy_type', 'unknown')
    print(f'{i}. {name}')
    print(f'   Modello: {model} | Tipo: {strategy_type}')
" 2>/dev/null || echo "Errore nell'analisi strategie"
}

start_dry_run() {
    local strategy_name="$1"
    
    if [ -z "$strategy_name" ]; then
        echo -e "${RED}❌ Nome strategia richiesto${NC}"
        echo "Uso: $0 start <strategy_name>"
        return 1
    fi
    
    echo -e "${BLUE}🚀 Avvio Dry Run per ${strategy_name}${NC}"
    
    # Verifica strategia
    strategy_file="user_data/strategies/${strategy_name,,}.py"
    if [ ! -f "$strategy_file" ]; then
        echo -e "${RED}❌ File strategia non trovato: $strategy_file${NC}"
        return 1
    fi
    
    # Configurazione dry run
    config_file="config_dry_run_${strategy_name}.json"
    cat > "$config_file" << EOF
{
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": 100,
    "timeframe": "5m",
    "dry_run": true,
    "dry_run_wallet": 1000,
    "trading_mode": "futures",
    "margin_mode": "isolated",
    "exchange": {
        "name": "binanceusdm",
        "key": "",
        "secret": "",
        "pair_whitelist": ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"]
    },
    "pairlists": [{"method": "StaticPairList"}],
    "edge": {"enabled": false},
    "telegram": {"enabled": false},
    "api_server": {
        "enabled": true,
        "listen_port": 8080,
        "verbosity": "error"
    },
    "bot_name": "dry-run-${strategy_name}"
}
EOF
    
    # Avvia Freqtrade con ambiente virtuale
    nohup bash -c "source venv/bin/activate && freqtrade trade --strategy \"$strategy_name\" --config \"$config_file\" --db-url \"sqlite:///dry_run_${strategy_name}.db\"" > "logs/dry_run_${strategy_name}.log" 2>&1 &
    
    echo -e "${GREEN}✅ Dry run avviato per $strategy_name${NC}"
    echo -e "   Log: logs/dry_run_${strategy_name}.log"
    echo -e "   Database: dry_run_${strategy_name}.db"
}

stop_dry_run() {
    local strategy_name="$1"
    
    if [ -z "$strategy_name" ]; then
        echo -e "${RED}❌ Nome strategia richiesto${NC}"
        echo "Uso: $0 stop <strategy_name>"
        return 1
    fi
    
    echo -e "${YELLOW}🛑 Fermando Dry Run per ${strategy_name}${NC}"
    pkill -f "freqtrade.*${strategy_name}" 2>/dev/null || true
    echo -e "${GREEN}✅ Dry run fermato per $strategy_name${NC}"
}

show_status() {
    echo -e "${BLUE}📊 Status Dry Run Attivi${NC}"
    echo ""
    
    active_count=$(ps aux | grep "freqtrade.*trade" | grep -v grep | wc -l)
    echo -e "🔄 Dry run attivi: $active_count"
    
    if [ $active_count -gt 0 ]; then
        echo ""
        echo -e "${GREEN}📋 Processi attivi:${NC}"
        ps aux | grep "freqtrade.*trade" | grep -v grep
    fi
    
    echo ""
    echo -e "${BLUE}📊 Database dry run:${NC}"
    shopt -s nullglob
    for db in dry_run_*.db; do
        if [ -f "$db" ]; then
            strategy_name=$(echo "$db" | sed 's/dry_run_\(.*\)\.db/\1/')
            db_size=$(du -h "$db" | cut -f1)
            echo -e "   📄 $strategy_name ($db_size)"
        fi
    done
    shopt -u nullglob
}

generate_report() {
    local strategy_name="$1"
    
    echo -e "${BLUE}📈 Report Dry Run${NC}"
    echo ""
    
    if [ -n "$strategy_name" ]; then
        db_file="dry_run_${strategy_name}.db"
        if [ -f "$db_file" ]; then
            python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('$db_file')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*), SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END), SUM(profit) FROM trades WHERE strategy = ?', ('$strategy_name',))
    result = cursor.fetchone()
    if result:
        total_trades, winning_trades, total_profit = result
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        print(f'Trades totali: {total_trades}')
        print(f'Win rate: {win_rate:.1f}%')
        print(f'Profitto totale: {total_profit:.2f} USDT')
    conn.close()
except Exception as e:
    print(f'Errore: {e}')
" 2>/dev/null || echo "Errore nel report"
        else
            echo -e "❌ Database non trovato per $strategy_name"
        fi
    else
        echo -e "📊 Report generale:"
        shopt -s nullglob
        for db in dry_run_*.db; do
            if [ -f "$db" ]; then
                strategy_name=$(echo "$db" | sed 's/dry_run_\(.*\)\.db/\1/')
                echo -e "   📄 $strategy_name"
            fi
        done
        shopt -u nullglob
    fi
}

monitor_performance() {
    echo -e "${BLUE}📊 Monitoraggio Performance Dry Run${NC}"
    echo ""
    echo -e "${YELLOW}⚠️ Monitoraggio in tempo reale (Ctrl+C per fermare)${NC}"
    echo ""
    
    while true; do
        clear
        echo -e "${BLUE}📊 Status Dry Run - $(date)${NC}"
        echo ""
        
        # Conta processi attivi
        active_count=$(ps aux | grep "freqtrade.*trade" | grep -v grep | wc -l)
        echo -e "🔄 Dry run attivi: $active_count"
        
        if [ $active_count -gt 0 ]; then
            echo ""
            echo -e "${GREEN}📋 Processi attivi:${NC}"
            ps aux | grep "freqtrade.*trade" | grep -v grep | while read line; do
                echo -e "   $line"
            done
        fi
        
        # Controlla database recenti
        echo ""
        echo -e "${BLUE}📊 Database recenti:${NC}"
        shopt -s nullglob
        for db in dry_run_*.db; do
            if [ -f "$db" ]; then
                strategy_name=$(echo "$db" | sed 's/dry_run_\(.*\)\.db/\1/')
                db_size=$(du -h "$db" | cut -f1)
                echo -e "   📄 $strategy_name ($db_size)"
            fi
        done
        shopt -u nullglob
        
        sleep 10
    done
}

cleanup_dry_runs() {
    echo -e "${YELLOW}🧹 Pulizia Dry Run Completati${NC}"
    echo ""
    
    # Rimuovi database completati
    removed_count=0
    shopt -s nullglob
    for db in dry_run_*.db; do
        if [ -f "$db" ]; then
            strategy_name=$(echo "$db" | sed 's/dry_run_\(.*\)\.db/\1/')
            
            # Controlla se il processo è ancora attivo
            if ! ps aux | grep -q "freqtrade.*${strategy_name}"; then
                rm -f "$db"
                echo -e "   🗑️ Rimosso: $db"
                removed_count=$((removed_count + 1))
            fi
        fi
    done
    shopt -u nullglob
    
    # Rimuovi log vecchi
    if [ -d "logs" ]; then
        old_logs=$(find logs -name "dry_run_*.log" -mtime +7 2>/dev/null)
        if [ -n "$old_logs" ]; then
            echo "$old_logs" | xargs rm -f
            echo -e "   🗑️ Rimossi log vecchi (>7 giorni)"
        fi
    fi
    
    echo -e "${GREEN}✅ Pulizia completata ($removed_count database rimossi)${NC}"
}

# Gestione comandi
case "${1:-help}" in
    list)
        list_strategies
        ;;
    select)
        select_strategies
        ;;
    start)
        start_dry_run "$2"
        ;;
    stop)
        stop_dry_run "$2"
        ;;
    status)
        show_status
        ;;
    report)
        generate_report "$2"
        ;;
    monitor)
        monitor_performance
        ;;
    cleanup)
        cleanup_dry_runs
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