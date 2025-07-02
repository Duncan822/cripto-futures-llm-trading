#!/usr/bin/env python3
"""
Test script per verificare che backtest e hyperopt funzionino correttamente.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_freqtrade_installation():
    """Testa se Freqtrade è installato correttamente."""
    try:
        import subprocess
        result = subprocess.run(["freqtrade", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Freqtrade installato: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ Freqtrade non funziona: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.error("❌ Freqtrade non trovato nel PATH")
        return False

def test_config_files():
    """Testa se i file di configurazione esistono."""
    config_files = [
        "user_data/config.json",
        "user_data/hyperopt_config.json"
    ]
    
    all_exist = True
    for config_file in config_files:
        if os.path.exists(config_file):
            logger.info(f"✅ {config_file} trovato")
        else:
            logger.error(f"❌ {config_file} mancante")
            all_exist = False
    
    return all_exist

def test_strategy_directory():
    """Testa se la directory delle strategie esiste e ha strategie."""
    strategies_dir = "user_data/strategies"
    
    if not os.path.exists(strategies_dir):
        logger.error(f"❌ Directory {strategies_dir} non trovata")
        return False
    
    strategies = [f for f in os.listdir(strategies_dir) if f.endswith('.py') and not f.startswith('__')]
    
    if strategies:
        logger.info(f"✅ Trovate {len(strategies)} strategie: {strategies}")
        return True
    else:
        logger.warning(f"⚠️ Nessuna strategia trovata in {strategies_dir}")
        return False

def test_data_directory():
    """Testa se ci sono dati storici disponibili."""
    data_dir = "user_data/data"
    
    if not os.path.exists(data_dir):
        logger.error(f"❌ Directory {data_dir} non trovata")
        return False
    
    # Cerca file di dati
    data_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.json'):
                data_files.append(os.path.join(root, file))
    
    if data_files:
        logger.info(f"✅ Trovati {len(data_files)} file di dati")
        return True
    else:
        logger.warning(f"⚠️ Nessun file di dati trovato in {data_dir}")
        return False

def test_backtest_command():
    """Testa se il comando backtest funziona."""
    try:
        import subprocess
        
        # Cerca una strategia da testare
        strategies_dir = "user_data/strategies"
        if not os.path.exists(strategies_dir):
            logger.error("❌ Directory strategie non trovata")
            return False
        
        strategies = [f[:-3] for f in os.listdir(strategies_dir) if f.endswith('.py') and not f.startswith('__')]
        
        if not strategies:
            logger.error("❌ Nessuna strategia trovata per il test")
            return False
        
        strategy_name = strategies[0]
        logger.info(f"🧪 Testando backtest con strategia: {strategy_name}")
        
        # Esegui backtest di test (solo validazione)
        cmd = [
            "freqtrade", "backtesting",
            "--config", "user_data/config.json",
            "--strategy", strategy_name,
            "--timerange", "20240101-20240102"  # Solo 1 giorno per test veloce
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Comando backtest funziona")
            return True
        else:
            logger.error(f"❌ Errore nel comando backtest: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout nel comando backtest")
        return False
    except Exception as e:
        logger.error(f"❌ Errore nel test backtest: {e}")
        return False

def test_hyperopt_command():
    """Testa se il comando hyperopt funziona."""
    try:
        import subprocess
        
        # Cerca una strategia da testare
        strategies_dir = "user_data/strategies"
        if not os.path.exists(strategies_dir):
            logger.error("❌ Directory strategie non trovata")
            return False
        
        strategies = [f[:-3] for f in os.listdir(strategies_dir) if f.endswith('.py') and not f.startswith('__')]
        
        if not strategies:
            logger.error("❌ Nessuna strategia trovata per il test")
            return False
        
        strategy_name = strategies[0]
        logger.info(f"🧪 Testando hyperopt con strategia: {strategy_name}")
        
        # Esegui hyperopt di test (solo 1 epoch per test veloce)
        cmd = [
            "freqtrade", "hyperopt",
            "--config", "user_data/config.json",
            "--strategy", strategy_name,
            "--epochs", "1",
            "--timerange", "20240101-20240102",  # Solo 1 giorno per test veloce
            "--spaces", "buy"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("✅ Comando hyperopt funziona")
            return True
        else:
            logger.error(f"❌ Errore nel comando hyperopt: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Timeout nel comando hyperopt")
        return False
    except Exception as e:
        logger.error(f"❌ Errore nel test hyperopt: {e}")
        return False

def main():
    """Esegue tutti i test."""
    logger.info("🧪 Iniziando test del sistema Freqtrade...")
    
    tests = [
        ("Installazione Freqtrade", test_freqtrade_installation),
        ("File di configurazione", test_config_files),
        ("Directory strategie", test_strategy_directory),
        ("Directory dati", test_data_directory),
        ("Comando backtest", test_backtest_command),
        ("Comando hyperopt", test_hyperopt_command)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Test: {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Errore nel test {test_name}: {e}")
            results.append((test_name, False))
    
    # Report finale
    logger.info("\n" + "="*50)
    logger.info("📊 REPORT FINALE TEST")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nRisultato: {passed}/{total} test passati")
    
    if passed == total:
        logger.info("🎉 Tutti i test sono passati! Il sistema è pronto per backtest e hyperopt.")
        return True
    else:
        logger.error("⚠️ Alcuni test sono falliti. Controlla la configurazione.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 