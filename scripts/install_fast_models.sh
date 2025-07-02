#!/bin/bash

# Script per installare modelli LLM veloci ottimizzati per CPU
# Basato sui risultati di ricerca per modelli efficienti

set -e

echo "🚀 INSTALLAZIONE MODELLI LLM VELOCI PER CPU"
echo "=========================================="

# Controlla se Ollama è installato
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama non è installato!"
    echo "💡 Installa Ollama da: https://ollama.ai"
    exit 1
fi

echo "✅ Ollama trovato: $(ollama --version)"

# Controlla modelli esistenti
echo -e "\n🔍 Controllo modelli esistenti..."
existing_models=$(ollama list | grep -E "(phi3|llama2|mistral)" | awk '{print $1}' || true)

if [ -n "$existing_models" ]; then
    echo "📦 Modelli esistenti trovati:"
    echo "$existing_models"
fi

# Modelli da installare (in ordine di velocità)
models=(
    "phi3:mini"              # 3.8B - Ultra veloce
    "llama2:7b-chat-q4_0"    # 7B quantizzato - Buon compromesso
    "mistral:7b-instruct-q4_0" # 7B quantizzato - Molto intelligente
)

echo -e "\n📥 Installazione modelli veloci..."

for model in "${models[@]}"; do
    echo -e "\n🎯 Installando: $model"
    
    # Controlla se già installato
    if ollama list | grep -q "$model"; then
        echo "✅ $model già installato, saltando..."
        continue
    fi
    
    echo "⏳ Download in corso... (può richiedere alcuni minuti)"
    
    # Installa con timeout e retry
    max_attempts=3
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "Tentativo $attempt/$max_attempts..."
        
        if timeout 600 ollama pull "$model"; then
            echo "✅ $model installato con successo!"
            break
        else
            echo "❌ Tentativo $attempt fallito"
            if [ $attempt -lt $max_attempts ]; then
                echo "⏳ Riprovo tra 10 secondi..."
                sleep 10
            fi
            attempt=$((attempt + 1))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        echo "❌ Impossibile installare $model dopo $max_attempts tentativi"
    fi
done

echo -e "\n📊 STATO FINALE MODELLI:"
echo "=========================="

ollama list | grep -E "(phi3|llama2|mistral)" || echo "Nessun modello trovato"

echo -e "\n🎯 RACCOMANDAZIONI PER IL TUO PROGETTO:"
echo "=========================================="

# Controlla quale modello è più veloce
if ollama list | grep -q "phi3:mini"; then
    echo "🥇 PHI-3 MINI: Migliore per velocità (~20-30 token/sec)"
    echo "   - Parametri: 3.8B"
    echo "   - Memoria: ~2GB"
    echo "   - Ideale per: Generazione strategie veloce"
elif ollama list | grep -q "llama2:7b-chat-q4_0"; then
    echo "🥈 LLAMA2-7B-Q4: Buon compromesso (~15-25 token/sec)"
    echo "   - Parametri: 7B quantizzato"
    echo "   - Memoria: ~4GB"
    echo "   - Ideale per: Analisi e ottimizzazione"
elif ollama list | grep -q "mistral:7b-instruct-q4_0"; then
    echo "🥉 MISTRAL-7B-Q4: Molto intelligente (~15-20 token/sec)"
    echo "   - Parametri: 7B quantizzato"
    echo "   - Memoria: ~4GB"
    echo "   - Ideale per: Strategie complesse"
fi

echo -e "\n🔧 CONFIGURAZIONE OTTIMIZZATA:"
echo "================================"

# Crea configurazione ottimizzata
if [ -f "background_config_cpu_optimized.json" ]; then
    echo "✅ Configurazione CPU ottimizzata già presente"
    echo "📁 File: background_config_cpu_optimized.json"
else
    echo "❌ Configurazione CPU ottimizzata non trovata"
    echo "💡 Crea il file background_config_cpu_optimized.json"
fi

echo -e "\n🧪 TEST RAPIDO:"
echo "================"

# Test rapido del modello più veloce
fastest_model=""
if ollama list | grep -q "phi3:mini"; then
    fastest_model="phi3:mini"
elif ollama list | grep -q "llama2:7b-chat-q4_0"; then
    fastest_model="llama2:7b-chat-q4_0"
elif ollama list | grep -q "mistral:7b-instruct-q4_0"; then
    fastest_model="mistral:7b-instruct-q4_0"
fi

if [ -n "$fastest_model" ]; then
    echo "🚀 Test rapido con $fastest_model..."
    echo "Prompt: 'Genera una strategia scalping BTC/USDT in 2 righe'"
    
    start_time=$(date +%s)
    
    response=$(timeout 30 ollama run "$fastest_model" "Genera una strategia scalping BTC/USDT in 2 righe" 2>/dev/null || echo "Timeout")
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo "⏱️  Tempo di risposta: ${duration}s"
    echo "📝 Risposta:"
    echo "$response" | head -3
else
    echo "❌ Nessun modello veloce disponibile per il test"
fi

echo -e "\n✅ INSTALLAZIONE COMPLETATA!"
echo "=============================="
echo "💡 Prossimi passi:"
echo "   1. Testa i modelli: python test_fast_llms.py"
echo "   2. Usa configurazione CPU: cp background_config_cpu_optimized.json background_config.json"
echo "   3. Avvia Background Agent: ./manage_background_agent.sh start" 