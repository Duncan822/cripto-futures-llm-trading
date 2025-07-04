"""
ContestScalpingcogito_8b - Strategia generata automaticamente (OTTIMIZZATA)
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class ContestScalpingcogito_8b(IStrategy):
    """
    Strategia generata automaticamente per trading futures crypto.
    OTTIMIZZATA con hyperopt - Parametri ottimali:
    - buy_rsi: 20 (ipervenduto più aggressivo)
    - sell_rsi: 80 (ipercomprato più aggressivo)
    """
    
    # Parametri ottimizzati da hyperopt
    buy_rsi = IntParameter(20, 40, default=20, space="buy")  # Ottimizzato: 20
    sell_rsi = IntParameter(60, 80, default=80, space="sell")  # Ottimizzato: 80
    
    # ROI ottimizzabile
    minimal_roi = {
        "0": 0.05,
        "30": 0.025,
        "60": 0.015,
        "120": 0.01
    }
    
    # Stoploss fisso
    stoploss = -0.02
    
    # Trailing stop fisso
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True
    
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola gli indicatori tecnici.
        """
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        bollinger = ta.BBANDS(dataframe, timeperiod=20)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_upperband'] = bollinger['upperband']
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        dataframe.loc[dataframe['rsi'] < self.buy_rsi.value, 'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        dataframe.loc[dataframe['rsi'] > self.sell_rsi.value, 'exit_long'] = 1
        return dataframe
