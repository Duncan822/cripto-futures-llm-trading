# 🧹 Pulizia Strategie nel Background Agent

## ❓ **Risposta alla Tua Domanda**

**La pulizia delle strategie è prevista per TUTTE le strategie che soddisfano i criteri di rimozione, non solo quelle che non funzionano.**

Il sistema utilizza **criteri multipli** per decidere quali strategie rimuovere.

## 🔍 **Criteri di Pulizia**

### **1. Età delle Strategie**
```json
"max_strategy_age_days": 30
```
- **Criterio**: Strategie più vecchie di 30 giorni
- **Logica**: Le strategie diventano obsolete nel tempo
- **Applicazione**: Tutte le strategie, indipendentemente dalle performance

### **2. Punteggio Backtest Basso**
```json
"min_backtest_score": 0.1
```
- **Criterio**: Strategie con punteggio backtest < 0.1
- **Logica**: Strategie con performance scarse
- **Applicazione**: Solo strategie che hanno completato un backtest

### **3. Combinazione dei Criteri**
Il sistema rimuove strategie che soddisfano **ALMENO UNO** dei criteri:
- ✅ **Vecchie** (età > 30 giorni) **O**
- ✅ **Scarse** (punteggio < 0.1)

## 📊 **Codice della Pulizia**

```python
def cleanup_old_strategies(self):
    """Rimuove strategie vecchie e con punteggi bassi."""
    if not self.config.get('cleanup_old_strategies', True):
        return
    
    try:
        current_time = datetime.now()
        min_score = self.config.get('min_backtest_score', 0.1)
        max_age_days = self.config.get('max_strategy_age_days', 30)
        
        strategies_to_remove = []
        
        for name, metadata in self.strategies_metadata.items():
            # Controlla età
            age_days = (current_time - metadata.generation_time).days
            
            # Controlla punteggio
            low_score = (metadata.backtest_score is not None and 
                       metadata.backtest_score < min_score)
            
            if age_days > max_age_days or low_score:
                strategies_to_remove.append(name)
        
        # Rimuovi strategie
        for name in strategies_to_remove:
            metadata = self.strategies_metadata[name]
            
            # Rimuovi file
            if os.path.exists(metadata.file_path):
                os.remove(metadata.file_path)
                logger.info(f"🗑️ Rimosso file: {metadata.file_path}")
            
            # Rimuovi dai metadati
            del self.strategies_metadata[name]
        
        if strategies_to_remove:
            self._save_metadata()
            logger.info(f"🧹 Rimosse {len(strategies_to_remove)} strategie vecchie")
            
    except Exception as e:
        logger.error(f"❌ Errore nella pulizia strategie: {e}")
```

## ⏰ **Programmazione della Pulizia**

### **Frequenza**
```python
# Pulizia periodica
schedule.every().day.at("02:00").do(self.cleanup_old_strategies)
```

- **Quando**: Ogni giorno alle 02:00
- **Automatico**: Si esegue senza intervento manuale
- **Log**: Tutte le operazioni vengono registrate

### **Configurazione**
```json
{
  "cleanup_old_strategies": true,
  "min_backtest_score": 0.1,
  "max_strategy_age_days": 30
}
```

## 📋 **Esempi di Strategie Rimosse**

### **Esempio 1: Strategia Vecchia con Buon Punteggio**
```
Nome: VolatilityStrategy_phi3_20240501_120000
Età: 35 giorni
Punteggio: 0.15 (buono)
Risultato: ❌ RIMOSSA (età > 30 giorni)
```

### **Esempio 2: Strategia Nuova con Punteggio Basso**
```
Nome: ScalpingStrategy_llama2_20250629_140000
Età: 2 giorni
Punteggio: 0.05 (basso)
Risultato: ❌ RIMOSSA (punteggio < 0.1)
```

### **Esempio 3: Strategia Nuova con Punteggio Buono**
```
Nome: BreakoutStrategy_mistral_20250629_150000
Età: 1 giorno
Punteggio: 0.12 (buono)
Risultato: ✅ MANTENUTA (nessun criterio soddisfatto)
```

### **Esempio 4: Strategia Senza Backtest**
```
Nome: MomentumStrategy_phi3_20250629_160000
Età: 5 giorni
Punteggio: Nessuno (backtest non eseguito)
Risultato: ✅ MANTENUTA (età < 30 giorni)
```

## 🎯 **Logica di Decisione**

### **Albero Decisionale**
```
Strategia da valutare
    ↓
Controlla età > 30 giorni?
    ↓ Sì
    ❌ RIMUOVI
    ↓ No
Controlla punteggio < 0.1?
    ↓ Sì
    ❌ RIMUOVI
    ↓ No
    ✅ MANTIENI
```

### **Priorità dei Criteri**
1. **Età**: Criterio assoluto (indipendentemente dal punteggio)
2. **Punteggio**: Solo se il backtest è stato eseguito
3. **Combinazione**: Se entrambi i criteri sono soddisfatti

## ⚙️ **Configurazione Personalizzabile**

### **Disabilitare la Pulizia**
```json
{
  "cleanup_old_strategies": false
}
```

### **Modificare i Criteri**
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

## 🔧 **Pulizia Manuale**

### **Forzare la Pulizia**
```python
# Nel codice Python
agent.cleanup_old_strategies()
```

### **Pulizia Selettiva**
```python
# Rimuovi solo strategie vecchie
for name, metadata in agent.strategies_metadata.items():
    age_days = (datetime.now() - metadata.generation_time).days
    if age_days > 30:
        # Rimuovi strategia
        pass
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