#!/usr/bin/env python3
"""
Sistema di Prompt Adattivi per LLM Trading Strategies
Genera prompt dinamici, casuali e personalizzati basati su vari fattori.
"""

import random
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class PromptConfig:
    """Configurazione per la generazione di prompt."""
    complexity: str  # "simple", "normal", "complex"
    strategy_type: str  # "volatility", "scalping", "breakout", "momentum", "adaptive"
    model_capability: str  # "fast", "balanced", "powerful"
    focus_areas: List[str]  # ["risk_management", "indicators", "timing", "optimization"]
    style: str  # "technical", "creative", "conservative", "aggressive"
    randomization_level: float  # 0.0 = fisso, 1.0 = completamente casuale

class AdaptivePromptGenerator:
    """
    Generatore di prompt adattivi che crea prompt personalizzati
    basati su modello LLM, complessità, tipo strategia e performance.
    """
    
    def __init__(self):
        self.prompt_templates = self._load_prompt_templates()
        self.performance_history = self._load_performance_history()
        self.model_capabilities = self._get_model_capabilities()
        self.strategy_components = self._get_strategy_components()
        
    def generate_adaptive_prompt(self, 
                               strategy_type: str,
                               model: str,
                               complexity: str = "normal",
                               style: str = "technical",
                               randomization: float = 0.3) -> str:
        """
        Genera un prompt adattivo basato sui parametri forniti.
        
        Args:
            strategy_type: Tipo di strategia
            model: Modello LLM da utilizzare
            complexity: Livello di complessità ("simple", "normal", "complex")
            style: Stile del prompt ("technical", "creative", "conservative", "aggressive")
            randomization: Livello di randomizzazione (0.0-1.0)
            
        Returns:
            Prompt personalizzato
        """
        # Determina le capacità del modello
        model_capability = self._assess_model_capability(model)
        
        # Crea configurazione
        config = PromptConfig(
            complexity=complexity,
            strategy_type=strategy_type,
            model_capability=model_capability,
            focus_areas=self._select_focus_areas(strategy_type, complexity),
            style=style,
            randomization_level=randomization
        )
        
        # Genera prompt adattivo
        if randomization > 0.7:
            return self._generate_random_prompt(config)
        elif randomization > 0.3:
            return self._generate_hybrid_prompt(config)
        else:
            return self._generate_structured_prompt(config)
    
    def _generate_random_prompt(self, config: PromptConfig) -> str:
        """Genera un prompt completamente casuale."""
        logger.info(f"🎲 Generazione prompt casuale per {config.strategy_type}")
        
        # Seleziona componenti casuali
        indicators = random.sample(self.strategy_components['indicators'], 
                                 random.randint(3, 6))
        timeframes = random.sample(self.strategy_components['timeframes'], 
                                 random.randint(1, 2))
        risk_levels = random.sample(self.strategy_components['risk_levels'], 1)[0]
        
        # Genera prompt casuale
        prompt = f"""Crea una strategia Freqtrade {config.strategy_type} per futures crypto.

APPROCCIO: {random.choice(['conservative', 'balanced', 'aggressive'])}
TIMEFRAME: {', '.join(timeframes)}
FOCUS: {random.choice(['momentum', 'trend', 'volatility', 'breakout'])}

INDICATORI DA USARE:
{chr(10).join([f"- {ind}" for ind in indicators])}

GESTIONE RISCHIO: {risk_levels}

Genera SOLO codice Python completo e funzionante."""
        
        return prompt
    
    def _generate_hybrid_prompt(self, config: PromptConfig) -> str:
        """Genera un prompt ibrido con elementi casuali e strutturati."""
        logger.info(f"🔄 Generazione prompt ibrido per {config.strategy_type}")
        
        # Base strutturata
        base_prompt = self._get_base_template(config.strategy_type, config.complexity)
        
        # Aggiungi elementi casuali
        random_elements = self._get_random_elements(config)
        
        # Combina
        hybrid_prompt = f"""{base_prompt}

ELEMENTI AGGIUNTIVI:
{random_elements}

STILE: {config.style.upper()}
COMPLESSITÀ: {config.complexity.upper()}

Genera SOLO codice Python completo."""
        
        return hybrid_prompt
    
    def _generate_structured_prompt(self, config: PromptConfig) -> str:
        """Genera un prompt strutturato e prevedibile."""
        logger.info(f"📋 Generazione prompt strutturato per {config.strategy_type}")
        
        template = self._get_advanced_template(config)
        return template
    
    def _get_base_template(self, strategy_type: str, complexity: str) -> str:
        """Ottiene un template base per il tipo di strategia."""
        templates = {
            "scalping": {
                "simple": "Crea una strategia di scalping semplice per futures crypto.",
                "normal": "Crea una strategia di scalping per futures crypto con gestione rischio.",
                "complex": "Crea una strategia di scalping avanzata per futures crypto con gestione rischio sofisticata."
            },
            "momentum": {
                "simple": "Crea una strategia di momentum semplice per futures crypto.",
                "normal": "Crea una strategia di momentum per futures crypto con filtri di trend.",
                "complex": "Crea una strategia di momentum avanzata per futures crypto con analisi multi-timeframe."
            },
            "breakout": {
                "simple": "Crea una strategia di breakout semplice per futures crypto.",
                "normal": "Crea una strategia di breakout per futures crypto con conferme.",
                "complex": "Crea una strategia di breakout avanzata per futures crypto con gestione falsi segnali."
            },
            "volatility": {
                "simple": "Crea una strategia di volatilità semplice per futures crypto.",
                "normal": "Crea una strategia di volatilità per futures crypto con gestione rischio.",
                "complex": "Crea una strategia di volatilità avanzata per futures crypto con position sizing adattivo."
            },
            "adaptive": {
                "simple": "Crea una strategia adattiva semplice per futures crypto.",
                "normal": "Crea una strategia adattiva per futures crypto che cambia approccio.",
                "complex": "Crea una strategia adattiva avanzata per futures crypto con machine learning."
            }
        }
        
        return templates.get(strategy_type, {}).get(complexity, "Crea una strategia Freqtrade per futures crypto.")
    
    def _get_advanced_template(self, config: PromptConfig) -> str:
        """Ottiene un template avanzato personalizzato."""
        
        # Template base
        base = self._get_base_template(config.strategy_type, config.complexity)
        
        # Aggiungi dettagli specifici per complessità
        if config.complexity == "complex":
            details = self._get_complex_details(config)
        elif config.complexity == "normal":
            details = self._get_normal_details(config)
        else:
            details = self._get_simple_details(config)
        
        # Aggiungi stile
        style_elements = self._get_style_elements(config.style)
        
        return f"""{base}

{details}

{style_elements}

Genera SOLO codice Python completo e funzionante."""
    
    def _get_complex_details(self, config: PromptConfig) -> str:
        """Dettagli per prompt complessi."""
        return f"""
REQUISITI AVANZATI:

1. TIMEFRAME E PARAMETRI:
   - Timeframe: {self._get_timeframe_for_strategy(config.strategy_type)}
   - ROI: {self._get_roi_structure(config.strategy_type)}
   - Stop loss: {self._get_stop_loss(config.strategy_type)}
   - Trailing stop: True

2. INDICATORI TECNICI OBBLIGATORI:
   {self._get_indicators_list(config.strategy_type, "complex")}

3. LOGICA DI ENTRATA STRETTA:
   {self._get_entry_logic(config.strategy_type, "complex")}

4. LOGICA DI USCITA:
   {self._get_exit_logic(config.strategy_type, "complex")}

5. GESTIONE RISCHIO AVANZATA:
   {self._get_risk_management(config.strategy_type, "complex")}

6. PARAMETRI OTTIMIZZABILI:
   {self._get_optimizable_params(config.strategy_type)}
"""
    
    def _get_normal_details(self, config: PromptConfig) -> str:
        """Dettagli per prompt normali."""
        return f"""
REQUISITI:

1. INDICATORI TECNICI:
   {self._get_indicators_list(config.strategy_type, "normal")}

2. LOGICA DI TRADING:
   {self._get_entry_logic(config.strategy_type, "normal")}

3. GESTIONE RISCHIO:
   {self._get_risk_management(config.strategy_type, "normal")}
"""
    
    def _get_simple_details(self, config: PromptConfig) -> str:
        """Dettagli per prompt semplici."""
        return f"""
REQUISITI BASE:

1. INDICATORI: {self._get_indicators_list(config.strategy_type, "simple")}
2. LOGICA: {self._get_entry_logic(config.strategy_type, "simple")}
3. RISCHIO: {self._get_risk_management(config.strategy_type, "simple")}
"""
    
    def _get_timeframe_for_strategy(self, strategy_type: str) -> str:
        """Ottiene il timeframe appropriato per la strategia."""
        timeframes = {
            "scalping": "15m",
            "momentum": "1h", 
            "breakout": "4h",
            "volatility": "30m",
            "adaptive": "1h"
        }
        return timeframes.get(strategy_type, "1h")
    
    def _get_roi_structure(self, strategy_type: str) -> str:
        """Ottiene la struttura ROI appropriata."""
        roi_structures = {
            "scalping": '{"0": 0.10, "60": 0.05, "120": 0.03, "240": 0.02}',
            "momentum": '{"0": 0.15, "120": 0.08, "240": 0.05, "480": 0.03}',
            "breakout": '{"0": 0.20, "240": 0.10, "480": 0.06, "720": 0.04}',
            "volatility": '{"0": 0.12, "90": 0.06, "180": 0.04, "360": 0.025}',
            "adaptive": '{"0": 0.15, "120": 0.08, "240": 0.05, "480": 0.03}'
        }
        return roi_structures.get(strategy_type, '{"0": 0.10}')
    
    def _get_stop_loss(self, strategy_type: str) -> str:
        """Ottiene lo stop loss appropriato."""
        stop_losses = {
            "scalping": "-0.03",
            "momentum": "-0.04", 
            "breakout": "-0.05",
            "volatility": "-0.035",
            "adaptive": "-0.04"
        }
        return stop_losses.get(strategy_type, "-0.03")
    
    def _get_indicators_list(self, strategy_type: str, complexity: str) -> str:
        """Ottiene la lista di indicatori appropriata."""
        indicators = {
            "scalping": {
                "simple": "- RSI(14)\n- EMA(9,21)\n- Volume",
                "normal": "- RSI(14) per momentum\n- EMA(9,21) per trend\n- MACD(12,26,9) per conferma\n- Volume SMA(20)",
                "complex": "- RSI(14) per momentum\n- EMA(9,21) per trend\n- MACD(12,26,9) per conferma\n- Bollinger Bands(20,2) per volatilità\n- Volume SMA(20) per conferma\n- ATR(14) per stop loss dinamico"
            },
            "momentum": {
                "simple": "- RSI(14)\n- MACD\n- EMA(20,50)",
                "normal": "- RSI(14) per momentum\n- MACD(12,26,9) per trend\n- EMA(20,50) per direzione\n- Volume per conferma",
                "complex": "- RSI(14) per momentum\n- EMA(20,50,200) per trend multi-timeframe\n- MACD(12,26,9) per momentum\n- Stochastic(14,3,3) per timing\n- ADX(14) per forza del trend\n- Volume SMA(20) per conferma"
            },
            "breakout": {
                "simple": "- Bollinger Bands\n- Volume\n- RSI",
                "normal": "- Bollinger Bands(20,2) per range\n- Volume SMA(20) per conferma\n- RSI(14) per momentum\n- EMA(50) per trend",
                "complex": "- Bollinger Bands(20,2) per range\n- Support/Resistance dinamici\n- Volume SMA(20) per conferma\n- RSI(14) per momentum\n- EMA(50) per trend\n- ATR(14) per volatilità"
            },
            "volatility": {
                "simple": "- ATR\n- Bollinger Bands\n- RSI",
                "normal": "- ATR(14) per volatilità\n- Bollinger Bands(20,2) per range\n- RSI(14) per momentum\n- EMA(20) per trend",
                "complex": "- ATR(14) per volatilità\n- Bollinger Bands(20,2) per range\n- RSI(14) per momentum\n- EMA(20) per trend\n- Volume SMA(20) per conferma\n- Volatility Ratio (ATR/EMA)"
            },
            "adaptive": {
                "simple": "- ADX\n- ATR\n- Bollinger Bands",
                "normal": "- ADX(14) per forza trend\n- ATR(14) per volatilità\n- Bollinger Bands(20,2) per range\n- EMA(20,50) per trend",
                "complex": "- ADX(14) per forza trend\n- ATR(14) per volatilità\n- Bollinger Bands(20,2) per range\n- EMA(20,50) per trend\n- RSI(14) per momentum\n- Volume SMA(20) per conferma"
            }
        }
        
        return indicators.get(strategy_type, {}).get(complexity, "- RSI(14)\n- EMA(20)\n- Volume")
    
    def _get_entry_logic(self, strategy_type: str, complexity: str) -> str:
        """Ottiene la logica di entrata appropriata."""
        entry_logic = {
            "scalping": {
                "simple": "- RSI < 30 (oversold)\n- EMA9 > EMA21 (trend positivo)",
                "normal": "- RSI < 25 (oversold)\n- EMA9 > EMA21 (trend positivo)\n- MACD > MACD_signal (momentum positivo)\n- Volume > 120% media",
                "complex": "- RSI < 25 (oversold)\n- EMA9 > EMA21 (trend positivo)\n- MACD > MACD_signal (momentum positivo)\n- Prezzo vicino alla banda inferiore di Bollinger\n- Volume > 120% della media\n- ATR > media ATR (volatilità sufficiente)"
            },
            "momentum": {
                "simple": "- RSI > 50 (momentum positivo)\n- MACD > MACD_signal",
                "normal": "- ADX > 25 (trend forte)\n- EMA20 > EMA50 (trend rialzista)\n- RSI > 50 (momentum positivo)\n- Volume > 150% media",
                "complex": "- ADX > 25 (trend forte)\n- EMA20 > EMA50 > EMA200 (trend rialzista)\n- RSI > 50 (momentum positivo)\n- MACD > MACD_signal (momentum confermato)\n- Stochastic non overbought\n- Volume > 150% media"
            },
            "breakout": {
                "simple": "- Prezzo > resistenza\n- Volume alto",
                "normal": "- Consolidamento pre-breakout\n- Volume > 200% media al breakout\n- RSI > 60 per breakout rialzista",
                "complex": "- Consolidamento pre-breakout (BB squeeze)\n- Volume > 200% media al breakout\n- RSI > 60 per breakout rialzista\n- Prezzo > resistenza + 0.5% conferma\n- ATR > media ATR (volatilità sufficiente)"
            },
            "volatility": {
                "simple": "- Volatilità alta\n- RSI estremo",
                "normal": "- Volatilità > 150% media\n- RSI < 30 (oversold) o > 70 (overbought)\n- Prezzo ai bordi delle Bollinger Bands",
                "complex": "- Volatilità > 150% media\n- RSI < 30 (oversold) o > 70 (overbought)\n- Prezzo ai bordi delle Bollinger Bands\n- Volume > 130% media\n- Trend direzionale chiaro"
            },
            "adaptive": {
                "simple": "- ADX > 25 (trend)\n- ATR > media (volatilità)",
                "normal": "- ADX > 25 (trend forte)\n- ATR > 150% media (volatilità)\n- Prezzo ai bordi BB (laterale)",
                "complex": "- ADX > 25 (trend forte)\n- ATR > 150% media (volatilità)\n- Prezzo ai bordi BB (laterale)\n- Volume > 150% media\n- Trend direzionale chiaro"
            }
        }
        
        return entry_logic.get(strategy_type, {}).get(complexity, "- RSI < 30\n- Trend positivo")
    
    def _get_exit_logic(self, strategy_type: str, complexity: str) -> str:
        """Ottiene la logica di uscita appropriata."""
        exit_logic = {
            "scalping": {
                "simple": "- RSI > 70 (overbought)\n- EMA9 < EMA21 (trend negativo)",
                "normal": "- RSI > 75 (overbought)\n- EMA9 < EMA21 (trend negativo)\n- MACD < MACD_signal (momentum negativo)",
                "complex": "- RSI > 75 (overbought)\n- EMA9 < EMA21 (trend negativo)\n- MACD < MACD_signal (momentum negativo)\n- Prezzo vicino alla banda superiore di Bollinger"
            },
            "momentum": {
                "simple": "- RSI > 70 (overbought)\n- MACD < MACD_signal",
                "normal": "- ADX < 20 (trend debole)\n- EMA20 < EMA50 (inversione trend)\n- RSI > 70 (overbought)",
                "complex": "- ADX < 20 (trend debole)\n- EMA20 < EMA50 (inversione trend)\n- RSI > 70 (overbought)\n- MACD < MACD_signal (momentum negativo)"
            },
            "breakout": {
                "simple": "- Ritorno dentro il range\n- Volume calante",
                "normal": "- Ritorno dentro il range\n- Volume calante\n- RSI estremo",
                "complex": "- Ritorno dentro il range\n- Volume calante\n- RSI estremo\n- Inversione trend"
            },
            "volatility": {
                "simple": "- Volatilità normalizzata\n- RSI ritorno normale",
                "normal": "- Volatilità normalizzata\n- RSI ritorno a livelli normali\n- Prezzo centro Bollinger Bands",
                "complex": "- Volatilità normalizzata\n- RSI ritorno a livelli normali\n- Prezzo centro Bollinger Bands\n- Volume calante"
            },
            "adaptive": {
                "simple": "- ADX < 20 (trend debole)\n- ATR < media (volatilità bassa)",
                "normal": "- ADX < 20 (trend debole)\n- ATR < media (volatilità bassa)\n- Prezzo centro BB (range)",
                "complex": "- ADX < 20 (trend debole)\n- ATR < media (volatilità bassa)\n- Prezzo centro BB (range)\n- Volume calante"
            }
        }
        
        return exit_logic.get(strategy_type, {}).get(complexity, "- RSI > 70\n- Trend negativo")
    
    def _get_risk_management(self, strategy_type: str, complexity: str) -> str:
        """Ottiene la gestione del rischio appropriata."""
        risk_management = {
            "scalping": {
                "simple": "- Stop loss: 2%\n- Max 3 trade simultanei",
                "normal": "- Stop loss dinamico basato su ATR\n- Max 2 trade simultanei\n- Position sizing basato su volatilità",
                "complex": "- Stop loss dinamico basato su ATR\n- Max 2 trade simultanei\n- Position sizing basato su volatilità\n- Filtro per mercati troppo volatili"
            },
            "momentum": {
                "simple": "- Stop loss: 4%\n- Max 1 trade per coppia",
                "normal": "- Stop loss basato su EMA200\n- Max 1 trade simultaneo per coppia\n- Take profit multipli",
                "complex": "- Stop loss basato su EMA200\n- Max 1 trade simultaneo per coppia\n- Take profit multipli\n- Filtro per mercati laterali"
            },
            "breakout": {
                "simple": "- Stop loss: 5%\n- Max 1 trade simultaneo",
                "normal": "- Stop loss sotto supporto/resistenza\n- Max 1 trade simultaneo\n- Take profit basato su ATR",
                "complex": "- Stop loss sotto supporto/resistenza\n- Max 1 trade simultaneo\n- Take profit basato su ATR\n- Filtro per mercati troppo volatili"
            },
            "volatility": {
                "simple": "- Stop loss: 3.5%\n- Max 2 trade simultanei",
                "normal": "- Position sizing basato su volatilità\n- Stop loss dinamico basato su ATR\n- Max 2 trade simultanei",
                "complex": "- Position sizing basato su volatilità\n- Stop loss dinamico basato su ATR\n- Max 2 trade simultanei\n- Filtro per mercati troppo volatili"
            },
            "adaptive": {
                "simple": "- Stop loss adattivo\n- Max 1 trade simultaneo",
                "normal": "- Stop loss adattivo per tipo mercato\n- Position sizing basato su volatilità\n- Max 1 trade simultaneo",
                "complex": "- Stop loss adattivo per tipo mercato\n- Position sizing basato su volatilità\n- Max 1 trade simultaneo\n- Filtri per transizioni di mercato"
            }
        }
        
        return risk_management.get(strategy_type, {}).get(complexity, "- Stop loss: 3%\n- Max 2 trade simultanei")
    
    def _get_optimizable_params(self, strategy_type: str) -> str:
        """Ottiene i parametri ottimizzabili appropriati."""
        params = {
            "scalping": "- rsi_oversold = IntParameter(20, 35, default=25)\n- rsi_overbought = IntParameter(65, 80, default=75)\n- ema_short = IntParameter(5, 15, default=9)\n- ema_long = IntParameter(15, 30, default=21)",
            "momentum": "- adx_threshold = IntParameter(20, 35, default=25)\n- rsi_threshold = IntParameter(45, 65, default=50)\n- ema_short = IntParameter(15, 25, default=20)\n- ema_medium = IntParameter(40, 60, default=50)",
            "breakout": "- volume_threshold = DecimalParameter(1.5, 3.0, default=2.0)\n- rsi_threshold = IntParameter(50, 70, default=60)\n- bb_period = IntParameter(15, 25, default=20)",
            "volatility": "- volatility_threshold = DecimalParameter(1.2, 2.0, default=1.5)\n- rsi_oversold = IntParameter(25, 35, default=30)\n- rsi_overbought = IntParameter(65, 75, default=70)",
            "adaptive": "- adx_threshold = IntParameter(20, 30, default=25)\n- volatility_threshold = DecimalParameter(1.2, 2.0, default=1.5)\n- bb_squeeze_threshold = DecimalParameter(0.8, 1.2, default=1.0)"
        }
        
        return params.get(strategy_type, "- rsi_threshold = IntParameter(30, 70, default=50)")
    
    def _get_style_elements(self, style: str) -> str:
        """Ottiene elementi di stile per il prompt."""
        style_elements = {
            "technical": "Focus su precisione tecnica e implementazione robusta.",
            "creative": "Sii creativo nell'approccio, prova combinazioni innovative di indicatori.",
            "conservative": "Approccio conservativo con gestione rischio rigorosa.",
            "aggressive": "Approccio aggressivo per massimizzare i profitti."
        }
        
        return style_elements.get(style, "Focus su implementazione pratica e funzionale.")
    
    def _get_random_elements(self, config: PromptConfig) -> str:
        """Ottiene elementi casuali per prompt ibridi."""
        random_indicators = random.sample(self.strategy_components['indicators'], 2)
        random_timeframe = random.choice(self.strategy_components['timeframes'])
        random_approach = random.choice(['momentum', 'trend', 'volatility', 'breakout', 'mean_reversion'])
        
        return f"""- Indicatori aggiuntivi: {', '.join(random_indicators)}
- Timeframe alternativo: {random_timeframe}
- Approccio secondario: {random_approach}"""
    
    def _assess_model_capability(self, model: str) -> str:
        """Valuta le capacità del modello."""
        fast_models = ["phi3", "llama2:7b", "codellama"]
        balanced_models = ["mistral:7b", "llama2:13b", "cogito:3b"]
        powerful_models = ["cogito:8b", "llama2:70b", "mistral:large"]
        
        if any(fast in model.lower() for fast in fast_models):
            return "fast"
        elif any(balanced in model.lower() for balanced in balanced_models):
            return "balanced"
        elif any(powerful in model.lower() for powerful in powerful_models):
            return "powerful"
        else:
            return "balanced"
    
    def _select_focus_areas(self, strategy_type: str, complexity: str) -> List[str]:
        """Seleziona aree di focus basate su strategia e complessità."""
        base_areas = ["indicators", "risk_management"]
        
        if complexity == "complex":
            base_areas.extend(["optimization", "timing", "position_sizing"])
        elif complexity == "normal":
            base_areas.extend(["timing"])
        
        if strategy_type == "adaptive":
            base_areas.append("market_classification")
        
        return base_areas
    
    def _load_prompt_templates(self) -> Dict[str, Any]:
        """Carica template di prompt da file."""
        # Per ora usa template hardcoded, in futuro può caricare da file
        return {}
    
    def _load_performance_history(self) -> Dict[str, Any]:
        """Carica storico performance per ottimizzazione prompt."""
        try:
            if os.path.exists("user_data/llm_scores.json"):
                with open("user_data/llm_scores.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Impossibile caricare storico performance: {e}")
        
        return {}
    
    def _get_model_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Ottiene le capacità dei modelli."""
        return {
            "phi3": {"speed": "fast", "quality": "good", "complexity": "simple"},
            "llama2:7b": {"speed": "fast", "quality": "good", "complexity": "normal"},
            "mistral:7b": {"speed": "balanced", "quality": "excellent", "complexity": "normal"},
            "cogito:8b": {"speed": "balanced", "quality": "excellent", "complexity": "complex"},
            "llama2:70b": {"speed": "slow", "quality": "excellent", "complexity": "complex"}
        }
    
    def _get_strategy_components(self) -> Dict[str, List[str]]:
        """Ottiene componenti per generazione casuale."""
        return {
            "indicators": [
                "RSI(14)", "EMA(20)", "MACD(12,26,9)", "Bollinger Bands(20,2)",
                "ATR(14)", "Stochastic(14,3,3)", "ADX(14)", "Williams %R",
                "CCI(20)", "MFI(14)", "OBV", "Volume SMA(20)"
            ],
            "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            "risk_levels": [
                "Stop loss stretto (1-2%) con take profit rapido",
                "Stop loss moderato (3-4%) con trailing stop",
                "Stop loss largo (5-6%) per trend following"
            ]
        }

# Funzioni di utilità per uso esterno
def generate_simple_prompt(strategy_type: str, model: str) -> str:
    """Genera un prompt semplice."""
    generator = AdaptivePromptGenerator()
    return generator.generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity="simple",
        style="technical",
        randomization=0.1
    )

def generate_complex_prompt(strategy_type: str, model: str) -> str:
    """Genera un prompt complesso."""
    generator = AdaptivePromptGenerator()
    return generator.generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity="complex",
        style="technical",
        randomization=0.2
    )

def generate_random_prompt(strategy_type: str, model: str) -> str:
    """Genera un prompt completamente casuale."""
    generator = AdaptivePromptGenerator()
    return generator.generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity="normal",
        style="creative",
        randomization=0.9
    )

def generate_adaptive_prompt(strategy_type: str, model: str, 
                           complexity: str = "normal", style: str = "technical",
                           randomization: float = 0.3) -> str:
    """Genera un prompt adattivo personalizzato."""
    generator = AdaptivePromptGenerator()
    return generator.generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity=complexity,
        style=style,
        randomization=randomization
    )
