# 🧠 Guida Modelli Cogito per Trading

Guida completa per l'uso dei modelli [Cogito](https://ollama.com/library/cogito:8b) di DeepCogito nel progetto crypto-futures-llm-trading.

## 🚀 **Panoramica Cogito**

### 🎯 **Caratteristiche Principali**
- **Hybrid Reasoning Models**: Capacità di ragionamento ibrido
- **Iterated Distillation and Amplification (IDA)**: Tecnica di auto-miglioramento
- **Optimizzato per**: Coding, STEM, instruction following
- **Multilingue**: Supporto per 30+ lingue
- **Context Length**: 128k token
- **Deep Thinking**: Subroutine di ragionamento avanzato

### 📊 **Modelli Disponibili**
- **Cogito 3B**: 2.2GB - Ultra veloce, ottimo per task semplici
- **Cogito 8B**: 4.9GB - Bilanciato, ottimo per analisi complesse
- **Cogito 14B**: ~7GB - Alta qualità, per task specializzati
- **Cogito 32B**: ~20GB - Massima qualità, risorse intensive
- **Cogito 70B**: ~40GB - Top performance, richiede GPU

## 📈 **Risultati Test Performance**

### 🏆 **Classifica Velocità (Prompt Semplice)**
1. **Cogito 3B**: 3.5s ⚡ (Più veloce)
2. **PHI-3 Mini**: 7.1s 🚀
3. **Cogito 8B**: 8.7s 📊
4. **Mistral-7B-Q4**: 13.0s 🧠
5. **Llama2-7B-Q4**: 17.9s 🔄

### 🎯 **Analisi Qualità (Strategia Trading)**
- **Cogito 3B**: 43 parole, 24.8s - Ottimo compromesso
- **Cogito 8B**: Timeout 60s - Troppo lento per task complessi
- **PHI-3 Mini**: Timeout 60s - Limitato per strategie complesse

## 🧠 **Deep Thinking Subroutine**

### ⚙️ **Attivazione**
```bash
# Metodo 1: Prompt diretto
ollama run cogito:3b "Enable deep thinking subroutine. Analizza..."

# Metodo 2: API
curl http://localhost:11434/api/chat -d '{
  "model": "cogito:3b",
  "messages": [
    {
      "role": "system", 
      "content": "Enable deep thinking subroutine."
    },
    {
      "role": "user",
      "content": "Analizza..."
    }
  ]
}'
```

### 📝 **Formato Risposta**
Quando attivato, Cogito usa il formato:
```
<think>
Ragionamento interno del modello...
</think>

Risposta finale all'utente...
```

## 🛠️ **Configurazione Ottimizzata**

### **Configurazione Con Cogito**
```json
{
  "models": ["cogito:3b", "phi3:mini", "cogito:8b", "mistral:7b-instruct-q4_0"],
  "model_selection": {
    "fast_generation": "cogito:3b",
    "quality_analysis": "cogito:8b", 
    "optimization": "cogito:3b",
    "fallback": "phi3:mini"
  },
  "cogito_features": {
    "enable_deep_thinking": true,
    "deep_thinking_prompt": "Enable deep thinking subroutine.",
    "use_for_complex_tasks": true
  }
}
```

### **Attivazione**
```bash
# Usa configurazione con Cogito
cp background_config_with_cogito.json background_config.json

# Riavvia Background Agent
./manage_background_agent.sh restart
```

## 🎯 **Strategie di Utilizzo**

### **1. Generazione Veloce (Cogito 3B)**
```python
# Per strategie semplici e veloci
prompt = "Genera strategia scalping BTC/USDT in 2 righe"
model = "cogito:3b"  # 3.5s di risposta
```

### **2. Analisi Complessa (Cogito 3B + Deep Thinking)**
```python
# Per analisi di mercato e ottimizzazione
prompt = """Enable deep thinking subroutine.
Analizza: quale strategia è più efficace per crypto futures?
Considera: volatilità, liquidità, timeframe."""
model = "cogito:3b"  # Con ragionamento avanzato
```

