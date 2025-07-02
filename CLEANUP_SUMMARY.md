# 🧹 Riepilogo Pulizia Strategie

## ❓ **Risposta alla Tua Domanda**

**La pulizia delle strategie è prevista per TUTTE le strategie che soddisfano i criteri di rimozione, non solo quelle che non funzionano.**

## 🎯 **Criteri di Pulizia**

### **1. Età delle Strategie**
- **Criterio**: Strategie più vecchie di 30 giorni
- **Configurazione**: `max_strategy_age_days: 30`
- **Logica**: Le strategie diventano obsolete nel tempo
- **Applicazione**: **TUTTE le strategie**, indipendentemente dalle performance

### **2. Punteggio Backtest Basso**
- **Criterio**: Strategie con punteggio backtest < 0.1
- **Configurazione**: `min_backtest_score: 0.1`
- **Logica**: Strategie con performance scarse
- **Applicazione**: Solo strategie che hanno completato un backtest

### **3. Combinazione dei Criteri**
Il sistema rimuove strategie che soddisfano **ALMENO UNO** dei criteri:
- ✅ **Vecchie** (età > 30 giorni) **O**
- ✅ **Scarse** (punteggio < 0.1)

## 📊 **Esempi Pratici**

### **Strategie che VERRANNO rimosse:**
```
❌ OldGoodStrategy_phi3_20240501_120000
   📅 Età: 35 giorni (max: 30)
   📊 Punteggio: 0.15 (buono)
   ⚠️  Criterio: Età > 30 giorni

❌ NewBadStrategy_llama2_20250629_140000
   📅 Età: 2 giorni (nuova)
   📊 Punteggio: 0.05 (basso)
   ⚠️  Criterio: Punteggio < 0.1

❌ OldNoBacktestStrategy_mistral_20250620_160000
   📅 Età: 35 giorni (vecchia)
   📊 Punteggio: N/A (senza backtest)
   ⚠️  Criterio: Età > 30 giorni
```

### **Strategie che RIMARRANNO:**
```
✅ NewGoodStrategy_phi3_20250629_150000
   📅 Età: 1 giorno (nuova)
   📊 Punteggio: 0.12 (buono)
   ✅ Sicura: Nessun criterio soddisfatto

✅ NewNoBacktestStrategy_llama2_20250629_160000
   📅 Età: 5 giorni (nuova)
   📊 Punteggio: N/A (senza backtest)
   ✅ Sicura: Età < 30 giorni

✅ BorderlineStrategy_phi3_20250629_170000
   📅 Età: 29 giorni (al limite)
   📊 Punteggio: 0.11 (buono)
   ✅ Sicura: Età = 29 giorni
```

## 🔧 **Strumenti Disponibili**

### **1. Analisi Pulizia**
```bash
# Analisi completa delle strategie attuali
./manage_background_agent.sh cleanup-analysis

# Oppure direttamente
python analyze_cleanup.py
```

### **2. Test Scenari**
```bash
# Testa diversi scenari di pulizia
python test_cleanup_scenarios.py
```

### **3. Configurazione**
```bash
# Modifica parametri di pulizia
./manage_background_agent.sh config
```

## ⚙️ **Configurazione Personalizzabile**

### **Disabilitare la Pulizia**
```json
{
  "cleanup_old_strategies": false
}
```

### **Criteri Più Permissivi**
```json
{
  "min_backtest_score": 0.05,      // Più permissivo
  "max_strategy_age_days": 60      // Più permissivo
}
```

### **Criteri Più Restrittivi**
```json
{
  "min_backtest_score": 0.2,       // Più restrittivo
  "max_strategy_age_days": 7       // Più restrittivo
}
```

## ⏰ **Programmazione**

- **Frequenza**: Ogni giorno alle 02:00
- **Automatico**: Si esegue senza intervento manuale
- **Log**: Tutte le operazioni vengono registrate

## 📝 **Log della Pulizia**

### **Esempio di Log**
```
INFO:__main__:🧹 Rimosse 3 strategie vecchie
INFO:__main__:🗑️ Rimosso file: user_data/strategies/volatilitystrategy_phi3_20240501_120000.py
INFO:__main__:🗑️ Rimosso file: user_data/strategies/scalpingstrategy_llama2_20250625_140000.py
INFO:__main__:🗑️ Rimosso file: user_data/strategies/breakoutstrategy_mistral_20250620_150000.py
```

### **Monitoraggio**
```bash
# Controlla i log di pulizia
grep "Rimosse\|Rimosso file" logs/background_agent_*.log

# Controlla lo stato delle strategie
./manage_background_agent.sh status
```

## ⚠️ **Considerazioni Importanti**

### **1. Strategie Senza Backtest**
- **Non vengono rimosse** se sono nuove (< 30 giorni)
- **Vengono rimosse** se sono vecchie (> 30 giorni)
- **Raccomandazione**: Esegui backtest regolarmente

### **2. Strategie Attive**
- **Vengono rimosse** se soddisfano i criteri
- **Non c'è protezione** per strategie "attive"
- **Attenzione**: Controlla prima di attivare strategie importanti

### **3. Backup**
- **Non c'è backup automatico** delle strategie rimosse
- **Raccomandazione**: Fai backup manuali delle strategie importanti
- **Soluzione**: Usa `git` per versionare le strategie

## 🎯 **Best Practices**

### **1. Monitoraggio Regolare**
```bash
# Controlla lo stato delle strategie
./manage_background_agent.sh status

# Controlla i log di pulizia
tail -f logs/background_agent_*.log | grep "Rimosse"
```

### **2. Configurazione Appropriata**
```json
{
  "cleanup_old_strategies": true,
  "min_backtest_score": 0.1,        // Adatta alle tue esigenze
  "max_strategy_age_days": 30       // Adatta alle tue esigenze
}
```

### **3. Backup delle Strategie Importanti**
```bash
# Backup manuale
cp user_data/strategies/strategia_importante.py backup/

# Versioning con git
git add user_data/strategies/
git commit -m "Backup strategie prima della pulizia"
```

## ✅ **Conclusione**

**La pulizia rimuove TUTTE le strategie che soddisfano i criteri:**

- ✅ **Strategie vecchie** (> 30 giorni)
- ✅ **Strategie con punteggio basso** (< 0.1)
- ✅ **Indipendentemente** dal fatto che "funzionino" o meno

**Il sistema è progettato per mantenere solo strategie:**
- 📅 **Recenti** (≤ 30 giorni) **E**
- 📊 **Performanti** (≥ 0.1 punteggio)

**Raccomandazione**: Configura i parametri in base alle tue esigenze e fai backup delle strategie importanti! 🎯

## 📚 **Documentazione Completa**

- 📄 [STRATEGY_CLEANUP.md](STRATEGY_CLEANUP.md) - Documentazione dettagliata
- 🧪 [test_cleanup_scenarios.py](test_cleanup_scenarios.py) - Test scenari
- 📊 [analyze_cleanup.py](analyze_cleanup.py) - Analisi pulizia
- 🔧 [manage_background_agent.sh](manage_background_agent.sh) - Gestione agente 