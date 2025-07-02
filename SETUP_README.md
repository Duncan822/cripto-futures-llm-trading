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
