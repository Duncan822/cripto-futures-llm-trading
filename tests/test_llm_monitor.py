#!/usr/bin/env python3
"""
Test completo del sistema di monitoraggio LLM.
Verifica tutte le funzionalità del monitor.
"""

import time
import requests
import json
import subprocess
import sys
from pathlib import Path

def test_monitor_startup():
    """Test dell'avvio del monitor."""
    print("🧪 Test avvio monitor...")

    try:
        # Avvia il monitor
        result = subprocess.run([
            "./start_llm_monitor.sh", "start", "8082"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("✅ Monitor avviato con successo")
            return True
        else:
            print(f"❌ Errore nell'avvio: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Timeout nell'avvio del monitor")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_api_endpoints():
    """Test degli endpoint API."""
    print("🌐 Test endpoint API...")

    base_url = "http://localhost:8082"
    endpoints = [
        "/api/status",
        "/api/models",
        "/api/stats",
        "/api/active",
        "/api/requests"
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {endpoint} - Errore: {e}")
            return False

    return True

def test_dashboard():
    """Test della dashboard web."""
    print("📊 Test dashboard web...")

    try:
        response = requests.get("http://localhost:8082/", timeout=10)
        if response.status_code == 200 and "LLM Monitor Dashboard" in response.text:
            print("✅ Dashboard caricata correttamente")
            return True
        else:
            print(f"❌ Dashboard non caricata correttamente (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Errore nel caricamento dashboard: {e}")
        return False

def test_monitored_requests():
    """Test delle richieste monitorate."""
    print("📝 Test richieste monitorate...")

    try:
        # Importa le funzioni monitorate
        sys.path.append('.')
        from llm_utils_monitored import query_ollama_fast_monitored, get_active_requests

        # Test di una richiesta semplice
        response = query_ollama_fast_monitored(
            "Rispondi solo con 'Test completato'",
            "phi3",
            timeout=30
        )

        if "Test completato" in response:
            print("✅ Richiesta monitorata completata")

            # Controlla che sia stata tracciata
            time.sleep(2)  # Attendi aggiornamento
            active = get_active_requests()
            if len(active) == 0:  # Dovrebbe essere completata
                print("✅ Tracciamento richiesta funzionante")
                return True
            else:
                print("⚠️ Richiesta ancora attiva")
                return False
        else:
            print(f"❌ Risposta inaspettata: {response}")
            return False

    except Exception as e:
        print(f"❌ Errore nel test richieste: {e}")
        return False

def test_model_status():
    """Test dello stato dei modelli."""
    print("🤖 Test stato modelli...")

    try:
        response = requests.get("http://localhost:8082/api/models", timeout=10)
        models = response.json()

        if len(models) > 0:
            print(f"✅ {len(models)} modelli configurati")

            # Controlla che almeno un modello sia disponibile
            available_models = [m for m in models if m.get('is_available', False)]
            if len(available_models) > 0:
                print(f"✅ {len(available_models)} modelli disponibili")
                return True
            else:
                print("⚠️ Nessun modello disponibile (normale se Ollama non è avviato)")
                return True  # Non è un errore se Ollama non è avviato
        else:
            print("❌ Nessun modello configurato")
            return False

    except Exception as e:
        print(f"❌ Errore nel test stato modelli: {e}")
        return False

def test_monitor_stop():
    """Test dell'arresto del monitor."""
    print("🛑 Test arresto monitor...")

    try:
        result = subprocess.run([
            "./start_llm_monitor.sh", "stop"
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            print("✅ Monitor fermato con successo")
            return True
        else:
            print(f"❌ Errore nell'arresto: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def main():
    """Test principale."""
    print("🚀 Test completo del sistema di monitoraggio LLM")
    print("=" * 50)

    tests = [
        ("Avvio Monitor", test_monitor_startup),
        ("API Endpoints", test_api_endpoints),
        ("Dashboard Web", test_dashboard),
        ("Stato Modelli", test_model_status),
        ("Richieste Monitorate", test_monitored_requests),
        ("Arresto Monitor", test_monitor_stop)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Risultati: {passed}/{total} test superati")

    if passed == total:
        print("🎉 Tutti i test superati! Il sistema di monitoraggio funziona correttamente.")
        return True
    else:
        print("⚠️ Alcuni test falliti. Controlla i log per dettagli.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
