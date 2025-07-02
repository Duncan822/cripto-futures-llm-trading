#!/usr/bin/env python3
"""
Live Strategies Exporter: Esporta automaticamente le strategie migliori per il live trading.
"""

import os
import json
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class LiveStrategyConfig:
    """Configurazione per l'esportazione delle strategie live."""
    min_backtest_score: float = 0.1
    min_win_rate: float = 0.4
    min_total_trades: int = 10
    max_drawdown_threshold: float = 0.15
    min_sharpe_ratio: float = 0.8
    export_optimized_only: bool = True
    export_interval_hours: int = 24
    max_live_strategies: int = 10
    backup_old_strategies: bool = True

class LiveStrategiesExporter:
    """
    Gestisce l'esportazione delle strategie migliori per il live trading.
    """
    
    def __init__(self, config: Optional[LiveStrategyConfig] = None):
        self.config = config or LiveStrategyConfig()
        self.live_dir = Path("live_strategies")
        self.backup_dir = Path("live_strategies_backup")
        self.metadata_file = self.live_dir / "live_strategies_metadata.json"
        
        # Crea directory se non esistono
        self.live_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Carica metadati esistenti
        self.live_metadata = self._load_live_metadata()
    
    def _load_live_metadata(self) -> Dict[str, Any]:
        """Carica i metadati delle strategie live esistenti."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Errore nel caricamento metadati live: {e}")
        return {}
    
    def _save_live_metadata(self):
        """Salva i metadati delle strategie live."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.live_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Errore nel salvataggio metadati live: {e}")
    
    def evaluate_strategy_for_live(self, strategy_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valuta se una strategia è adatta per il live trading.
        """
        evaluation = {
            'strategy_name': strategy_name,
            'eligible': False,
            'score': 0.0,
            'reasons': [],
            'strengths': [],
            'weaknesses': []
        }
        
        # Criteri di valutazione
        backtest_score = metadata.get('backtest_score', 0)
        validation_status = metadata.get('validation_status', 'unknown')
        model_used = metadata.get('model_used', 'unknown')
        strategy_type = metadata.get('strategy_type', 'unknown')
        generation_time = metadata.get('generation_time', '')
        
        # Calcola punteggio complessivo
        score = 0.0
        
        # 1. Punteggio backtest (40% del peso)
        if backtest_score is not None and backtest_score >= self.config.min_backtest_score:
            score += backtest_score * 0.4
            evaluation['strengths'].append(f"Buon backtest score: {backtest_score:.3f}")
        else:
            evaluation['reasons'].append(f"Backtest score insufficiente: {backtest_score}")
        
        # 2. Status di validazione (20% del peso)
        if validation_status == 'optimized':
            score += 0.2
            evaluation['strengths'].append("Strategia ottimizzata")
        elif validation_status == 'validated':
            score += 0.1
            evaluation['strengths'].append("Strategia validata")
        else:
            evaluation['reasons'].append(f"Status non ottimale: {validation_status}")
        
        # 3. Qualità del modello (20% del peso)
        model_score = 0.0
        if 'cogito:8b' in model_used:
            model_score = 0.2
            evaluation['strengths'].append("Modello ad alta qualità (cogito:8b)")
        elif 'cogito:3b' in model_used:
            model_score = 0.15
            evaluation['strengths'].append("Modello di buona qualità (cogito:3b)")
        elif 'mistral' in model_used:
            model_score = 0.1
            evaluation['strengths'].append("Modello affidabile (mistral)")
        else:
            evaluation['weaknesses'].append(f"Modello sconosciuto: {model_used}")
        score += model_score
        
        # 4. Età della strategia (10% del peso)
        if generation_time:
            try:
                gen_dt = datetime.fromisoformat(generation_time.replace('Z', '+00:00'))
                age_days = (datetime.now() - gen_dt).days
                if age_days <= 7:
                    score += 0.1
                    evaluation['strengths'].append("Strategia recente")
                elif age_days <= 30:
                    score += 0.05
                    evaluation['strengths'].append("Strategia moderatamente recente")
                else:
                    evaluation['weaknesses'].append(f"Strategia vecchia ({age_days} giorni)")
            except:
                evaluation['weaknesses'].append("Data generazione non valida")
        
        # 5. Tipo di strategia (10% del peso)
        if strategy_type in ['volatility', 'momentum']:
            score += 0.1
            evaluation['strengths'].append(f"Tipo strategia affidabile: {strategy_type}")
        else:
            evaluation['weaknesses'].append(f"Tipo strategia meno testato: {strategy_type}")
        
        # Determina se è eleggibile
        evaluation['score'] = score
        evaluation['eligible'] = (
            score >= 0.6 and  # Punteggio minimo complessivo
            backtest_score is not None and backtest_score >= self.config.min_backtest_score and
            validation_status in ['validated', 'optimized']
        )
        
        if not evaluation['eligible']:
            evaluation['reasons'].append(f"Punteggio complessivo insufficiente: {score:.3f}")
        
        return evaluation
    
    def find_best_strategies(self) -> List[Dict[str, Any]]:
        """
        Trova le migliori strategie candidate per il live trading.
        """
        try:
            # Carica metadati delle strategie
            if not os.path.exists("strategies_metadata.json"):
                logger.warning("File metadati strategie non trovato")
                return []
            
            with open("strategies_metadata.json", 'r') as f:
                strategies_data = json.load(f)
            
            # Valuta tutte le strategie
            evaluations = []
            for strategy_name, metadata in strategies_data.items():
                evaluation = self.evaluate_strategy_for_live(strategy_name, metadata)
                if evaluation['eligible']:
                    evaluations.append(evaluation)
            
            # Ordina per punteggio (migliori prima)
            evaluations.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Trovate {len(evaluations)} strategie candidate per live trading")
            return evaluations
            
        except Exception as e:
            logger.error(f"Errore nella ricerca strategie migliori: {e}")
            return []
    
    def export_strategy_to_live(self, strategy_name: str, evaluation: Dict[str, Any]) -> bool:
        """
        Esporta una strategia nella cartella live.
        """
        try:
            # Trova il file della strategia
            strategy_file = f"user_data/strategies/{strategy_name.lower()}.py"
            if not os.path.exists(strategy_file):
                logger.error(f"File strategia non trovato: {strategy_file}")
                return False
            
            # Crea nome file per live
            live_filename = f"live_{strategy_name}.py"
            live_filepath = self.live_dir / live_filename
            
            # Backup strategia esistente se presente
            if live_filepath.exists() and self.config.backup_old_strategies:
                backup_filepath = self.backup_dir / f"{live_filename}.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(live_filepath, backup_filepath)
                logger.info(f"Backup strategia esistente: {backup_filepath}")
            
            # Copia strategia
            shutil.copy2(strategy_file, live_filepath)
            
            # Aggiorna metadati live
            self.live_metadata[strategy_name] = {
                'export_time': datetime.now().isoformat(),
                'evaluation_score': evaluation['score'],
                'strengths': evaluation['strengths'],
                'weaknesses': evaluation['weaknesses'],
                'live_filename': live_filename,
                'status': 'active'
            }
            
            self._save_live_metadata()
            
            logger.info(f"✅ Strategia esportata per live: {strategy_name}")
            logger.info(f"   Punteggio: {evaluation['score']:.3f}")
            logger.info(f"   File: {live_filepath}")
            
            return True
            
        except Exception as e:
            logger.error(f"Errore nell'esportazione strategia {strategy_name}: {e}")
            return False
    
    def export_best_strategies(self) -> Dict[str, Any]:
        """
        Esporta le migliori strategie per il live trading.
        """
        logger.info("🚀 Esportazione strategie migliori per live trading...")
        
        # Trova strategie candidate
        evaluations = self.find_best_strategies()
        
        if not evaluations:
            logger.warning("Nessuna strategia candidata trovata")
            return {'exported': 0, 'total_candidates': 0}
        
        # Limita il numero di strategie da esportare
        max_strategies = min(self.config.max_live_strategies, len(evaluations))
        evaluations = evaluations[:max_strategies]
        
        # Esporta strategie
        exported_count = 0
        for evaluation in evaluations:
            strategy_name = evaluation['strategy_name']
            
            # Controlla se già esportata
            if strategy_name in self.live_metadata:
                logger.info(f"ℹ️ Strategia già esportata: {strategy_name}")
                continue
            
            if self.export_strategy_to_live(strategy_name, evaluation):
                exported_count += 1
        
        logger.info(f"✅ Esportazione completata: {exported_count}/{len(evaluations)} strategie")
        
        return {
            'exported': exported_count,
            'total_candidates': len(evaluations),
            'evaluations': evaluations
        }
    
    def get_live_strategies_status(self) -> Dict[str, Any]:
        """
        Restituisce lo status delle strategie live.
        """
        status = {
            'total_live_strategies': len(self.live_metadata),
            'active_strategies': sum(1 for s in self.live_metadata.values() if s.get('status') == 'active'),
            'strategies': []
        }
        
        for strategy_name, metadata in self.live_metadata.items():
            strategy_info = {
                'name': strategy_name,
                'export_time': metadata.get('export_time'),
                'evaluation_score': metadata.get('evaluation_score'),
                'status': metadata.get('status'),
                'live_filename': metadata.get('live_filename'),
                'strengths': metadata.get('strengths', []),
                'weaknesses': metadata.get('weaknesses', [])
            }
            status['strategies'].append(strategy_info)
        
        return status
    
    def cleanup_old_live_strategies(self, max_age_days: int = 90):
        """
        Pulisce le strategie live troppo vecchie.
        """
        try:
            current_time = datetime.now()
            strategies_to_remove = []
            
            for strategy_name, metadata in self.live_metadata.items():
                export_time = metadata.get('export_time')
                if export_time:
                    try:
                        export_dt = datetime.fromisoformat(export_time.replace('Z', '+00:00'))
                        age_days = (current_time - export_dt).days
                        
                        if age_days > max_age_days:
                            strategies_to_remove.append(strategy_name)
                    except:
                        continue
            
            # Rimuovi strategie vecchie
            for strategy_name in strategies_to_remove:
                metadata = self.live_metadata[strategy_name]
                live_filename = metadata.get('live_filename')
                
                if live_filename:
                    live_filepath = self.live_dir / live_filename
                    if live_filepath.exists():
                        os.remove(live_filepath)
                        logger.info(f"🗑️ Rimossa strategia live vecchia: {strategy_name}")
                
                del self.live_metadata[strategy_name]
            
            if strategies_to_remove:
                self._save_live_metadata()
                logger.info(f"🧹 Rimosse {len(strategies_to_remove)} strategie live vecchie")
            
        except Exception as e:
            logger.error(f"Errore nella pulizia strategie live: {e}")
    
    def generate_live_report(self) -> str:
        """
        Genera un report delle strategie live.
        """
        status = self.get_live_strategies_status()
        
        report = f"""
🚀 REPORT STRATEGIE LIVE TRADING
{'=' * 50}

📊 Statistiche Generali:
   • Strategie totali: {status['total_live_strategies']}
   • Strategie attive: {status['active_strategies']}

📋 Strategie Live:
"""
        
        for strategy in status['strategies']:
            report += f"""
🔹 {strategy['name']}
   📅 Esportata: {strategy['export_time'][:10] if strategy['export_time'] else 'N/A'}
   📊 Punteggio: {strategy['evaluation_score']:.3f}
   📁 File: {strategy['live_filename']}
   ✅ Status: {strategy['status']}
   
   💪 Punti di forza:
"""
            for strength in strategy['strengths']:
                report += f"      • {strength}\n"
            
            if strategy['weaknesses']:
                report += "   ⚠️ Debolezze:\n"
                for weakness in strategy['weaknesses']:
                    report += f"      • {weakness}\n"
        
        report += f"""
📁 Directory: {self.live_dir.absolute()}
📄 Metadati: {self.metadata_file.absolute()}

💡 Per utilizzare queste strategie:
   1. Copia i file da {self.live_dir} in user_data/strategies/
   2. Configura Freqtrade per il live trading
   3. Avvia il bot con le strategie selezionate
"""
        
        return report

def main():
    """Funzione principale per testare l'esportatore."""
    config = LiveStrategyConfig(
        min_backtest_score=0.1,
        export_optimized_only=True,
        max_live_strategies=5
    )
    
    exporter = LiveStrategiesExporter(config)
    
    print("🚀 Test Esportatore Strategie Live")
    print("=" * 40)
    
    # Trova strategie candidate
    evaluations = exporter.find_best_strategies()
    
    print(f"\n📊 Strategie candidate trovate: {len(evaluations)}")
    
    if evaluations:
        print("\n🏆 Top 3 strategie candidate:")
        for i, eval in enumerate(evaluations[:3], 1):
            print(f"\n{i}. {eval['strategy_name']}")
            print(f"   Punteggio: {eval['score']:.3f}")
            print(f"   Eleggibile: {'✅' if eval['eligible'] else '❌'}")
            if eval['strengths']:
                print(f"   Punti di forza: {', '.join(eval['strengths'][:2])}")
        
        # Esporta strategie
        result = exporter.export_best_strategies()
        print(f"\n✅ Esportazione completata: {result['exported']} strategie esportate")
        
        # Genera report
        report = exporter.generate_live_report()
        print(report)
    else:
        print("❌ Nessuna strategia candidata trovata")

if __name__ == "__main__":
    main() 