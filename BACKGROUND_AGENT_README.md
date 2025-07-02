# Background Agent - Gestione Automatica Strategie

## Panoramica

Il **Background Agent** è un sistema automatizzato che gestisce il ciclo completo di generazione, validazione e ottimizzazione delle strategie di trading crypto futures. Risolve i problemi di sovrascrittura e validazione manuale.

## Caratteristiche Principali

### ✅ **Nessuna Sovrascrittura**
- Ogni strategia ha un nome **univoco** con timestamp
- Formato: `{TipoStrategy}_{Modello}_{YYYYMMDD_HHMMSS}`
- Esempio: `VolatilityStrategy_phi3_20241201_143022`

### ✅ **Validazione Automatica**
- Controllo automatico dei nomi delle classi
- Validazione sintassi Python
- Correzione automatica degli errori comuni
- Fallback a strategie di default se necessario

### ✅ **Gestione Intelligente**
- Limite configurabile di strategie (default: 50)
- Pulizia automatica di strategie vecchie o con performance scarse
- Metadati persistenti per ogni strategia
- Backtest automatico periodico

## Come Funziona

### 1. **Generazione Sicura**
```python
# Il sistema genera nomi univoci
strategy_name = "VolatilityStrategy_phi3_20241201_143022"
file_path = "user_data/strategies/volatilitystrategy_phi3_20241201_143022.py"

# Controlla se esiste già
if os.path.exists(file_path):
    # Genera nuovo nome con timestamp diverso
    strategy_name = generate_unique_name()
```

### 2. **Validazione Automatica**
```python
# Ogni strategia viene validata automaticamente
strategy_code = generator.generate_futures_strategy(...)
validated_code = converter.validate_and_fix_code(strategy_code, strategy_name)

# Se la validazione fallisce, usa fallback
if not validated_code:
    validated_code = get_default_strategy(strategy_name)
```

### 3. **Metadati Persistenti**
```json
{
  "VolatilityStrategy_phi3_20241201_143022": {
    "name": "VolatilityStrategy_phi3_20241201_143022",
    "file_path": "user_data/strategies/volatilitystrategy_phi3_20241201_143022.py",
    "strategy_type": "volatility",
    "model_used": "phi3",
    "generation_time": "2024-12-01T14:30:22",
    "validation_status": "validated",
    "backtest_score": 0.15,
    "last_backtest": "2024-12-01T16:45:30",
    "is_active": false
  }
}
```

## Configurazione

### File: `background_config.json`
```json
{
  "auto_validation": true,           // Validazione automatica
  "auto_backtest": true,             // Backtest automatico
  "max_strategies": 50,              // Limite strategie
  "generation_interval": 3600,       // Generazione ogni ora
  "backtest_interval": 7200,         // Backtest ogni 2 ore
  "cleanup_old_strategies": true,    // Pulizia automatica
  "strategy_types": ["volatility", "scalping", "breakout", "momentum"],
  "models": ["phi3", "llama2", "mistral"],
  "min_backtest_score": 0.1,         // Punteggio minimo
  "max_strategy_age_days": 30        // Età massima strategie
}
```

## Utilizzo

### Avvio dell'Agente
```bash
# Avvia l'agente
./start_background_agent.sh

# Oppure usa lo script di gestione
./manage_background_agent.sh start
```

### Gestione dell'Agente
```bash
# Controlla lo stato
./manage_background_agent.sh status

# Visualizza log in tempo reale
./manage_background_agent.sh logs

# Modifica configurazione
./manage_background_agent.sh config

# Riavvia l'agente
./manage_background_agent.sh restart

# Ferma l'agente
./manage_background_agent.sh stop
```

### Test Manuale
```bash
# Test rapido dell'agente
python background_agent.py
```

## Attività Automatiche

### 📅 **Programmazione**
- **Generazione strategie**: Ogni ora (configurabile)
- **Backtest strategie**: Ogni 2 ore (configurabile)
- **Pulizia strategie**: Ogni giorno alle 02:00

### 🔄 **Ciclo di Vita Strategia**
1. **Generazione** → Nome univoco + validazione automatica
2. **Salvataggio** → File + metadati
3. **Backtest** → Valutazione performance
4. **Monitoraggio** → Controllo periodico
5. **Pulizia** → Rimozione se vecchia/scarsa

### 📊 **Metriche Tracciate**
- Nome e tipo strategia
- Modello LLM utilizzato
- Timestamp generazione
- Status validazione
- Punteggio backtest
- Ultimo backtest eseguito
- Status attivo/inattivo

## Risoluzione Problemi

### ❌ **Strategia non riconosciuta da FreqTrade**
```bash
# Correggi manualmente i nomi delle classi
python fix_strategies.py

# Oppure valida tutte le strategie
python -c "
from agents.strategy_converter import StrategyConverter
converter = StrategyConverter()
# Valida e correggi automaticamente
"
```

### ❌ **Errore di validazione**
- Il sistema usa automaticamente strategie di fallback
- Controlla i log per dettagli: `./manage_background_agent.sh logs`
- Modifica la configurazione se necessario: `./manage_background_agent.sh config`

### ❌ **Troppe strategie**
- Il sistema rispetta il limite `max_strategies`
- Pulizia automatica di strategie vecchie/scarse
- Puoi aumentare il limite in `background_config.json`

## Vantaggi del Sistema

### 🛡️ **Sicurezza**
- Nessuna sovrascrittura accidentale
- Backup automatico dei metadati
- Validazione robusta

### ⚡ **Efficienza**
- Automazione completa
- Gestione intelligente delle risorse
- Pulizia automatica

### 📈 **Scalabilità**
- Limiti configurabili
- Metadati persistenti
- Monitoraggio continuo

### 🔧 **Flessibilità**
- Configurazione personalizzabile
- Fallback automatici
- Logging dettagliato

## File di Sistema

```
crypto-futures-llm-trading/
├── background_agent.py              # Agente principale
├── background_config.json           # Configurazione
├── strategies_metadata.json         # Metadati strategie
├── background_agent.pid             # PID dell'agente
├── background_agent.log             # Log principale
├── logs/                            # Directory log
│   └── background_agent_*.log       # Log con timestamp
├── start_background_agent.sh        # Script avvio
└── manage_background_agent.sh       # Script gestione
```

## Monitoraggio

### 📊 **Stato in Tempo Reale**
```bash
./manage_background_agent.sh status
```

### 📋 **Log Dettagliati**
```bash
# Log in tempo reale
./manage_background_agent.sh logs

# Log specifico
tail -f logs/background_agent_20241201_143022.log
```

### 📈 **Metriche Performance**
- Numero totale strategie
- Strategie validate
- Strategie con backtest
- Strategie attive
- Uptime agente
- Utilizzo memoria

## Integrazione con FreqTrade

Il Background Agent si integra perfettamente con FreqTrade:

1. **Strategie compatibili** → Nomi classi corretti
2. **Validazione automatica** → Sintassi Python valida
3. **Backtest automatico** → Valutazione performance
4. **Gestione file** → Organizzazione strategie

Tutte le strategie generate sono immediatamente utilizzabili con FreqTrade senza intervento manuale. 