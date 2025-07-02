#!/usr/bin/env python3
"""
Sistema di monitoraggio in tempo reale per i backtest Freqtrade.
Permette di monitorare l'avanzamento dei backtest anche quando sono in background.
"""

import os
import time
import json
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import signal
import sys

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BacktestMonitor:
    """
    Monitor per i backtest Freqtrade con supporto per monitoraggio in tempo reale.
    """
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.active_backtests: Dict[str, Dict[str, Any]] = {}
        self.backtest_logs_dir = Path("logs/backtests")
        self.backtest_logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Stato del monitor
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_backtest_with_monitoring(self, strategy_name: str, timerange: str = "20240101-20241231") -> str:
        """
        Avvia un backtest con monitoraggio in tempo reale.
        
        Args:
            strategy_name: Nome della strategia da testare
            timerange: Intervallo temporale per il backtest
            
        Returns:
            ID del backtest avviato
        """
        backtest_id = f"{strategy_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        log_file = self.backtest_logs_dir / f"{backtest_id}.log"
        
        # Comando Freqtrade per backtest
        cmd = [
            "freqtrade", "backtesting",
            "--config", self.config_path,
            "--strategy", strategy_name,
            "--timerange", timerange,
            "--export", "trades",
            "--export-filename", f"backtest_results/{backtest_id}.json"
        ]
        
        try:
            # Avvia il processo in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Registra il backtest attivo
            self.active_backtests[backtest_id] = {
                "strategy_name": strategy_name,
                "timerange": timerange,
                "process": process,
                "log_file": log_file,
                "start_time": datetime.now(),
                "status": "running",
                "progress": 0.0,
                "last_update": datetime.now()
            }
            
            # Avvia thread per monitorare l'output
            monitor_thread = threading.Thread(
                target=self._monitor_backtest_output,
                args=(backtest_id, process, log_file),
                daemon=True
            )
            monitor_thread.start()
            
            logger.info(f"🚀 Backtest avviato: {backtest_id}")
            return backtest_id
            
        except Exception as e:
            logger.error(f"❌ Errore nell'avvio backtest {strategy_name}: {e}")
            return None
    
    def _monitor_backtest_output(self, backtest_id: str, process: subprocess.Popen, log_file: Path):
        """
        Monitora l'output di un backtest in tempo reale.
        """
        try:
            with open(log_file, 'w') as f:
                for line in iter(process.stdout.readline, ''):
                    if line:
                        # Scrivi nel file di log
                        f.write(line)
                        f.flush()
                        
                        # Aggiorna lo stato del backtest
                        self._update_backtest_status(backtest_id, line)
                        
                        # Log in tempo reale
                        logger.info(f"[{backtest_id}] {line.strip()}")
            
            # Processo completato
            return_code = process.wait()
            self._finalize_backtest(backtest_id, return_code)
            
        except Exception as e:
            logger.error(f"❌ Errore nel monitoraggio {backtest_id}: {e}")
            self._finalize_backtest(backtest_id, -1)
    
    def _update_backtest_status(self, backtest_id: str, output_line: str):
        """
        Aggiorna lo stato del backtest basandosi sull'output.
        """
        if backtest_id not in self.active_backtests:
            return
        
        backtest = self.active_backtests[backtest_id]
        backtest["last_update"] = datetime.now()
        
        # Analizza l'output per determinare il progresso
        line = output_line.lower()
        
        if "loading data" in line:
            backtest["status"] = "loading_data"
            backtest["progress"] = 10.0
        elif "analyzing" in line:
            backtest["status"] = "analyzing"
            backtest["progress"] = 30.0
        elif "backtesting" in line:
            backtest["status"] = "backtesting"
            backtest["progress"] = 50.0
        elif "generating report" in line:
            backtest["status"] = "generating_report"
            backtest["progress"] = 80.0
        elif "backtest completed" in line or "backtest finished" in line:
            backtest["status"] = "completed"
            backtest["progress"] = 100.0
        elif "error" in line or "failed" in line:
            backtest["status"] = "error"
    
    def _finalize_backtest(self, backtest_id: str, return_code: int):
        """
        Finalizza un backtest completato.
        """
        if backtest_id not in self.active_backtests:
            return
        
        backtest = self.active_backtests[backtest_id]
        backtest["end_time"] = datetime.now()
        backtest["return_code"] = return_code
        
        if return_code == 0:
            backtest["status"] = "completed"
            logger.info(f"✅ Backtest completato: {backtest_id}")
        else:
            backtest["status"] = "failed"
            logger.error(f"❌ Backtest fallito: {backtest_id} (code: {return_code})")
    
    def get_backtest_status(self, backtest_id: str) -> Optional[Dict[str, Any]]:
        """
        Restituisce lo stato di un backtest specifico.
        """
        if backtest_id not in self.active_backtests:
            return None
        
        backtest = self.active_backtests[backtest_id]
        status = backtest.copy()
        
        # Calcola durata
        if "end_time" in status:
            duration = status["end_time"] - status["start_time"]
        else:
            duration = datetime.now() - status["start_time"]
        
        status["duration"] = str(duration)
        status["duration_seconds"] = duration.total_seconds()
        
        # Rimuovi oggetti non serializzabili
        if "process" in status:
            del status["process"]
        
        return status
    
    def get_all_backtests(self) -> Dict[str, Dict[str, Any]]:
        """
        Restituisce lo stato di tutti i backtest attivi.
        """
        return {
            backtest_id: self.get_backtest_status(backtest_id)
            for backtest_id in self.active_backtests.keys()
        }
    
    def stop_backtest(self, backtest_id: str) -> bool:
        """
        Ferma un backtest in esecuzione.
        """
        if backtest_id not in self.active_backtests:
            return False
        
        backtest = self.active_backtests[backtest_id]
        process = backtest["process"]
        
        try:
            # Invia segnale di arresto
            process.terminate()
            
            # Aspetta fino a 10 secondi
            process.wait(timeout=10)
            logger.info(f"🛑 Backtest fermato: {backtest_id}")
            return True
            
        except subprocess.TimeoutExpired:
            # Forza arresto
            process.kill()
            logger.warning(f"⚠️ Backtest forzatamente arrestato: {backtest_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Errore nell'arresto backtest {backtest_id}: {e}")
            return False
    
    def cleanup_completed_backtests(self):
        """
        Rimuove i backtest completati dalla memoria.
        """
        completed_ids = []
        
        for backtest_id, backtest in self.active_backtests.items():
            if backtest["status"] in ["completed", "failed", "stopped"]:
                completed_ids.append(backtest_id)
        
        for backtest_id in completed_ids:
            del self.active_backtests[backtest_id]
            logger.info(f"🧹 Backtest rimosso dalla memoria: {backtest_id}")
    
    def start_monitoring(self):
        """
        Avvia il monitoraggio continuo dei backtest.
        """
        if self.is_monitoring:
            logger.warning("Monitoraggio già attivo")
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    # Controlla backtest completati
                    self.cleanup_completed_backtests()
                    
                    # Log stato ogni 30 secondi
                    active_count = len([b for b in self.active_backtests.values() if b["status"] == "running"])
                    if active_count > 0:
                        logger.info(f"📊 Backtest attivi: {active_count}")
                    
                    time.sleep(30)
                    
                except Exception as e:
                    logger.error(f"❌ Errore nel loop di monitoraggio: {e}")
                    time.sleep(60)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 Monitoraggio backtest avviato")
    
    def stop_monitoring(self):
        """
        Ferma il monitoraggio continuo.
        """
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Monitoraggio backtest fermato")

def main():
    """
    Funzione principale per testare il monitor.
    """
    monitor = BacktestMonitor()
    
    try:
        # Avvia monitoraggio
        monitor.start_monitoring()
        
        # Test: avvia un backtest
        print("🧪 Test avvio backtest con monitoraggio...")
        backtest_id = monitor.start_backtest_with_monitoring("LLMStrategy")
        
        if backtest_id:
            print(f"✅ Backtest avviato: {backtest_id}")
            
            # Monitora per 60 secondi
            for i in range(12):
                time.sleep(5)
                status = monitor.get_backtest_status(backtest_id)
                if status:
                    print(f"📊 Stato: {status['status']} - Progresso: {status['progress']:.1f}%")
                
                # Controlla se è completato
                if status and status['status'] in ['completed', 'failed']:
                    break
        
        # Mostra tutti i backtest
        print("\n📋 Tutti i backtest:")
        all_backtests = monitor.get_all_backtests()
        for bid, status in all_backtests.items():
            print(f"  {bid}: {status['status']} ({status['progress']:.1f}%)")
            
    except KeyboardInterrupt:
        print("\n🛑 Interruzione manuale")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main() 