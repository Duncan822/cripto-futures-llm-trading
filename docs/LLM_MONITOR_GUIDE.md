# 🤖 LLM Monitor - Guida Completa

## Panoramica

Il **LLM Monitor** è un sistema di monitoraggio completo per gli LLM (Large Language Models) in esecuzione nel progetto crypto-futures-llm-trading. Fornisce:

- **Monitoraggio in tempo reale** delle richieste LLM
- **Dashboard web** per visualizzare stato e performance
- **Metriche dettagliate** su modelli, richieste e sistema
- **Tracciamento automatico** di tutte le operazioni LLM
- **API REST** per integrazione con altri sistemi

## 🚀 Avvio Rapido

### 1. Avvia il Monitor

```bash
# Avvia su porta default (8080)
./start_llm_monitor.sh start

# Avvia su porta specifica
./start_llm_monitor.sh start 9090
```

### 2. Accedi alla Dashboard

Apri il browser su: `http://localhost:8080`

### 3. Verifica lo Stato

```bash
# Controlla se il monitor è in esecuzione
./start_llm_monitor.sh status

# Visualizza i log in tempo reale
./start_llm_monitor.sh logs
```

## 📊 Funzionalità

### Dashboard Web

La dashboard fornisce una vista completa del sistema:

- **Status Bar**: Uptime, richieste attive, totale richieste, modelli disponibili
- **Statistiche Generali**: Metriche aggregate di performance
- **Stato Modelli**: Disponibilità e performance di ogni modello
- **Richieste Attive**: Richieste LLM attualmente in corso
- **Richieste Recenti**: Storico delle ultime operazioni

### API REST

Il monitor espone le seguenti API:

```bash
# Stato generale
GET /api/status

# Lista modelli e loro stato
GET /api/models

# Statistiche aggregate
GET /api/stats

# Richieste attualmente attive
GET /api/active

# Storico richieste
GET /api/requests
```

### Tracciamento Automatico

Il sistema traccia automaticamente:

- **Tempo di inizio/fine** di ogni richiesta
- **Durata** dell'elaborazione
- **Modello utilizzato**
- **Prompt inviato** (troncato per privacy)
- **Risposta ricevuta**
- **Errori e timeout**
- **Utilizzo CPU/memoria**

## 🔧 Integrazione con il Codice

### Funzioni Monitorate

Sostituisci le chiamate LLM esistenti con le versioni monitorate:

```python
# Invece di:
from llm_utils import query_ollama, query_ollama_fast

# Usa:
from llm_utils_monitored import (
    query_ollama_monitored,
    query_ollama_fast_monitored
)

# Le funzioni hanno la stessa interfaccia ma tracciano automaticamente
response = query_ollama_monitored(prompt, model="phi3")
```

### Accesso Programmatico

```python
from llm_utils_monitored import (
    get_monitor_status,
    get_active_requests,
    get_recent_requests,
    get_model_performance
)

# Ottieni stato del monitor
status = get_monitor_status()

# Richieste attualmente attive
active = get_active_requests()

# Ultime 10 richieste
recent = get_recent_requests(limit=10)

# Performance dei modelli
performance = get_model_performance()
```

## 📈 Metriche Disponibili

### Per Modello

- **Disponibilità**: Se il modello risponde
- **Tempo medio di risposta**: Performance aggregata
- **Tasso di successo**: Percentuale di richieste completate
- **Numero totale di richieste**: Utilizzo del modello

### Per Richiesta

- **ID univoco**: Identificatore della richiesta
- **Modello utilizzato**: Nome del modello LLM
- **Prompt**: Testo inviato (troncato)
- **Stato**: running/completed/failed/timeout
- **Durata**: Tempo di elaborazione
- **Token generati**: Stima dei token prodotti
- **Utilizzo risorse**: CPU e memoria durante l'elaborazione

### Aggregate

- **Uptime**: Tempo di funzionamento del monitor
- **Richieste totali**: Numero di richieste processate
- **Tasso di successo**: Percentuale di successi
- **Tempo medio di risposta**: Performance generale
- **Token totali**: Somma dei token generati

## 🛠️ Gestione del Sistema

### Comandi Disponibili

```bash
# Avvia il monitor
./start_llm_monitor.sh start [PORT]

# Ferma il monitor
./start_llm_monitor.sh stop

# Riavvia il monitor
./start_llm_monitor.sh restart [PORT]

# Mostra stato
./start_llm_monitor.sh status

# Visualizza log in tempo reale
./start_llm_monitor.sh logs

# Test del sistema
./start_llm_monitor.sh test

# Pulizia file temporanei
./start_llm_monitor.sh cleanup

# Mostra aiuto
./start_llm_monitor.sh help
```

### File di Sistema

