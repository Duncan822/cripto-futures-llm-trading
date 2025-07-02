#!/bin/bash

# Script per installare e configurare Freqtrade per il progetto crypto-futures-llm-trading

set -e  # Exit on any error

echo "🚀 Setup completo Freqtrade per crypto-futures-llm-trading"
echo "=================================================="

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se siamo nella directory corretta
if [ ! -f "requirements.txt" ]; then
    log_error "Eseguire questo script dalla directory del progetto crypto-futures-llm-trading"
    exit 1
fi

# 1. Setup ambiente virtuale
log_info "1. Configurazione ambiente virtuale..."
if [ ! -d "venv" ]; then
    log_info "Creazione nuovo ambiente virtuale..."
    python3 -m venv venv
    log_success "Ambiente virtuale creato"
else
    log_warning "Ambiente virtuale già esistente"
fi

# Attiva ambiente virtuale con path assoluto
log_info "Attivazione ambiente virtuale..."
source "$(pwd)/venv/bin/activate"

# Verifica che l'ambiente sia attivato correttamente
if [[ "$VIRTUAL_ENV" == "" ]]; then
    log_error "Fallimento nell'attivazione dell'ambiente virtuale"
    exit 1
fi

log_success "Ambiente virtuale attivato: $VIRTUAL_ENV"

# 2. Aggiorna pip
log_info "2. Aggiornamento pip..."
"$VIRTUAL_ENV/bin/pip" install --upgrade pip

# 3. Installa dipendenze base
log_info "3. Installazione dipendenze base..."
"$VIRTUAL_ENV/bin/pip" install -r requirements.txt

# 4. Installa Freqtrade
log_info "4. Installazione Freqtrade..."
"$VIRTUAL_ENV/bin/pip" install freqtrade[plot]

# 5. Verifica installazione Freqtrade
log_info "5. Verifica installazione Freqtrade..."
if "$VIRTUAL_ENV/bin/freqtrade" --version &> /dev/null; then
    log_success "Freqtrade installato correttamente"
    "$VIRTUAL_ENV/bin/freqtrade" --version
else
    log_error "Freqtrade non trovato nel PATH dell'ambiente virtuale"
    exit 1
fi

# 6. Crea struttura directory
log_info "6. Creazione struttura directory..."
mkdir -p user_data/strategies
mkdir -p user_data/data
mkdir -p user_data/logs
mkdir -p user_data/backtest_results
mkdir -p user_data/hyperopt_results
mkdir -p user_data/plot
log_success "Struttura directory creata"

# 7. Verifica configurazione
log_info "7. Verifica configurazione..."
if [ -f "user_data/config.json" ]; then
    log_success "File di configurazione trovato"
else
    log_error "File di configurazione mancante: user_data/config.json"
    exit 1
fi

# 8. Test configurazione Freqtrade
log_info "8. Test configurazione Freqtrade..."
if "$VIRTUAL_ENV/bin/freqtrade" show-config --config user_data/config.json &> /dev/null; then
    log_success "Configurazione Freqtrade valida"
else
    log_warning "Configurazione Freqtrade potrebbe avere problemi"
fi

# 9. Download dati di esempio
log_info "9. Download dati di esempio per BTC/USDT..."
if "$VIRTUAL_ENV/bin/freqtrade" download-data --config user_data/config.json --pairs BTC/USDT:USDT --timeframe 5m --timerange 20240101-20240131 &> /dev/null; then
    log_success "Download dati completato"
else
    log_warning "Download dati fallito (potrebbe essere normale se non ci sono credenziali)"
fi

# 10. Test strategia base
log_info "10. Test strategia base..."
if [ -f "user_data/strategies/LLMStrategy.py" ]; then
    if "$VIRTUAL_ENV/bin/freqtrade" show-config --config user_data/config.json --strategy LLMStrategy &> /dev/null; then
        log_success "Strategia base valida"
    else
        log_warning "Strategia base potrebbe avere problemi"
    fi
else
    log_warning "Strategia base non trovata"
fi

