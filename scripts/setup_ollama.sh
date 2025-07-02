#!/bin/bash

# Script per verificare e installare i modelli Ollama necessari

set -e

echo "🤖 Setup modelli Ollama per crypto-futures-llm-trading"
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

# 1. Verifica se Ollama è installato
log_info "1. Verifica installazione Ollama..."
if command -v ollama &> /dev/null; then
    log_success "Ollama installato: $(ollama --version)"
else
    log_error "Ollama non installato. Installare da: https://ollama.ai"
    exit 1
fi

# 2. Verifica se Ollama è in esecuzione
log_info "2. Verifica servizio Ollama..."
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    log_success "Ollama è in esecuzione"
else
    log_warning "Ollama non è in esecuzione. Avvio del servizio..."
    sudo systemctl start ollama
    sleep 5
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        log_success "Ollama avviato con successo"
    else
        log_error "Impossibile avviare Ollama"
        exit 1
    fi
fi

# 3. Lista modelli attuali
log_info "3. Modelli attualmente installati:"
CURRENT_MODELS=$(ollama list | grep -v "NAME" | awk '{print $1}' | tr '\n' ' ')
if [ -z "$CURRENT_MODELS" ]; then
    log_warning "Nessun modello installato"
else
    log_success "Modelli trovati: $CURRENT_MODELS"
fi

# 4. Modelli necessari
REQUIRED_MODELS=("mistral" "llama2" "phi3")

# 5. Verifica e installa modelli mancanti
log_info "4. Verifica modelli necessari..."
for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list | grep -q "^$model "; then
        log_success "✅ $model già installato"
    else
        log_info "📥 Installazione $model..."
        if ollama pull "$model"; then
            log_success "✅ $model installato con successo"
        else
            log_error "❌ Errore nell'installazione di $model"
        fi
    fi
done

# 6. Verifica finale
log_info "5. Verifica finale modelli..."
FINAL_MODELS=$(ollama list | grep -v "NAME" | awk '{print $1}' | tr '\n' ' ')
log_success "Modelli disponibili: $FINAL_MODELS"

# 7. Test connessione
log_info "6. Test connessione API..."
if curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{"model": "mistral", "prompt": "Hello", "stream": false}' &> /dev/null; then
    log_success "✅ API Ollama funzionante"
else
    log_warning "⚠️  API Ollama potrebbe non essere completamente funzionante"
fi

echo ""
echo "🎉 Setup modelli Ollama completato!"
echo "=================================="
log_success "Modelli disponibili: $FINAL_MODELS"
echo ""
log_info "Per testare:"
echo "  ollama run mistral 'Ciao, come stai?'"
echo "  ollama run llama2 'Explain quantum computing'"
echo "  ollama run phi3 'Write a Python function'"
echo ""
log_info "Per il progetto:"
echo "  python coordinator.py" 