#!/usr/bin/env python3
"""
Cooperative Monitor: Estensione del LLM Monitor per tracciare le interazioni cooperative tra LLM.
Monitora conversazioni, contest, consensi e validazioni incrociate.
"""

import os
import time
import json
import logging
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import queue
from flask import Flask, render_template, jsonify, request
import webbrowser

# Importa il monitor LLM esistente
from llm_monitor import LLMMonitor, LLMRequest, ModelStatus

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cooperative_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CooperativeSession:
    """Rappresenta una sessione cooperativa tra LLM."""
    session_id: str
    session_type: str  # "cooperative_generation", "contest", "consensus", "validation"
    strategy_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"  # "running", "completed", "failed"
    participants: Optional[List[str]] = None  # Lista dei modelli partecipanti
    conversation_log: Optional[List[Dict[str, Any]]] = None  # Log delle conversazioni
    results: Optional[Dict[str, Any]] = None  # Risultati della sessione
    hardware_metrics: Optional[Dict[str, Any]] = None  # Metriche hardware durante la sessione
    duration: Optional[float] = None

@dataclass
class LLMConversation:
    """Rappresenta una conversazione tra LLM."""
    conversation_id: str
    session_id: str
    model: str
    role: str  # "generator", "validator", "optimizer", "contestant"
    prompt: str
    response: str
    timestamp: datetime
    duration: float
    tokens_generated: Optional[int] = None
    validation_score: Optional[float] = None
    contest_score: Optional[float] = None

@dataclass
class ConsensusRound:
    """Rappresenta un round di consenso."""
    round_id: str
    session_id: str
    round_number: int
    participants: Optional[List[str]] = None
    ideas_collected: Optional[Dict[str, str]] = None  # model -> idea
    timestamp: Optional[datetime] = None
    duration: float = 0.0
    synthesis: Optional[str] = None

