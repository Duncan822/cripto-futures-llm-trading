#!/usr/bin/env python3
"""
LLM Monitor: Sistema di monitoraggio completo per gli LLM in esecuzione.
Traccia stato, attività, performance e fornisce dashboard web.
"""

import os
import time
import json
import logging
import threading
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import queue
import subprocess
from flask import Flask, render_template, jsonify, request
import webbrowser

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LLMRequest:
    """Rappresenta una richiesta LLM in corso."""
    id: str
    model: str
    prompt: str
    start_time: datetime
    timeout: int
    status: str  # "running", "completed", "failed", "timeout"
    response: Optional[str] = None
    error: Optional[str] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    tokens_generated: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None

@dataclass
class ModelStatus:
    """Stato di un modello LLM."""
    name: str
    is_available: bool
    last_check: datetime
    response_time: Optional[float] = None
    error_count: int = 0
    success_count: int = 0
    total_requests: int = 0
    avg_response_time: Optional[float] = None

class LLMMonitor:
    """
    Monitor completo per gli LLM in esecuzione.
    """

    def __init__(self, port: int = 8080):
        self.port = port
        self.requests: Dict[str, LLMRequest] = {}
        self.model_status: Dict[str, ModelStatus] = {}
        self.active_requests: Dict[str, LLMRequest] = {}
        self.request_queue = queue.Queue()
        self.is_running = False
        self.monitor_thread = None
        self.flask_app = None
        self.flask_thread = None

        # Statistiche
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "avg_response_time": 0.0,
            "start_time": datetime.now()
        }

        # Inizializza stato modelli
        self._init_model_status()

    def _init_model_status(self):
        """Inizializza lo stato dei modelli disponibili."""
        models = ["phi3", "llama2", "mistral", "cogito:8b"]
        for model in models:
            self.model_status[model] = ModelStatus(
                name=model,
                is_available=False,
                last_check=datetime.now()
            )

    def start(self):
        """Avvia il monitor."""
        if self.is_running:
            logger.warning("Monitor già in esecuzione")
            return

        self.is_running = True

        # Avvia thread di monitoraggio
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        # Avvia dashboard web
        self._start_dashboard()

        logger.info(f"✅ LLM Monitor avviato su porta {self.port}")
        logger.info(f"🌐 Dashboard disponibile su http://localhost:{self.port}")

        # Apri browser automaticamente
        try:
            webbrowser.open(f"http://localhost:{self.port}")
        except:
            pass

    def stop(self):
        """Ferma il monitor."""
        self.is_running = False
        if self.flask_thread:
            self.flask_thread.join(timeout=5)
        logger.info("🛑 LLM Monitor fermato")

    def _start_dashboard(self):
        """Avvia la dashboard web Flask."""
        self.flask_app = Flask(__name__)

        @self.flask_app.route('/')
        def dashboard():
            return render_template('llm_dashboard.html')

        @self.flask_app.route('/api/status')
        def api_status():
            return jsonify(self.get_status())

        @self.flask_app.route('/api/requests')
        def api_requests():
            return jsonify([asdict(req) for req in self.requests.values()])

        @self.flask_app.route('/api/models')
        def api_models():
            return jsonify([asdict(status) for status in self.model_status.values()])

        @self.flask_app.route('/api/stats')
        def api_stats():
            return jsonify(self.stats)

        @self.flask_app.route('/api/active')
        def api_active():
            return jsonify([asdict(req) for req in self.active_requests.values()])

        @self.flask_app.route('/api/stop', methods=['POST'])
        def api_stop():
            logger.info("🛑 Arresto richiesto via API web. Il monitor si fermerà ora.")
            def shutdown():
                import os
                import signal
                os.kill(os.getpid(), signal.SIGTERM)
            threading.Thread(target=shutdown, daemon=True).start()
            return jsonify({"status": "stopping", "message": "Monitor in arresto..."})

        # Avvia Flask in thread separato
        self.flask_thread = threading.Thread(
            target=lambda: self.flask_app.run(host='0.0.0.0', port=self.port, debug=False),
            daemon=True
        )
        self.flask_thread.start()

    def _monitor_loop(self):
        """Loop principale di monitoraggio."""
        while self.is_running:
            try:
                # Controlla stato modelli
                self._check_model_status()

                # Aggiorna metriche sistema
                self._update_system_metrics()

                # Pulisci richieste vecchie
                self._cleanup_old_requests()

                time.sleep(5)  # Controlla ogni 5 secondi

            except Exception as e:
                logger.error(f"Errore nel loop di monitoraggio: {e}")
                time.sleep(10)

    def _check_model_status(self):
        """Controlla lo stato di disponibilità dei modelli."""
        for model_name, status in self.model_status.items():
            try:
                start_time = time.time()
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "test",
                        "stream": False,
                        "options": {"num_predict": 1}
                    },
                    timeout=10
                )

                response_time = time.time() - start_time

                if response.status_code == 200:
                    status.is_available = True
                    status.response_time = response_time
                    status.success_count += 1
                    status.last_check = datetime.now()

                    # Aggiorna tempo medio di risposta
                    if status.avg_response_time is None:
                        status.avg_response_time = response_time
                    else:
                        status.avg_response_time = (status.avg_response_time + response_time) / 2
                else:
                    status.is_available = False
                    status.error_count += 1

            except Exception as e:
                status.is_available = False
                status.error_count += 1
                logger.debug(f"Modello {model_name} non disponibile: {e}")

            status.total_requests = status.success_count + status.error_count

    def _update_system_metrics(self):
        """Aggiorna le metriche del sistema."""
        try:
            # CPU e memoria per processo Ollama
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                if 'ollama' in proc.info['name'].lower():
                    # Aggiorna metriche per richieste attive
                    for req in self.active_requests.values():
                        req.cpu_usage = proc.info['cpu_percent']
                        req.memory_usage = proc.info['memory_percent']
                    break
        except Exception as e:
            logger.debug(f"Errore nell'aggiornamento metriche sistema: {e}")

    def _cleanup_old_requests(self):
        """Pulisce le richieste vecchie dalla memoria."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        old_requests = [
            req_id for req_id, req in self.requests.items()
            if req.start_time < cutoff_time
        ]

        for req_id in old_requests:
            del self.requests[req_id]

    def track_request(self, request_id: str, model: str, prompt: str, timeout: int = 1800):
        """Traccia una nuova richiesta LLM."""
        request = LLMRequest(
            id=request_id,
            model=model,
            prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,  # Tronca prompt lungo
            start_time=datetime.now(),
            timeout=timeout,
            status="running"
        )

        self.requests[request_id] = request
        self.active_requests[request_id] = request
        self.stats["total_requests"] += 1

        logger.info(f"📊 Tracciamento richiesta {request_id} per modello {model}")

    def update_request_status(self, request_id: str, status: str, response: str = None, error: str = None):
        """Aggiorna lo stato di una richiesta."""
        if request_id in self.requests:
            request = self.requests[request_id]
            request.status = status
            request.end_time = datetime.now()
            request.duration = (request.end_time - request.start_time).total_seconds()

            if response:
                request.response = response
                # Stima token generati (approssimativo)
                request.tokens_generated = len(response.split()) * 1.3
                self.stats["total_tokens"] += request.tokens_generated

            if error:
                request.error = error
                self.stats["failed_requests"] += 1
            else:
                self.stats["successful_requests"] += 1

            # Rimuovi dalle richieste attive
            if request_id in self.active_requests:
                del self.active_requests[request_id]

            # Aggiorna tempo medio di risposta
            if request.duration:
                if self.stats["avg_response_time"] == 0:
                    self.stats["avg_response_time"] = request.duration
                else:
                    total_requests = self.stats["successful_requests"] + self.stats["failed_requests"]
                    self.stats["avg_response_time"] = (
                        (self.stats["avg_response_time"] * (total_requests - 1) + request.duration) / total_requests
                    )

            logger.info(f"📊 Aggiornamento richiesta {request_id}: {status}")

    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo stato completo del monitor."""
        return {
            "is_running": self.is_running,
            "active_requests_count": len(self.active_requests),
            "total_requests_count": len(self.requests),
            "models_available": sum(1 for s in self.model_status.values() if s.is_available),
            "models_total": len(self.model_status),
            "stats": self.stats,
            "uptime": (datetime.now() - self.stats["start_time"]).total_seconds()
        }

    def get_active_requests(self) -> List[Dict[str, Any]]:
        """Restituisce le richieste attualmente in corso."""
        return [asdict(req) for req in self.active_requests.values()]

    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Restituisce le richieste più recenti."""
        sorted_requests = sorted(
            self.requests.values(),
            key=lambda x: x.start_time,
            reverse=True
        )
        return [asdict(req) for req in sorted_requests[:limit]]

    def get_model_performance(self) -> Dict[str, Any]:
        """Restituisce le performance dei modelli."""
        performance = {}
        for model_name, status in self.model_status.items():
            performance[model_name] = {
                "availability": status.is_available,
                "success_rate": (status.success_count / status.total_requests * 100) if status.total_requests > 0 else 0,
                "avg_response_time": status.avg_response_time,
                "total_requests": status.total_requests,
                "last_check": status.last_check.isoformat()
            }
        return performance

# Istanza globale del monitor
_monitor_instance = None

def get_monitor() -> LLMMonitor:
    """Restituisce l'istanza globale del monitor."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = LLMMonitor()
    return _monitor_instance

