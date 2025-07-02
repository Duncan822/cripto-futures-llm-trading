# 🔧 Session Manager per Background Agent

## 🎯 **Problema: Sessioni Multiple**

Hai ragione! Le sessioni multiple si attivano perché:
- **Tu** testi dal tuo terminale
- **Io** uso un terminale diverso
- Questo può creare **conflitti** e **duplicazione** di operazioni

## 💡 **Soluzione: Session Manager**

Ho creato un **Session Manager** che fornisce un'interfaccia unificata per gestire le sessioni in modo controllato.

## 🔧 **Come Funziona**

### **Sistema di Lock**
- 🔒 **File di lock**: `session.lock` - Contiene l'ID della sessione attiva
- 📝 **Log delle sessioni**: `session_manager.log` - Traccia tutte le operazioni
- 🆔 **ID sessione**: Identifica chi ha avviato la sessione

### **Controllo Centralizzato**
- ✅ **Una sola sessione controllata** alla volta
- 🤝 **Join sessioni esistenti** invece di crearne di nuove
- 🧹 **Pulizia automatica** per evitare conflitti

## 📋 **Comandi Disponibili**

### **1. Avvio Sessione Controllata**
```bash
./session_manager.sh start [session_id]
```
- ✅ Crea un lock per la sessione
- ✅ Avvia il Background Agent
- ❌ Blocca se c'è già una sessione attiva

**Esempio:**
```bash
./session_manager.sh start my_test_session
```

### **2. Unirsi a Sessione Esistente**
```bash
./session_manager.sh join [session_id]
```
- 🤝 Si unisce alla sessione esistente
- 📊 Mostra informazioni sulla sessione
- ✅ Non crea conflitti

**Esempio:**
```bash
./session_manager.sh join my_test_session
```

### **3. Fermare Sessione Controllata**
```bash
./session_manager.sh stop [session_id]
```
- 🛑 Ferma il Background Agent
- 🔓 Rimuove il lock
- ✅ Verifica che sia la sessione corretta

**Esempio:**
```bash
./session_manager.sh stop my_test_session
```

### **4. Stato Sessioni**
```bash
./session_manager.sh status
```
- 📊 Mostra processi attivi
- 🔗 Informazioni sessione (TTY, User, Start time)
- 🔍 Operazioni attive (backtest, generazione, etc.)

### **5. Pulizia Completa**
```bash
./session_manager.sh cleanup
```
- 🧹 Ferma tutti i processi
- 🔓 Rimuove tutti i lock
- ✅ Reset completo

### **6. Log Sessioni**
```bash
./session_manager.sh logs
```
- 📋 Mostra log delle sessioni
- 🕐 Timestamp di tutte le operazioni
- 📄 Ultime 20 righe

## 🎯 **Workflow Raccomandato**

### **Per i Test (Tu)**
```bash
# 1. Controlla stato attuale
./session_manager.sh status

# 2. Se necessario, pulisci
./session_manager.sh cleanup

# 3. Avvia sessione controllata
./session_manager.sh start my_test

# 4. Esegui i tuoi test
# ... i tuoi comandi ...

# 5. Ferma sessione
./session_manager.sh stop my_test
```

### **Per il Monitoraggio (Io)**
```bash
# 1. Controlla se c'è una sessione attiva
./session_manager.sh status

# 2. Se c'è una sessione, unisciti
./session_manager.sh join my_test

# 3. Monitora senza interferire
./manage_background_agent.sh logs
./manage_background_agent.sh backtest
```

## 📊 **Esempio di Output**

### **Stato Sessioni**
```
🔍 Stato Sessioni Background Agent

🔒 Sessione attiva: my_test_session

📊 Processi Background Agent Attivi: 1

📋 Dettagli Processi:

🔄 Processo #1:
   🆔 PID: 29625
   ⏱️  Uptime:       19:58
   💾 Memoria: 29.125 MB
   📊 CPU:  0.0%
   🔗 Sessione: TTY: pts/0, User: dria10, Start: dom giu 29 10:34:03 2025
   📌 PID Memorizzato: Sì

🔍 Operazioni Attive:
   📊 Backtest attivi: 0
   🎯 Generazione strategie: 0
   ✅ Validazione strategie: 0
   🔧 Ottimizzazione strategie: 0
```

### **Log Sessioni**
```
📋 Log Session Manager

📄 File di log: session_manager.log
💡 Ultime 20 righe:

[2025-06-29 10:34:03] 🔒 Lock creato per sessione: my_test_session
[2025-06-29 10:34:05] ✅ Sessione avviata con successo
[2025-06-29 10:35:12] ✅ Nuovo utente unito alla sessione: my_test_session
[2025-06-29 10:40:23] ✅ Sessione fermata con successo
```

## ⚠️ **Gestione Errori**

### **Sessione Già Attiva**
```
❌ Sessione già attiva: my_test_session
💡 Usa 'join' per unirti alla sessione esistente
```

### **Processi Già Attivi**
```
⚠️ Processi già attivi (2)
💡 Usa 'cleanup' per pulire prima di avviare
```

### **Sessione Non Corrisponde**
```
❌ Sessione non corrisponde: attesa my_test, trovata other_session
```

## 🔄 **Integrazione con Comandi Esistenti**

Il Session Manager **non sostituisce** i comandi esistenti, ma li **complementa**:

### **Comandi Originali (sempre disponibili)**
```bash
./manage_background_agent.sh start
./manage_background_agent.sh stop
./manage_background_agent.sh status
./manage_background_agent.sh logs
```

### **Comandi Session Manager (per controllo centralizzato)**
```bash
./session_manager.sh start my_session
./session_manager.sh join my_session
./session_manager.sh stop my_session
./session_manager.sh status
```

## 🎯 **Best Practices**

### **1. Usa ID Sessione Descritivi**
```bash
# ✅ Buono
./session_manager.sh start testing_strategies
./session_manager.sh start production_run
./session_manager.sh start optimization_test

# ❌ Evita
./session_manager.sh start test
./session_manager.sh start session1
```

### **2. Controlla Sempre lo Stato**
```bash
# Prima di qualsiasi operazione
./session_manager.sh status
```

### **3. Pulisci Dopo i Test**
```bash
# Dopo aver finito i test
./session_manager.sh cleanup
```

### **4. Usa Join per Monitoraggio**
```bash
# Per monitorare senza interferire
./session_manager.sh join existing_session
```

## 📝 **File di Sistema**

### **File Creati dal Session Manager**
- `session.lock` - Lock della sessione attiva
- `session_manager.log` - Log delle operazioni
- `session_manager.sh` - Script principale

### **File Esistenti (non modificati)**
- `background_agent.pid` - PID del processo
- `background_config.json` - Configurazione
- `logs/` - Directory log

## ✅ **Vantaggi**

1. **🎯 Controllo Centralizzato**: Una sola sessione controllata alla volta
2. **🤝 Collaborazione**: Possibilità di unirsi a sessioni esistenti
3. **📊 Trasparenza**: Informazioni dettagliate su chi usa cosa
4. **🧹 Pulizia**: Gestione automatica dei conflitti
5. **📝 Tracciabilità**: Log di tutte le operazioni
6. **🔄 Compatibilità**: Funziona con i comandi esistenti

## 🚀 **Prossimi Passi**

1. **Testa il Session Manager** con una sessione controllata
2. **Usa 'join'** quando vuoi monitorare senza interferire
3. **Pulisci sempre** dopo i test
4. **Condividi l'ID sessione** quando collaboriamo

Questo sistema risolve il problema delle sessioni multiple e fornisce un'interfaccia pulita per la collaborazione! 