class CooperativeMonitor:
    """
    Monitor per le interazioni cooperative tra LLM.
    Estende il monitor LLM esistente con funzionalità cooperative.
    """
    
    def __init__(self, port: int = 8081):
        self.port = port
        self.sessions: Dict[str, CooperativeSession] = {}
        self.conversations: Dict[str, LLMConversation] = {}
        self.consensus_rounds: Dict[str, ConsensusRound] = {}
        self.active_sessions: Dict[str, CooperativeSession] = {}
        self.is_running = False
        self.flask_app = None
        self.flask_thread = None
        
        # Statistiche cooperative
        self.cooperative_stats = {
            "total_sessions": 0,
            "completed_sessions": 0,
            "failed_sessions": 0,
            "total_conversations": 0,
            "total_consensus_rounds": 0,
            "avg_session_duration": 0.0,
            "most_used_models": {},
            "session_types": {
                "cooperative_generation": 0,
                "contest": 0,
                "consensus": 0,
                "validation": 0
            },
            "start_time": datetime.now()
        }
        
        # Istanza del monitor LLM esistente
        self.llm_monitor = LLMMonitor(port=8080)
        
    def start(self):
        """Avvia il monitor cooperativo."""
        if self.is_running:
            logger.warning("Cooperative Monitor già in esecuzione")
            return
        
        self.is_running = True
        
        # Avvia il monitor LLM base
        self.llm_monitor.start()
        
        # Avvia dashboard cooperativa
        self._start_cooperative_dashboard()
        
        logger.info(f"✅ Cooperative Monitor avviato su porta {self.port}")
        logger.info(f"🌐 Dashboard cooperativa: http://localhost:{self.port}")
        logger.info(f"🔗 Monitor LLM base: http://localhost:8080")
        
        # Apri browser automaticamente
        try:
            webbrowser.open(f"http://localhost:{self.port}")
        except:
            pass
    
    def stop(self):
        """Ferma il monitor cooperativo."""
        self.is_running = False
        if self.flask_thread:
            self.flask_thread.join(timeout=5)
        self.llm_monitor.stop()
        logger.info("🛑 Cooperative Monitor fermato")
    
    def _start_cooperative_dashboard(self):
        """Avvia la dashboard web per il monitor cooperativo."""
        self.flask_app = Flask(__name__)
        
        @self.flask_app.route('/')
        def cooperative_dashboard():
            return render_template('cooperative_dashboard.html')
        
        @self.flask_app.route('/api/cooperative/status')
        def api_cooperative_status():
            return jsonify(self.get_cooperative_status())
        
        @self.flask_app.route('/api/cooperative/sessions')
        def api_cooperative_sessions():
            return jsonify([asdict(session) for session in self.sessions.values()])
        
        @self.flask_app.route('/api/cooperative/conversations')
        def api_cooperative_conversations():
            return jsonify([asdict(conv) for conv in self.conversations.values()])
        
        @self.flask_app.route('/api/cooperative/consensus')
        def api_cooperative_consensus():
            return jsonify([asdict(round) for round in self.consensus_rounds.values()])
        
        @self.flask_app.route('/api/cooperative/stats')
        def api_cooperative_stats():
            return jsonify(self.cooperative_stats)
        
        @self.flask_app.route('/api/cooperative/active')
        def api_cooperative_active():
            return jsonify([asdict(session) for session in self.active_sessions.values()])
        
        @self.flask_app.route('/api/cooperative/session/<session_id>')
        def api_session_details(session_id):
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session_data = asdict(session)
                
                # Aggiungi conversazioni della sessione
                session_conversations = [
                    asdict(conv) for conv in self.conversations.values()
                    if conv.session_id == session_id
                ]
                session_data['conversations'] = session_conversations
                
                # Aggiungi round di consenso se presenti
                session_consensus = [
                    asdict(round) for round in self.consensus_rounds.values()
                    if round.session_id == session_id
                ]
                session_data['consensus_rounds'] = session_consensus
                
                return jsonify(session_data)
            else:
                return jsonify({"error": "Session not found"}), 404
        
        @self.flask_app.route('/api/cooperative/llm-status')
        def api_llm_status():
            # Reindirizza al monitor LLM base
            return jsonify(self.llm_monitor.get_status())
        
        @self.flask_app.route('/api/cooperative/stop', methods=['POST'])
        def api_cooperative_stop():
            logger.info("🛑 Arresto richiesto via API web. Il monitor cooperativo si fermerà ora.")
            def shutdown():
                import os
                import signal
                os.kill(os.getpid(), signal.SIGTERM)
            threading.Thread(target=shutdown, daemon=True).start()
            return jsonify({"status": "stopping", "message": "Cooperative Monitor in arresto..."})
        
        # Avvia Flask in thread separato
        self.flask_thread = threading.Thread(
            target=lambda: self.flask_app.run(host='0.0.0.0', port=self.port, debug=False),
            daemon=True
        )
        self.flask_thread.start()
    
    def start_cooperative_session(self, session_type: str, strategy_type: str, participants: List[str]) -> str:
        """Avvia una nuova sessione cooperativa."""
        session_id = str(uuid.uuid4())
        
        session = CooperativeSession(
            session_id=session_id,
            session_type=session_type,
            strategy_type=strategy_type,
            start_time=datetime.now(),
            participants=participants,
            conversation_log=[],
            results={},
            hardware_metrics={}
        )
        
        self.sessions[session_id] = session
        self.active_sessions[session_id] = session
        self.cooperative_stats["total_sessions"] += 1
        self.cooperative_stats["session_types"][session_type] += 1
        
        # Aggiorna statistiche modelli
        for model in participants:
            if model not in self.cooperative_stats["most_used_models"]:
                self.cooperative_stats["most_used_models"][model] = 0
            self.cooperative_stats["most_used_models"][model] += 1
        
        logger.info(f"🤝 Avviata sessione cooperativa {session_id}: {session_type} per {strategy_type}")
        logger.info(f"   Partecipanti: {', '.join(participants)}")
        
        return session_id
    
    def end_cooperative_session(self, session_id: str, status: str = "completed", results: Dict[str, Any] = None):
        """Termina una sessione cooperativa."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.end_time = datetime.now()
            session.status = status
            session.duration = (session.end_time - session.start_time).total_seconds()
            
            if results:
                session.results = results
            
            # Rimuovi dalle sessioni attive
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Aggiorna statistiche
            if status == "completed":
                self.cooperative_stats["completed_sessions"] += 1
            elif status == "failed":
                self.cooperative_stats["failed_sessions"] += 1
            
            # Aggiorna durata media
            if session.duration:
                total_completed = self.cooperative_stats["completed_sessions"]
                if total_completed == 1:
                    self.cooperative_stats["avg_session_duration"] = session.duration
                else:
                    self.cooperative_stats["avg_session_duration"] = (
                        (self.cooperative_stats["avg_session_duration"] * (total_completed - 1) + session.duration) / total_completed
                    )
            
            logger.info(f"✅ Sessione cooperativa {session_id} terminata: {status} ({session.duration:.1f}s)")
    
    def log_conversation(self, session_id: str, model: str, role: str, prompt: str, response: str, 
                        duration: float, validation_score: Optional[float] = None, 
                        contest_score: Optional[float] = None) -> str:
        """Registra una conversazione tra LLM."""
        conversation_id = str(uuid.uuid4())
        
        conversation = LLMConversation(
            conversation_id=conversation_id,
            session_id=session_id,
            model=model,
            role=role,
            prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,  # Tronca prompt lungo
            response=response[:1000] + "..." if len(response) > 1000 else response,  # Tronca risposta lunga
            timestamp=datetime.now(),
            duration=duration,
            tokens_generated=len(response.split()) * 1.3,  # Stima approssimativa
            validation_score=validation_score,
            contest_score=contest_score
        )
        
        self.conversations[conversation_id] = conversation
        self.cooperative_stats["total_conversations"] += 1
        
        # Aggiungi alla sessione
        if session_id in self.sessions:
            self.sessions[session_id].conversation_log.append({
                "conversation_id": conversation_id,
                "model": model,
                "role": role,
                "timestamp": conversation.timestamp.isoformat(),
                "duration": duration,
                "validation_score": validation_score,
                "contest_score": contest_score
            })
        
        logger.info(f"💬 Conversazione {conversation_id}: {model} ({role}) - {duration:.1f}s")
        
        return conversation_id
    
    def log_consensus_round(self, session_id: str, round_number: int, participants: List[str], 
                           ideas_collected: Dict[str, str], synthesis: Optional[str] = None, 
                           duration: float = 0.0) -> str:
        """Registra un round di consenso."""
        round_id = str(uuid.uuid4())
        
        consensus_round = ConsensusRound(
            round_id=round_id,
            session_id=session_id,
            round_number=round_number,
            participants=participants,
            ideas_collected=ideas_collected,
            synthesis=synthesis,
            timestamp=datetime.now(),
            duration=duration
        )
        
        self.consensus_rounds[round_id] = consensus_round
        self.cooperative_stats["total_consensus_rounds"] += 1
        
        logger.info(f"🤝 Round consenso {round_id}: {len(participants)} partecipanti, {duration:.1f}s")
        
        return round_id
    
    def update_hardware_metrics(self, session_id: str, metrics: Dict[str, Any]):
        """Aggiorna le metriche hardware per una sessione."""
        if session_id in self.sessions:
            self.sessions[session_id].hardware_metrics = metrics
    
    def get_cooperative_status(self) -> Dict[str, Any]:
        """Restituisce lo stato completo del monitor cooperativo."""
        return {
            "is_running": self.is_running,
            "active_sessions_count": len(self.active_sessions),
            "total_sessions_count": len(self.sessions),
            "total_conversations_count": len(self.conversations),
            "total_consensus_rounds_count": len(self.consensus_rounds),
            "cooperative_stats": self.cooperative_stats,
            "uptime": (datetime.now() - self.cooperative_stats["start_time"]).total_seconds(),
            "llm_monitor_status": self.llm_monitor.get_status()
        }
    
    def get_session_conversations(self, session_id: str) -> List[Dict[str, Any]]:
        """Restituisce tutte le conversazioni di una sessione."""
        return [
            asdict(conv) for conv in self.conversations.values()
            if conv.session_id == session_id
        ]
    
    def get_model_cooperation_stats(self, model: str) -> Dict[str, Any]:
        """Restituisce le statistiche di cooperazione di un modello."""
        model_conversations = [
            conv for conv in self.conversations.values()
            if conv.model == model
        ]
        
        if not model_conversations:
            return {"model": model, "conversations": 0, "avg_duration": 0}
        
        total_duration = sum(conv.duration for conv in model_conversations)
        avg_duration = total_duration / len(model_conversations)
        
        roles = {}
        for conv in model_conversations:
            if conv.role not in roles:
                roles[conv.role] = 0
            roles[conv.role] += 1
        
        return {
            "model": model,
            "conversations": len(model_conversations),
            "avg_duration": avg_duration,
            "roles": roles,
            "total_tokens": sum(conv.tokens_generated or 0 for conv in model_conversations)
        }
    
    def export_conversation_log(self, session_id: str, format: str = "json") -> str:
        """Esporta il log delle conversazioni di una sessione."""
        if session_id not in self.sessions:
            return ""
        
        session = self.sessions[session_id]
        conversations = self.get_session_conversations(session_id)
        
        if format == "json":
            log_data = {
                "session": asdict(session),
                "conversations": conversations
            }
            return json.dumps(log_data, indent=2, default=str)
        
        elif format == "markdown":
            md_content = f"# Sessione Cooperativa: {session_id}\n\n"
            md_content += f"**Tipo**: {session.session_type}\n"
            md_content += f"**Strategia**: {session.strategy_type}\n"
            md_content += f"**Partecipanti**: {', '.join(session.participants)}\n"
            md_content += f"**Durata**: {session.duration:.1f}s\n\n"
            
            md_content += "## Conversazioni\n\n"
            for conv in conversations:
                md_content += f"### {conv['model']} ({conv['role']})\n"
                md_content += f"**Timestamp**: {conv['timestamp']}\n"
                md_content += f"**Durata**: {conv['duration']:.1f}s\n\n"
                md_content += f"**Prompt**:\n```\n{conv['prompt']}\n```\n\n"
                md_content += f"**Risposta**:\n```\n{conv['response']}\n```\n\n"
                if conv.get('validation_score'):
                    md_content += f"**Punteggio Validazione**: {conv['validation_score']}\n\n"
                if conv.get('contest_score'):
                    md_content += f"**Punteggio Contest**: {conv['contest_score']}\n\n"
                md_content += "---\n\n"
            
            return md_content
        
        return ""

# Istanza globale del monitor cooperativo
_cooperative_monitor_instance = None

def get_cooperative_monitor() -> CooperativeMonitor:
    """Restituisce l'istanza globale del monitor cooperativo."""
    global _cooperative_monitor_instance
    if _cooperative_monitor_instance is None:
        _cooperative_monitor_instance = CooperativeMonitor()
    return _cooperative_monitor_instance