### **3. Fallback (PHI-3 Mini)**
```python
# Quando Cogito è troppo lento
if cogito_timeout:
    model = "phi3:mini"  # Fallback veloce
```

## 📊 **Benchmark e Confronti**

### **vs Altri Modelli**
| Modello | Velocità | Qualità | Memoria | Specialità |
|---------|----------|---------|---------|------------|
| **Cogito 3B** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Ragionamento |
| **PHI-3 Mini** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Velocità |
| **Cogito 8B** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Qualità |
| **Mistral-7B** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | Stabilità |

### **Punti di Forza Cogito**
- ✅ **Ragionamento Avanzato**: Deep thinking subroutine
- ✅ **Velocità**: 3B è il più veloce testato
- ✅ **Qualità**: Ottima per task complessi
- ✅ **Coding**: Ottimizzato per generazione codice
- ✅ **STEM**: Eccellente per analisi tecniche

### **Limitazioni**
- ❌ **8B Lento**: Timeout per task complessi
- ❌ **Memoria**: 8B richiede più RAM
- ❌ **Stabilità**: Occasionalmente timeout

## 🔧 **Integrazione nel Progetto**

### **Background Agent**
Il Background Agent userà automaticamente:
- **Cogito 3B**: Per generazione strategie veloce
- **Cogito 3B + Deep Thinking**: Per ottimizzazione
- **PHI-3 Mini**: Come fallback

### **Optimizer Agent**
L'Optimizer Agent può sfruttare:
- **Deep Thinking**: Per analisi risultati backtest
- **Ragionamento**: Per suggerimenti miglioramenti
- **Coding**: Per ottimizzazione parametri

### **Prompt Engineering**
```python
# Prompt ottimizzato per Cogito
def create_cogito_prompt(task_type, complexity):
    if complexity == "high":
        return f"Enable deep thinking subroutine. {task_type}"
    else:
        return task_type
```

## 🚀 **Best Practices**

### **1. Selezione Modello**
- **Task Semplici**: Cogito 3B
- **Task Complessi**: Cogito 3B + Deep Thinking
- **Fallback**: PHI-3 Mini
- **Qualità Massima**: Cogito 8B (se tempo disponibile)

### **2. Gestione Timeout**
```python
# Timeout adattivi
timeouts = {
    "cogito:3b": 30,
    "cogito:8b": 60,
    "phi3:mini": 30
}
```

### **3. Prompt Ottimizzati**
- Usa "Enable deep thinking subroutine." per task complessi
- Prompt brevi per velocità massima
- Specifica formato output per consistenza

### **4. Monitoraggio Performance**
```bash
# Monitora uso risorse
./monitor_hardware.sh

# Controlla log
./manage_background_agent.sh logs
```

## 📚 **Riferimenti**

### **Documentazione Ufficiale**
- [Cogito su Ollama](https://ollama.com/library/cogito:8b)
- [DeepCogito Blog](https://www.deepcogito.com/research/cogito-v1-preview)
- [Hugging Face](https://huggingface.co/collections/deepcogito/cogito-v1-preview-67eb105721081abe4ce2ee53)

### **Articoli Tecnici**
- [How to Run Cogito v1 Preview Locally with Ollama](https://apidog.com/blog/run-deep-cogito-locally-with-ollama/)

## 🎯 **Prossimi Passi**

1. **Testa Deep Thinking**: Verifica funzionalità ragionamento
2. **Ottimizza Prompt**: Adatta per massima efficienza
3. **Monitora Performance**: Traccia velocità e qualità
4. **Integra nel Workflow**: Usa per ottimizzazione strategie

---

**💡 Suggerimento**: Cogito 3B è il miglior compromesso velocità/qualità per il tuo progetto. Usa il deep thinking per task complessi e PHI-3 Mini come fallback veloce. 