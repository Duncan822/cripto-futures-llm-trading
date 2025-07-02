#!/usr/bin/env python3
"""
Dry Run Manager: Gestisce il dry run delle strategie ottimizzate.
Monitora performance, gestisce rischi e genera report.
"""

import os
import json
import sqlite3
import logging
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import threading
import signal

logger = logging.getLogger(__name__)

@dataclass
class DryRunConfig:
    """Configurazione per il dry run."""
    strategy_name: str
    duration_days: int = 7
    stake_amount: float = 100.0
    max_open_trades: int = 3
    pairs: List[str] = None
    risk_limits: Dict[str, float] = None
    
    def __post_init__(self):
        if self.pairs is None:
            self.pairs = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"]
        if self.risk_limits is None:
            self.risk_limits = {
                "max_drawdown": 0.15,
                "max_consecutive_losses": 5,
                "min_win_rate": 0.4,
                "max_daily_loss": 0.10
            }

@dataclass
class PerformanceMetrics:
    """Metriche di performance del dry run."""
    strategy_name: str
    start_time: datetime
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    consecutive_losses: int = 0
    current_drawdown: float = 0.0
    daily_return: float = 0.0
    status: str = "running"

class DryRunManager:
    """
    Gestisce il dry run delle strategie ottimizzate.
    """
    
    def __init__(self, db_path: str = "dry_run.db"):
        self.db_path = db_path
        self.active_runs: Dict[str, DryRunConfig] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Inizializza database
        self._init_database()
        
        # Criteri di successo
        self.success_criteria = {
            "min_win_rate": 0.4,
            "max_drawdown": 0.15,
            "min_sharpe_ratio": 0.8,
            "min_total_return": 0.05,
            "max_consecutive_losses": 5
        }
    
    def _init_database(self):
        """Inizializza il database per il dry run."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella per i dry run
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dry_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                status TEXT DEFAULT 'running',
                config TEXT NOT NULL,
                results TEXT
            )
        ''')
        
        # Tabella per le metriche giornaliere
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                date DATE NOT NULL,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                total_trades INTEGER,
                consecutive_losses INTEGER,
                daily_return REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_dry_run(self, strategy_name: str, config: Optional[DryRunConfig] = None) -> bool:
        """
        Avvia un dry run per una strategia.
        """
        try:
            if config is None:
                config = DryRunConfig(strategy_name)
            
            # Verifica che la strategia esista
            strategy_file = f"user_data/strategies/{strategy_name.lower()}.py"
            if not os.path.exists(strategy_file):
                logger.error(f"❌ Strategia {strategy_name} non trovata")
                return False
            
            # Crea configurazione Freqtrade per dry run
            freqtrade_config = self._create_freqtrade_config(config)
            config_file = f"config_dry_run_{strategy_name}.json"
            
            with open(config_file, 'w') as f:
                json.dump(freqtrade_config, f, indent=2)
            
            # Avvia Freqtrade in dry run
            cmd = [
                'freqtrade', 'trade',
                '--strategy', strategy_name,
                '--config', config_file,
                '--db-url', f'sqlite:///dry_run_{strategy_name}.db'
            ]
            
            logger.info(f"🚀 Avvio dry run per {strategy_name}")
            logger.info(f"   Comando: {' '.join(cmd)}")
            
            # Avvia processo in background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Salva configurazione
            self.active_runs[strategy_name] = config
            self.performance_metrics[strategy_name] = PerformanceMetrics(
                strategy_name=strategy_name,
                start_time=datetime.now()
            )
            
            # Salva nel database
            self._save_dry_run_to_db(strategy_name, config, process.pid)
            
            logger.info(f"✅ Dry run avviato per {strategy_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore nell'avvio dry run per {strategy_name}: {e}")
            return False
    
    def _create_freqtrade_config(self, config: DryRunConfig) -> Dict[str, Any]:
        """Crea configurazione Freqtrade per dry run."""
        base_config = {
            "max_open_trades": config.max_open_trades,
            "stake_currency": "USDT",
            "stake_amount": config.stake_amount,
            "tradable_balance_ratio": 0.99,
            "fiat_display_currency": "USD",
            "timeframe": "5m",
            "dry_run": True,
            "dry_run_wallet": 1000,
            "cancel_open_orders_on_exit": False,
            "trading_mode": "futures",
            "margin_mode": "isolated",
            "unfilledtimeout": {
                "entry": 10,
                "exit": 10,
                "exit_timeout_count": 0,
                "unit": "minutes"
            },
            "entry_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1
            },
            "exit_pricing": {
                "price_side": "same",
                "use_order_book": True,
                "order_book_top": 1
            },
            "exchange": {
                "name": "binanceusdm",
                "key": "",
                "secret": "",
                "ccxt_config": {
                    "enableRateLimit": True,
                    "options": {
                        "defaultType": "future"
                    }
                },
                "pair_whitelist": config.pairs,
                "pair_blacklist": []
            },
            "pairlists": [
                {
                    "method": "StaticPairList"
                }
            ],
            "edge": {
                "enabled": False
            },
            "telegram": {
                "enabled": False
            },
            "api_server": {
                "enabled": True,
                "listen_ip_address": "0.0.0.0",
                "listen_port": 8080,
                "verbosity": "error",
                "enable_openapi": False,
                "jwt_secret_key": "dry-run-secret-key",
                "CORS_origins": [],
                "username": "",
                "password": ""
            },
            "bot_name": f"dry-run-{config.strategy_name}",
            "initial_state": "running",
            "force_entry_enable": False,
            "internals": {
                "process_throttle_secs": 5
            }
        }
        
        return base_config
    
    def _save_dry_run_to_db(self, strategy_name: str, config: DryRunConfig, pid: int):
        """Salva informazioni del dry run nel database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO dry_runs (strategy_name, start_time, config)
            VALUES (?, ?, ?)
        ''', (strategy_name, datetime.now(), json.dumps(config.__dict__)))
        
        conn.commit()
        conn.close()
    
    def stop_dry_run(self, strategy_name: str) -> bool:
        """
        Ferma un dry run e genera report.
        """
        try:
            if strategy_name not in self.active_runs:
                logger.warning(f"⚠️ Dry run {strategy_name} non attivo")
                return False
            
            # Ferma processo Freqtrade
            cmd = f"pkill -f 'freqtrade.*{strategy_name}'"
            subprocess.run(cmd, shell=True)
            
            # Genera report finale
            report = self.generate_report(strategy_name)
            
            # Aggiorna database
            self._update_dry_run_status(strategy_name, "completed", report)
            
            # Rimuovi da attivi
            del self.active_runs[strategy_name]
            if strategy_name in self.performance_metrics:
                del self.performance_metrics[strategy_name]
            
            logger.info(f"✅ Dry run fermato per {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Errore nel fermare dry run {strategy_name}: {e}")
            return False
    
    def _update_dry_run_status(self, strategy_name: str, status: str, results: str = None):
        """Aggiorna status del dry run nel database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE dry_runs 
            SET end_time = ?, status = ?, results = ?
            WHERE strategy_name = ? AND status = 'running'
        ''', (datetime.now(), status, results, strategy_name))
        
        conn.commit()
        conn.close()
    
    def monitor_performance(self):
        """
        Monitora performance dei dry run attivi.
        """
        while self.is_monitoring:
            try:
                for strategy_name in list(self.active_runs.keys()):
                    self._update_performance_metrics(strategy_name)
                    self._check_risk_limits(strategy_name)
                
                time.sleep(300)  # Controlla ogni 5 minuti
                
            except Exception as e:
                logger.error(f"❌ Errore nel monitoraggio: {e}")
                time.sleep(60)
    
    def _update_performance_metrics(self, strategy_name: str):
        """Aggiorna metriche di performance per una strategia."""
        try:
            # Leggi metriche da database Freqtrade
            db_path = f"dry_run_{strategy_name}.db"
            if not os.path.exists(db_path):
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Calcola metriche
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(profit) as total_profit,
                    MAX(profit) as max_profit,
                    MIN(profit) as max_loss
                FROM trades 
                WHERE strategy = ?
            ''', (strategy_name,))
            
            result = cursor.fetchone()
            if result:
                total_trades, winning_trades, total_profit, max_profit, max_loss = result
                
                if strategy_name in self.performance_metrics:
                    metrics = self.performance_metrics[strategy_name]
                    metrics.total_trades = total_trades or 0
                    metrics.win_rate = (winning_trades / total_trades) if total_trades > 0 else 0
                    metrics.total_return = total_profit or 0
                    metrics.max_drawdown = abs(max_loss) if max_loss else 0
            
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Errore nell'aggiornamento metriche {strategy_name}: {e}")
    
    def _check_risk_limits(self, strategy_name: str):
        """Controlla limiti di rischio e ferma se necessario."""
        if strategy_name not in self.active_runs or strategy_name not in self.performance_metrics:
            return
        
        config = self.active_runs[strategy_name]
        metrics = self.performance_metrics[strategy_name]
        
        # Controlla drawdown
        if metrics.current_drawdown > config.risk_limits["max_drawdown"]:
            logger.warning(f"🚨 Drawdown limite superato per {strategy_name}: {metrics.current_drawdown:.2%}")
            self.stop_dry_run(strategy_name)
            return
        
        # Controlla consecutive losses
        if metrics.consecutive_losses > config.risk_limits["max_consecutive_losses"]:
            logger.warning(f"🚨 Troppe perdite consecutive per {strategy_name}: {metrics.consecutive_losses}")
            self.stop_dry_run(strategy_name)
            return
        
        # Controlla win rate
        if metrics.total_trades > 10 and metrics.win_rate < config.risk_limits["min_win_rate"]:
            logger.warning(f"🚨 Win rate troppo basso per {strategy_name}: {metrics.win_rate:.2%}")
            self.stop_dry_run(strategy_name)
            return
    
    def start_monitoring(self):
        """Avvia il monitoraggio in background."""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitor_performance, daemon=True)
            self.monitoring_thread.start()
            logger.info("✅ Monitoraggio dry run avviato")
    
    def stop_monitoring(self):
        """Ferma il monitoraggio."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("🛑 Monitoraggio dry run fermato")
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo status dei dry run attivi."""
        status = {
            'active_runs': len(self.active_runs),
            'total_runs': len(self.performance_metrics),
            'monitoring_active': self.is_monitoring
        }
        
        # Dettagli dry run attivi
        active_details = {}
        for strategy_name, config in self.active_runs.items():
            metrics = self.performance_metrics.get(strategy_name)
            active_details[strategy_name] = {
                'start_time': config.start_time.isoformat() if hasattr(config, 'start_time') else None,
                'duration_days': config.duration_days,
                'stake_amount': config.stake_amount,
                'total_return': metrics.total_return if metrics else 0,
                'win_rate': metrics.win_rate if metrics else 0,
                'total_trades': metrics.total_trades if metrics else 0,
                'status': metrics.status if metrics else 'running'
            }
        
        status['active_details'] = active_details
        return status
    
    def generate_report(self, strategy_name: str) -> Dict[str, Any]:
        """Genera report finale per una strategia."""
        if strategy_name not in self.performance_metrics:
            return {}
        
        metrics = self.performance_metrics[strategy_name]
        
        # Valuta successo
        success = (
            metrics.win_rate >= self.success_criteria["min_win_rate"] and
            metrics.max_drawdown <= self.success_criteria["max_drawdown"] and
            metrics.total_return >= self.success_criteria["min_total_return"] and
            metrics.consecutive_losses <= self.success_criteria["max_consecutive_losses"]
        )
        
        report = {
            'strategy_name': strategy_name,
            'start_time': metrics.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration_days': (datetime.now() - metrics.start_time).days,
            'total_return': metrics.total_return,
            'sharpe_ratio': metrics.sharpe_ratio,
            'max_drawdown': metrics.max_drawdown,
            'win_rate': metrics.win_rate,
            'total_trades': metrics.total_trades,
            'consecutive_losses': metrics.consecutive_losses,
            'success': success,
            'recommendation': 'LIVE_READY' if success else 'NEEDS_OPTIMIZATION'
        }
        
        return report
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Restituisce tutti i report completati."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT strategy_name, start_time, end_time, results
            FROM dry_runs 
            WHERE status = 'completed'
            ORDER BY end_time DESC
        ''')
        
        reports = []
        for row in cursor.fetchall():
            strategy_name, start_time, end_time, results = row
            if results:
                report = json.loads(results)
                reports.append(report)
        
        conn.close()
        return reports

def main():
    """Funzione principale per testare il Dry Run Manager."""
    manager = DryRunManager()
    
    # Test con strategia esistente
    test_strategy = "VolatilityStrategy_cogito:8b_20250630_223230"
    
    print(f"🧪 Test Dry Run Manager con {test_strategy}")
    
    # Avvia dry run
    success = manager.start_dry_run(test_strategy)
    if success:
        print(f"✅ Dry run avviato per {test_strategy}")
        
        # Avvia monitoraggio
        manager.start_monitoring()
        
        # Simula monitoraggio per 30 secondi
        time.sleep(30)
        
        # Ferma dry run
        manager.stop_dry_run(test_strategy)
        manager.stop_monitoring()
        
        # Genera report
        report = manager.generate_report(test_strategy)
        print(f"📊 Report: {json.dumps(report, indent=2)}")
    else:
        print(f"❌ Errore nell'avvio dry run per {test_strategy}")

if __name__ == "__main__":
    main() 