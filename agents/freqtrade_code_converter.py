#!/usr/bin/env python3
"""
Convertitore specializzato per FreqTrade
Seconda fase: converte descrizioni testuali in codice FreqTrade corretto
"""

import re
import ast
from typing import Dict, List, Any, Optional
from llm_utils import query_ollama_fast

class FreqTradeCodeConverter:
    def __init__(self, default_model: str = "mistral:7b-instruct-q4_0"):
        self.default_model = default_model
        
        # Template base per strategia FreqTrade
        self.base_template = '''
"""
{strategy_name} - Strategia generata automaticamente
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class {class_name}(IStrategy):
    """
    {description}
    """
    
    # Parametri di base
    minimal_roi = {roi_config}
    stoploss = {stoploss}
    trailing_stop = {trailing_stop}
    trailing_stop_positive = {trailing_stop_positive}
    trailing_stop_positive_offset = {trailing_stop_positive_offset}
    trailing_only_offset_is_reached = {trailing_only_offset_is_reached}
    
    # Parametri ottimizzabili
    {optimization_params}
    
    # Timeframe
    timeframe = "{timeframe}"
    
    # Indicatori
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola gli indicatori tecnici.
        """
        {indicators_code}
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        {entry_conditions}
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        {exit_conditions}
        return dataframe
'''
    
    def convert_description_to_code(self, 
                                  description: str, 
                                  strategy_name: str,
                                  strategy_type: str = "volatility") -> str:
        """
        Converte una descrizione testuale in codice FreqTrade.
        
        Args:
            description: Descrizione testuale della strategia
            strategy_name: Nome della strategia
            strategy_type: Tipo di strategia
            
        Returns:
            Codice Python della strategia FreqTrade
        """
        
        try:
            # Estrai informazioni dalla descrizione
            extracted_info = self._extract_strategy_info(description)
            
            # Genera codice usando LLM specializzato
            code = self._generate_freqtrade_code(description, strategy_name, strategy_type, extracted_info)
            
            # Valida e correggi il codice
            validated_code = self._validate_and_fix_code(code, strategy_name)
            
            return validated_code
            
        except Exception as e:
            print(f"❌ Errore nella conversione: {e}")
            return self._generate_fallback_code(strategy_name, strategy_type)
    
    def _extract_strategy_info(self, description: str) -> Dict[str, Any]:
        """Estrae informazioni dalla descrizione testuale."""
        info = {
            'indicators': [],
            'timeframe': '5m',
            'roi_config': '{"0": 0.05, "30": 0.025, "60": 0.015, "120": 0.01}',
            'stoploss': -0.02,
            'trailing_stop': True,
            'trailing_stop_positive': 0.01,
            'trailing_stop_positive_offset': 0.02,
            'trailing_only_offset_is_reached': True,
            'optimization_params': [],
            'entry_conditions': [],
            'exit_conditions': []
        }
        
        # Estrai indicatori
        indicator_patterns = [
            r'RSI\s*\(?(\d+)?\)?',
            r'EMA\s*\(?(\d+)?\)?',
            r'SMA\s*\(?(\d+)?\)?',
            r'MACD',
            r'Bollinger\s+Bands?',
            r'ATR\s*\(?(\d+)?\)?',
            r'Stochastic',
            r'ADX\s*\(?(\d+)?\)?',
            r'Volume',
            r'CCI\s*\(?(\d+)?\)?'
        ]
        
        for pattern in indicator_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                indicator_name = re.search(pattern, description, re.IGNORECASE).group(0)
                info['indicators'].append(indicator_name)
        
        # Estrai timeframe
        timeframe_match = re.search(r'(\d+[mh])', description)
        if timeframe_match:
            info['timeframe'] = timeframe_match.group(1)
        
        # Estrai ROI e stoploss
        roi_match = re.search(r'(\d+(?:\.\d+)?)\s*%', description)
        if roi_match:
            roi_value = float(roi_match.group(1)) / 100
            info['roi_config'] = f'{{"0": {roi_value}}}'
        
        stoploss_match = re.search(r'stoploss[:\s]*(\d+(?:\.\d+)?)\s*%', description, re.IGNORECASE)
        if stoploss_match:
            info['stoploss'] = -float(stoploss_match.group(1)) / 100
        
        return info
    
    def _generate_freqtrade_code(self, 
                               description: str, 
                               strategy_name: str, 
                               strategy_type: str,
                               extracted_info: Dict[str, Any]) -> str:
        """Genera codice FreqTrade usando LLM specializzato."""
        
        # Crea prompt specializzato per FreqTrade
        prompt = self._create_freqtrade_prompt(description, strategy_name, strategy_type, extracted_info)
        
        try:
            code = query_ollama_fast(prompt, self.default_model, timeout=600)
            return self._clean_generated_code(code)
        except Exception as e:
            print(f"❌ Errore nella generazione codice: {e}")
            return self._generate_template_code(strategy_name, strategy_type, extracted_info)
    
    def _create_freqtrade_prompt(self, 
                               description: str, 
                               strategy_name: str, 
                               strategy_type: str,
                               extracted_info: Dict[str, Any]) -> str:
        """Crea prompt specializzato per FreqTrade."""
        
        class_name = self._generate_class_name(strategy_name)
        
        prompt = f"""
Sei un esperto sviluppatore di strategie FreqTrade. Converti questa descrizione in codice Python valido.

DESCRIZIONE STRATEGIA:
{description}

REQUISITI FREQTRADE:
- Nome classe: {class_name}
- Tipo strategia: {strategy_type}
- Indicatori identificati: {', '.join(extracted_info['indicators'])}
- Timeframe: {extracted_info['timeframe']}

REGOLE IMPORTANTI:
1. Usa sempre 'dataframe.loc[conditions, "enter_long"] = 1' per entrate
2. Usa sempre 'dataframe.loc[conditions, "exit_long"] = 1' per uscite
3. Tutti gli indicatori devono essere calcolati in populate_indicators()
4. Usa IntParameter/DecimalParameter per parametri ottimizzabili
5. Includi sempre docstring e commenti
6. Gestisci correttamente gli import di talib e freqtrade

GENERA SOLO IL CODICE PYTHON COMPLETO, senza spiegazioni.
"""
        
        return prompt
    
    def _generate_class_name(self, strategy_name: str) -> str:
        """Genera un nome di classe valido."""
        # Rimuovi caratteri non validi e capitalizza
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', strategy_name)
        if clean_name and clean_name[0].isdigit():
            clean_name = 'Strategy' + clean_name
        
        if not clean_name:
            clean_name = 'LLMStrategy'
        
        return clean_name.capitalize()
    
    def _clean_generated_code(self, code: str) -> str:
        """Pulisce il codice generato."""
        # Rimuovi markdown se presente
        if '```python' in code:
            code = code.split('```python')[1]
        if '```' in code:
            code = code.split('```')[0]
        
        # Rimuovi spiegazioni testuali
        lines = code.split('\n')
        cleaned_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('import') or line.strip().startswith('class') or line.strip().startswith('def'):
                in_code = True
            if in_code:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _validate_and_fix_code(self, code: str, strategy_name: str) -> str:
        """Valida e corregge il codice generato."""
        
        # Verifica sintassi
        try:
            ast.parse(code)
        except SyntaxError as e:
            print(f"⚠️ Errore di sintassi nel codice generato: {e}")
            return self._generate_fallback_code(strategy_name)
        
        # Verifica che contenga elementi essenziali
        required_elements = [
            'class',
            'IStrategy',
            'populate_indicators',
            'populate_entry_trend',
            'populate_exit_trend'
        ]
        
        missing_elements = [elem for elem in required_elements if elem not in code]
        if missing_elements:
            print(f"⚠️ Elementi mancanti: {missing_elements}")
            return self._generate_fallback_code(strategy_name)
        
        return code
    
    def _generate_template_code(self, 
                              strategy_name: str, 
                              strategy_type: str,
                              extracted_info: Dict[str, Any]) -> str:
        """Genera codice template se la generazione LLM fallisce."""
        
        class_name = self._generate_class_name(strategy_name)
        
        # Genera indicatori
        indicators_code = self._generate_indicators_code(extracted_info['indicators'])
        
        # Genera condizioni
        entry_conditions = self._generate_entry_conditions(extracted_info['indicators'])
        exit_conditions = self._generate_exit_conditions(extracted_info['indicators'])
        
        # Genera parametri di ottimizzazione
        optimization_params = self._generate_optimization_params(extracted_info['indicators'])
        
        return self.base_template.format(
            strategy_name=strategy_name,
            class_name=class_name,
            description=f"Strategia di {strategy_type} per futures crypto",
            roi_config=extracted_info['roi_config'],
            stoploss=extracted_info['stoploss'],
            trailing_stop=extracted_info['trailing_stop'],
            trailing_stop_positive=extracted_info['trailing_stop_positive'],
            trailing_stop_positive_offset=extracted_info['trailing_stop_positive_offset'],
            trailing_only_offset_is_reached=extracted_info['trailing_only_offset_is_reached'],
            optimization_params=optimization_params,
            timeframe=extracted_info['timeframe'],
            indicators_code=indicators_code,
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions
        )
    
    def _generate_indicators_code(self, indicators: List[str]) -> str:
        """Genera codice per gli indicatori."""
        code_lines = []
        
        for indicator in indicators:
            if 'RSI' in indicator:
                code_lines.append("dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)")
            elif 'EMA' in indicator:
                code_lines.append("dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)")
                code_lines.append("dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)")
            elif 'MACD' in indicator:
                code_lines.append("macd = ta.MACD(dataframe)")
                code_lines.append("dataframe['macd'] = macd['macd']")
                code_lines.append("dataframe['macdsignal'] = macd['macdsignal']")
            elif 'Bollinger' in indicator:
                code_lines.append("bollinger = ta.BBANDS(dataframe, timeperiod=20)")
                code_lines.append("dataframe['bb_lowerband'] = bollinger['lowerband']")
                code_lines.append("dataframe['bb_upperband'] = bollinger['upperband']")
            elif 'ATR' in indicator:
                code_lines.append("dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)")
        
        if not code_lines:
            code_lines = [
                "dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)",
                "dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)",
                "dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)"
            ]
        
        return '\n        '.join(code_lines)
    
    def _generate_entry_conditions(self, indicators: List[str]) -> str:
        """Genera condizioni di entrata."""
        conditions = []
        
        if any('RSI' in i for i in indicators):
            conditions.append("dataframe['rsi'] < 30")
        if any('EMA' in i for i in indicators):
            conditions.append("dataframe['ema_short'] > dataframe['ema_long']")
        if any('MACD' in i for i in indicators):
            conditions.append("dataframe['macd'] > dataframe['macdsignal']")
        
        if conditions:
            condition_str = ' & '.join(conditions)
            return f"dataframe.loc[{condition_str}, 'enter_long'] = 1"
        else:
            return "dataframe.loc[dataframe['rsi'] < 30, 'enter_long'] = 1"
    
    def _generate_exit_conditions(self, indicators: List[str]) -> str:
        """Genera condizioni di uscita."""
        conditions = []
        
        if any('RSI' in i for i in indicators):
            conditions.append("dataframe['rsi'] > 70")
        if any('EMA' in i for i in indicators):
            conditions.append("dataframe['ema_short'] < dataframe['ema_long']")
        if any('MACD' in i for i in indicators):
            conditions.append("dataframe['macd'] < dataframe['macdsignal']")
        
        if conditions:
            condition_str = ' | '.join(conditions)
            return f"dataframe.loc[{condition_str}, 'exit_long'] = 1"
        else:
            return "dataframe.loc[dataframe['rsi'] > 70, 'exit_long'] = 1"
    
    def _generate_optimization_params(self, indicators: List[str]) -> str:
        """Genera parametri di ottimizzazione."""
        params = []
        
        if any('RSI' in i for i in indicators):
            params.append("buy_rsi = IntParameter(20, 40, default=30, space=\"buy\")")
            params.append("sell_rsi = IntParameter(60, 80, default=70, space=\"sell\")")
        
        if not params:
            params = [
                "buy_rsi = IntParameter(20, 40, default=30, space=\"buy\")",
                "sell_rsi = IntParameter(60, 80, default=70, space=\"sell\")"
            ]
        
        return '\n    '.join(params)
    
    def _generate_fallback_code(self, strategy_name: str, strategy_type: str = "volatility") -> str:
        """Genera codice di fallback."""
        class_name = self._generate_class_name(strategy_name)
        
        return f'''
"""
{strategy_name} - Strategia di fallback
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class {class_name}(IStrategy):
    """
    Strategia di {strategy_type} per futures crypto.
    """
    
    minimal_roi = {{"0": 0.05, "30": 0.025, "60": 0.015, "120": 0.01}}
    stoploss = -0.02
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True
    
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    sell_rsi = IntParameter(60, 80, default=70, space="sell")
    
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] < self.buy_rsi.value) & 
            (dataframe['ema_short'] > dataframe['ema_long']),
            'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] > self.sell_rsi.value) | 
            (dataframe['ema_short'] < dataframe['ema_long']),
            'exit_long'] = 1
        return dataframe
'''

