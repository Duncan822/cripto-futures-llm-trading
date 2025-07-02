#!/usr/bin/env python3
"""
Background Agent: Automatizza la generazione, validazione e gestione delle strategie.
Gestisce il ciclo completo senza sovrascritture e con validazione automatica.
"""

import os
import time
import json
import logging
import schedule
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading
import queue
import re

from agents.generator import GeneratorAgent
from agents.strategy_converter import StrategyConverter
from agents.optimizer import OptimizerAgent
from freqtrade_utils import FreqtradeManager

# Importa il Dry Run Manager
try:
    from dry_run_manager import DryRunManager, DryRunConfig
    DRY_RUN_MANAGER_AVAILABLE = True
except ImportError:
    DRY_RUN_MANAGER_AVAILABLE = False
    print("⚠️ DryRunManager non disponibile, dry run automatico disabilitato")

# Importa il monitor dei backtest
try:
    from backtest_monitor import BacktestMonitor
    BACKTEST_MONITOR_AVAILABLE = True
except ImportError:
    BACKTEST_MONITOR_AVAILABLE = False
    print("⚠️ BacktestMonitor non disponibile, monitoraggio backtest disabilitato")

# Importa l'esportatore di strategie live
try:
    from live_strategies_exporter import LiveStrategiesExporter, LiveStrategyConfig
    LIVE_EXPORTER_AVAILABLE = True
except ImportError:
    LIVE_EXPORTER_AVAILABLE = False
    print("⚠️ LiveStrategiesExporter non disponibile, esportazione live disabilitata")

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Variabile globale per l'agente
_agent_instance = None

def signal_handler(signum, frame):
    """Gestisce i segnali di interruzione per un arresto pulito."""
    global _agent_instance
    logger.info(f"🛑 Ricevuto segnale {signum}, arresto in corso...")
    
    if _agent_instance:
        _agent_instance.stop()
    
    logger.info("✅ Arresto completato")
    sys.exit(0)

# Registra i gestori di segnale
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill

@dataclass
class StrategyMetadata:
    """Metadati di una strategia generata."""
    name: str
    file_path: str
    strategy_type: str
    model_used: str
    generation_time: datetime
    validation_status: str
    backtest_score: Optional[float] = None
    last_backtest: Optional[datetime] = None
    is_active: bool = False