def start_cooperative_monitoring(port: int = 8081):
    """Avvia il monitoraggio cooperativo."""
    monitor = get_cooperative_monitor()
    monitor.port = port
    monitor.start()
    return monitor

def stop_cooperative_monitoring():
    """Ferma il monitoraggio cooperativo."""
    global _cooperative_monitor_instance
    if _cooperative_monitor_instance:
        _cooperative_monitor_instance.stop()
        _cooperative_monitor_instance = None

# Funzioni helper per integrazione con background_agent_cooperative.sh
def track_cooperative_session(session_type: str, strategy_type: str, participants: List[str]) -> str:
    """Traccia una sessione cooperativa (da usare nel background agent)."""
    monitor = get_cooperative_monitor()
    if monitor.is_running:
        return monitor.start_cooperative_session(session_type, strategy_type, participants)
    return ""

def log_cooperative_conversation(session_id: str, model: str, role: str, prompt: str, response: str, 
                                duration: float, validation_score: Optional[float] = None, 
                                contest_score: Optional[float] = None) -> str:
    """Registra una conversazione cooperativa (da usare nel background agent)."""
    monitor = get_cooperative_monitor()
    if monitor.is_running:
        return monitor.log_conversation(session_id, model, role, prompt, response, duration, 
                                       validation_score, contest_score)
    return ""