# 11. Setup Ollama (se non già installato)
log_info "11. Verifica Ollama..."
if command -v ollama &> /dev/null; then
    log_success "Ollama già installato"
    
    # Verifica se i modelli sono disponibili
    if ollama list | grep -q "mistral"; then
        log_success "Modello Mistral disponibile"
    else
        log_warning "Modello Mistral non trovato. Eseguire: ollama pull mistral"
    fi
    
    if ollama list | grep -q "llama2"; then
        log_success "Modello Llama2 disponibile"
    else
        log_warning "Modello Llama2 non trovato. Eseguire: ollama pull llama2"
    fi
    
    if ollama list | grep -q "phi3"; then
        log_success "Modello Phi3 disponibile"
    else
        log_warning "Modello Phi3 non trovato. Eseguire: ollama pull phi3"
    fi
else
    log_warning "Ollama non installato. Installare da: https://ollama.ai"
fi

# 12. Crea script di utilità
log_info "12. Creazione script di utilità..."

# Script per avviare il bot
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
freqtrade trade --config user_data/config.json --strategy LLMStrategy
EOF
chmod +x start_bot.sh

# Script per backtest
cat > run_backtest.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
freqtrade backtesting --config user_data/config.json --strategy LLMStrategy --timerange 20240101-20241231
EOF
chmod +x run_backtest.sh

# Script per hyperopt
cat > run_hyperopt.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
freqtrade hyperopt --config user_data/config.json --strategy LLMStrategy --epochs 100 --spaces buy sell roi stoploss
EOF
chmod +x run_hyperopt.sh

log_success "Script di utilità creati"

# 13. Crea file .env template
log_info "13. Creazione template .env..."
cat > .env.template << 'EOF'
# Configurazione API Exchange
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

# Configurazione Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Configurazione Telegram (opzionale)
TELEGRAM_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Configurazione Trading
DRY_RUN=true
MAX_OPEN_TRADES=3
STAKE_AMOUNT=100
EOF

log_success "Template .env creato"

# 14. Crea README di setup
log_info "14. Creazione README di setup..."
cat > SETUP_README.md << 'EOF'
# Setup Completato! 🎉

Il progetto crypto-futures-llm-trading è ora completamente configurato con Freqtrade.

## Prossimi Passi

### 1. Configurazione API (Opzionale)
Se vuoi fare trading reale:
1. Copia `.env.template` in `.env`
2. Inserisci le tue credenziali API di Binance
3. Imposta `DRY_RUN=false` nel file `.env`

### 2. Download Modelli Ollama
```bash
ollama pull mistral
ollama pull llama2
ollama pull phi3
```

### 3. Download Dati Storici
```bash
source venv/bin/activate
freqtrade download-data --config user_data/config.json --pairs BTC/USDT:USDT ETH/USDT:USDT --timeframe 5m --timerange 20240101-20241231
```

### 4. Test Strategia
```bash
# Backtest
./run_backtest.sh

# Hyperopt
./run_hyperopt.sh

# Trading (dry-run)
./start_bot.sh
```

### 5. Generazione Strategie con LLM
```bash
source venv/bin/activate
python coordinator.py
```

## Struttura del Progetto
```
crypto-futures-llm-trading/
├── user_data/
│   ├── config.json          # Configurazione Freqtrade
│   ├── strategies/          # Strategie di trading
│   ├── data/               # Dati storici
│   ├── logs/               # Log del bot
│   ├── backtest_results/   # Risultati backtest
│   └── hyperopt_results/   # Risultati hyperopt
├── agents/                 # Agenti LLM
├── strategies/             # Strategie generate
├── coordinator.py          # Orchestratore principale
└── freqtrade_utils.py      # Utility Freqtrade
```

## Comandi Utili

- `./start_bot.sh` - Avvia il bot in modalità dry-run
- `./run_backtest.sh` - Esegue backtest della strategia
- `./run_hyperopt.sh` - Ottimizza parametri strategia
- `python coordinator.py` - Genera strategie con LLM

## Note Importanti

- Il bot è configurato in modalità **dry-run** per default
- Le strategie sono salvate in `user_data/strategies/`
- I risultati sono salvati in `user_data/backtest_results/` e `user_data/hyperopt_results/`
- Il bot usa timeframe 5m e trading futures su Binance
EOF

log_success "README di setup creato"

echo ""
echo "🎉 Setup completato con successo!"
echo "=================================="
log_success "Freqtrade è ora completamente configurato"
log_success "Leggi SETUP_README.md per i prossimi passi"
echo ""
log_info "Per iniziare:"
echo "  1. source venv/bin/activate"
echo "  2. python coordinator.py"
echo "  3. ./run_backtest.sh"
echo ""
log_warning "Ricorda di configurare le API keys se vuoi fare trading reale!" 