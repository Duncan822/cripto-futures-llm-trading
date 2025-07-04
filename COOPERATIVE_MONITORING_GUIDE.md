# 🤖 Guida al Monitoraggio Cooperativo

## Panoramica

Il **Cooperative Monitor** è un'estensione avanzata del sistema di monitoraggio LLM esistente che traccia e visualizza le interazioni cooperative tra i modelli di linguaggio. Permette di monitorare in tempo reale:

- 💬 **Conversazioni tra LLM**
- 🤝 **Sessioni cooperative**
- 🏆 **Contest tra modelli**
- ✅ **Validazioni incrociate**
- 📊 **Metriche di performance**

## 🚀 Avvio del Sistema

### 1. Avvio del Monitor Cooperativo

```bash
# Avvia il monitor cooperativo
./background_agent_cooperative.sh monitor

# Verifica lo stato
./background_agent_cooperative.sh monitor-status

# Ferma il monitor
./background_agent_cooperative.sh monitor-stop
```

### 2. Dashboard Web

Una volta avviato, il monitor fornisce due dashboard:

- **🤖 Dashboard Cooperativa**: http://localhost:8081
- **📊 Monitor LLM Base**: http://localhost:8080

## 📊 Funzionalità del Monitor

### 1. Tracciamento Sessioni Cooperative

Il monitor registra automaticamente:

```python
# Esempio di tracciamento sessione
session_id = track_cooperative_session(
    session_type="cooperative_generation",
    strategy_type="volatility",
    participants=["cogito:8b", "mistral:7b", "phi3:14b"]
)
```

**Tipi di Sessione:**
- `cooperative_generation` - Generazione collaborativa
- `contest` - Competizione tra LLM
- `consensus` - Processo di consenso
- `validation` - Validazione incrociata

### 2. Log delle Conversazioni

Ogni interazione tra LLM viene registrata:

```python
# Esempio di log conversazione
conversation_id = log_cooperative_conversation(
    session_id=session_id,
    model="cogito:8b",
    role="generator",
    prompt="Genera strategia per volatilità alta",
    response="Strategia basata su...",
    duration=5.2,
    validation_score=8.5
)
```

**Ruoli Supportati:**
- `generator` - Generatore di strategie
- `validator` - Validatore di strategie
- `optimizer` - Ottimizzatore
- `contestant` - Partecipante al contest

### 3. Round di Consenso

Tracciamento dei processi di consenso:

```python
# Esempio di round consenso
round_id = log_consensus_round(
    session_id=session_id,
    round_number=1,
    participants=["cogito:8b", "mistral:7b"],
    ideas_collected={
        "cogito:8b": "Strategia A",
        "mistral:7b": "Strategia B"
    },
    synthesis="Strategia ibrida A+B",
    duration=12.5
)
```

## 🎛️ Comandi da Terminale

### Comandi di Monitoraggio

```bash
# Avvia monitor cooperativo
./background_agent_cooperative.sh monitor

# Verifica stato monitor
./background_agent_cooperative.sh monitor-status

# Ferma monitor
./background_agent_cooperative.sh monitor-stop

# Visualizza conversazioni recenti
./background_agent_cooperative.sh conversations
```

### Output del Comando `conversations`

```
💬 Visualizzazione Conversazioni LLM

📡 Recupero conversazioni recenti...
✅ Conversazioni recuperate

📋 Ultime 5 Conversazioni:

💬 Conversazione 1:
   🤖 Modello: cogito:8b
   🎭 Ruolo: generator
   ⏱️  Durata: 5.2s
   📅 Timestamp: 2024-01-15T10:30:15
   ✅ Punteggio Validazione: 8.5
   💭 Prompt: Genera strategia per volatilità alta...
   💬 Risposta: Strategia basata su indicatori...

💬 Conversazione 2:
   🤖 Modello: mistral:7b
   🎭 Ruolo: validator
   ⏱️  Durata: 3.8s
   📅 Timestamp: 2024-01-15T10:30:20
   ✅ Punteggio Validazione: 7.9
   💭 Prompt: Valida la strategia proposta...
   💬 Risposta: La strategia è valida ma...
```