def main():
    """Test del convertitore FreqTrade."""
    converter = FreqTradeCodeConverter()
    
    print("🔧 Test convertitore FreqTrade...")
    
    # Test con descrizione di esempio
    description = """
    Strategia di volatilità per futures crypto.
    
    INDICATORI:
    - RSI (14): per identificare condizioni di ipercomprato/ipervenduto
    - EMA (9, 21): per trend direction
    - Bollinger Bands (20): per volatilità e breakout
    
    CONDIZIONI DI ENTRATA:
    - RSI < 30 (ipervenduto)
    - EMA 9 > EMA 21 (trend positivo)
    - Prezzo vicino alla banda inferiore di Bollinger
    
    CONDIZIONI DI USCITA:
    - RSI > 70 (ipercomprato)
    - EMA 9 < EMA 21 (trend negativo)
    - Prezzo tocca la banda superiore di Bollinger
    
    GESTIONE RISCHIO:
    - Stoploss: 2%
    - Take profit: 3%
    - Trailing stop: 1% dopo 1% di profitto
    """
    
    code = converter.convert_description_to_code(
        description=description,
        strategy_name="TestVolatilityStrategy",
        strategy_type="volatility"
    )
    
    print("\n📝 Codice generato:")
    print("="*50)
    print(code)
    print("="*50)

if __name__ == "__main__":
    main() 