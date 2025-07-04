# Background Agent Cooperativo - Guida Completa

## 📖 Panoramica

Il **Background Agent Cooperativo** è una versione avanzata del sistema di generazione strategie che sfrutta la cooperazione tra multipli LLM (Large Language Models) per produrre strategie di trading più sofisticate e affidabili. Il sistema integra controlli hardware intelligenti per evitare sovraccarichi del sistema.

## 🎯 Caratteristiche Principali

### 🤖 Cooperazione Multi-LLM
- **Generazione Parallela**: Multipli LLM generano strategie simultaneamente
- **Validazione Incrociata**: Ogni strategia viene validata da più LLM
- **Selezione Consensuale**: Scelta automatica della migliore strategia basata su punteggi combinati
- **Contest tra LLM**: Competizione diretta tra modelli per la strategia ottimale

### 🔧 Gestione Hardware Intelligente
- **Monitoraggio Risorse**: Controllo continuo di CPU, temperatura, memoria e carico sistema
- **Adattamento Dinamico**: Numero di LLM paralleli adattato alle risorse disponibili
- **Protezione Sistema**: Interruzione automatica delle operazioni in caso di sovraccarico
- **Ottimizzazione Modelli**: Selezione automatica dei modelli più adatti all'hardware

### 📊 Modalità Operative
1. **Cooperative Generate**: Generazione collaborativa standard
2. **LLM Contest**: Contest competitivo tra LLM
3. **Consensus Strategy**: Strategia basata su consenso tra tutti i LLM
4. **Validate Cooperative**: Validazione incrociata avanzata

## 🚀 Installazione e Setup

### Prerequisiti
```bash
# Verifica che Ollama sia installato e in esecuzione
ollama serve

# Installa i modelli necessari
ollama pull cogito:8b
ollama pull mistral:7b
ollama pull phi3:14b
ollama pull llama3.1:8b

# Verifica strumenti di sistema (opzionali ma raccomandati)
sudo apt-get install lm-sensors htop
```

### Configurazione Permessi
```bash
# Rendi eseguibile lo script
chmod +x background_agent_cooperative.sh

# Verifica che le directory necessarie esistano
mkdir -p user_data/strategies
mkdir -p logs
mkdir -p cooperative_results
mkdir -p llm_contest
mkdir -p consensus_strategies
```

## 🎮 Utilizzo

### Comandi Base

#### Avvio dell'Agente Cooperativo
```bash
./background_agent_cooperative.sh start
```

#### Controllo Stato
```bash
./background_agent_cooperative.sh status
```

#### Visualizzazione Log
```bash
./background_agent_cooperative.sh logs
```

#### Arresto
```bash
./background_agent_cooperative.sh stop
```

### Comandi Cooperativi Avanzati

#### Generazione Cooperativa
Genera una strategia utilizzando la collaborazione tra LLM:
```bash
# Strategia di volatilità cooperativa
./background_agent_cooperative.sh cooperative-generate volatility

# Strategia di scalping cooperativa
./background_agent_cooperative.sh cooperative-generate scalping

# Strategia di momentum cooperativa
./background_agent_cooperative.sh cooperative-generate momentum
```

#### Contest tra LLM
Organizza una competizione tra LLM per la migliore strategia:
```bash
# Contest per strategia breakout
./background_agent_cooperative.sh llm-contest breakout

# Contest per strategia scalping
./background_agent_cooperative.sh llm-contest scalping
```

#### Strategia Consensuale
Crea una strategia basata sul consenso di tutti i LLM:
```bash
# Strategia momentum consensuale
./background_agent_cooperative.sh consensus-strategy momentum

# Strategia volatilità consensuale
./background_agent_cooperative.sh consensus-strategy volatility
```

#### Validazione Cooperativa
Esegue validazione incrociata delle strategie:
```bash
./background_agent_cooperative.sh validate-cooperative
```

## ⚙️ Configurazione

### Configurazione Hardware
Le soglie hardware sono configurabili nel file:

```bash
# Modifica i limiti hardware
nano background_agent_cooperative.sh

# Parametri principali:
MAX_CPU_USAGE=70          # Massimo utilizzo CPU (%)
MAX_TEMPERATURE=75        # Temperatura massima CPU (°C)
MIN_FREE_MEMORY=2         # Memoria minima libera (GB)
MAX_PARALLEL_LLMS=4       # Massimo LLM paralleli
```

### Configurazione Cooperativa
Il file `background_config_cooperative.json` viene creato automaticamente:

```json
{
  "cooperative_mode": {
    "enable_cooperation": true,
    "cooperative_generation_interval": 10800,
    "llm_consensus_threshold": 0.7,
    "use_llm_voting": true,
    "parallel_generation_count": 3,
    "enable_contest_mode": true,
    "contest_interval": 21600
  },
  "model_selection": {
    "generation": ["cogito:8b", "mistral:7b", "phi3:14b"],
    "validation": ["cogito:8b", "mistral:7b"],
    "optimization": "cogito:8b"
  }
}
```

## 🔍 Algoritmi di Cooperazione

### 1. Generazione Cooperativa
```
1. Controllo risorse hardware
2. Calcolo numero ottimale di LLM paralleli
3. Generazione simultanea con LLM multipli
4. Validazione incrociata
5. Selezione della strategia migliore
6. Salvataggio risultati
```

### 2. Contest LLM
```
1. Verifica disponibilità LLM
2. Lancio contest paralleli
3. Valutazione risultati con criteri multipli:
   - Complessità del codice
   - Uso di indicatori tecnici
   - Gestione del rischio
   - Originalità dell'approccio
4. Generazione report comparativo
```

### 3. Strategia Consensuale
```
1. Raccolta idee da tutti i LLM
2. Combinazione e analisi delle proposte
3. Sintesi consensuale con LLM più potente
4. Implementazione strategia unificata
5. Validazione finale
```

## 📊 Monitoraggio Hardware

### Parametri Monitorati
- **CPU Usage**: Utilizzo processore in tempo reale
- **CPU Temperature**: Temperatura del processore
- **Memory**: Memoria RAM libera
- **System Load**: Carico medio del sistema
- **Disk Usage**: Utilizzo spazio disco

### Soglie di Sicurezza
- **CPU > 90%**: Interruzione immediata
- **Temperatura > 85°C**: Interruzione per surriscaldamento
- **RAM libera < 1GB**: Interruzione per memoria insufficiente
- **Load > 8.0**: Sistema sovraccarico

### Adattamento Dinamico
Il sistema adatta automaticamente il numero di LLM paralleli in base a:
- Utilizzo CPU attuale
- Memoria disponibile
- Carico del sistema
- Temperatura del processore

## 📁 Struttura Directory

```
./
├── background_agent_cooperative.sh     # Script principale
├── background_config_cooperative.json  # Configurazione
├── logs/                               # Log del sistema
│   └── background_agent_cooperative_*.log
├── cooperative_results/                # Risultati cooperativi
│   └── YYYYMMDD_HHMMSS/
│       ├── strategy_*.py
│       ├── validation_results.json
│       └── best_strategy.txt
├── llm_contest/                        # Contest tra LLM
│   └── YYYYMMDD_HHMMSS/
│       ├── contest_*.py
│       └── contest_report.md
├── consensus_strategies/               # Strategie consensuali
│   └── YYYYMMDD_HHMMSS/
│       ├── ideas_*.txt
│       ├── consensus_synthesis.txt
│       └── consensus_strategy.py
└── user_data/strategies/              # Strategie finali
    ├── CooperativeStrategy_*.py
    ├── ConsensusStrategy_*.py
    └── ContestStrategy_*.py
```

## 🎯 Esempi Pratici

### Esempio 1: Generazione Strategia Volatilità Cooperativa

```bash
# 1. Controlla risorse hardware
./background_agent_cooperative.sh status

# 2. Genera strategia cooperativa
./background_agent_cooperative.sh cooperative-generate volatility

# 3. Controlla risultati
ls -la cooperative_results/
cat cooperative_results/*/validation_results.json
```

### Esempio 2: Contest per Strategia Scalping

```bash
# 1. Avvia contest
./background_agent_cooperative.sh llm-contest scalping

# 2. Analizza risultati del contest
ls -la llm_contest/
cat llm_contest/*/contest_report.md

# 3. Controlla strategie generate
ls -la llm_contest/*/contest_*.py
```

### Esempio 3: Strategia Consensuale Momentum

```bash
# 1. Genera strategia consensuale
./background_agent_cooperative.sh consensus-strategy momentum

# 2. Verifica processo di consenso
cat consensus_strategies/*/all_ideas.txt
cat consensus_strategies/*/consensus_synthesis.txt

# 3. Controlla strategia finale
ls -la user_data/strategies/ConsensusStrategy_*.py
```

## 🚨 Risoluzione Problemi

### Problema: LLM Non Disponibili
```bash
# Verifica Ollama
ps aux | grep ollama

# Riavvia Ollama se necessario
ollama serve

# Verifica modelli installati
ollama list
```