## 🌐 Dashboard Web

### Dashboard Cooperativa (Porta 8081)

La dashboard cooperativa fornisce:

#### 📈 Statistiche Generali
- **Sessioni Totali**: Numero di sessioni cooperative
- **Conversazioni**: Interazioni tra LLM registrate
- **Round Consenso**: Processi di consenso completati
- **Durata Media**: Tempo medio per sessione

#### 🔄 Sessioni Attive
- Lista delle sessioni cooperative in corso
- Tipo di sessione e partecipanti
- Durata e stato attuale

#### 📋 Sessioni Recenti
- Storico delle ultime 5 sessioni
- Risultati e metriche di performance

#### 💬 Conversazioni Recenti
- Log dettagliato delle interazioni
- Prompt e risposte dei modelli
- Punteggi di validazione e contest

### Dashboard LLM Base (Porta 8080)

Il monitor LLM base fornisce:
- Stato dei modelli individuali
- Metriche di performance
- Richieste attive
- Statistiche generali

## 📊 API REST

Il monitor cooperativo espone API REST per l'integrazione:

### Endpoint Principali

```bash
# Stato generale
GET http://localhost:8081/api/cooperative/status

# Sessioni cooperative
GET http://localhost:8081/api/cooperative/sessions

# Conversazioni
GET http://localhost:8081/api/cooperative/conversations

# Round di consenso
GET http://localhost:8081/api/cooperative/consensus

# Statistiche
GET http://localhost:8081/api/cooperative/stats

# Sessioni attive
GET http://localhost:8081/api/cooperative/active

# Dettagli sessione specifica
GET http://localhost:8081/api/cooperative/session/{session_id}

# Stato monitor LLM base
GET http://localhost:8081/api/cooperative/llm-status
```

### Esempio di Risposta API

```json
{
  "is_running": true,
  "active_sessions_count": 2,
  "total_sessions_count": 15,
  "total_conversations_count": 47,
  "total_consensus_rounds_count": 8,
  "cooperative_stats": {
    "total_sessions": 15,
    "completed_sessions": 13,
    "failed_sessions": 0,
    "avg_session_duration": 45.2,
    "most_used_models": {
      "cogito:8b": 12,
      "mistral:7b": 10,
      "phi3:14b": 8
    }
  }
}
```

## 📁 Struttura File

```
cooperative_monitor.py          # Monitor cooperativo principale
templates/
  cooperative_dashboard.html    # Template dashboard web
logs/
  cooperative_monitor_*.log     # Log del monitor
cooperative_monitor.pid         # PID del processo
```

## 🔧 Configurazione

### Variabili di Ambiente

```bash
# Porta del monitor cooperativo
COOPERATIVE_MONITOR_PORT=8081

# Porta del monitor LLM base
LLM_MONITOR_PORT=8080

# Livello di logging
COOPERATIVE_LOG_LEVEL=INFO
```

### Configurazione Python

Il monitor può essere configurato modificando `cooperative_monitor.py`:

```python
# Configurazione monitor
MONITOR_CONFIG = {
    "port": 8081,
    "log_level": "INFO",
    "max_sessions": 100,
    "session_retention_hours": 24,
    "auto_cleanup": True
}
```

## 📈 Metriche e Statistiche

### Statistiche Cooperative

- **Sessioni per Tipo**: Distribuzione dei tipi di sessione
- **Modelli Più Utilizzati**: Frequenza di utilizzo per modello
- **Durata Media**: Tempo medio per sessione e conversazione
- **Tasso di Successo**: Percentuale di sessioni completate

### Metriche Hardware

- **Utilizzo CPU**: Durante le sessioni cooperative
- **Memoria**: Consumo di RAM per sessione
- **Temperatura**: Monitoraggio termico del sistema