def start_monitoring(port: int = 8080):
    """Avvia il monitoraggio LLM."""
    monitor = get_monitor()
    monitor.port = port
    monitor.start()
    return monitor

def stop_monitoring():
    """Ferma il monitoraggio LLM."""
    global _monitor_instance
    if _monitor_instance:
        _monitor_instance.stop()
        _monitor_instance = None

def track_llm_request(request_id: str, model: str, prompt: str, timeout: int = 1800):
    """Traccia una richiesta LLM (da usare nei wrapper)."""
    monitor = get_monitor()
    if monitor.is_running:
        monitor.track_request(request_id, model, prompt, timeout)

def update_llm_request(request_id: str, status: str, response: str = None, error: str = None):
    """Aggiorna lo stato di una richiesta LLM (da usare nei wrapper)."""
    monitor = get_monitor()
    if monitor.is_running:
        monitor.update_request_status(request_id, status, response, error)

if __name__ == "__main__":
    # Test del monitor
    monitor = start_monitoring()

    try:
        print("🚀 LLM Monitor avviato!")
        print("🌐 Dashboard: http://localhost:8080")
        print("⏹️  Premi Ctrl+C per fermare...")

        # Simula alcune richieste per test
        import uuid
        for i in range(3):
            req_id = str(uuid.uuid4())
            monitor.track_request(req_id, "phi3", f"Test prompt {i+1}")
            time.sleep(2)
            monitor.update_request_status(req_id, "completed", f"Test response {i+1}")

        # Mantieni in esecuzione
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Arresto monitor...")
        stop_monitoring()
        print("✅ Monitor fermato")
