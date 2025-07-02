# 🚀 Crypto Futures LLM Trading - Sistema Completo

Framework modulare per la creazione, generazione e test di strategie di trading su futures cripto, con la collaborazione di agenti LLM locali e **orchestrazione automatica completa**.

## 📋 **Indice**
- [🎯 Panoramica](#-panoramica)
- [🚀 Setup Rapido](#-setup-rapido)
- [📁 Struttura del Progetto](#-struttura-del-progetto)
- [🤖 Agenti e Componenti](#-agenti-e-componenti)
- [🧠 Modelli LLM Supportati](#-modelli-llm-supportati)
- [⚙️ Configurazione](#️-configurazione)
- [🛠️ Utilizzo](#️-utilizzo)
- [📊 Monitoraggio e Gestione](#-monitoraggio-e-gestione)
- [🔧 Troubleshooting](#-troubleshooting)
- [📚 Documentazione](#-documentazione)

## 🎯 **Panoramica**

### ✅ **Funzionalità Implementate**
- **🤖 Background Agent**: Orchestrazione automatica completa del ciclo di vita strategie
- **🧠 LLM Locali**: Supporto per Cogito, PHI-3, Llama2, Mistral con ottimizzazioni CPU
- **📈 Backtesting Automatico**: Test periodico su dati storici con monitoraggio real-time
- **🔧 Validazione Automatica**: Controllo sintassi e correzione errori strategie
- **📊 Optimizer Agent**: Analisi e ottimizzazione risultati con LLM
- **🔄 Gestione Intelligente**: Pulizia automatica strategie vecchie/scarse
- **📝 Sistema Metadati**: Tracciamento completo strategie generate
- **⚡ Performance Ottimizzate**: Timeout adattivi e gestione risorse CPU

### 🎯 **Caratteristiche Avanzate**
- **Deep Thinking**: Subroutine di ragionamento avanzato con Cogito
- **Multi-Session Support**: Gestione multiple sessioni e controllo processi
- **Persistenza**: Agente rimane attivo dopo disconnessione
- **Real-time Monitoring**: Monitoraggio backtest in tempo reale
- **Hardware Monitoring**: Controllo risorse sistema
- **Fallback Strategy**: Modelli di backup per massima affidabilità

## 🚀 **Setup Rapido**

### 1. **Installazione Completa**
```bash
# Clona il repository (se non già fatto)
git clone <repository-url>
cd crypto-futures-llm-trading

# Esegui il setup automatico
./setup_freqtrade.sh
```

### 2. **Installazione Modelli LLM Veloce**
```bash
# Installa modelli ottimizzati per CPU
./install_fast_models.sh

# Oppure installazione manuale
ollama pull cogito:3b
ollama pull cogito:8b
ollama pull phi3:mini
ollama pull llama2:7b-chat-q4_0
ollama pull mistral:7b-instruct-q4_0
```

### 3. **Configurazione Ottimizzata**
```bash
# Usa configurazione con Cogito (raccomandato)
cp background_config_with_cogito.json background_config.json

# Oppure configurazione CPU ottimizzata
cp background_config_cpu_optimized.json background_config.json
```

### 4. **Avvio Sistema**
```bash
# Avvia Background Agent
./manage_background_agent.sh start

# Controlla stato
./manage_background_agent.sh status
```

## 📁 **Struttura del Progetto**

```
crypto-futures-llm-trading/
├── 🤖 AGENTI PRINCIPALI
│   ├── background_agent.py          # 🆕 Orchestratore automatico completo
│   ├── backtest_monitor.py          # 🆕 Monitoraggio backtest real-time
│   └── agents/
│       ├── generator.py             # Generatore strategie con LLM
│       ├── optimizer.py             # 🆕 Ottimizzatore risultati
│       ├── strategy_converter.py    # Convertitore e validatore
│       ├── ollama_agent.py          # Interfaccia modelli locali
│       └── reviewer.py              # ❌ OBSOLETO (sostituito)
│
├── ⚙️ CONFIGURAZIONE
│   ├── background_config.json       # Configurazione principale
│   ├── background_config_with_cogito.json  # 🆕 Con Cogito
│   ├── background_config_cpu_optimized.json # 🆕 CPU ottimizzata
│   ├── user_data/config.json        # Configurazione Freqtrade
│   └── strategies_metadata.json     # 🆕 Metadati strategie
│
├── 🛠️ GESTIONE E MONITORAGGIO
│   ├── manage_background_agent.sh   # 🆕 Gestione completa agente
│   ├── session_manager.sh           # 🆕 Gestione sessioni
│   ├── monitor_hardware.sh          # 🆕 Monitoraggio hardware
│   └── global_session_manager.sh    # 🆕 Gestione globale
│
├── 🧪 TEST E VALIDAZIONE
│   ├── test_complete_system.py      # 🆕 Test sistema completo
│   ├── test_cogito_models.py        # 🆕 Test modelli Cogito
│   ├── test_fast_llms.py            # 🆕 Test LLM veloci
│   ├── test_optimizer.py            # Test Optimizer Agent
│   └── quick_llm_test.py            # Test rapido LLM
│
├── 📚 DOCUMENTAZIONE
│   ├── README_COMPLETE.md           # 🆕 Questo file
│   ├── COGITO_GUIDE.md              # 🆕 Guida Cogito
│   ├── FAST_LLM_GUIDE.md            # 🆕 Guida LLM veloci
│   ├── BACKGROUND_AGENT_README.md   # Guida Background Agent
│   ├── INTEGRATED_MONITORING.md     # 🆕 Monitoraggio integrato
│   ├── MULTIPLE_SESSIONS.md         # 🆕 Gestione sessioni
│   ├── PERSISTENCE.md               # 🆕 Persistenza
│   ├── TIMEOUT_AND_MONITORING.md    # 🆕 Timeout e monitoraggio
│   └── HARDWARE_RISKS.md            # 🆕 Rischi hardware
│
├── 📊 DATI E RISULTATI
│   ├── strategies/                  # Strategie generate
│   ├── backtest_results/            # Risultati backtest
│   ├── logs/                        # Log sistema
│   └── data/                        # Dati storici
│
└── 🔧 UTILITY
    ├── freqtrade_utils.py           # Utility Freqtrade
    ├── llm_utils.py                 # Utility LLM
    ├── setup_freqtrade.sh           # Setup automatico
    └── requirements.txt             # Dipendenze Python
```

## 🤖 **Agenti e Componenti**

### 🎯 **Background Agent (Principale)**
Il cuore del sistema che orchestra automaticamente tutto il ciclo di vita delle strategie.

**Funzionalità:**
- 🔄 **Generazione Automatica**: Strategie generate periodicamente con nomi univoci
- ✅ **Validazione Automatica**: Controllo sintassi e correzione errori
- 📊 **Backtest Automatico**: Test periodico su dati storici
- 🧹 **Gestione Intelligente**: Pulizia automatica strategie vecchie/scarse
- 📈 **Monitoraggio Continuo**: Tracciamento performance e metadati

**Comandi:**
```bash
./manage_background_agent.sh start      # Avvia agente
./manage_background_agent.sh stop       # Ferma agente
./manage_background_agent.sh status     # Controlla stato
./manage_background_agent.sh logs       # Visualizza log
./manage_background_agent.sh restart    # Riavvia agente
./manage_background_agent.sh backtest   # Monitora backtest
./manage_background_agent.sh config     # Modifica configurazione
```

### 🧠 **Optimizer Agent**
Analizza i risultati dei backtest e suggerisce miglioramenti usando LLM.

**Funzionalità:**
- 📊 **Analisi Risultati**: Interpretazione automatica backtest
- 🎯 **Suggerimenti Miglioramenti**: Ottimizzazioni basate su LLM
- 📈 **Metriche Performance**: Analisi dettagliata indicatori
- 🔧 **Ottimizzazione Parametri**: Suggerimenti parametri migliori

**Utilizzo:**
```bash
python test_optimizer.py
```

### 📊 **Backtest Monitor**
Monitoraggio real-time dei backtest in esecuzione.

**Funzionalità:**
- 🔍 **Monitoraggio Real-time**: Controllo stato backtest attivi
- 📝 **Log Streaming**: Visualizzazione log in tempo reale
- ⏱️ **Gestione Timeout**: Controllo automatico durata
- 📊 **Metriche Performance**: Tracciamento risorse utilizzate

## 🧠 **Modelli LLM Supportati**

### 🏆 **Classifica Performance**
1. **Cogito 3B**: 3.5s ⚡ (Più veloce + Deep Thinking)
2. **PHI-3 Mini**: 4.1s 🚀 (Fallback veloce)
3. **Cogito 8B**: 8.7s 📊 (Qualità superiore)
4. **Mistral-7B-Q4**: 13.3s 🧠 (Stabilità)
5. **Llama2-7B-Q4**: 16.4s 🔄 (Compatibilità)

### 🧠 **Cogito (Raccomandato)**
- **Deep Thinking**: Subroutine di ragionamento avanzato
- **Hybrid Reasoning**: Capacità di ragionamento ibrido
- **IDA Technology**: Iterated Distillation and Amplification
- **Coding Optimized**: Ottimizzato per generazione codice
- **STEM Focus**: Eccellente per analisi tecniche

**Attivazione Deep Thinking:**
```bash
ollama run cogito:3b "Enable deep thinking subroutine. Analizza..."
```

### ⚡ **PHI-3 Mini (Fallback)**
- **Velocità Massima**: 4.1s per prompt semplice
- **Memoria Ottimizzata**: ~2GB
- **Stabilità**: Raramente timeout
- **Ideale per**: Generazione strategie veloce

### 📊 **Configurazione Modelli**
```json
{
  "models": ["cogito:3b", "phi3:mini", "cogito:8b", "mistral:7b-instruct-q4_0"],
  "model_selection": {
    "fast_generation": "cogito:3b",
    "quality_analysis": "cogito:8b",
    "optimization": "cogito:3b",
    "fallback": "phi3:mini"
  }
}
```

## ⚙️ **Configurazione**

### 🎯 **Configurazione Principale**
Il file `background_config.json` controlla l'orchestrazione automatica:

```json
{
  "auto_validation": true,           // Validazione automatica
  "auto_backtest": true,             // Backtest automatico
  "max_strategies": 30,              // Limite strategie
  "generation_interval": 7200,       // Generazione ogni 2 ore
  "backtest_interval": 14400,        // Backtest ogni 4 ore
  "cleanup_old_strategies": true,    // Pulizia automatica
  "strategy_types": ["volatility", "scalping", "momentum", "breakout"],
  "models": ["cogito:3b", "phi3:mini", "cogito:8b"],
  "min_backtest_score": 0.1,         // Punteggio minimo
  "max_strategy_age_days": 20,       // Età massima strategie
  "cpu_optimization": {
    "enable": true,
    "max_memory_usage": "4GB",
    "threads": 4,
    "timeout_seconds": 120
  }
}
```

### 🧠 **Configurazione Cogito**
```json
{
  "cogito_features": {
    "enable_deep_thinking": true,
    "deep_thinking_prompt": "Enable deep thinking subroutine.",
    "use_for_complex_tasks": true
  }
}
```

### 📊 **Configurazione Trading**
Il file `user_data/config.json` contiene:
- **Exchange**: Binance Futures
- **Trading Mode**: Futures con margine isolato
- **Timeframe**: 5m
- **Pairs**: BTC/USDT, ETH/USDT, BNB/USDT, etc.
- **Risk Management**: Stoploss dinamico, trailing stop

## 🛠️ **Utilizzo**

### 🚀 **Avvio Sistema Completo**
```bash
# 1. Setup iniziale
./setup_freqtrade.sh
./install_fast_models.sh

# 2. Configurazione
cp background_config_with_cogito.json background_config.json

# 3. Avvio Background Agent
./manage_background_agent.sh start

# 4. Monitoraggio
./manage_background_agent.sh logs
```

### 📊 **Monitoraggio e Controllo**
```bash
# Controlla stato sistema
./manage_background_agent.sh status

# Visualizza log real-time
./manage_background_agent.sh logs

# Monitora backtest attivi
./manage_background_agent.sh backtest

# Controlla risorse hardware
./monitor_hardware.sh

# Gestione sessioni multiple
./session_manager.sh status
```

### 🧪 **Test e Validazione**
```bash
# Test sistema completo
python test_complete_system.py

# Test modelli Cogito
python test_cogito_models.py

# Test LLM veloci
python test_fast_llms.py

# Test Optimizer Agent
python test_optimizer.py
```

### 📈 **Backtest Manuale**
```bash
# Backtest strategia specifica
./run_backtest.sh

# Hyperopt strategia
./run_hyperopt.sh

# Download dati storici
freqtrade download-data --config user_data/config.json \
  --pairs BTC/USDT:USDT ETH/USDT:USDT \
  --timeframe 5m --timerange 20240101-20241231
```

### 🤖 **Trading (Dry-Run)**
```bash
# Avvia bot in modalità dry-run
./start_bot.sh
```

## 📊 **Monitoraggio e Gestione**

### 🔍 **Comandi di Monitoraggio**
```bash
# Stato Background Agent
./manage_background_agent.sh status

# Log real-time
./manage_background_agent.sh logs

# Backtest attivi
./manage_background_agent.sh backtest

# Log backtest
./manage_background_agent.sh backtest-logs

# Risorse hardware
./monitor_hardware.sh

# Sessioni multiple
./session_manager.sh status
```

### 📈 **Metriche Sistema**
- **Strategie Generate**: Numero totale strategie create
- **Strategie Valide**: Percentuale strategie validate con successo
- **Performance Media**: Punteggio backtest medio
- **Strategie Attive**: Numero strategie in uso
- **Uptime**: Tempo di funzionamento continuo
- **Uso CPU/Memoria**: Monitoraggio risorse

### 📊 **Metriche Backtest**
- **Total Profit**: Profitto totale
- **Sharpe Ratio**: Rapporto rischio/rendimento
- **Max Drawdown**: Massima perdita consecutiva
- **Win Rate**: Percentuale trade vincenti
- **Total Trades**: Numero totale di trade

## 🔧 **Troubleshooting**

### ❌ **Problemi Comuni**

#### **1. Background Agent Non Avvia**
```bash
# Controlla dipendenze
pip install -r requirements.txt

# Controlla Ollama
ollama list

# Controlla log
tail -f logs/background_agent_*.log
```

#### **2. Modelli LLM Lenti**
```bash
# Controlla risorse
./monitor_hardware.sh

# Usa modelli più piccoli
cp background_config_cpu_optimized.json background_config.json

# Riavvia agente
./manage_background_agent.sh restart
```

#### **3. Timeout Modelli**
```bash
# Aumenta timeout in configurazione
"timeout_seconds": 180

# Usa modelli più veloci
"models": ["cogito:3b", "phi3:mini"]
```

#### **4. Memoria Insufficiente**
```bash
# Riduci task concorrenti
"max_concurrent_tasks": 1

# Usa modelli più piccoli
"models": ["cogito:3b", "phi3:mini"]
```

#### **5. Strategie Non Generate**
```bash
# Controlla log generazione
./manage_background_agent.sh logs

# Verifica configurazione
cat background_config.json

# Test manuale generazione
python -c "from agents.generator import StrategyGenerator; sg = StrategyGenerator(); sg.generate_strategy()"
```

### 🔍 **Diagnostica Avanzata**
```bash
# Test completo sistema
python test_complete_system.py

# Test modelli specifici
python test_cogito_models.py

# Controlla processi
ps aux | grep -E "(background_agent|freqtrade|ollama)"

# Controlla porte
netstat -tlnp | grep -E "(11434|5000)"
```

## 📚 **Documentazione**

### 📖 **Guide Principali**
- [COGITO_GUIDE.md](COGITO_GUIDE.md) - Guida completa modelli Cogito
- [FAST_LLM_GUIDE.md](FAST_LLM_GUIDE.md) - Guida LLM veloci
- [BACKGROUND_AGENT_README.md](BACKGROUND_AGENT_README.md) - Guida Background Agent
- [INTEGRATED_MONITORING.md](INTEGRATED_MONITORING.md) - Monitoraggio integrato
- [MULTIPLE_SESSIONS.md](MULTIPLE_SESSIONS.md) - Gestione sessioni
- [PERSISTENCE.md](PERSISTENCE.md) - Persistenza sistema
- [TIMEOUT_AND_MONITORING.md](TIMEOUT_AND_MONITORING.md) - Timeout e monitoraggio
- [HARDWARE_RISKS.md](HARDWARE_RISKS.md) - Rischi hardware

### 🔗 **Riferimenti Esterni**
- [Cogito su Ollama](https://ollama.com/library/cogito:8b)
- [DeepCogito Blog](https://www.deepcogito.com/research/cogito-v1-preview)
- [Freqtrade Documentation](https://www.freqtrade.io/en/latest/)
- [Ollama Documentation](https://ollama.ai/docs)

### 📊 **File di Configurazione**
- `background_config.json` - Configurazione principale
- `background_config_with_cogito.json` - Con modelli Cogito
- `background_config_cpu_optimized.json` - CPU ottimizzata
- `user_data/config.json` - Configurazione Freqtrade

## 🎯 **Prossimi Passi**

### 🚀 **Sviluppi Futuri**
1. **Dashboard Web**: Interfaccia web per monitoraggio
2. **Trading Reale**: Integrazione API exchange
3. **Machine Learning**: Modelli ML per predizioni
4. **Alert System**: Notifiche eventi critici
5. **Portfolio Management**: Gestione multi-strategia avanzata

### 🔧 **Ottimizzazioni Suggerite**
1. **Test Deep Thinking**: Verifica funzionalità ragionamento
2. **Ottimizza Prompt**: Adatta per massima efficienza
3. **Monitora Performance**: Traccia velocità e qualità
4. **Backtest Completi**: Esegui backtest su strategie generate
5. **Hyperopt**: Ottimizzazione parametri automatica

---

## 📞 **Supporto**

Per problemi o domande:
1. Controlla la documentazione nelle guide specifiche
2. Verifica i log: `./manage_background_agent.sh logs`
3. Esegui test diagnostici: `python test_complete_system.py`
4. Controlla risorse: `./monitor_hardware.sh`

---

**🎉 Il sistema è ora completamente funzionale e ottimizzato per CPU con i modelli LLM più avanzati disponibili!** 