#!/usr/bin/env python3
"""
Wrapper per le funzioni LLM con monitoraggio automatico.
Integra il sistema di monitoraggio con le funzioni esistenti.
"""

import uuid
import time
from typing import Optional
from llm_utils import query_ollama, query_ollama_fast
from llm_monitor import track_llm_request, update_llm_request

def query_ollama_monitored(prompt: str, model: str = "mistral", timeout: int = 1800) -> str:
    """
    Versione monitorata di query_ollama.
    Traccia automaticamente la richiesta nel monitor.
    """
    request_id = str(uuid.uuid4())

    try:
        # Traccia l'inizio della richiesta
        track_llm_request(request_id, model, prompt, timeout)

        # Esegui la richiesta originale
        start_time = time.time()
        response = query_ollama(prompt, model, timeout)
        duration = time.time() - start_time

        # Aggiorna lo stato con successo
        update_llm_request(request_id, "completed", response)

        return response

    except Exception as e:
        # Aggiorna lo stato con errore
        update_llm_request(request_id, "failed", error=str(e))
        raise

def query_ollama_fast_monitored(prompt: str, model: str = "phi3", timeout: int = 600) -> str:
    """
    Versione monitorata di query_ollama_fast.
    Traccia automaticamente la richiesta nel monitor.
    """
    request_id = str(uuid.uuid4())

    try:
        # Traccia l'inizio della richiesta
        track_llm_request(request_id, model, prompt, timeout)

        # Esegui la richiesta originale
        start_time = time.time()
        response = query_ollama_fast(prompt, model, timeout)
        duration = time.time() - start_time

        # Aggiorna lo stato con successo
        update_llm_request(request_id, "completed", response)

        return response

    except Exception as e:
        # Aggiorna lo stato con errore
        update_llm_request(request_id, "failed", error=str(e))
        raise

def query_ollama_with_timeout_monitoring(prompt: str, model: str = "mistral", timeout: int = 1800) -> str:
    """
    Versione con monitoraggio del timeout.
    Traccia anche i timeout come errori specifici.
    """
    request_id = str(uuid.uuid4())

    try:
        # Traccia l'inizio della richiesta
        track_llm_request(request_id, model, prompt, timeout)

        # Esegui la richiesta con gestione timeout
        start_time = time.time()
        response = query_ollama(prompt, model, timeout)
        duration = time.time() - start_time

        # Aggiorna lo stato con successo
        update_llm_request(request_id, "completed", response)

        return response

    except Exception as e:
        error_type = "timeout" if "timeout" in str(e).lower() else "failed"
        update_llm_request(request_id, error_type, error=str(e))
        raise

# Funzioni di utilità per il monitoraggio

def get_monitor_status():
    """Restituisce lo stato del monitor."""
    from llm_monitor import get_monitor
    monitor = get_monitor()
    return monitor.get_status() if monitor.is_running else None

def get_active_requests():
    """Restituisce le richieste attualmente attive."""
    from llm_monitor import get_monitor
    monitor = get_monitor()
    return monitor.get_active_requests() if monitor.is_running else []

def get_recent_requests(limit: int = 10):
    """Restituisce le richieste più recenti."""
    from llm_monitor import get_monitor
    monitor = get_monitor()
    return monitor.get_recent_requests(limit) if monitor.is_running else []

def get_model_performance():
    """Restituisce le performance dei modelli."""
    from llm_monitor import get_monitor
    monitor = get_monitor()
    return monitor.get_model_performance() if monitor.is_running else {}

# Funzioni per avviare/fermare il monitoraggio

def start_llm_monitoring(port: int = 8080):
    """Avvia il monitoraggio LLM."""
    from llm_monitor import start_monitoring
    return start_monitoring(port)

def stop_llm_monitoring():
    """Ferma il monitoraggio LLM."""
    from llm_monitor import stop_monitoring
    stop_monitoring()

# Funzione per test rapido
def test_monitored_llm():
    """Test rapido del sistema di monitoraggio."""
    print("🧪 Test del sistema di monitoraggio LLM...")

    try:
        # Avvia il monitor
        monitor = start_llm_monitoring(port=8081)
        print("✅ Monitor avviato su porta 8081")

        # Test di una richiesta
        print("📝 Test richiesta monitorata...")
        response = query_ollama_fast_monitored(
            "Rispondi solo con 'Test completato'",
            "phi3",
            timeout=30
        )
        print(f"✅ Risposta: {response}")

        # Mostra stato
        status = get_monitor_status()
        print(f"📊 Stato monitor: {status}")

        # Mostra richieste attive
        active = get_active_requests()
        print(f"⚡ Richieste attive: {len(active)}")

        return True

    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        return False

if __name__ == "__main__":
    test_monitored_llm()
