# Timeout e Monitoraggio - Crypto Futures LLM Trading

## 🕐 Gestione Timeout per Generazione Strategie

### ⏱️ **Timeout Ottimali per Modelli LLM**

Il sistema utilizza timeout intelligenti basati sul modello e sulla complessità del prompt:

#### **Configurazione Timeout per Modello**

| Modello | Prompt Semplice | Prompt Normale | Prompt Complesso |
|---------|----------------|----------------|------------------|
| **phi3** | 5 minuti | 10 minuti | 15 minuti |
| **llama2** | 10 minuti | 20 minuti | 30 minuti |
| **mistral** | 15 minuti | 30 minuti | 45 minuti |

#### **Calcolo Automatico della Complessità**

Il sistema analizza automaticamente la complessità del prompt:

```python
def estimate_prompt_complexity(prompt: str) -> str:
    length = len(prompt)
    has_code = "def " in prompt or "class " in prompt
    has_instructions = prompt.count("Includi") + prompt.count("Genera")
    
    if length < 200 and not has_code and has_instructions < 2:
        return "fast"
    elif length < 800 and has_instructions < 5:
        return "normal"
    else:
        return "complex"
```

### 🔧 **Implementazione nel GeneratorAgent**

```python
# Calcola timeout ottimale automaticamente
if timeout is None:
    complexity = estimate_prompt_complexity(prompt)
    timeout = get_optimal_timeout(model_to_use, complexity)
    print(f"⏱️ Timeout calcolato: {timeout}s per {model_to_use} ({complexity})")
```

### 📊 **Strategie di Fallback**

1. **Timeout Primario**: Usa il timeout calcolato per il modello
2. **Fallback Modello**: Se un modello fallisce, prova con modelli più veloci
3. **Fallback Strategia**: Se tutti i modelli falliscono, usa strategie predefinite

## 📊 Monitoraggio Backtest in Tempo Reale

### 🔍 **Sistema di Monitoraggio**

Il `BacktestMonitor` permette di monitorare i backtest anche quando sono in background:

#### **Funzionalità Principali**

- ✅ **Monitoraggio in tempo reale** dell'avanzamento
- ✅ **Log dettagliati** per ogni backtest
- ✅ **Stato progressivo** (loading, analyzing, backtesting, completed)
- ✅ **Gestione errori** e timeout
- ✅ **Interfaccia CLI** per controllo

### 🚀 **Utilizzo del Monitor**

#### **Avvio del Monitor**
```bash
# Avvia il monitor
./manage_backtest_monitor.sh start

# Controlla lo stato
./manage_backtest_monitor.sh status

# Visualizza log in tempo reale
./manage_backtest_monitor.sh logs
```

#### **Monitoraggio Attivo**
```bash
# Monitora backtest attivi in tempo reale
./manage_backtest_monitor.sh monitor
```

### 📈 **Stati del Backtest**

| Stato | Descrizione | Progresso |
|-------|-------------|-----------|
| **loading_data** | Caricamento dati storici | 10% |
| **analyzing** | Analisi indicatori | 30% |
| **backtesting** | Esecuzione backtest | 50% |
| **generating_report** | Generazione report | 80% |
| **completed** | Backtest completato | 100% |
| **error** | Errore durante l'esecuzione | - |

### 🔧 **Integrazione con Background Agent**

Il Background Agent può utilizzare il monitor per i backtest:

```python
from backtest_monitor import BacktestMonitor

class BackgroundAgent:
    def __init__(self):
        self.backtest_monitor = BacktestMonitor()
        self.backtest_monitor.start_monitoring()
    
    def backtest_strategy(self, strategy_name: str):
        # Avvia backtest con monitoraggio
        backtest_id = self.backtest_monitor.start_backtest_with_monitoring(
            strategy_name, 
            timerange="20240101-20241231"
        )
        
        # Il monitor gestisce automaticamente il processo
        return backtest_id
```

## 📋 **Comandi di Gestione**

### **Background Agent**
```bash
# Gestione agente principale
./manage_background_agent.sh start
./manage_background_agent.sh status
./manage_background_agent.sh logs
./manage_background_agent.sh stop
```

### **Backtest Monitor**
```bash
# Gestione monitor backtest
./manage_backtest_monitor.sh start
./manage_backtest_monitor.sh status
./manage_backtest_monitor.sh monitor
./manage_backtest_monitor.sh logs
./manage_backtest_monitor.sh stop
```

## 🎯 **Best Practices**

### **Per i Timeout LLM**

1. **Usa timeout automatici**: Lascia che il sistema calcoli il timeout ottimale
2. **Monitora i fallback**: Controlla i log per vedere se vengono usati modelli di fallback
3. **Ottimizza i prompt**: Prompt più concisi = timeout più brevi
4. **Usa modelli veloci**: phi3 per operazioni semplici, mistral per complesse

### **Per il Monitoraggio Backtest**

1. **Avvia sempre il monitor**: Prima di eseguire backtest
2. **Controlla i log**: Monitora l'avanzamento in tempo reale
3. **Gestisci gli errori**: Il monitor rileva automaticamente i fallimenti
4. **Pulisci i risultati**: Rimuovi i backtest completati dalla memoria

## 🔍 **Troubleshooting**

### **Timeout LLM Frequenti**

```bash
# Controlla se Ollama è in esecuzione
ps aux | grep ollama

# Controlla i modelli disponibili
ollama list

# Testa un modello specifico
python -c "from llm_utils import test_model_availability; print(test_model_availability('phi3'))"
```

### **Backtest che Non Partono**

```bash
# Controlla lo stato del monitor
./manage_backtest_monitor.sh status

# Controlla i log del monitor
./manage_backtest_monitor.sh logs

# Riavvia il monitor
./manage_backtest_monitor.sh restart
```

### **Backtest Bloccati**

```bash
# Ferma tutti i processi Freqtrade
pkill -f freqtrade

# Pulisci i file temporanei
rm -rf user_data/data/*.json

# Riavvia il monitor
./manage_backtest_monitor.sh restart
```

## 📝 **Riepilogo**

### **Timeout Intelligenti**
- ✅ Calcolo automatico basato su modello e complessità
- ✅ Fallback automatico su modelli più veloci
- ✅ Configurazione ottimizzata per ogni modello LLM

### **Monitoraggio Real-time**
- ✅ Monitoraggio continuo dei backtest in background
- ✅ Log dettagliati e stato progressivo
- ✅ Gestione automatica degli errori
- ✅ Interfaccia CLI completa

### **Integrazione Completa**
- ✅ Background Agent con timeout ottimali
- ✅ Backtest Monitor per controllo real-time
- ✅ Gestione robusta degli errori
- ✅ Logging completo per debugging 