### Problema: Risorse Hardware Insufficienti
```bash
# Controlla utilizzo risorse
./background_agent_cooperative.sh status

# Riduci numero LLM paralleli
nano background_agent_cooperative.sh
# Modifica MAX_PARALLEL_LLMS=2

# Chiudi applicazioni non necessarie
```

### Problema: Generazione Fallita
```bash
# Controlla log dettagliati
./background_agent_cooperative.sh logs

# Verifica file di errore
find cooperative_results/ -name "*.error" -exec cat {} \;

# Riavvia con configurazione ridotta
MAX_PARALLEL_LLMS=1 ./background_agent_cooperative.sh cooperative-generate volatility
```

### Problema: Memoria Insufficiente
```bash
# Libera memoria cache
sudo sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Chiudi Ollama e riavvia
pkill ollama
sleep 5
ollama serve

# Usa modelli più leggeri
./background_agent_cooperative.sh cooperative-generate volatility
```

## 📈 Performance e Ottimizzazione

### Configurazioni Hardware Consigliate

#### Sistema Minimo
- **CPU**: 4 core, 2.5GHz+
- **RAM**: 8GB+
- **Storage**: 20GB+ libero
- **LLM Paralleli**: 1-2

#### Sistema Raccomandato
- **CPU**: 8 core, 3.0GHz+
- **RAM**: 16GB+
- **Storage**: 50GB+ libero
- **LLM Paralleli**: 2-3

#### Sistema Ottimale
- **CPU**: 16+ core, 3.5GHz+
- **RAM**: 32GB+
- **Storage**: 100GB+ libero SSD
- **LLM Paralleli**: 3-4

### Ottimizzazioni Suggerite

1. **Modelli per Hardware Limitato**:
   ```bash
   # Usa solo modelli veloci
   LLM_STRATEGY_GENERATORS=("phi3:14b" "mistral:7b")
   ```

2. **Intervalli Aumentati**:
   ```bash
   # Riduci frequenza operazioni
   HARDWARE_CHECK_INTERVAL=60
   ```

3. **Limiti Più Conservativi**:
   ```bash
   MAX_CPU_USAGE=50
   MAX_TEMPERATURE=70
   MIN_FREE_MEMORY=4
   ```

## 🔄 Integrazione con Sistema Esistente

Il Background Agent Cooperativo è completamente compatibile con il sistema esistente:

- **Mantiene tutte le funzioni standard** del background agent originale
- **Usa la stessa configurazione base** di Freqtrade
- **Si integra con gli stessi file** di strategia
- **Condivide i log e i risultati** con il sistema principale

### Passaggio dal Sistema Standard
```bash
# Ferma l'agente standard
./manage_background_agent.sh stop

# Avvia l'agente cooperativo
./background_agent_cooperative.sh start

# Entrambi possono coesistere se necessario
```

## 📝 Log e Debugging

### File di Log Principali
- `logs/background_agent_cooperative_*.log` - Log principale
- `cooperative_results/*/validation_results.json` - Risultati validazioni
- `llm_contest/*/contest_report.md` - Report contest
- `consensus_strategies/*/consensus_synthesis.txt` - Sintesi consensuali

### Debugging Avanzato
```bash
# Abilita debug verbose
export DEBUG=1
./background_agent_cooperative.sh cooperative-generate volatility

# Monitora risorse in tempo reale
watch -n 5 './background_agent_cooperative.sh status'

# Controlla log in tempo reale
tail -f logs/background_agent_cooperative_*.log
```

## 🛡️ Sicurezza e Limiti

### Protezioni Implementate
- **Timeout automatico** per operazioni lunghe
- **Interruzione su sovraccarico** hardware
- **Validazione input** e parametri
- **Gestione errori** robusta

### Limiti Attuali
- Richiede almeno 2 LLM per cooperazione completa
- Performance dipendente dalle risorse hardware
- Tempo di generazione più lungo del sistema standard

## 🔮 Sviluppi Futuri

### Funzionalità Pianificate
- **Auto-tuning dinamico** dei parametri
- **Integrazione GPU** per accelerazione
- **Caching intelligente** dei risultati LLM
- **Metriche avanzate** di performance cooperativa

### Contributi
Per contribuire al progetto:
1. Testa il sistema su configurazioni diverse
2. Riporta bug e suggerimenti
3. Proponi nuove modalità cooperative
4. Ottimizza gli algoritmi di consenso

---

*Documentazione aggiornata al: $(date)*

*Per supporto: controlla i log e la sezione risoluzione problemi*