def end_cooperative_session(session_id: str, status: str = "completed", results: Dict[str, Any] = None):
    """Termina una sessione cooperativa (da usare nel background agent)."""
    monitor = get_cooperative_monitor()
    if monitor.is_running:
        monitor.end_cooperative_session(session_id, status, results)

if __name__ == "__main__":
    # Test del monitor cooperativo
    monitor = start_cooperative_monitoring()
    
    try:
        print("🚀 Cooperative Monitor avviato!")
        print("🌐 Dashboard cooperativa: http://localhost:8081")
        print("🔗 Monitor LLM base: http://localhost:8080")
        print("⏹️  Premi Ctrl+C per fermare...")
        
        # Simula una sessione cooperativa per test
        session_id = monitor.start_cooperative_session(
            "cooperative_generation", 
            "volatility", 
            ["cogito:8b", "mistral:7b", "phi3:14b"]
        )
        
        # Simula alcune conversazioni
        for i, model in enumerate(["cogito:8b", "mistral:7b", "phi3:14b"]):
            monitor.log_conversation(
                session_id, model, "generator",
                f"Genera strategia volatilità round {i+1}",
                f"Strategia generata da {model} per round {i+1}",
                5.0 + i, validation_score=8.0 - i
            )
            time.sleep(1)
        
        # Termina la sessione
        monitor.end_cooperative_session(session_id, "completed", {"best_strategy": "cogito:8b"})
        
        # Mantieni in esecuzione
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Arresto monitor cooperativo...")
        stop_cooperative_monitoring()
        print("✅ Monitor cooperativo fermato") 