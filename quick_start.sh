#!/bin/bash

# Script di avvio rapido per testare il sistema crypto-futures-llm-trading

echo "🚀 Avvio Rapido Crypto Futures LLM Trading"
echo "=========================================="

# Colori per output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funzione per log colorato
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Verifica se siamo nella directory corretta
if [ ! -f "coordinator.py" ]; then
    echo "❌ Eseguire questo script dalla directory del progetto"
    exit 1
fi

# 1. Attiva ambiente virtuale
log_info "1. Attivazione ambiente virtuale..."
if [ -d "venv" ]; then
    source venv/bin/activate
    log_success "Ambiente virtuale attivato"
else
    log_warning "Ambiente virtuale non trovato. Esegui prima: ./setup_freqtrade.sh"
    exit 1
fi

# 2. Test configurazione
log_info "2. Test configurazione..."
if [ -f "test_setup.py" ]; then
    python test_setup.py
    if [ $? -ne 0 ]; then
        log_warning "Test configurazione falliti. Esegui: ./setup_freqtrade.sh"
        exit 1
    fi
else
    log_warning "Script di test non trovato"
fi

# 3. Verifica Ollama
log_info "3. Verifica Ollama..."
if command -v ollama &> /dev/null; then
    if ollama list | grep -q "mistral"; then
        log_success "Ollama e Mistral disponibili"
    else
        log_warning "Mistral non trovato. Esegui: ollama pull mistral"
    fi
else
    log_warning "Ollama non installato. Installare da: https://ollama.ai"
fi

# 4. Download dati di esempio (se non presenti)
log_info "4. Verifica dati storici..."
if [ ! -d "user_data/data" ] || [ -z "$(ls -A user_data/data 2>/dev/null)" ]; then
    log_info "Download dati di esempio..."
    freqtrade download-data --config user_data/config.json \
        --pairs BTC/USDT:USDT \
        --timeframe 5m \
        --timerange 20240101-20240131 || log_warning "Download dati fallito"
else
    log_success "Dati storici già presenti"
fi

# 5. Test strategia base
log_info "5. Test strategia base..."
if [ -f "user_data/strategies/LLMStrategy.py" ]; then
    freqtrade show-config --config user_data/config.json --strategy LLMStrategy > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "Strategia base valida"
    else
        log_warning "Strategia base potrebbe avere problemi"
    fi
else
    log_warning "Strategia base non trovata"
fi

echo ""
echo "🎯 SISTEMA PRONTO!"
echo "=================="
log_success "Il sistema è configurato e pronto per l'uso"
echo ""
log_info "Comandi disponibili:"
echo "  📊 Genera strategie: python coordinator.py"
echo "  🔄 Backtest: ./run_backtest.sh"
echo "  🔧 Hyperopt: ./run_hyperopt.sh"
echo "  🤖 Trading: ./start_bot.sh"
echo ""
log_info "Per iniziare subito:"
echo "  python coordinator.py"
echo ""
log_warning "Ricorda: Il sistema è in modalità dry-run per default" 