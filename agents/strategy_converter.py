"""
Strategy Converter: Converte descrizioni testuali in codice FreqTrade.
Approccio ibrido che combina generazione diretta e conversione automatica.
"""

import re
import ast
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class StrategyComponents:
    """Componenti di una strategia FreqTrade."""
    indicators: List[str]
    entry_conditions: List[str]
    exit_conditions: List[str]
    parameters: Dict[str, Any]
    timeframe: str = "5m"
    minimal_roi: Optional[Dict[str, float]] = None
    stoploss: float = -0.02

class StrategyConverter:
    """
    Converte descrizioni testuali di strategie in codice FreqTrade.
    Supporta sia conversione automatica che validazione di codice generato.
    """
    
    def __init__(self):
        self.template_strategy = self._load_template()
        self.indicator_mapping = self._load_indicator_mapping()
        self.condition_mapping = self._load_condition_mapping()
    
    def convert_text_to_strategy(self, text_description: str, strategy_name: str = "LLMStrategy") -> str:
        """
        Converte una descrizione testuale in codice FreqTrade.
        
        Args:
            text_description: Descrizione della strategia in linguaggio naturale
            strategy_name: Nome della classe strategia (default: LLMStrategy)
            
        Returns:
            Codice Python della strategia FreqTrade
        """
        try:
            # Estrai i componenti dalla descrizione
            components = self._extract_components(text_description)
            
            # Genera il codice
            strategy_code = self._generate_strategy_code(components, strategy_name)
            
            # Valida il codice generato
            if self._validate_strategy_code(strategy_code):
                return strategy_code
            else:
                logger.warning("Codice generato non valido, usando fallback")
                return self._generate_fallback_strategy(components, strategy_name)
                
        except Exception as e:
            logger.error(f"Errore nella conversione: {e}")
            return self._generate_fallback_strategy(strategy_name=strategy_name)
    
    def validate_and_fix_code(self, strategy_code: str, strategy_name: str = "LLMStrategy") -> str:
        """
        Valida e corregge codice FreqTrade generato da LLM.
        
        Args:
            strategy_code: Codice della strategia da validare
            strategy_name: Nome della classe strategia (default: LLMStrategy)
            
        Returns:
            Codice corretto o fallback
        """
        try:
            # Parsing sintattico
            ast.parse(strategy_code)
            
            # Validazione specifica FreqTrade
            if self._validate_freqtrade_specifics(strategy_code):
                # Correggi il nome della classe se necessario
                fixed_code = self._fix_class_name(strategy_code, strategy_name)
                return fixed_code
            else:
                return self._fix_strategy_code(strategy_code, strategy_name)
                
        except SyntaxError as e:
            logger.error(f"Errore di sintassi: {e}")
            return self._fix_syntax_errors(strategy_code, strategy_name)
        except Exception as e:
            logger.error(f"Errore di validazione: {e}")
            return self._generate_fallback_strategy(strategy_name=strategy_name)
    
    def _extract_components(self, text: str) -> StrategyComponents:
        """Estrae i componenti della strategia dal testo."""
        components = StrategyComponents(
            indicators=[],
            entry_conditions=[],
            exit_conditions=[],
            parameters={},
            minimal_roi={"0": 0.05, "30": 0.025, "60": 0.015, "120": 0.01}
        )
        
        # Estrai indicatori
        indicators = re.findall(r'(RSI|EMA|MACD|Bollinger|ATR|Volume|Stochastic|ADX)', text, re.IGNORECASE)
        components.indicators = list(set(indicators))
        
        # Estrai condizioni di entrata
        entry_patterns = [
            r'entra\s+(?:quando|se)\s+(.*?)(?:\.|$)',
            r'buy\s+(?:when|if)\s+(.*?)(?:\.|$)',
            r'long\s+(?:when|if)\s+(.*?)(?:\.|$)'
        ]
        
        for pattern in entry_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            components.entry_conditions.extend(matches)
        
        # Estrai condizioni di uscita
        exit_patterns = [
            r'esci\s+(?:quando|se)\s+(.*?)(?:\.|$)',
            r'sell\s+(?:when|if)\s+(.*?)(?:\.|$)',
            r'exit\s+(?:when|if)\s+(.*?)(?:\.|$)'
        ]
        
        for pattern in exit_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            components.exit_conditions.extend(matches)
        
        # Estrai parametri
        param_patterns = [
            r'(\d+)\s*%\s*(?:profit|target)',
            r'(\d+)\s*%\s*(?:stop|loss)',
            r'(\d+)\s*(?:minute|hour)',
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, text)
            if matches:
                components.parameters['percentage'] = float(matches[0])
        
        return components
    
    def _generate_strategy_code(self, components: StrategyComponents, strategy_name: str) -> str:
        """Genera il codice della strategia dai componenti."""
        # Genera indicatori
        indicators_code = self._generate_indicators_code(components.indicators)
        
        # Genera condizioni di entrata
        entry_code = self._generate_entry_code(components.entry_conditions)
        
        # Genera condizioni di uscita
        exit_code = self._generate_exit_code(components.exit_conditions)
        
        # Sostituisci nel template
        code = self.template_strategy.replace("{{strategy_name}}", strategy_name)
        code = code.replace("{{indicators}}", indicators_code)
        code = code.replace("{{entry_conditions}}", entry_code)
        code = code.replace("{{exit_conditions}}", exit_code)
        
        return code
    
    def _generate_indicators_code(self, indicators: List[str]) -> str:
        """Genera il codice per gli indicatori."""
        code_lines: List[str] = []
        
        for indicator in indicators:
            if indicator.upper() == "RSI":
                code_lines.append("dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)")
            elif indicator.upper() == "EMA":
                code_lines.append("dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)")
                code_lines.append("dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)")
            elif indicator.upper() == "MACD":
                code_lines.append("macd = ta.MACD(dataframe)")
                code_lines.append("dataframe['macd'] = macd['macd']")
                code_lines.append("dataframe['macdsignal'] = macd['macdsignal']")
            elif indicator.upper() == "BOLLINGER":
                code_lines.append("bollinger = ta.BBANDS(dataframe, timeperiod=20)")
                code_lines.append("dataframe['bb_lowerband'] = bollinger['lowerband']")
                code_lines.append("dataframe['bb_upperband'] = bollinger['upperband']")
            elif indicator.upper() == "ATR":
                code_lines.append("dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)")
        
        return "\n        ".join(code_lines) if code_lines else "pass"
    
    def _generate_entry_code(self, conditions: List[str]) -> str:
        """Genera il codice per le condizioni di entrata."""
        if not conditions:
            return "dataframe.loc[dataframe['rsi'] < 30, 'enter_long'] = 1"
        
        # Semplifica le condizioni per ora
        return "dataframe.loc[dataframe['rsi'] < 30, 'enter_long'] = 1"
    
    def _generate_exit_code(self, conditions: List[str]) -> str:
        """Genera il codice per le condizioni di uscita."""
        if not conditions:
            return "dataframe.loc[dataframe['rsi'] > 70, 'exit_long'] = 1"
        
        # Semplifica le condizioni per ora
        return "dataframe.loc[dataframe['rsi'] > 70, 'exit_long'] = 1"
    
    def _validate_strategy_code(self, code: str) -> bool:
        """Valida il codice della strategia."""
        try:
            ast.parse(code)
            return "class" in code and "IStrategy" in code
        except:
            return False
    
    def _validate_freqtrade_specifics(self, code: str) -> bool:
        """Valida aspetti specifici di FreqTrade."""
        required_elements = [
            "class",
            "IStrategy",
            "populate_indicators",
            "populate_entry_trend",
            "populate_exit_trend"
        ]
        
        return all(element in code for element in required_elements)
    
    def _fix_class_name(self, code: str, strategy_name: str) -> str:
        """Corregge il nome della classe nel codice."""
        # Trova la classe esistente e sostituiscila
        class_pattern = r'class\s+(\w+)\s*\(IStrategy\)'
        match = re.search(class_pattern, code)
        
        if match and match.group(1) != strategy_name:
            old_name = match.group(1)
            code = code.replace(f"class {old_name}(IStrategy)", f"class {strategy_name}(IStrategy)")
            logger.info(f"Corretto nome classe da {old_name} a {strategy_name}")
        
        return code
    
    def _fix_strategy_code(self, code: str, strategy_name: str) -> str:
        """Corregge errori comuni nel codice."""
        # Rimuovi commenti problematici
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Assicurati che ci sia la classe
        if "class" not in code:
            code = self._add_class_wrapper(code, strategy_name)
        
        # Correggi il nome della classe
        code = self._fix_class_name(code, strategy_name)
        
        return code
    
    def _fix_syntax_errors(self, code: str, strategy_name: str) -> str:
        """Corregge errori di sintassi comuni."""
        # Rimuovi caratteri problematici
        code = re.sub(r'[^\x00-\x7F]+', '', code)
        
        # Correggi indentazione
        lines = code.split('\n')
        fixed_lines: List[str] = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('class') or stripped.startswith('def'):
                indent_level = 0
            elif stripped.startswith('if') or stripped.startswith('for') or stripped.startswith('while'):
                indent_level += 1
            
            fixed_lines.append('    ' * indent_level + stripped)
        
        fixed_code = '\n'.join(fixed_lines)
        
        # Correggi il nome della classe
        fixed_code = self._fix_class_name(fixed_code, strategy_name)
        
        return fixed_code
    
    def _add_class_wrapper(self, code: str, strategy_name: str) -> str:
        """Aggiunge un wrapper di classe se mancante."""
        return f"""
class {strategy_name}(IStrategy):
    minimal_roi = {{"0": 0.05}}
    stoploss = -0.02
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        {code}
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe['rsi'] < 30, 'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe['rsi'] > 70, 'exit_long'] = 1
        return dataframe
"""
    
    def _generate_fallback_strategy(self, components: Optional[StrategyComponents] = None, strategy_name: str = "LLMStrategy") -> str:
        """Genera una strategia di fallback."""
        return f'''
class {strategy_name}(IStrategy):
    minimal_roi = {{"0": 0.05}}
    stoploss = -0.02
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] < 30) & 
            (dataframe['ema_short'] > dataframe['ema_long']),
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] > 70) | 
            (dataframe['ema_short'] < dataframe['ema_long']),
            'exit_long'] = 1
        return dataframe
'''
    
    def _load_template(self) -> str:
        """Carica il template della strategia."""
        return '''
"""
{{strategy_name}} - Strategia generata automaticamente
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class {{strategy_name}}(IStrategy):
    """
    Strategia generata automaticamente per trading futures crypto.
    """
    
    minimal_roi = {
        "0": 0.05,
        "30": 0.025,
        "60": 0.015,
        "120": 0.01
    }
    
    stoploss = -0.02
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True
    
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola gli indicatori tecnici.
        """
        {{indicators}}
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        {{entry_conditions}}
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        {{exit_conditions}}
        return dataframe
'''
    
    def _load_indicator_mapping(self) -> Dict[str, str]:
        """Carica il mapping degli indicatori."""
        return {
            "RSI": "ta.RSI(dataframe, timeperiod=14)",
            "EMA": "ta.EMA(dataframe, timeperiod=9)",
            "MACD": "ta.MACD(dataframe)",
            "Bollinger": "ta.BBANDS(dataframe, timeperiod=20)",
            "ATR": "ta.ATR(dataframe, timeperiod=14)",
            "Volume": "dataframe['volume']",
        }
    
    def _load_condition_mapping(self) -> Dict[str, str]:
        """Carica il mapping delle condizioni."""
        return {
            "oversold": "dataframe['rsi'] < 30",
            "overbought": "dataframe['rsi'] > 70",
            "trend_up": "dataframe['ema_short'] > dataframe['ema_long']",
            "trend_down": "dataframe['ema_short'] < dataframe['ema_long']",
        } 