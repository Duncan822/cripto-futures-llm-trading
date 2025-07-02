#!/usr/bin/env python3
"""
Hyperopt + LLM Optimizer: Combina ottimizzazione numerica con miglioramenti logici.
Prima esegue Hyperopt per ottimizzare parametri, poi usa LLM per miglioramenti logici.
"""

import os
import json
import logging
import subprocess
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import re

from llm_utils import query_ollama_fast
from .strategy_converter import StrategyConverter

logger = logging.getLogger(__name__)

@dataclass
class HyperoptResult:
    """Risultato dell'ottimizzazione Hyperopt."""
    best_params: Dict[str, Any]
    best_score: float
    total_epochs: int
    optimization_time: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class CombinedOptimizationResult:
    """Risultato dell'ottimizzazione combinata Hyperopt + LLM."""
    original_score: float
    hyperopt_score: float
    final_score: Optional[float]
    hyperopt_result: HyperoptResult
    llm_improvements: List[str]
    final_code: str
    optimization_time: datetime
    success: bool
    error_message: Optional[str] = None

class HyperoptLLMOptimizer:
    """
    Agente che combina Hyperopt per ottimizzazione parametri e LLM per miglioramenti logici.
    """

    def __init__(self, default_model: str = "cogito:8b"):
        self.default_model = default_model
        self.converter = StrategyConverter()

        # Configurazione
        self.config = {
            'hyperopt_epochs': 50,
            'hyperopt_spaces': ['buy', 'sell', 'roi', 'stoploss'],
            'hyperopt_timeout': 1800,  # 30 minuti
            'llm_timeout': 300,  # 5 minuti
            'min_improvement_threshold': 0.05
        }

    def optimize_strategy(self, strategy_code: str, backtest_results: dict[str, float], strategy_name: str = None) -> CombinedOptimizationResult:
        """
        Ottimizza la strategia usando Hyperopt + LLM.
        """
        try:
            if strategy_name is None:
                strategy_name = self._extract_strategy_name(strategy_code)

            original_score = backtest_results.get('total_return', 0.0)
            logger.info(f"🔧 Ottimizzazione combinata strategia {strategy_name} (score attuale: {original_score})")

            # Step 1: Hyperopt per ottimizzazione parametri
            logger.info("📊 Step 1: Esecuzione Hyperopt...")
            hyperopt_result = self._run_hyperopt(strategy_code, strategy_name)

            if not hyperopt_result.success:
                return CombinedOptimizationResult(
                    original_score=original_score,
                    hyperopt_score=original_score,
                    final_score=None,
                    hyperopt_result=hyperopt_result,
                    llm_improvements=[],
                    final_code=strategy_code,
                    optimization_time=datetime.now(),
                    success=False,
                    error_message=hyperopt_result.error_message
                )

            # Step 2: Applica parametri ottimizzati
            logger.info("🔧 Step 2: Applicazione parametri Hyperopt...")
            hyperopt_code = self._apply_hyperopt_params(strategy_code, hyperopt_result.best_params)

            # Step 3: LLM per miglioramenti logici
            logger.info("🧠 Step 3: Analisi LLM per miglioramenti...")
            llm_improvements = self._generate_llm_improvements(
                hyperopt_code, backtest_results, hyperopt_result
            )

            # Step 4: Applica miglioramenti LLM
            final_code = self._apply_llm_improvements(hyperopt_code, llm_improvements)

            # Valida codice finale
            validated_code = self.converter.validate_and_fix_code(final_code, strategy_name)

            return CombinedOptimizationResult(
                original_score=original_score,
                hyperopt_score=hyperopt_result.best_score,
                final_score=None,  # Sarà calcolato dal backtest successivo
                hyperopt_result=hyperopt_result,
                llm_improvements=llm_improvements,
                final_code=validated_code,
                optimization_time=datetime.now(),
                success=True
            )

        except Exception as e:
            logger.error(f"❌ Errore nell'ottimizzazione combinata: {e}")
            return CombinedOptimizationResult(
                original_score=original_score,
                hyperopt_score=original_score,
                final_score=None,
                hyperopt_result=HyperoptResult({}, 0.0, 0, datetime.now(), False, str(e)),
                llm_improvements=[],
                final_code=strategy_code,
                optimization_time=datetime.now(),
                success=False,
                error_message=str(e)
            )

    def _run_hyperopt(self, strategy_code: str, strategy_name: str) -> HyperoptResult:
        """
        Esegue Hyperopt per ottimizzare i parametri della strategia.
        """
        try:
            # Salva strategia temporaneamente
            temp_strategy_file = f"user_data/strategies/{strategy_name.lower()}_temp.py"
            with open(temp_strategy_file, 'w') as f:
                f.write(strategy_code)

            # Configurazione Hyperopt
            hyperopt_config = {
                'strategy': strategy_name,
                'epochs': self.config['hyperopt_epochs'],
                'spaces': self.config['hyperopt_spaces'],
                'timerange': '20240101-20241231',
                'timeframe': '5m'
            }

            # Salva config temporanea
            config_file = f"hyperopt_config_{strategy_name}.json"
            with open(config_file, 'w') as f:
                json.dump(hyperopt_config, f, indent=2)

            # Esegui Hyperopt
            cmd = [
                'freqtrade', 'hyperopt',
                '--strategy', strategy_name,
                '--epochs', str(self.config['hyperopt_epochs']),
                '--timerange', '20240101-20241231',
                '--timeframe', '5m',
                '--config', 'config.json'
            ]

            # Aggiungi spazi separatamente
            for space in self.config['hyperopt_spaces']:
                cmd.extend(['--spaces', space])

            logger.info(f"🚀 Esecuzione Hyperopt: {' '.join(cmd)}")

            # Esegui comando con timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config['hyperopt_timeout']
            )

            # Pulisci file temporanei
            if os.path.exists(temp_strategy_file):
                os.remove(temp_strategy_file)
            if os.path.exists(config_file):
                os.remove(config_file)

            if result.returncode == 0:
                # Estrai risultati da output
                best_params, best_score = self._extract_hyperopt_results(result.stdout)

                return HyperoptResult(
                    best_params=best_params,
                    best_score=best_score,
                    total_epochs=self.config['hyperopt_epochs'],
                    optimization_time=datetime.now(),
                    success=True
                )
            else:
                logger.error(f"❌ Hyperopt fallito: {result.stderr}")
                return HyperoptResult(
                    best_params={},
                    best_score=0.0,
                    total_epochs=0,
                    optimization_time=datetime.now(),
                    success=False,
                    error_message=result.stderr
                )

        except subprocess.TimeoutExpired:
            logger.error("⏰ Timeout Hyperopt")
            return HyperoptResult(
                best_params={},
                best_score=0.0,
                total_epochs=0,
                optimization_time=datetime.now(),
                success=False,
                error_message="Timeout Hyperopt"
            )
        except Exception as e:
            logger.error(f"❌ Errore Hyperopt: {e}")
            return HyperoptResult(
                best_params={},
                best_score=0.0,
                total_epochs=0,
                optimization_time=datetime.now(),
                success=False,
                error_message=str(e)
            )

    def _extract_hyperopt_results(self, output: str) -> Tuple[Dict[str, Any], float]:
        """
        Estrae i migliori parametri e score dall'output di Hyperopt.
        """
        try:
            # Cerca i migliori parametri nell'output
            best_params = {}
            best_score = 0.0

            # Pattern per estrarre parametri
            param_pattern = r"(\w+):\s*([\d.]+)"
            score_pattern = r"Best\s+result:\s*([\d.-]+)"

            # Estrai parametri
            params = re.findall(param_pattern, output)
            for param, value in params:
                try:
                    best_params[param] = float(value)
                except ValueError:
                    best_params[param] = value

            # Estrai score
            score_match = re.search(score_pattern, output)
            if score_match:
                best_score = float(score_match.group(1))

            return best_params, best_score

        except Exception as e:
            logger.warning(f"⚠️ Errore nell'estrazione risultati Hyperopt: {e}")
            return {}, 0.0

    def _apply_hyperopt_params(self, strategy_code: str, best_params: Dict[str, Any]) -> str:
        """
        Applica i parametri ottimizzati da Hyperopt al codice della strategia.
        """
        try:
            modified_code = strategy_code

            # Applica parametri ROI
            if 'roi' in best_params:
                roi_value = best_params['roi']
                modified_code = re.sub(
                    r'minimal_roi\s*=\s*\{[^}]*\}',
                    f'minimal_roi = {{"0": {roi_value}}}',
                    modified_code
                )

            # Applica parametri stoploss
            if 'stoploss' in best_params:
                stoploss_value = best_params['stoploss']
                modified_code = re.sub(
                    r'stoploss\s*=\s*[-\d.]+',
                    f'stoploss = {stoploss_value}',
                    modified_code
                )

            # Applica parametri buy/sell
            for param, value in best_params.items():
                if param.startswith('buy_') or param.startswith('sell_'):
                    # Cerca e sostituisci parametri nelle condizioni
                    pattern = rf'{param}\s*=\s*[-\d.]+'
                    replacement = f'{param} = {value}'
                    modified_code = re.sub(pattern, replacement, modified_code)

            return modified_code

        except Exception as e:
            logger.error(f"❌ Errore nell'applicazione parametri Hyperopt: {e}")
            return strategy_code

    def _generate_llm_improvements(self, strategy_code: str, backtest_results: dict[str, float], hyperopt_result: HyperoptResult) -> List[str]:
        """
        Genera miglioramenti logici usando LLM dopo Hyperopt.
        """
        try:
            prompt = self._create_llm_prompt(strategy_code, backtest_results, hyperopt_result)

            llm_response = query_ollama_fast(prompt, self.default_model, timeout=self.config['llm_timeout'])

            improvements = self._extract_improvements_from_llm(llm_response)

            return improvements

        except Exception as e:
            logger.error(f"❌ Errore nella generazione miglioramenti LLM: {e}")
            return []

    def _create_llm_prompt(self, strategy_code: str, backtest_results: dict[str, float], hyperopt_result: HyperoptResult) -> str:
        """
        Crea prompt per LLM dopo Hyperopt.
        """
        return f"""
Analizza questa strategia di trading che è stata ottimizzata con Hyperopt e suggerisci miglioramenti logici.

STRATEGIA ORIGINALE:
{strategy_code}

RISULTATI BACKTEST ORIGINALI:
{json.dumps(backtest_results, indent=2)}

RISULTATI HYPEROPT:
- Migliori parametri: {hyperopt_result.best_params}
- Score migliorato: {hyperopt_result.best_score}
- Epochs eseguiti: {hyperopt_result.total_epochs}

Suggerisci miglioramenti logici alla strategia (non parametri, ma logica di trading):
1. Condizioni di entrata/uscita
2. Indicatori aggiuntivi
3. Gestione del rischio
4. Filtri di trend
5. Ottimizzazioni del codice

Fornisci solo suggerimenti specifici e implementabili, uno per riga.
"""

    def _extract_improvements_from_llm(self, llm_response: str) -> List[str]:
        """
        Estrae i miglioramenti dalla risposta LLM.
        """
        improvements = []

        # Estrai suggerimenti numerati o con trattini
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line)):
                # Rimuovi numerazione e simboli
                clean_line = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if clean_line:
                    improvements.append(clean_line)

        return improvements

    def _apply_llm_improvements(self, strategy_code: str, improvements: List[str]) -> str:
        """
        Applica i miglioramenti suggeriti dal LLM.
        """
        # Per ora restituisce il codice invariato
        # Implementazione avanzata richiederebbe parsing più sofisticato
        return strategy_code

    def _extract_strategy_name(self, strategy_code: str) -> str:
        """
        Estrae il nome della strategia dal codice.
        """
        match = re.search(r'class\s+(\w+)', strategy_code)
        return match.group(1) if match else "UnknownStrategy"

    def get_optimization_summary(self, result: CombinedOptimizationResult) -> str:
        """
        Genera un riepilogo dell'ottimizzazione combinata.
        """
        summary = f"""
🔧 OTTIMIZZAZIONE COMBINATA HYPEROPT + LLM
{'='*50}

📊 RISULTATI:
   Score originale: {result.original_score:.3f}
   Score dopo Hyperopt: {result.hyperopt_score:.3f}
   Miglioramento Hyperopt: {((result.hyperopt_score - result.original_score) / result.original_score * 100):.1f}%

⚙️ HYPEROPT:
   Parametri ottimizzati: {len(result.hyperopt_result.best_params)}
   Epochs eseguiti: {result.hyperopt_result.total_epochs}
   Successo: {'✅' if result.hyperopt_result.success else '❌'}

🧠 MIGLIORAMENTI LLM:
   Suggerimenti generati: {len(result.llm_improvements)}
"""

        if result.llm_improvements:
            summary += "\n   Suggerimenti:\n"
            for i, improvement in enumerate(result.llm_improvements[:5], 1):
                summary += f"   {i}. {improvement}\n"

        summary += f"""
⏱️ Tempo totale: {result.optimization_time.strftime('%Y-%m-%d %H:%M:%S')}
✅ Successo: {'Sì' if result.success else 'No'}
"""

        return summary
