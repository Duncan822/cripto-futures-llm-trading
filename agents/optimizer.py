"""
Agente Ottimizzatore: propone miglioramenti e ottimizza parametri delle strategie.
Analizza i risultati del backtest e suggerisce miglioramenti usando LLM.
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import ast

from llm_utils import query_ollama, query_ollama_fast
from .strategy_converter import StrategyConverter

logger = logging.getLogger(__name__)

@dataclass
class OptimizationResult:
    """Risultato dell'ottimizzazione di una strategia."""
    original_score: float
    optimized_score: Optional[float]
    improvements: List[str]
    changes_made: Dict[str, Any]
    optimization_time: datetime
    success: bool
    error_message: Optional[str] = None

class OptimizerAgent:
    """
    Agente che ottimizza strategie di trading basandosi sui risultati del backtest.
    """
    
    def __init__(self, default_model: str = "phi3"):
        self.default_model = default_model
        self.converter = StrategyConverter()
        
        # Configurazione ottimizzazione
        self.optimization_config = {
            'min_improvement_threshold': 0.05,  # 5% miglioramento minimo
            'max_optimization_attempts': 3,
            'optimization_timeout': 600,  # 10 minuti
            'enable_parameter_optimization': True,
            'enable_logic_optimization': True,
            'enable_risk_management_optimization': True
        }
    
    def optimize_strategy(self, strategy_code: str, backtest_results: dict[str, float], strategy_name: str = None) -> OptimizationResult:
        """
        Ottimizza la strategia in base ai risultati del backtest.
        
        Args:
            strategy_code: Codice della strategia da ottimizzare
            backtest_results: Risultati del backtest (total_return, sharpe_ratio, max_drawdown, etc.)
            strategy_name: Nome della strategia (se None, viene estratto dal codice)
            
        Returns:
            OptimizationResult con i dettagli dell'ottimizzazione
        """
        try:
            # Estrai nome strategia se non fornito
            if strategy_name is None:
                strategy_name = self._extract_strategy_name(strategy_code)
            
            original_score = backtest_results.get('total_return', 0.0)
            
            logger.info(f"🔧 Ottimizzazione strategia {strategy_name} (score attuale: {original_score})")
            
            # Analizza la strategia e i risultati
            analysis = self._analyze_strategy_performance(strategy_code, backtest_results)
            
            # Genera suggerimenti di ottimizzazione
            optimization_suggestions = self._generate_optimization_suggestions(
                strategy_code, backtest_results, analysis
            )
            
            # Applica le ottimizzazioni
            optimized_code = self._apply_optimizations(
                strategy_code, optimization_suggestions, strategy_name
            )
            
            # Valida il codice ottimizzato
            if optimized_code != strategy_code:
                validated_code = self.converter.validate_and_fix_code(optimized_code, strategy_name)
                
                # Calcola le modifiche apportate
                changes = self._calculate_changes(strategy_code, validated_code)
                
                return OptimizationResult(
                    original_score=original_score,
                    optimized_score=None,  # Sarà calcolato dal backtest successivo
                    improvements=optimization_suggestions,
                    changes_made=changes,
                    optimization_time=datetime.now(),
                    success=True
                )
            else:
                return OptimizationResult(
                    original_score=original_score,
                    optimized_score=original_score,
                    improvements=["Nessuna ottimizzazione necessaria"],
                    changes_made={},
                    optimization_time=datetime.now(),
                    success=True
                )
                
        except Exception as e:
            logger.error(f"❌ Errore nell'ottimizzazione: {e}")
            return OptimizationResult(
                original_score=backtest_results.get('total_return', 0.0),
                optimized_score=None,
                improvements=[],
                changes_made={},
                optimization_time=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _analyze_strategy_performance(self, strategy_code: str, backtest_results: dict[str, float]) -> dict[str, Any]:
        """
        Analizza le performance della strategia per identificare aree di miglioramento.
        """
        analysis = {
            'total_return': backtest_results.get('total_return', 0.0),
            'sharpe_ratio': backtest_results.get('sharpe_ratio', 0.0),
            'max_drawdown': backtest_results.get('max_drawdown', 0.0),
            'win_rate': backtest_results.get('win_rate', 0.0),
            'total_trades': backtest_results.get('total_trades', 0),
            'avg_trade_duration': backtest_results.get('avg_trade_duration', 0),
            'issues': [],
            'strengths': [],
            'optimization_areas': []
        }
        
        # Analisi basata sui risultati
        if analysis['total_return'] < 0.1:
            analysis['issues'].append("Rendimento basso")
            analysis['optimization_areas'].append("entry_conditions")
            
        if analysis['sharpe_ratio'] < 1.0:
            analysis['issues'].append("Sharpe ratio basso")
            analysis['optimization_areas'].append("risk_management")
            
        if analysis['max_drawdown'] > 0.15:
            analysis['issues'].append("Drawdown eccessivo")
            analysis['optimization_areas'].append("stop_loss")
            
        if analysis['win_rate'] < 0.4:
            analysis['issues'].append("Win rate basso")
            analysis['optimization_areas'].append("entry_conditions")
            
        if analysis['total_trades'] < 10:
            analysis['issues'].append("Pochi trade")
            analysis['optimization_areas'].append("entry_conditions")
            
        # Analisi del codice
        code_analysis = self._analyze_strategy_code(strategy_code)
        analysis.update(code_analysis)
        
        return analysis
    
    def _analyze_strategy_code(self, strategy_code: str) -> dict[str, Any]:
        """
        Analizza il codice della strategia per identificare problemi e opportunità.
        """
        analysis = {
            'indicators_used': [],
            'entry_conditions': [],
            'exit_conditions': [],
            'parameters': [],
            'code_issues': [],
            'optimization_opportunities': []
        }
        
        try:
            # Estrai indicatori
            indicators = re.findall(r"dataframe\['([^']+)'\]", strategy_code)
            analysis['indicators_used'] = list(set(indicators))
            
            # Estrai condizioni di entrata
            entry_matches = re.findall(r"enter_long.*?=.*?1", strategy_code)
            analysis['entry_conditions'] = entry_matches
            
            # Estrai condizioni di uscita
            exit_matches = re.findall(r"exit_long.*?=.*?1", strategy_code)
            analysis['exit_conditions'] = exit_matches
            
            # Analizza parametri
            param_matches = re.findall(r"(IntParameter|DecimalParameter)", strategy_code)
            analysis['parameters'] = param_matches
            
            # Identifica problemi comuni
            if len(analysis['entry_conditions']) < 2:
                analysis['code_issues'].append("Condizioni di entrata limitate")
                analysis['optimization_opportunities'].append("Aggiungere più condizioni di entrata")
                
            if len(analysis['exit_conditions']) < 2:
                analysis['code_issues'].append("Condizioni di uscita limitate")
                analysis['optimization_opportunities'].append("Aggiungere più condizioni di uscita")
                
            if 'atr' not in analysis['indicators_used']:
                analysis['optimization_opportunities'].append("Aggiungere ATR per gestione volatilità")
                
            if 'volume' not in analysis['indicators_used']:
                analysis['optimization_opportunities'].append("Aggiungere indicatori di volume")
                
        except Exception as e:
            analysis['code_issues'].append(f"Errore nell'analisi del codice: {e}")
            
        return analysis
    
    def _generate_optimization_suggestions(self, strategy_code: str, backtest_results: dict[str, float], analysis: dict[str, Any]) -> List[str]:
        """
        Genera suggerimenti di ottimizzazione usando LLM.
        """
        suggestions = []
        
        # Crea prompt per l'ottimizzazione
        optimization_prompt = self._create_optimization_prompt(strategy_code, backtest_results, analysis)
        
        try:
            # Usa LLM per generare suggerimenti
            llm_response = query_ollama_fast(optimization_prompt, self.default_model, timeout=300)
            
            # Estrai suggerimenti dalla risposta
            suggestions = self._extract_suggestions_from_llm(llm_response)
            
            # Aggiungi suggerimenti basati sull'analisi
            suggestions.extend(analysis.get('optimization_opportunities', []))
            
        except Exception as e:
            logger.warning(f"Errore nella generazione suggerimenti LLM: {e}")
            # Fallback a suggerimenti basati su regole
            suggestions = self._generate_rule_based_suggestions(analysis)
            
        return suggestions[:5]  # Limita a 5 suggerimenti principali
    
    def _create_optimization_prompt(self, strategy_code: str, backtest_results: dict[str, float], analysis: dict[str, Any]) -> str:
        """
        Crea un prompt specifico per l'ottimizzazione della strategia.
        """
        return f"""
Analizza questa strategia di trading FreqTrade e suggerisci miglioramenti specifici.

CODICE STRATEGIA:
{strategy_code[:1000]}...

RISULTATI BACKTEST:
- Total Return: {backtest_results.get('total_return', 0.0)}
- Sharpe Ratio: {backtest_results.get('sharpe_ratio', 0.0)}
- Max Drawdown: {backtest_results.get('max_drawdown', 0.0)}
- Win Rate: {backtest_results.get('win_rate', 0.0)}
- Total Trades: {backtest_results.get('total_trades', 0)}

ANALISI:
- Problemi identificati: {', '.join(analysis.get('issues', []))}
- Indicatori utilizzati: {', '.join(analysis.get('indicators_used', []))}
- Condizioni di entrata: {len(analysis.get('entry_conditions', []))}
- Condizioni di uscita: {len(analysis.get('exit_conditions', []))}

Suggerisci 3-5 miglioramenti specifici e concreti per ottimizzare questa strategia.
Focus su:
1. Condizioni di entrata/uscita più sofisticate
2. Gestione del rischio migliorata
3. Indicatori tecnici aggiuntivi
4. Parametri ottimizzabili
5. Logica di trading più robusta

Rispondi con una lista numerata di suggerimenti specifici e implementabili.
"""
    
    def _extract_suggestions_from_llm(self, llm_response: str) -> List[str]:
        """
        Estrae suggerimenti dalla risposta dell'LLM.
        """
        suggestions = []
        
        # Cerca pattern numerati
        numbered_patterns = [
            r'\d+\.\s*(.+)',
            r'-\s*(.+)',
            r'\*\s*(.+)'
        ]
        
        for pattern in numbered_patterns:
            matches = re.findall(pattern, llm_response, re.MULTILINE)
            suggestions.extend([match.strip() for match in matches])
            
        # Se non trova pattern numerati, cerca frasi che iniziano con parole chiave
        if not suggestions:
            keywords = ['migliora', 'aggiungi', 'ottimizza', 'modifica', 'implementa', 'suggerisco']
            lines = llm_response.split('\n')
            for line in lines:
                line = line.strip()
                if any(keyword in line.lower() for keyword in keywords):
                    suggestions.append(line)
                    
        return suggestions[:5]  # Limita a 5 suggerimenti
    
    def _generate_rule_based_suggestions(self, analysis: dict[str, Any]) -> List[str]:
        """
        Genera suggerimenti basati su regole quando l'LLM non è disponibile.
        """
        suggestions = []
        
        # Suggerimenti basati sui problemi identificati
        if 'Rendimento basso' in analysis.get('issues', []):
            suggestions.append("Migliorare le condizioni di entrata con filtri più sofisticati")
            
        if 'Sharpe ratio basso' in analysis.get('issues', []):
            suggestions.append("Ottimizzare la gestione del rischio e stop loss")
            
        if 'Drawdown eccessivo' in analysis.get('issues', []):
            suggestions.append("Implementare trailing stop e gestione posizione")
            
        if 'Win rate basso' in analysis.get('issues', []):
            suggestions.append("Aggiungere filtri di trend e momentum")
            
        if 'Pochi trade' in analysis.get('issues', []):
            suggestions.append("Rilassare le condizioni di entrata per più opportunità")
            
        # Suggerimenti basati sul codice
        if len(analysis.get('indicators_used', [])) < 3:
            suggestions.append("Aggiungere più indicatori tecnici per conferma")
            
        if len(analysis.get('entry_conditions', [])) < 2:
            suggestions.append("Implementare condizioni di entrata multiple")
            
        return suggestions
    
    def _apply_optimizations(self, strategy_code: str, suggestions: List[str], strategy_name: str) -> str:
        """
        Applica le ottimizzazioni suggerite al codice della strategia.
        """
        optimized_code = strategy_code
        
        for suggestion in suggestions:
            try:
                # Applica ottimizzazioni specifiche
                if "condizioni di entrata" in suggestion.lower():
                    optimized_code = self._optimize_entry_conditions(optimized_code)
                    
                elif "gestione del rischio" in suggestion.lower() or "stop loss" in suggestion.lower():
                    optimized_code = self._optimize_risk_management(optimized_code)
                    
                elif "indicatori" in suggestion.lower():
                    optimized_code = self._optimize_indicators(optimized_code)
                    
                elif "parametri" in suggestion.lower():
                    optimized_code = self._optimize_parameters(optimized_code)
                    
                elif "trend" in suggestion.lower() or "momentum" in suggestion.lower():
                    optimized_code = self._optimize_trend_filters(optimized_code)
                    
            except Exception as e:
                logger.warning(f"Errore nell'applicazione ottimizzazione '{suggestion}': {e}")
                continue
                
        return optimized_code
    
    def _optimize_entry_conditions(self, strategy_code: str) -> str:
        """
        Ottimizza le condizioni di entrata della strategia.
        """
        # Aggiungi condizioni di entrata più sofisticate
        entry_improvements = """
        # Condizioni di entrata ottimizzate
        dataframe.loc[
            (dataframe['rsi'] < 30) & 
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['close'] > dataframe['close'].shift(1)),
            'enter_long'
        ] = 1
        
        # Entrata su breakout
        dataframe.loc[
            (dataframe['close'] > dataframe['close'].shift(1) * 1.01) &
            (dataframe['volume'] > dataframe['volume'].rolling(20).mean()),
            'enter_long'
        ] = 1
        """
        
        # Sostituisci le condizioni di entrata esistenti
        if "enter_long" in strategy_code:
            strategy_code = re.sub(
                r"dataframe\.loc\[.*?enter_long.*?\] = 1",
                entry_improvements.strip(),
                strategy_code,
                flags=re.DOTALL
            )
            
        return strategy_code
    
    def _optimize_risk_management(self, strategy_code: str) -> str:
        """
        Ottimizza la gestione del rischio della strategia.
        """
        # Migliora stop loss e trailing stop
        risk_improvements = """
    stoploss = -0.015  # Stop loss più stretto
    trailing_stop = True
    trailing_stop_positive = 0.008
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True
    
    # Stop loss dinamico basato su ATR
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
        """
        
        # Sostituisci la configurazione del rischio
        strategy_code = re.sub(
            r"stoploss = -0\.02.*?trailing_only_offset_is_reached = True",
            risk_improvements.strip(),
            strategy_code,
            flags=re.DOTALL
        )
        
        return strategy_code
    
    def _optimize_indicators(self, strategy_code: str) -> str:
        """
        Ottimizza gli indicatori della strategia.
        """
        # Aggiungi indicatori utili
        indicator_improvements = """
        # Indicatori base
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        # Indicatori aggiuntivi per ottimizzazione
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_upperband'] = bollinger['upperband']
        dataframe['bb_middleband'] = bollinger['middleband']
        
        # Volume e momentum
        dataframe['volume_sma'] = dataframe['volume'].rolling(20).mean()
        dataframe['price_change'] = dataframe['close'].pct_change()
        """
        
        # Sostituisci gli indicatori esistenti
        if "populate_indicators" in strategy_code:
            strategy_code = re.sub(
                r"def populate_indicators\(self, dataframe: DataFrame, metadata: dict\) -> DataFrame:.*?return dataframe",
                f"def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:\n        {indicator_improvements.strip()}\n        return dataframe",
                strategy_code,
                flags=re.DOTALL
            )
            
        return strategy_code
    
    def _optimize_parameters(self, strategy_code: str) -> str:
        """
        Ottimizza i parametri della strategia rendendoli configurabili.
        """
        # Aggiungi parametri ottimizzabili
        parameter_improvements = """
    # Parametri ottimizzabili
    rsi_period = IntParameter(10, 20, default=14, space="buy")
    rsi_oversold = IntParameter(20, 35, default=30, space="buy")
    rsi_overbought = IntParameter(65, 80, default=70, space="sell")
    
    # Parametri ATR
    atr_period = IntParameter(10, 20, default=14, space="buy")
    atr_multiplier = DecimalParameter(1.0, 3.0, default=2.0, space="buy")
        """
        
        # Aggiungi parametri se non esistono
        if "IntParameter" not in strategy_code:
            # Trova la posizione dopo la definizione della classe
            class_end = strategy_code.find("def populate_indicators")
            if class_end != -1:
                strategy_code = strategy_code[:class_end] + parameter_improvements + "\n    \n    " + strategy_code[class_end:]
                
        return strategy_code
    
    def _optimize_trend_filters(self, strategy_code: str) -> str:
        """
        Ottimizza i filtri di trend della strategia.
        """
        # Aggiungi filtri di trend
        trend_improvements = """
        # Filtri di trend
        dataframe['trend_up'] = (
            (dataframe['ema_short'] > dataframe['ema_long']) &
            (dataframe['close'] > dataframe['sma_50'])
        )
        
        dataframe['momentum_positive'] = (
            (dataframe['macd'] > dataframe['macd'].shift(1)) &
            (dataframe['rsi'] > 50)
        )
        """
        
        # Aggiungi filtri se non esistono
        if "trend_up" not in strategy_code:
            # Trova la posizione dopo gli indicatori
            indicators_end = strategy_code.find("return dataframe")
            if indicators_end != -1:
                strategy_code = strategy_code[:indicators_end] + trend_improvements + "\n        " + strategy_code[indicators_end:]
                
        return strategy_code
    
    def _calculate_changes(self, original_code: str, optimized_code: str) -> Dict[str, Any]:
        """
        Calcola le modifiche apportate al codice.
        """
        changes = {
            'lines_added': 0,
            'lines_modified': 0,
            'indicators_added': [],
            'conditions_modified': [],
            'parameters_added': []
        }
        
        # Conta le linee
        original_lines = len(original_code.split('\n'))
        optimized_lines = len(optimized_code.split('\n'))
        changes['lines_added'] = optimized_lines - original_lines
        
        # Identifica indicatori aggiunti
        original_indicators = re.findall(r"dataframe\['([^']+)'\]", original_code)
        optimized_indicators = re.findall(r"dataframe\['([^']+)'\]", optimized_code)
        changes['indicators_added'] = list(set(optimized_indicators) - set(original_indicators))
        
        # Identifica parametri aggiunti
        if "IntParameter" not in original_code and "IntParameter" in optimized_code:
            changes['parameters_added'].append("Parametri ottimizzabili")
            
        return changes
    
    def _extract_strategy_name(self, strategy_code: str) -> str:
        """
        Estrae il nome della strategia dal codice.
        """
        # Cerca pattern di definizione classe
        class_pattern = r"class\s+(\w+)\s*\(IStrategy\)"
        match = re.search(class_pattern, strategy_code)
        
        if match:
            return match.group(1)
        else:
            return "OptimizedStrategy"
    
    def get_optimization_summary(self, result: OptimizationResult) -> str:
        """
        Genera un riassunto dell'ottimizzazione.
        """
        optimized_score_str = f"{result.optimized_score:.4f}" if result.optimized_score is not None else 'N/A'
        
        summary = f"""
🔧 OTTIMIZZAZIONE STRATEGIA
==========================
📊 Score Originale: {result.original_score:.4f}
📈 Score Ottimizzato: {optimized_score_str}
✅ Successo: {'Sì' if result.success else 'No'}
⏱️ Tempo: {result.optimization_time.strftime('%Y-%m-%d %H:%M:%S')}

🔍 MIGLIORAMENTI SUGGERITI:
"""
        
        for i, improvement in enumerate(result.improvements, 1):
            summary += f"{i}. {improvement}\n"
            
        if result.changes_made:
            summary += f"""
📝 MODIFICHE APPORTATE:
- Linee aggiunte: {result.changes_made.get('lines_added', 0)}
- Indicatori aggiunti: {', '.join(result.changes_made.get('indicators_added', []))}
- Parametri aggiunti: {', '.join(result.changes_made.get('parameters_added', []))}
"""
            
        if result.error_message:
            summary += f"\n❌ ERRORE: {result.error_message}"
            
        return summary 