- `llm_monitor.py`: Sistema di monitoraggio principale
- `llm_utils_monitored.py`: Wrapper per funzioni LLM
- `templates/llm_dashboard.html`: Template della dashboard
- `start_llm_monitor.sh`: Script di gestione
- `llm_monitor.log`: Log del sistema
- `llm_monitor.pid`: File PID per gestione processo

## 🔍 Debug e Troubleshooting

### Problemi Comuni

#### Monitor non si avvia

```bash
# Controlla dipendenze
pip install flask psutil

# Controlla porta
netstat -tlnp | grep 8080

# Controlla log
tail -f llm_monitor.log
```

#### Dashboard non carica

```bash
# Controlla se il processo è attivo
ps aux | grep llm_monitor

# Controlla porta
curl http://localhost:8080/api/status

# Riavvia il monitor
./start_llm_monitor.sh restart
```

#### Richieste non tracciate

```bash
# Verifica che il monitor sia attivo
./start_llm_monitor.sh status

# Controlla che usi le funzioni monitorate
# Invece di query_ollama() usa query_ollama_monitored()
```

### Log e Debug

```bash
# Log in tempo reale
./start_llm_monitor.sh logs

# Ultime 50 righe
tail -n 50 llm_monitor.log

# Cerca errori
grep ERROR llm_monitor.log

# Monitora richieste
watch -n 1 'curl -s http://localhost:8080/api/active | jq length'
```

## 🔒 Sicurezza e Privacy

### Protezione Dati

- **Prompt troncati**: I prompt lunghi vengono troncati a 200 caratteri
- **Log locali**: Tutti i dati rimangono locali
- **Nessuna condivisione**: Nessun dato viene inviato esternamente
- **Controllo accesso**: Dashboard accessibile solo localmente

### Configurazione Sicurezza

```python
# Nel file llm_monitor.py
# Modifica per limitare accesso
self.flask_app.run(host='127.0.0.1', port=self.port)  # Solo locale
```

## 📊 Esempi di Utilizzo

### Monitoraggio Continuo

```bash
# Avvia monitor in background
nohup ./start_llm_monitor.sh start > monitor.log 2>&1 &

# Controlla stato periodicamente
watch -n 30 './start_llm_monitor.sh status'
```

### Integrazione con Script

```python
#!/usr/bin/env python3
from llm_utils_monitored import (
    query_ollama_monitored,
    get_monitor_status
)

# Genera strategie con monitoraggio
def generate_strategy_with_monitoring():
    # Controlla stato monitor
    status = get_monitor_status()
    if not status:
        print("⚠️ Monitor non attivo")
        return
    
    # Genera strategia monitorata
    response = query_ollama_monitored(
        "Genera una strategia di trading per futures crypto",
        model="phi3"
    )
    
    print(f"✅ Strategia generata in {status['avg_response_time']:.2f}s")
    return response
```

### Alert e Notifiche

```python
import requests
import time

def check_llm_health():
    """Controlla salute del sistema LLM."""
    try:
        response = requests.get("http://localhost:8080/api/status")
        status = response.json()
        
        if status['failed_requests'] > 10:
            print("🚨 Troppi errori LLM!")
            
        if status['avg_response_time'] > 60:
            print("⚠️ Performance LLM degradate!")
            
    except Exception as e:
        print(f"❌ Monitor non raggiungibile: {e}")

# Controlla ogni 5 minuti
while True:
    check_llm_health()
    time.sleep(300)
```

## 🚀 Performance e Ottimizzazione

### Configurazione Ottimale

```python
# Nel file llm_monitor.py
# Riduci frequenza controlli per performance
time.sleep(10)  # Controlla ogni 10 secondi invece di 5

# Limita numero richieste in memoria
MAX_REQUESTS = 1000  # Mantieni solo ultime 1000 richieste
```

### Monitoraggio Risorse

```bash
# Monitora utilizzo CPU/memoria
htop

# Controlla processi Ollama
ps aux | grep ollama

# Monitora rete
iftop -i lo
```

## 📚 Riferimenti

- **Flask**: Framework web per la dashboard
- **psutil**: Monitoraggio risorse sistema
- **requests**: Client HTTP per API
- **Ollama**: Server LLM locale

## 🤝 Contributi

Per migliorare il sistema di monitoraggio:

1. Modifica `llm_monitor.py` per nuove funzionalità
2. Aggiorna `templates/llm_dashboard.html` per UI
3. Estendi `llm_utils_monitored.py` per nuovi wrapper
4. Aggiungi test in `test_llm_monitor.py`

---

**Nota**: Il sistema di monitoraggio è progettato per essere leggero e non impattare le performance degli LLM. Tutti i dati sono mantenuti localmente e non vengono condivisi. 