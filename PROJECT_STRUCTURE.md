# Struttura Progetto Ottimizzata

## 📁 Directory

- **docs/**: Documentazione completa del progetto
- **tests/**: Test suite per tutte le componenti
- **scripts/**: Script di utilità e setup
- **configs/**: File di configurazione alternativi
- **agents/**: Agenti AI per generazione e ottimizzazione
- **prompts/**: Prompt specializzati per LLMs
- **strategies/**: Strategie di trading generate
- **user_data/**: Dati e configurazioni Freqtrade
- **examples/**: Esempi e template
- **templates/**: Template per strategie

## 🐍 File Python Principali

- **background_agent.py**: Agente principale del sistema
- **freqtrade_utils.py**: Utilità per Freqtrade
- **dry_run_manager.py**: Gestione dry run
- **live_strategies_exporter.py**: Esportazione strategie live
- **backtest_monitor.py**: Monitoraggio backtest
- **llm_monitor.py**: Monitoraggio LLM
- **session_manager.py**: Gestione sessioni
- **requirements.txt**: Dipendenze Python

## 🔧 Script Chiave

- **manage_background_agent.sh**: Gestione agente principale
- **start_background_agent.sh**: Avvio rapido agente
- **manage_backtest_monitor.sh**: Gestione monitoraggio
- **manage_dry_run.sh**: Gestione dry run
- **quick_start.sh**: Setup rapido sistema

## 🚀 Quick Start

```bash
# Setup iniziale
./scripts/setup_freqtrade.sh
./scripts/setup_ollama.sh

# Avvio sistema
./start_background_agent.sh

# Monitoraggio
./manage_background_agent.sh status
./manage_background_agent.sh logs
```
