# 🚀 Guida Modelli LLM Veloci per CPU

Guida completa per l'uso di modelli LLM ottimizzati per CPU nel progetto crypto-futures-llm-trading.

## 📊 **Panoramica Modelli Veloce**

### 🥇 **PHI-3 Mini (Raccomandato)**
- **Parametri**: 3.8B
- **Velocità**: ~20-30 token/sec su CPU
- **Memoria**: ~2GB
- **Qualità**: Eccellente per task specifici
- **Ideale per**: Generazione strategie veloce

### 🥈 **Llama2-7B-Chat (Q4)**
- **Parametri**: 7B quantizzato a 4-bit
- **Velocità**: ~15-25 token/sec su CPU
- **Memoria**: ~4GB
- **Qualità**: Molto buona, stabile
- **Ideale per**: Analisi e ottimizzazione

### 🥉 **Mistral-7B-Instruct (Q4)**
- **Parametri**: 7B quantizzato a 4-bit
- **Velocità**: ~15-20 token/sec su CPU
- **Memoria**: ~4GB
- **Qualità**: Eccellente comprensione
- **Ideale per**: Strategie complesse

## 🛠️ **Installazione Rapida**

### 1. **Installazione Automatica**
```bash
# Installa tutti i modelli veloci
./install_fast_models.sh
```

### 2. **Installazione Manuale**
```bash
# Installa modelli singolarmente
ollama pull phi3:mini
ollama pull llama2:7b-chat-q4_0
ollama pull mistral:7b-instruct-q4_0
```

### 3. **Test Performance**
```bash
# Testa tutti i modelli e misura velocità
python test_fast_llms.py
```

## ⚙️ **Configurazione Ottimizzata**

### **Configurazione CPU-Optimized**
Il file `background_config_cpu_optimized.json` contiene:
```json
{
  "models": ["phi3:mini", "llama2:7b-chat-q4_0", "mistral:7b-instruct-q4_0"],
  "cpu_optimization": {
    "enable": true,
    "max_memory_usage": "4GB",
    "threads": 4,
    "batch_size": 1,
    "timeout_seconds": 120
  }
}
```

### **Attivazione Configurazione**
```bash
# Usa configurazione CPU ottimizzata
cp background_config_cpu_optimized.json background_config.json

# Riavvia Background Agent
./manage_background_agent.sh restart
```

## 📈 **Performance e Benchmark**

### **Risultati Attesi**
| Modello | Velocità | Memoria | Qualità | Uso Consigliato |
|---------|----------|---------|---------|-----------------|
| PHI-3 Mini | 20-30 t/s | 2GB | ⭐⭐⭐⭐ | Generazione veloce |
| Llama2-7B-Q4 | 15-25 t/s | 4GB | ⭐⭐⭐⭐⭐ | Analisi generale |
| Mistral-7B-Q4 | 15-20 t/s | 4GB | ⭐⭐⭐⭐⭐ | Strategie complesse |

### **Ottimizzazioni CPU**
- **Threading**: Usa 4 thread per CPU multi-core
- **Batch Size**: 1 per ridurre latenza
- **Memory Limit**: 4GB per evitare swap
- **Timeout**: 120s per evitare blocchi

## 🎯 **Utilizzo nel Progetto**

### **Background Agent**
Il Background Agent userà automaticamente i modelli più veloci:
```bash
# Avvia con modelli veloci
./manage_background_agent.sh start

# Monitora performance
./manage_background_agent.sh logs
```

### **Generazione Strategie**
- **PHI-3 Mini**: Strategie semplici e veloci
- **Llama2-7B-Q4**: Strategie bilanciate
- **Mistral-7B-Q4**: Strategie complesse

### **Ottimizzazione**
- **Llama2-7B-Q4**: Analisi risultati backtest
- **Mistral-7B-Q4**: Ottimizzazione parametri
- **PHI-3 Mini**: Validazione rapida

## 🔧 **Troubleshooting**

### **Problemi Comuni**

#### **1. Modello Lento**
```bash
# Controlla uso CPU
htop

# Riduci thread
# Modifica background_config.json
"threads": 2
```

#### **2. Memoria Insufficiente**
```bash
# Controlla memoria
free -h

# Riduci batch size
"batch_size": 1
```

#### **3. Timeout**
```bash
# Aumenta timeout
"timeout_seconds": 180

# Usa modello più piccolo
"models": ["phi3:mini"]
```

### **Monitoraggio Performance**
```bash
# Monitora uso risorse
./monitor_hardware.sh

# Controlla log
tail -f logs/background_agent_*.log
```

## 📊 **Confronto con Modelli Grandi**

### **Vantaggi Modelli Veloce**
- ✅ **Velocità**: 3-5x più veloci
- ✅ **Memoria**: 50-70% meno RAM
- ✅ **Costo**: Nessun costo GPU
- ✅ **Disponibilità**: Sempre online
- ✅ **Privacy**: Elaborazione locale

### **Svantaggi**
- ❌ **Qualità**: Leggermente inferiore
- ❌ **Complessità**: Limitata per task complessi
- ❌ **Contesto**: Memoria limitata

## 🚀 **Best Practices**

### **1. Selezione Modello**
- **Task Semplici**: PHI-3 Mini
- **Task Generali**: Llama2-7B-Q4
- **Task Complessi**: Mistral-7B-Q4

### **2. Ottimizzazione Prompt**
- Prompt brevi e specifici
- Evita contesto eccessivo
- Usa esempi concreti

### **3. Gestione Risorse**
- Monitora uso CPU/memoria
- Riduci task concorrenti
- Usa timeout appropriati

### **4. Fallback Strategy**
```python
# Esempio di fallback
models = ["phi3:mini", "llama2:7b-chat-q4_0", "mistral:7b-instruct-q4_0"]
for model in models:
    try:
        result = generate_with_model(model, prompt)
        if result:
            return result
    except:
        continue
```

## 📚 **Riferimenti**

### **Articoli Tecnici**
- [Open-Source LLMs for CPU](https://medium.com/gitconnected/open-source-llms-for-cpu-769a57bb98bd)
- [Small Language Model Inference on Arm CPUs](https://www.arcee.ai/blog/the-case-for-small-language-model-inference-on-arm-cpus)

### **Modelli Disponibili**
- **PHI-3**: Microsoft Research
- **Llama2**: Meta AI
- **Mistral**: Mistral AI

### **Strumenti**
- **Ollama**: Runtime locale
- **llama.cpp**: Ottimizzazioni CPU
- **Arm Kleidi**: Kernel ottimizzati

## 🎯 **Prossimi Passi**

1. **Testa i modelli**: `python test_fast_llms.py`
2. **Configura ottimizzazione**: Usa `background_config_cpu_optimized.json`
3. **Avvia Background Agent**: `./manage_background_agent.sh start`
4. **Monitora performance**: `./monitor_hardware.sh`
5. **Ottimizza prompt**: Adatta per velocità vs qualità

---

**💡 Suggerimento**: Inizia con PHI-3 Mini per la massima velocità, poi scala su modelli più grandi se necessario per qualità superiore. 