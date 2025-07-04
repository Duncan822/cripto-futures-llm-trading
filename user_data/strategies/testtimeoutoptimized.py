
"""
TestTimeoutOptimized - Strategia di fallback
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class Testtimeoutoptimized(IStrategy):
    """
    Strategia di volatility per futures crypto.
    """
    
    minimal_roi = {"0": 0.05, "30": 0.025, "60": 0.015, "120": 0.01}
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