class BackgroundAgent:
    """
    Agente di background che automatizza la gestione delle strategie.
    """
    
    def __init__(self, config_path: str = "background_config.json"):
        self.config = self._load_config(config_path)
        self.generator = GeneratorAgent()
        self.converter = StrategyConverter()
        # Usa il modello configurato per l'ottimizzazione
        optimization_model = self.config.get('model_selection', {}).get('optimization', 'cogito:8b')
        self.optimizer = OptimizerAgent(default_model=optimization_model)
        self.freqtrade = FreqtradeManager()
        
        # Stato dell'agente
        self.is_running = False
        self.strategies_metadata: Dict[str, StrategyMetadata] = {}
        self.task_queue = queue.Queue()
        
        # Carica metadati esistenti
        self._load_existing_metadata()
        
        # Configurazione automatica
        self.auto_validation = self.config.get('auto_validation', True)
        self.auto_backtest = self.config.get('auto_backtest', True)
        
        # Configurazione dry run
        dry_run_config = self.config.get('dry_run', {})
        self.auto_dry_run = dry_run_config.get('auto_dry_run', True)
        self.dry_run_interval = dry_run_config.get('dry_run_interval', 21600)  # 6 ore
        self.max_dry_runs = dry_run_config.get('max_dry_runs', 3)  # Max 3 dry run contemporanei
        self.dry_run_duration_days = dry_run_config.get('duration_days', 7)
        self.dry_run_stake_amount = dry_run_config.get('stake_amount', 100.0)
        self.dry_run_max_trades = dry_run_config.get('max_open_trades', 3)
        self.dry_run_pairs = dry_run_config.get('pairs', ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"])
        self.dry_run_risk_limits = dry_run_config.get('risk_limits', {})
        
        self.max_strategies = self.config.get('max_strategies', 50)
        self.generation_interval = self.config.get('generation_interval', 3600)  # 1 ora
        
        # Inizializza il monitor dei backtest se disponibile
        self.backtest_monitor = None
        if BACKTEST_MONITOR_AVAILABLE:
            try:
                self.backtest_monitor = BacktestMonitor()
                logger.info("✅ BacktestMonitor integrato nel Background Agent")
            except Exception as e:
                logger.warning(f"⚠️ Errore nell'inizializzazione BacktestMonitor: {e}")
                self.backtest_monitor = None
        
        # Inizializza il Dry Run Manager se disponibile
        self.dry_run_manager = None
        if DRY_RUN_MANAGER_AVAILABLE:
            try:
                self.dry_run_manager = DryRunManager()
                logger.info("✅ DryRunManager integrato nel Background Agent")
            except Exception as e:
                logger.warning(f"⚠️ Errore nell'inizializzazione DryRunManager: {e}")
                self.dry_run_manager = None
        
        # Inizializza l'esportatore di strategie live se disponibile
        self.live_exporter = None
        if LIVE_EXPORTER_AVAILABLE:
            try:
                live_config = LiveStrategyConfig(
                    min_backtest_score=self.config.get('min_backtest_score', 0.1),
                    export_optimized_only=True,
                    max_live_strategies=10
                )
                self.live_exporter = LiveStrategiesExporter(live_config)
                logger.info("✅ LiveStrategiesExporter integrato nel Background Agent")
            except Exception as e:
                logger.warning(f"⚠️ Errore nell'inizializzazione LiveStrategiesExporter: {e}")
                self.live_exporter = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carica la configurazione dell'agente."""
        default_config = {
            'auto_validation': True,
            'auto_backtest': True,
            'max_strategies': 50,
            'generation_interval': 3600,
            'backtest_interval': 7200,
            'cleanup_old_strategies': True,
            'strategy_types': ['volatility', 'scalping', 'breakout', 'momentum'],
            'models': ['phi3', 'llama2', 'mistral'],
            'min_backtest_score': 0.1,
            'max_concurrent_tasks': 3
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"Configurazione caricata da {config_path}")
            except Exception as e:
                logger.warning(f"Errore nel caricamento config, usando default: {e}")
        else:
            # Crea file di configurazione di default
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Configurazione di default creata in {config_path}")
        
        return default_config
    
    def _load_existing_metadata(self):
        """Carica i metadati delle strategie esistenti."""
        metadata_file = "strategies_metadata.json"
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    for strategy_data in data.values():
                        # Converti stringhe datetime in oggetti datetime
                        if 'generation_time' in strategy_data:
                            strategy_data['generation_time'] = datetime.fromisoformat(strategy_data['generation_time'])
                        if 'last_backtest' in strategy_data and strategy_data['last_backtest']:
                            strategy_data['last_backtest'] = datetime.fromisoformat(strategy_data['last_backtest'])
                        
                        self.strategies_metadata[strategy_data['name']] = StrategyMetadata(**strategy_data)
                logger.info(f"Caricate {len(self.strategies_metadata)} strategie esistenti")
            except Exception as e:
                logger.error(f"Errore nel caricamento metadati: {e}")
    
    def _save_metadata(self):
        """Salva i metadati delle strategie."""
        metadata_file = "strategies_metadata.json"
        try:
            # Converti datetime in stringhe per JSON
            data = {}
            for name, metadata in self.strategies_metadata.items():
                metadata_dict = asdict(metadata)
                if metadata_dict['generation_time']:
                    metadata_dict['generation_time'] = metadata_dict['generation_time'].isoformat()
                if metadata_dict['last_backtest']:
                    metadata_dict['last_backtest'] = metadata_dict['last_backtest'].isoformat()
                data[name] = metadata_dict
            
            with open(metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Errore nel salvataggio metadati: {e}")
    
    def generate_unique_strategy_name(self, strategy_type: str, model: str) -> str:
        """Genera un nome univoco per la strategia, sostituendo caratteri non validi."""
        base_name = f"{strategy_type.capitalize()}Strategy"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sostituisci caratteri non validi per Python (es: :, /, -) con _
        safe_model = re.sub(r'[^a-zA-Z0-9_]', '_', model)
        return f"{base_name}_{safe_model}_{timestamp}"
    
    def generate_strategy_safely(self, strategy_type: str, model: str) -> Optional[StrategyMetadata]:
        """
        Genera una strategia in modo sicuro, evitando sovrascritture.
        """
        try:
            # Genera nome univoco
            strategy_name = self.generate_unique_strategy_name(strategy_type, model)
            file_name = f"{strategy_name.lower()}.py"
            file_path = f"user_data/strategies/{file_name}"
            
            # Controlla se esiste già
            if os.path.exists(file_path):
                logger.warning(f"File {file_path} esiste già, generando nuovo nome...")
                strategy_name = self.generate_unique_strategy_name(strategy_type, model)
                file_name = f"{strategy_name.lower()}.py"
                file_path = f"user_data/strategies/{file_name}"
            
            logger.info(f"Generando strategia: {strategy_name} con {model}")
            
            # Genera la strategia
            strategy_code = self.generator.generate_futures_strategy(
                strategy_type=strategy_type,
                use_hybrid=True,
                strategy_name=strategy_name
            )
            
            # Validazione automatica
            if self.auto_validation:
                strategy_code = self.converter.validate_and_fix_code(strategy_code, strategy_name)
            
            # Salva la strategia
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(strategy_code)
            
            # Crea metadati
            metadata = StrategyMetadata(
                name=strategy_name,
                file_path=file_path,
                strategy_type=strategy_type,
                model_used=model,
                generation_time=datetime.now(),
                validation_status="validated" if self.auto_validation else "generated"
            )
            
            # Salva metadati
            self.strategies_metadata[strategy_name] = metadata
            self._save_metadata()
            
            logger.info(f"✅ Strategia {strategy_name} generata e salvata")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Errore nella generazione strategia {strategy_type}: {e}")
            return None
    
    def backtest_strategy(self, strategy_name: str) -> Optional[float]:
        """
        Esegue backtest di una strategia e restituisce il punteggio.
        """
        try:
            logger.info(f"Backtesting strategia: {strategy_name}")
            
            # Usa il monitor se disponibile
            if self.backtest_monitor:
                backtest_id = self.backtest_monitor.start_backtest_with_monitoring(
                    strategy_name, 
                    timerange="20240101-20241231"
                )
                logger.info(f"🔄 Backtest avviato con monitoraggio: {backtest_id}")
                
                # Aspetta il completamento (con timeout)
                timeout = 3600  # 1 ora
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    status = self.backtest_monitor.get_backtest_status(backtest_id)
                    if status and status['status'] in ['completed', 'failed']:
                        break
                    time.sleep(10)  # Controlla ogni 10 secondi
                
                # Ottieni il risultato finale
                final_status = self.backtest_monitor.get_backtest_status(backtest_id)
                if final_status and final_status['status'] == 'completed':
                    # Estrai punteggio dal file di risultato
                    result_file = f"backtest_results/{backtest_id}.json"
                    if os.path.exists(result_file):
                        with open(result_file, 'r') as f:
                            result_data = json.load(f)
                            score = result_data.get('total_return', 0.0)
                    else:
                        score = 0.0
                else:
                    logger.warning(f"⚠️ Backtest {strategy_name} fallito o timeout")
                    score = None
            else:
                # Fallback al metodo originale
                result = self.freqtrade.run_backtest(
                    strategy=strategy_name,
                    config_file="config.json",
                    timerange="20240101-20241231"
                )
                
                if result and 'results' in result:
                    score = result['results'].get('total_return', 0.0)
                else:
                    score = None
            
            # Aggiorna metadati se il backtest è riuscito
            if score is not None:
                if strategy_name in self.strategies_metadata:
                    self.strategies_metadata[strategy_name].backtest_score = score
                    self.strategies_metadata[strategy_name].last_backtest = datetime.now()
                    self._save_metadata()
                
                logger.info(f"✅ Backtest {strategy_name}: score {score}")
                return score
            else:
                logger.warning(f"⚠️ Backtest {strategy_name}: nessun risultato")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore backtest {strategy_name}: {e}")
            return None
    
    def get_backtest_status(self) -> Dict[str, Any]:
        """
        Restituisce lo stato dei backtest attivi.
        """
        if not self.backtest_monitor:
            return {"error": "BacktestMonitor non disponibile"}
        
        try:
            return self.backtest_monitor.get_all_backtests()
        except Exception as e:
            logger.error(f"❌ Errore nel recupero stato backtest: {e}")
            return {"error": str(e)}
    
    def start_backtest_monitoring(self) -> bool:
        """
        Avvia il monitoraggio dei backtest.
        """
        if not self.backtest_monitor:
            logger.error("❌ BacktestMonitor non disponibile")
            return False
        
        try:
            self.backtest_monitor.start_monitoring()
            logger.info("✅ Monitoraggio backtest avviato")
            return True
        except Exception as e:
            logger.error(f"❌ Errore nell'avvio monitoraggio: {e}")
            return False
    
    def stop_backtest_monitoring(self) -> bool:
        """
        Ferma il monitoraggio dei backtest.
        """
        if not self.backtest_monitor:
            return False
        
        try:
            self.backtest_monitor.stop_monitoring()
            logger.info("🛑 Monitoraggio backtest fermato")
            return True
        except Exception as e:
            logger.error(f"❌ Errore nell'arresto monitoraggio: {e}")
            return False
    
    def start_backtest_with_monitoring(self, strategy_name: str, timerange: str = "20240101-20241231") -> Optional[str]:
        """
        Avvia un backtest con monitoraggio e restituisce l'ID del backtest.
        """
        if not self.backtest_monitor:
            logger.error("❌ BacktestMonitor non disponibile")
            return None
        
        try:
            backtest_id = self.backtest_monitor.start_backtest_with_monitoring(strategy_name, timerange)
            logger.info(f"🚀 Backtest avviato: {backtest_id}")
            return backtest_id
        except Exception as e:
            logger.error(f"❌ Errore nell'avvio backtest: {e}")
            return None
    
    def cleanup_old_strategies(self):
        """Rimuove solo strategie vecchie e con scarso rendimento. Conserva sempre le strategie buone o ottimizzate."""
        if not self.config.get('cleanup_old_strategies', True):
            return
        
        try:
            current_time = datetime.now()
            min_score = self.config.get('min_backtest_score', 0.1)
            max_age_days = self.config.get('max_strategy_age_days', 30)
            
            strategies_to_remove = []
            
            for name, metadata in self.strategies_metadata.items():
                age_days = (current_time - metadata.generation_time).days
                # Conserva sempre strategie buone o ottimizzate
                is_good = (
                    (metadata.backtest_score is not None and metadata.backtest_score >= min_score)
                    or metadata.validation_status == 'optimized'
                )
                if is_good:
                    continue
                # Elimina solo se vecchia e con scarso rendimento
                if age_days > max_age_days:
                    strategies_to_remove.append(name)
            
            for name in strategies_to_remove:
                metadata = self.strategies_metadata[name]
                if os.path.exists(metadata.file_path):
                    os.remove(metadata.file_path)
                    logger.info(f"🗑️ Rimosso file: {metadata.file_path}")
                del self.strategies_metadata[name]
            
            if strategies_to_remove:
                self._save_metadata()
                logger.info(f"🧹 Rimosse {len(strategies_to_remove)} strategie vecchie/scarse")
        
        except Exception as e:
            logger.error(f"❌ Errore nella pulizia strategie: {e}")
    
    def schedule_tasks(self):
        """Programma le attività automatiche."""
        
        # Generazione periodica di strategie
        schedule.every(self.generation_interval).seconds.do(self.generate_periodic_strategies)
        
        # Backtest periodico
        schedule.every(self.config.get('backtest_interval', 7200)).seconds.do(self.backtest_periodic_strategies)
        
        # Ottimizzazione periodica (ogni 6 ore)
        optimization_interval = self.config.get('optimization', {}).get('optimization_interval', 21600)  # 6 ore
        schedule.every(optimization_interval).seconds.do(self.optimize_periodic_strategies)
        
        # Dry run periodico (ogni 6 ore)
        schedule.every(self.dry_run_interval).seconds.do(self.dry_run_periodic_strategies)
        
        # Esportazione strategie live (ogni 12 ore)
        live_export_interval = self.config.get('live_export', {}).get('export_interval', 43200)  # 12 ore
        schedule.every(live_export_interval).seconds.do(self.export_live_strategies)
        
        # Pulizia periodica
        schedule.every().day.at("02:00").do(self.cleanup_old_strategies)
        
        logger.info("📅 Attività programmate:")
        logger.info(f"   - Generazione strategie: ogni {self.generation_interval} secondi")
        logger.info(f"   - Backtest strategie: ogni {self.config.get('backtest_interval', 7200)} secondi")
        logger.info(f"   - Ottimizzazione strategie: ogni {optimization_interval} secondi")
        logger.info(f"   - Dry run strategie: ogni {self.dry_run_interval} secondi")
        logger.info(f"   - Esportazione strategie live: ogni {live_export_interval} secondi")
        logger.info("   - Pulizia strategie: ogni giorno alle 02:00")
    
    def generate_periodic_strategies(self):
        """Genera strategie periodicamente."""
        try:
            # Controlla limite strategie
            if len(self.strategies_metadata) >= self.max_strategies:
                logger.info(f"Limite strategie raggiunto ({self.max_strategies}), saltando generazione")
                return
            
            strategy_types = self.config.get('strategy_types', ['volatility'])
            models = self.config.get('models', ['phi3'])
            
            # Genera una strategia casuale
            import random
            strategy_type = random.choice(strategy_types)
            model = random.choice(models)
            
            logger.info(f"🔄 Generazione periodica: {strategy_type} con {model}")
            self.generate_strategy_safely(strategy_type, model)
            
        except Exception as e:
            logger.error(f"❌ Errore nella generazione periodica: {e}")
    
    def backtest_periodic_strategies(self):
        """Esegue backtest periodico delle strategie."""
        try:
            if not self.auto_backtest:
                return
            
            # Trova strategie che non hanno backtest recente
            current_time = datetime.now()
            backtest_interval = timedelta(hours=6)  # 6 ore
            
            strategies_to_backtest = []
            
            for name, metadata in self.strategies_metadata.items():
                if (metadata.last_backtest is None or 
                    current_time - metadata.last_backtest > backtest_interval):
                    strategies_to_backtest.append(name)
            
            # Esegui backtest per le prime 3 strategie
            for name in strategies_to_backtest[:3]:
                self.backtest_strategy(name)
                time.sleep(10)  # Pausa tra backtest
                
        except Exception as e:
            logger.error(f"❌ Errore nel backtest periodico: {e}")
    
    def optimize_periodic_strategies(self):
        """Esegue ottimizzazione periodica delle strategie con punteggi bassi."""
        try:
            if not self.config.get('optimization', {}).get('enable_hyperopt', False):
                return
            
            # Trova strategie che necessitano ottimizzazione
            min_score = self.config.get('min_backtest_score', 0.1)
            strategies_to_optimize = []
            
            for name, metadata in self.strategies_metadata.items():
                if (metadata.backtest_score is not None and 
                    metadata.backtest_score < min_score and
                    metadata.validation_status == 'validated'):
                    strategies_to_optimize.append((name, metadata))
            
            # Ordina per punteggio (peggiori prima)
            strategies_to_optimize.sort(key=lambda x: x[1].backtest_score)
            
            # Ottimizza le prime 2 strategie
            for name, metadata in strategies_to_optimize[:2]:
                logger.info(f"🔧 Ottimizzazione automatica strategia: {name}")
                self.optimize_strategy_automatically(name)
                time.sleep(30)  # Pausa tra ottimizzazioni
                
        except Exception as e:
            logger.error(f"❌ Errore nell'ottimizzazione periodica: {e}")
    
    def optimize_strategy_automatically(self, strategy_name: str) -> bool:
        """
        Ottimizza automaticamente una strategia basandosi sui risultati del backtest.
        """
        try:
            # Carica la strategia
            metadata = self.strategies_metadata.get(strategy_name)
            if not metadata or not os.path.exists(metadata.file_path):
                logger.error(f"Strategia {strategy_name} non trovata")
                return False
            
            # Leggi il codice della strategia
            with open(metadata.file_path, 'r') as f:
                strategy_code = f.read()
            
            # Prepara i risultati del backtest per l'ottimizzazione
            backtest_results = {
                'total_return': metadata.backtest_score or 0.0,
                'sharpe_ratio': 0.0,  # Placeholder
                'max_drawdown': 0.0,  # Placeholder
                'win_rate': 0.0,  # Placeholder
                'total_trades': 0  # Placeholder
            }
            
            # Esegui l'ottimizzazione
            optimization_result = self.optimizer.optimize_strategy(
                strategy_code, backtest_results, strategy_name
            )
            
            if optimization_result.success and optimization_result.changes_made:
                # Salva la strategia ottimizzata
                optimized_file_path = metadata.file_path.replace('.py', '_optimized.py')
                with open(optimized_file_path, 'w') as f:
                    f.write(optimization_result.changes_made.get('optimized_code', strategy_code))
                
                # Aggiorna i metadati
                metadata.file_path = optimized_file_path
                metadata.validation_status = 'optimized'
                self._save_metadata()
                
                logger.info(f"✅ Strategia {strategy_name} ottimizzata con successo")
                logger.info(f"   Miglioramenti: {len(optimization_result.improvements)}")
                
                return True
            else:
                logger.info(f"ℹ️ Nessuna ottimizzazione necessaria per {strategy_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore nell'ottimizzazione automatica di {strategy_name}: {e}")
            return False
    
    def start(self):
        """Avvia l'agente di background."""
        if self.is_running:
            logger.warning("Agente già in esecuzione")
            return
        
        logger.info("🚀 Avvio Background Agent...")
        self.is_running = True
        
        # Avvia il monitoraggio dei backtest se disponibile
        if self.backtest_monitor:
            self.start_backtest_monitoring()
        
        # Programma attività
        self.schedule_tasks()
        
        # Avvia thread per le attività programmate
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("✅ Background Agent avviato")
    
    def stop(self):
        """Ferma l'agente di background."""
        logger.info("🛑 Arresto Background Agent...")
        self.is_running = False
        
        # Ferma il monitoraggio dei backtest
        if self.backtest_monitor:
            self.stop_backtest_monitoring()
        
        self._save_metadata()
        logger.info("✅ Background Agent arrestato")
    
    def dry_run_periodic_strategies(self):
        """Esegue dry run periodico delle strategie ottimizzate."""
        try:
            if not self.auto_dry_run or not self.dry_run_manager:
                return
            
            # Controlla quanti dry run sono attivi
            active_dry_runs = len(self.dry_run_manager.active_runs)
            if active_dry_runs >= self.max_dry_runs:
                logger.info(f"ℹ️ Numero massimo di dry run raggiunto ({self.max_dry_runs})")
                return
            
            # Trova strategie candidate per dry run
            strategies_for_dry_run = []
            
            for name, metadata in self.strategies_metadata.items():
                # Criteri per dry run:
                # 1. Strategia validata
                # 2. Backtest score > 0.1 (se disponibile)
                # 3. Non già in dry run
                # 4. Generata negli ultimi 7 giorni
                if (metadata.validation_status == 'validated' and
                    name not in self.dry_run_manager.active_runs and
                    (metadata.backtest_score is None or metadata.backtest_score > 0.1)):
                    
                    # Controlla età della strategia
                    age_days = (datetime.now() - metadata.generation_time).days
                    if age_days <= 7:
                        strategies_for_dry_run.append((name, metadata))
            
            # Ordina per priorità (cogito:8b prima, poi per data)
            def get_priority(metadata):
                priority = 0
                if 'cogito:8b' in metadata.model_used:
                    priority += 10
                elif 'cogito:3b' in metadata.model_used:
                    priority += 5
                elif 'mistral' in metadata.model_used:
                    priority += 3
                return priority
            
            strategies_for_dry_run.sort(key=lambda x: (get_priority(x[1]), x[1].generation_time), reverse=True)
            
            # Avvia dry run per le strategie migliori
            available_slots = self.max_dry_runs - active_dry_runs
            for name, metadata in strategies_for_dry_run[:available_slots]:
                logger.info(f"🚀 Avvio dry run per strategia: {name}")
                self.start_dry_run_for_strategy(name)
                time.sleep(10)  # Pausa tra avvii
                
        except Exception as e:
            logger.error(f"❌ Errore nel dry run periodico: {e}")
    
    def start_dry_run_for_strategy(self, strategy_name: str) -> bool:
        """Avvia un dry run per una strategia specifica."""
        try:
            if not self.dry_run_manager:
                logger.warning("Dry Run Manager non disponibile")
                return False
            
            metadata = self.strategies_metadata.get(strategy_name)
            if not metadata:
                logger.error(f"Strategia {strategy_name} non trovata nei metadati")
                return False
            
            # Crea configurazione dry run
            config = DryRunConfig(
                strategy_name=strategy_name,
                duration_days=self.dry_run_duration_days,
                stake_amount=self.dry_run_stake_amount,
                max_open_trades=self.dry_run_max_trades,
                pairs=self.dry_run_pairs,
                risk_limits=self.dry_run_risk_limits
            )
            
            # Avvia dry run
            success = self.dry_run_manager.start_dry_run(strategy_name, config)
            
            if success:
                logger.info(f"✅ Dry run avviato per {strategy_name}")
                # Aggiorna metadati
                metadata.is_active = True
                self._save_metadata()
                return True
            else:
                logger.error(f"❌ Errore nell'avvio dry run per {strategy_name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore nell'avvio dry run per {strategy_name}: {e}")
            return False
    
    def stop_dry_run_for_strategy(self, strategy_name: str) -> bool:
        """Ferma un dry run per una strategia specifica."""
        try:
            if not self.dry_run_manager:
                return False
            
            success = self.dry_run_manager.stop_dry_run(strategy_name)
            
            if success:
                logger.info(f"✅ Dry run fermato per {strategy_name}")
                # Aggiorna metadati
                metadata = self.strategies_metadata.get(strategy_name)
                if metadata:
                    metadata.is_active = False
                    self._save_metadata()
                return True
            else:
                logger.warning(f"⚠️ Dry run {strategy_name} non trovato o già fermato")
                return False
                
        except Exception as e:
            logger.error(f"❌ Errore nel fermare dry run per {strategy_name}: {e}")
            return False
    
    def get_dry_run_status(self) -> Dict[str, Any]:
        """Restituisce lo status dei dry run attivi."""
        if not self.dry_run_manager:
            return {'error': 'Dry Run Manager non disponibile'}
        
        try:
            return self.dry_run_manager.get_status()
        except Exception as e:
            return {'error': f'Errore nel recupero status: {e}'}
    
    def export_live_strategies(self):
        """Esporta automaticamente le migliori strategie per il live trading."""
        try:
            if not self.live_exporter:
                logger.warning("Live Strategies Exporter non disponibile")
                return
            
            logger.info("🚀 Esportazione automatica strategie per live trading...")
            
            # Esegui esportazione
            result = self.live_exporter.export_best_strategies()
            
            if result['exported'] > 0:
                logger.info(f"✅ Esportate {result['exported']} strategie per live trading")
                
                # Genera report
                report = self.live_exporter.generate_live_report()
                logger.info("📊 Report strategie live:")
                logger.info(report)
            else:
                logger.info("ℹ️ Nessuna nuova strategia esportata per live trading")
                
        except Exception as e:
            logger.error(f"❌ Errore nell'esportazione strategie live: {e}")
    
    def get_live_strategies_status(self) -> Dict[str, Any]:
        """Restituisce lo status delle strategie live."""
        if not self.live_exporter:
            return {'error': 'Live Strategies Exporter non disponibile'}
        
        try:
            return self.live_exporter.get_live_strategies_status()
        except Exception as e:
            return {'error': f'Errore nel recupero status live: {e}'}
    
    def get_status(self) -> Dict[str, Any]:
        """Restituisce lo stato dell'agente."""
        status = {
            'is_running': self.is_running,
            'total_strategies': len(self.strategies_metadata),
            'active_strategies': sum(1 for s in self.strategies_metadata.values() if s.is_active),
            'validated_strategies': sum(1 for s in self.strategies_metadata.values() if s.validation_status == 'validated'),
            'backtested_strategies': sum(1 for s in self.strategies_metadata.values() if s.backtest_score is not None),
            'config': self.config,
            'backtest_monitor_available': self.backtest_monitor is not None,
            'dry_run_manager_available': self.dry_run_manager is not None
        }
        
        # Aggiungi stato dei backtest se il monitor è disponibile
        if self.backtest_monitor:
            try:
                backtest_status = self.get_backtest_status()
                status['active_backtests'] = len([b for b in backtest_status.values() if isinstance(b, dict) and b.get('status') == 'running'])
                status['backtest_status'] = backtest_status
            except Exception as e:
                status['backtest_status_error'] = str(e)
        
        # Aggiungi stato dei dry run se il manager è disponibile
        if self.dry_run_manager:
            try:
                dry_run_status = self.get_dry_run_status()
                status['active_dry_runs'] = dry_run_status.get('active_runs', 0)
                status['dry_run_status'] = dry_run_status
            except Exception as e:
                status['dry_run_status_error'] = str(e)
        
        return status

def main():
    """Funzione principale per testare l'agente."""
    global _agent_instance
    agent = BackgroundAgent()
    _agent_instance = agent
    
    try:
        # Avvia l'agente
        agent.start()
        
        # Mantieni l'agente in esecuzione
        logger.info("🔄 Background Agent in esecuzione. Premi Ctrl+C per fermare.")
        
        while agent.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Interruzione manuale (Ctrl+C)")
    finally:
        agent.stop()
        _agent_instance = None

if __name__ == "__main__":
    main() 