#!/usr/bin/env python3
"""
Template migliorato per strategie di trading futures crypto.
Risolve i problemi identificati nel backtest precedente.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class ImprovedStrategyTemplate(IStrategy):
    """
    Template migliorato per strategie di trading futures.
    Risolve i problemi di over-trading e drawdown eccessivo.
    """

    # ROI più conservativo - riduce il numero di chiusure premature
    minimal_roi = {
        "0": 0.10,      # 10% invece di 5%
        "60": 0.05,     # 5% dopo 1 ora
        "120": 0.03,    # 3% dopo 2 ore
        "240": 0.02,    # 2% dopo 4 ore
        "480": 0.01     # 1% dopo 8 ore
    }

    # Stop loss più conservativo
    stoploss = -0.03    # 3% invece di 2%

    # Trailing stop più conservativo
    trailing_stop = True
    trailing_stop_positive = 0.02      # 2% invece di 1%
    trailing_stop_positive_offset = 0.03  # 3% invece di 2%
    trailing_only_offset_is_reached = True

    # Timeframe più lungo per ridurre il rumore
    timeframe = "15m"   # 15m invece di 5m

    # Parametri ottimizzabili
    rsi_oversold = IntParameter(20, 35, default=25, space="buy")
    rsi_overbought = IntParameter(65, 80, default=75, space="sell")
    ema_short_period = IntParameter(5, 15, default=9, space="buy")
    ema_long_period = IntParameter(15, 30, default=21, space="buy")

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola indicatori tecnici migliorati.
        """
        # RSI con periodo ottimizzabile
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)

        # EMA per trend
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=self.ema_short_period.value)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=self.ema_long_period.value)

        # MACD per momentum
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # Bollinger Bands per volatilità
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']

        # Volume per conferma
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_mean']

        # Trend strength
        dataframe['trend_strength'] = abs(dataframe['ema_short'] - dataframe['ema_long']) / dataframe['ema_long']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Segnali di entrata migliorati con più filtri.
        """
        conditions = []

        # Condizione 1: RSI oversold
        conditions.append(dataframe['rsi'] < self.rsi_oversold.value)

        # Condizione 2: Trend positivo (EMA short > EMA long)
        conditions.append(dataframe['ema_short'] > dataframe['ema_long'])

        # Condizione 3: MACD positivo o in ripresa
        conditions.append(
            (dataframe['macd'] > dataframe['macdsignal']) |
            (dataframe['macdhist'] > dataframe['macdhist'].shift(1))
        )

        # Condizione 4: Prezzo vicino alla banda inferiore di Bollinger
        conditions.append(dataframe['close'] <= dataframe['bb_lowerband'] * 1.02)

        # Condizione 5: Volume sopra la media
        conditions.append(dataframe['volume_ratio'] > 1.2)

        # Condizione 6: Trend strength sufficiente
        conditions.append(dataframe['trend_strength'] > 0.005)

        # Combina tutte le condizioni
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'
            ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Segnali di uscita migliorati.
        """
        conditions = []

        # Condizione 1: RSI overbought
        conditions.append(dataframe['rsi'] > self.rsi_overbought.value)

        # Condizione 2: Trend negativo
        conditions.append(dataframe['ema_short'] < dataframe['ema_long'])

        # Condizione 3: MACD negativo
        conditions.append(dataframe['macd'] < dataframe['macdsignal'])

        # Condizione 4: Prezzo vicino alla banda superiore di Bollinger
        conditions.append(dataframe['close'] >= dataframe['bb_upperband'] * 0.98)

        # Combina le condizioni
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'
            ] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Stop loss dinamico basato sul profitto.
        """
        # Se siamo in profitto, stop loss più stretto
        if current_profit > 0.05:  # 5% di profitto
            return -0.01  # 1% di stop loss
        elif current_profit > 0.02:  # 2% di profitto
            return -0.015  # 1.5% di stop loss
        else:
            return self.stoploss  # Stop loss normale

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                           side: str, **kwargs) -> bool:
        """
        Conferma aggiuntiva per l'entrata nel trade.
        """
        # Controlla se il mercato è troppo volatile
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        # Non entrare se il volume è troppo basso
        if last_candle['volume_ratio'] < 0.8:
            return False

        # Non entrare se il trend è troppo debole
        if last_candle['trend_strength'] < 0.003:
            return False

        return True

# Funzione helper per ridurre le condizioni
from functools import reduce
