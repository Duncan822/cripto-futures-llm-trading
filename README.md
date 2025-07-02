# Crypto Futures LLM Trading System

Un sistema completo per l'automazione della generazione, validazione, backtesting e ottimizzazione di strategie di trading su futures crypto utilizzando Large Language Models (LLMs) e Freqtrade.

## 🚀 Panoramica del Progetto

Questo progetto implementa un sistema end-to-end per il trading automatizzato su futures crypto che combina:

- **Generazione Automatica di Strategie**: Utilizzo di LLMs per creare strategie di trading basate su prompt specializzati
- **Validazione e Backtesting**: Sistema integrato di test e validazione delle strategie
- **Ottimizzazione Automatica**: Hyperopt automatizzato per ottimizzare i parametri delle strategie
- **Monitoraggio in Tempo Reale**: Sistema di monitoraggio e gestione delle operazioni
- **Persistenza e Robustezza**: Background Agent che persiste anche dopo la disconnessione

## 📁 Struttura del Progetto

```
crypto-futures-llm-trading/
├── agents/                     # Agenti AI per generazione e ottimizzazione
│   ├── generator.py           # Generatore di strategie con LLMs
│   ├── optimizer.py           # Ottimizzatore automatico
│   ├── hyperopt_optimizer.py  # Hyperopt integrato
│   └── strategy_converter.py  # Convertitore di strategie
├── prompts/                   # Prompt specializzati per LLMs
│   ├── improved_futures_prompts.py
│   └── futures_strategy_prompt.py
├── strategies/                # Strategie generate
├── background_agent.py        # Agente di background principale
├── manage_background_agent.sh # Script di gestione
├── backtest_monitor.py        # Monitor di backtest integrato
├── docs/                      # Documentazione
└── user_data/                 # Configurazione Freqtrade
```

## 🛠️ Componenti Principali

### 1. Background Agent
- **File**: `background_agent.py`
- **Gestione**: `manage_background_agent.sh`
- **Funzionalità**:
  - Gestione completa del ciclo di vita delle strategie
  - Monitoraggio in tempo reale dei backtest
  - Persistenza anche dopo disconnessione
  - Timeout intelligenti per LLMs

### 2. Sistema di Generazione Strategie
- **Agente**: `agents/generator.py`
- **Prompt**: `prompts/improved_futures_prompts.py`
- **Caratteristiche**:
  - Generazione basata su LLMs (Ollama)
  - Prompt specializzati per futures
  - Validazione automatica del codice

### 3. Sistema di Ottimizzazione
- **Ottimizzatore**: `agents/optimizer.py`
- **Hyperopt**: `agents/hyperopt_optimizer.py`
- **Funzionalità**:
  - Ottimizzazione automatica dei parametri
  - Confronto tra strategie
  - Selezione delle migliori configurazioni

### 4. Monitor di Backtest Integrato
- **File**: `backtest_monitor.py`
- **Gestione**: `manage_backtest_monitor.sh`
- **Caratteristiche**:
  - Monitoraggio in tempo reale
  - Logs accessibili via comando
  - Gestione di multiple sessioni

## 🚀 Quick Start

### 1. Setup Iniziale
```bash
# Clona il repository
git clone <repository-url>
cd crypto-futures-llm-trading

# Setup Freqtrade
./setup_freqtrade.sh

# Setup Ollama
./setup_ollama.sh

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Avvio del Background Agent
```bash
# Avvia l'agente
./manage_background_agent.sh start

# Verifica lo stato
./manage_background_agent.sh status

# Visualizza logs
./manage_background_agent.sh logs
```

### 3. Gestione delle Strategie
```bash
# Genera nuove strategie
./manage_background_agent.sh generate

# Esegui backtest
./manage_background_agent.sh backtest

# Ottimizza strategie
./manage_background_agent.sh optimize
```

## 📊 Funzionalità Avanzate

### Monitoraggio Hardware
- **Script**: `monitor_hardware.sh`
- **Monitoraggio**: CPU, RAM, GPU, temperatura
- **Avvisi**: Rischio di sovraccarico

### Gestione Sessioni Multiple
- **Script**: `session_manager.sh`
- **Funzionalità**: Gestione di multiple connessioni
- **Sicurezza**: Lock file per evitare conflitti

### Timeout Intelligenti
- **Calcolo automatico** basato su modello LLM e complessità
- **Fallback** per modelli lenti
- **Monitoraggio** in tempo reale

## 📚 Documentazione

- `DOCUMENTATION_INDEX.md` - Indice completo della documentazione
- `BACKGROUND_AGENT_README.md` - Guida dettagliata del Background Agent
- `INTEGRATED_MONITORING.md` - Monitoraggio integrato
- `PERSISTENCE.md` - Persistenza e robustezza
- `TIMEOUT_AND_MONITORING.md` - Gestione timeout e monitoraggio

## 🔧 Configurazione

### File di Configurazione Principali
- `background_config.json` - Configurazione principale
- `background_config_cpu_optimized.json` - Ottimizzato per CPU
- `background_config_safe.json` - Configurazione sicura

### Variabili d'Ambiente
```bash
export OLLAMA_HOST=localhost:11434
export FREQTRADE_CONFIG_PATH=user_data/config.json
```

## 🧪 Testing

### Test di Sistema
```bash
# Test completo del sistema
python test_complete_system.py

# Test dei prompt migliorati
python test_improved_prompts.py

# Test di ottimizzazione
python test_optimizer.py
```

### Test di Persistenza
```bash
# Test persistenza agente
./test_persistence.sh

# Test comportamento Ctrl+C
./test_ctrl_c_behavior.sh
```

## 📈 Stato Attuale del Progetto

### ✅ Completato
- [x] Setup completo Freqtrade + Ollama
- [x] Background Agent con persistenza
- [x] Sistema di generazione strategie
- [x] Monitor di backtest integrato
- [x] Sistema di ottimizzazione automatica
- [x] Gestione timeout intelligenti
- [x] Monitoraggio hardware
- [x] Gestione sessioni multiple
- [x] Documentazione completa

### 🔄 In Sviluppo
- [ ] Integrazione con exchange reali
- [ ] Sistema di alerting avanzato
- [ ] Dashboard web per monitoraggio
- [ ] Backtesting distribuito

### 📋 TODO
- [ ] Ottimizzazione performance
- [ ] Test su dataset più grandi
- [ ] Integrazione con più modelli LLM
- [ ] Sistema di versioning strategie

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/nuova-feature`)
3. Commit delle modifiche (`git commit -am 'Aggiunge nuova feature'`)
4. Push del branch (`git push origin feature/nuova-feature`)
5. Crea una Pull Request

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per i dettagli.

## ⚠️ Disclaimer

Questo software è fornito "così com'è" senza garanzie. Il trading su crypto è ad alto rischio. Utilizzare a proprio rischio e responsabilità.

---

**Ultimo aggiornamento**: Luglio 2024
**Versione**: 1.0.0
