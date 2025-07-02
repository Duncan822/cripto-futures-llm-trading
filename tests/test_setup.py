#!/usr/bin/env python3
"""
Script di test per verificare la configurazione Freqtrade.
Esegue test di base per assicurarsi che tutto sia configurato correttamente.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def test_environment():
    """Test dell'ambiente Python e dipendenze."""
    print("🔍 Test ambiente Python...")

    # Verifica Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("❌ Python 3.9+ richiesto")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Verifica ambiente virtuale
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Ambiente virtuale attivo")
    else:
        print("⚠️ Ambiente virtuale non rilevato (opzionale)")

    return True

def test_dependencies():
    """Test delle dipendenze installate."""
    print("\n🔍 Test dipendenze...")

    required_packages = [
        'freqtrade',
        'pandas',
        'numpy',
        'ccxt',
        'requests'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} mancante")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ Pacchetti mancanti: {', '.join(missing_packages)}")
        print("Esegui: pip install -r requirements.txt")
        return False

    return True

def test_freqtrade_installation():
    """Test dell'installazione Freqtrade."""
    print("\n🔍 Test installazione Freqtrade...")

    try:
        result = subprocess.run(['freqtrade', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Freqtrade installato: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Errore Freqtrade: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Freqtrade non trovato nel PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout nel test Freqtrade")
        return False

def test_configuration_files():
    """Test dei file di configurazione."""
    print("\n🔍 Test file di configurazione...")

    config_files = [
        'user_data/config.json',
        'user_data/strategies/LLMStrategy.py'
    ]

    all_exist = True
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ {config_file}")
        else:
            print(f"❌ {config_file} mancante")
            all_exist = False

    return all_exist

def test_freqtrade_config():
    """Test della configurazione Freqtrade."""
    print("\n🔍 Test configurazione Freqtrade...")

    try:
        result = subprocess.run([
            'freqtrade', 'show-config',
            '--config', 'user_data/config.json'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Configurazione Freqtrade valida")
            return True
        else:
            print(f"❌ Errore configurazione: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Errore test configurazione: {e}")
        return False

def test_strategy_validation():
    """Test della validazione strategia."""
    print("\n🔍 Test validazione strategia...")

    try:
        result = subprocess.run([
            'freqtrade', 'show-config',
            '--config', 'user_data/config.json',
            '--strategy', 'LLMStrategy'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Strategia LLMStrategy valida")
            return True
        else:
            print(f"❌ Errore strategia: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Errore test strategia: {e}")
        return False

def test_directory_structure():
    """Test della struttura directory."""
    print("\n🔍 Test struttura directory...")

    required_dirs = [
        'user_data',
        'user_data/strategies',
        'user_data/data',
        'user_data/logs',
        'user_data/backtest_results',
        'user_data/hyperopt_results'
    ]

    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ mancante")
            all_exist = False

    return all_exist

def test_ollama():
    """Test di Ollama (opzionale)."""
    print("\n🔍 Test Ollama...")

    try:
        result = subprocess.run(['ollama', 'list'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Ollama disponibile")
            models = result.stdout.strip().split('\n')[1:]  # Skip header
            available_models = []
            for line in models:
                if line.strip():
                    model_name = line.split()[0]
                    available_models.append(model_name)

            print(f"📋 Modelli disponibili: {', '.join(available_models) if available_models else 'Nessuno'}")

            # Check for required models
            required_models = ['mistral', 'llama2', 'phi3']
            missing_models = [model for model in required_models if model not in available_models]

            if missing_models:
                print(f"⚠️ Modelli mancanti: {', '.join(missing_models)}")
                print("Esegui: ollama pull <model_name>")
            else:
                print("✅ Tutti i modelli richiesti disponibili")

            return True
        else:
            print("❌ Ollama non risponde correttamente")
            return False
    except FileNotFoundError:
        print("⚠️ Ollama non installato (opzionale)")
        return True
    except Exception as e:
        print(f"❌ Errore test Ollama: {e}")
        return False

def test_imports():
    """Test degli import Python."""
    print("\n🔍 Test import Python...")

    try:
        from freqtrade_utils import FreqtradeManager
        print("✅ freqtrade_utils importato")

        from agents.generator import GeneratorAgent
        print("✅ agents.generator importato")

        from agents.reviewer import ReviewerAgent
        print("✅ agents.reviewer importato")

        from agents.optimizer import OptimizerAgent
        print("✅ agents.optimizer importato")

        return True
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        return False

def main():
    """Funzione principale di test."""
    print("🚀 Test Setup Crypto Futures LLM Trading")
    print("=" * 50)

    tests = [
        ("Ambiente Python", test_environment),
        ("Dipendenze", test_dependencies),
        ("Installazione Freqtrade", test_freqtrade_installation),
        ("File Configurazione", test_configuration_files),
        ("Configurazione Freqtrade", test_freqtrade_config),
        ("Validazione Strategia", test_strategy_validation),
        ("Struttura Directory", test_directory_structure),
        ("Ollama", test_ollama),
        ("Import Python", test_imports)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Errore in {test_name}: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Risultati: {passed}/{total} test superati")

    if passed == total:
        print("🎉 Setup completato con successo!")
        print("\nProssimi passi:")
        print("1. source venv/bin/activate")
        print("2. ./manage_background_agent.sh start")
        print("3. ./run_backtest.sh")
    else:
        print("⚠️ Alcuni test falliti. Controlla i messaggi sopra.")
        print("\nPer risolvere:")
        print("1. Esegui: ./setup_freqtrade.sh")
        print("2. Verifica che Ollama sia installato")
        print("3. Controlla le dipendenze Python")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
