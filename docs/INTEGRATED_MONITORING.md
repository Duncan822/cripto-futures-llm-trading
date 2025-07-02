# Monitoraggio Integrato - Background Agent

## 🎯 **Integrazione Completata**

Il **BacktestMonitor** è stato integrato direttamente nel **Background Agent**, rendendo il monitoraggio dei backtest più comodo e accessibile attraverso un unico menu.

## 📋 **Nuovi Comandi Disponibili**

### **Menu Principale**
```bash
./manage_background_agent.sh [comando]
```

| Comando | Descrizione |
|---------|-------------|
| `start` | Avvia l'agente con monitoraggio automatico |
| `stop` | Ferma l'agente e il monitoraggio |
| `status` | Stato completo con info backtest |
| `logs` | Log dell'agente in tempo reale |
| `backtest` | Monitora backtest attivi |
| `backtest-logs` | Log backtest in tempo reale |
| `config` | Modifica configurazione |
| `restart` | Riavvia l'agente |

## 🔧 **Funzionalità Integrate**

### **1. Avvio Automatico del Monitoraggio**
```python
def start(self):
    # Avvia il monitoraggio dei backtest se disponibile
    if self.backtest_monitor:
        self.start_backtest_monitoring()
```

### **2. Backtest con Monitoraggio Automatico**
```python
def backtest_strategy(self, strategy_name: str):
    # Usa il monitor se disponibile
    if self.backtest_monitor:
        backtest_id = self.backtest_monitor.start_backtest_with_monitoring(
            strategy_name, 
            timerange="20240101-20241231"
        )
```

### **3. Stato Completo**
```bash
./manage_background_agent.sh status
```

**Output includerà:**
- Stato dell'agente
- Strategie totali e attive
- **Backtest attivi e completati**
- Log disponibili
- Comandi utili

## 📊 **Monitoraggio Backtest**

### **Comando: `backtest`**
```bash
./manage_background_agent.sh backtest
```

**Mostra:**
- 🔄 Backtest attivi (ultimi 10 minuti)
- 📋 Lista backtest recenti con timestamp
- ✅ Backtest completati
- 🔧 Comandi utili

### **Comando: `backtest-logs`**
```bash
./manage_background_agent.sh backtest-logs
```

**Funzionalità:**
- 📄 Visualizza log del backtest più recente
- 🔄 Aggiornamento in tempo reale
- 💡 Premi Ctrl+C per uscire
- 📁 Mostra tutti i log disponibili

## 🚀 **Utilizzo Pratico**

### **Scenario 1: Avvio Completo**
```bash
# 1. Avvia l'agente (include monitoraggio automatico)
./manage_background_agent.sh start

# 2. Controlla lo stato completo
./manage_background_agent.sh status

# 3. Monitora backtest attivi
./manage_background_agent.sh backtest

# 4. Visualizza log backtest in tempo reale
./manage_background_agent.sh backtest-logs
```

### **Scenario 2: Monitoraggio Continuo**
```bash
# In un terminale: avvia l'agente
./manage_background_agent.sh start

# In un altro terminale: monitora i backtest
./manage_background_agent.sh backtest-logs

# In un terzo terminale: controlla lo stato
./manage_background_agent.sh status
```

## 📁 **Struttura File**

```
crypto-futures-llm-trading/
├── logs/
│   ├── background_agent_*.log    # Log dell'agente
│   └── backtests/                # Log dei backtest
│       └── strategy_*.log        # Log per ogni backtest
├── backtest_results/             # Risultati completati
│   └── strategy_*.json           # File JSON con risultati
├── background_agent.py           # Agente principale
├── backtest_monitor.py           # Monitor integrato
└── manage_background_agent.sh    # Script di gestione
```

## 🔍 **Vantaggi dell'Integrazione**

### **✅ Comodità**
- Un solo script per tutto
- Menu unificato
- Comandi intuitivi

### **✅ Automazione**
- Monitoraggio automatico all'avvio
- Gestione automatica dei backtest
- Log centralizzati

### **✅ Monitoraggio Real-time**
- Stato backtest in tempo reale
- Log dettagliati per ogni backtest
- Progresso visuale

### **✅ Gestione Errori**
- Fallback automatico se il monitor non è disponibile
- Gestione robusta degli errori
- Logging completo

## 🎯 **Best Practices**

### **Per l'Utilizzo**
1. **Usa sempre `start`**: Avvia tutto automaticamente
2. **Monitora con `status`**: Controlla lo stato completo
3. **Segui i backtest**: Usa `backtest-logs` per monitoraggio real-time
4. **Gestisci gli errori**: Controlla i log se qualcosa non funziona

### **Per il Debugging**
1. **Controlla lo stato**: `./manage_background_agent.sh status`
2. **Visualizza log**: `./manage_background_agent.sh logs`
3. **Monitora backtest**: `./manage_background_agent.sh backtest`
4. **Log backtest**: `./manage_background_agent.sh backtest-logs`

## 🔧 **Configurazione**

### **File: `background_config.json`**
```json
{
  "auto_validation": true,
  "auto_backtest": true,
  "max_strategies": 50,
  "generation_interval": 3600,
  "backtest_interval": 7200,
  "cleanup_old_strategies": true,
  "strategy_types": ["volatility", "scalping", "breakout", "momentum"],
  "models": ["phi3", "llama2", "mistral"],
  "min_backtest_score": 0.1,
  "max_concurrent_tasks": 3
}
```

## 📝 **Riepilogo**

### **Integrazione Completata**
- ✅ BacktestMonitor integrato nel BackgroundAgent
- ✅ Menu unificato con comandi intuitivi
- ✅ Monitoraggio automatico all'avvio
- ✅ Gestione completa dei backtest

### **Comandi Principali**
- `./manage_background_agent.sh start` - Avvia tutto
- `./manage_background_agent.sh status` - Stato completo
- `./manage_background_agent.sh backtest` - Monitora backtest
- `./manage_background_agent.sh backtest-logs` - Log real-time

### **Vantaggi**
- 🎯 **Più comodo**: Un solo script per tutto
- 🔄 **Automatico**: Monitoraggio integrato
- 📊 **Real-time**: Stato e log in tempo reale
- 🛡️ **Robusto**: Gestione errori e fallback 