## 🛠️ Integrazione con Background Agent

Il monitor cooperativo si integra automaticamente con il background agent:

```bash
# Avvia agente con monitor
./background_agent_cooperative.sh start
./background_agent_cooperative.sh monitor

# Verifica stato completo
./background_agent_cooperative.sh status
./background_agent_cooperative.sh monitor-status
```

### Log Integrati

I log del monitor cooperativo vengono salvati in:
- `logs/cooperative_monitor_YYYYMMDD_HHMMSS.log`
- `logs/background_agent_cooperative_*.log` (per l'agente)

## 🔍 Debug e Troubleshooting

### Problemi Comuni

#### 1. Monitor non si avvia
```bash
# Verifica dipendenze
pip3 install flask psutil

# Controlla porte
netstat -tlnp | grep :8081
```

#### 2. Dashboard non accessibile
```bash
# Verifica firewall
sudo ufw allow 8081

# Controlla servizio
./background_agent_cooperative.sh monitor-status
```

#### 3. Conversazioni non registrate
```bash
# Verifica integrazione
./background_agent_cooperative.sh conversations

# Controlla log
tail -f logs/cooperative_monitor_*.log
```

### Comandi di Debug

```bash
# Log in tempo reale
tail -f logs/cooperative_monitor_*.log

# Stato dettagliato
curl http://localhost:8081/api/cooperative/status

# Test API
curl http://localhost:8081/api/cooperative/conversations
```

## 📚 Esempi Pratici

### Esempio 1: Monitoraggio Sessione Contest

```bash
# Avvia contest
./background_agent_cooperative.sh llm-contest volatility

# Monitora in tempo reale
./background_agent_cooperative.sh monitor
# Apri http://localhost:8081

# Visualizza conversazioni
./background_agent_cooperative.sh conversations
```

### Esempio 2: Analisi Performance

```bash
# Avvia generazione cooperativa
./background_agent_cooperative.sh cooperative-generate momentum

# Monitora performance
./background_agent_cooperative.sh monitor-status

# Esporta dati
curl http://localhost:8081/api/cooperative/stats > stats.json
```

### Esempio 3: Debug Sessione

```bash
# Trova session ID
curl http://localhost:8081/api/cooperative/sessions

# Dettagli sessione specifica
curl http://localhost:8081/api/cooperative/session/{session_id}

# Conversazioni della sessione
curl http://localhost:8081/api/cooperative/conversations | jq '.[] | select(.session_id == "{session_id}")'
```

## 🎯 Best Practices

### 1. Monitoraggio Continuo
- Mantieni sempre attivo il monitor durante le sessioni cooperative
- Verifica regolarmente lo stato via `monitor-status`

### 2. Analisi Dati
- Esporta periodicamente le statistiche
- Analizza i pattern di conversazione
- Identifica i modelli più performanti

### 3. Ottimizzazione
- Monitora l'utilizzo delle risorse
- Regola il numero di sessioni parallele
- Pulisci i log vecchi periodicamente

### 4. Sicurezza
- Limita l'accesso alle dashboard in produzione
- Usa HTTPS per le connessioni remote
- Monitora gli accessi alle API

## 🔮 Sviluppi Futuri

### Funzionalità Pianificate

1. **Analisi Semantica**: Analisi del contenuto delle conversazioni
2. **Alerting**: Notifiche per eventi critici
3. **Export Avanzato**: Esportazione in formati multipli
4. **Integrazione ML**: Analisi predittiva delle performance
5. **Dashboard Mobile**: Interfaccia responsive per dispositivi mobili

### Contributi

Per contribuire al sistema di monitoraggio:

1. Fork del repository
2. Implementa nuove funzionalità
3. Aggiungi test unitari
4. Documenta le modifiche
5. Crea pull request

---

**📞 Supporto**: Per problemi o domande, consulta i log o apri un issue nel repository. 