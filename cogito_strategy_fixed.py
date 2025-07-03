#!/usr/bin/env python3
"""
Strategia di trading avanzata per futures crypto - Versione corretta basata su cogito:8b
"""

from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from pandas import DataFrame
import talib.abstract as ta
import numpy as np
import logging
from functools import reduce

logger = logging.getLogger(__name__)

class CryptoFuturesStrategy(IStrategy):
    """
    Strategia avanzata per futures crypto con analisi multi-timeframe e gestione del rischio.
    Basata sulla generazione di cogito:8b con correzioni per FreqTrade.
    """

    # Parametri di base
    minimal_roi = {
        "0": 0.15,
        "30": 0.10,
        "60": 0.05,
        "120": 0.02
    }
    
    stoploss = -0.10
    timeframe = '1h'
    
    # Parametri configurabili tramite config.json
    timeframe_param = IntParameter(60, 240, default=120, space='buy')
    rsi_period = IntParameter(14, 30, default=21, space='buy')
    macd_fast = IntParameter(12, 26, default=15, space='buy')
    macd_slow = IntParameter(26, 52, default=32, space='buy')
    bollinger_std = DecimalParameter(0.02, 0.1, default=0.05, space='buy')
    ichimoku_period = IntParameter(9, 21, default=13, space='buy')
    stochastic_k = IntParameter(3, 7, default=5, space='buy')
    stochastic_d = IntParameter(3, 7, default=3, space='buy')

    # Parametri di gestione del rischio
    max_position_size = DecimalParameter(0.01, 0.1, default=0.05, space='buy')
    trailing_stop_percent = DecimalParameter(0.02, 0.2, default=0.1, space='buy')
    max_correlation = DecimalParameter(0.5, 0.9, default=0.7, space='buy')
    min_diversification = IntParameter(2, 10, default=3, space='buy')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calcola gli indicatori tecnici per la strategia.
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=self.rsi_period.value)
        
        # MACD
        macd = ta.MACD(dataframe['close'],
                      fastperiod=self.macd_fast.value,
                      slowperiod=self.macd_slow.value,
                      signalperiod=9)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe['close'],
                             timeperiod=20,
                             nbdevup=self.bollinger_std.value,
                             nbdevdn=self.bollinger_std.value)
        dataframe['bb_upperband'] = bollinger['upperband']
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        
        # Ichimoku Cloud
        ichimoku = ta.ICHIMOKU(dataframe['high'],
                              dataframe['low'],
                              dataframe['close'],
                              conversion_period=self.ichimoku_period.value,
                              base_period=26,
                              lag_period=52)
        dataframe['ichimoku_a'] = ichimoku['tenkan_sen']
        dataframe['ichimoku_b'] = ichimoku['kijun_sen']
        dataframe['ichimoku_c'] = ichimoku['senkou_span_a']
        dataframe['ichimoku_d'] = ichimoku['senkou_span_b']
        
        # Stochastic Oscillator
        stoch = ta.STOCH(dataframe['high'],
                         dataframe['low'],
                         dataframe['close'],
                         fastk_period=self.stochastic_k.value,
                         slowk_period=3,
                         slowd_period=self.stochastic_d.value)
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']
        
        # Volume Profile
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        
        # ATR per volatilità
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        
        # EMA per trend
        dataframe['ema_20'] = ta.EMA(dataframe['close'], timeperiod=20)
        dataframe['ema_50'] = ta.EMA(dataframe['close'], timeperiod=50)
        
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Identifica le condizioni di acquisto per la strategia.
        """
        conditions = []
        
        # Condizione 1: Breakout su Bollinger Bands con RSI non overbought
        conditions.append(
            (dataframe['close'] > dataframe['bb_upperband']) &
            (dataframe['rsi'] < 70) &
            (dataframe['volume_ratio'] > 1.2)
        )
        
        # Condizione 2: Divergenza al rialzo con Stochastic
        conditions.append(
            (dataframe['stoch_k'] > 80) & 
            (dataframe['stoch_d'].shift(1) <= 20) &
            (dataframe['macd'] > dataframe['macdsignal'])
        )
        
        # Condizione 3: Ichimoku Cloud supportivo
        conditions.append(
            (dataframe['close'] > dataframe['ichimoku_a']) &
            (dataframe['close'] > dataframe['ichimoku_b']) &
            (dataframe['rsi'] < 50) &
            (dataframe['ema_20'] > dataframe['ema_50'])
        )
        
        # Condizione 4: RSI oversold con rimbalzo
        conditions.append(
            (dataframe['rsi'] < 30) &
            (dataframe['rsi'] > dataframe['rsi'].shift(1)) &
            (dataframe['close'] > dataframe['bb_lowerband'])
        )
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, conditions),
                'buy'
            ] = 1
        
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Identifica le condizioni di vendita per la strategia.
        """
        conditions = []
        
        # Condizione 1: Breakout al ribasso su Bollinger Bands
        conditions.append(
            (dataframe['close'] < dataframe['bb_lowerband']) &
            (dataframe['rsi'] > 30) &
            (dataframe['volume_ratio'] > 1.2)
        )
        
        # Condizione 2: Divergenza al ribasso con Stochastic
        conditions.append(
            (dataframe['stoch_k'] < 20) & 
            (dataframe['stoch_d'].shift(1) >= 80) &
            (dataframe['macd'] < dataframe['macdsignal'])
        )
        
        # Condizione 3: Ichimoku Cloud resistente
        conditions.append(
            (dataframe['close'] < dataframe['ichimoku_b']) &
            (dataframe['close'] < dataframe['ichimoku_a']) &
            (dataframe['rsi'] > 70) &
            (dataframe['ema_20'] < dataframe['ema_50'])
        )
        
        # Condizione 4: RSI overbought con calo
        conditions.append(
            (dataframe['rsi'] > 70) &
            (dataframe['rsi'] < dataframe['rsi'].shift(1)) &
            (dataframe['close'] < dataframe['bb_upperband'])
        )
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x | y, conditions),
                'sell'
            ] = 1
        
        return dataframe

    def custom_stop_loss(self, pair: str, trade: 'Trade', current_time: 'datetime',
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Implementa un trailing stop loss personalizzato.
        """
        # Trailing stop loss basato su ATR
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        if last_candle['atr'] is not None:
            # Stop loss dinamico basato su ATR
            atr_stop = last_candle['atr'] * 2
            return current_rate - atr_stop
        
        # Fallback al trailing stop percentuale
        return current_rate * (1 - self.trailing_stop_percent.value)

    def custom_entry_price(self, pair: str, current_time: 'datetime', proposed_rate: float,
                          entry_tag: Optional[str], side: str, **kwargs) -> float:
        """
        Calcola il prezzo di entry ottimale.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        if side == 'long':
            # Entry al prezzo di chiusura o leggermente sopra
            return proposed_rate * 1.001  # 0.1% sopra per slippage
        else:
            # Entry al prezzo di chiusura o leggermente sotto
            return proposed_rate * 0.999  # 0.1% sotto per slippage

    def custom_exit(self, pair: str, trade: 'Trade', current_time: 'datetime', current_rate: float,
                   current_profit: float, **kwargs) -> Optional[str]:
        """
        Implementa una strategia di uscita personalizzata.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # Exit su divergenza
        if trade.is_long:
            if (last_candle['stoch_k'] > 80 and last_candle['stoch_d'] <= 20):
                return "stoch_divergence_exit"
        else:
            if (last_candle['stoch_k'] < 20 and last_candle['stoch_d'] >= 80):
                return "stoch_divergence_exit"
        
        # Exit su time-based (dopo 24 ore)
        if (current_time - trade.open_date_utc).total_seconds() > 86400:  # 24 ore
            return "time_based_exit"
        
        return None

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: 'datetime', entry_tag: Optional[str],
                           side: str, **kwargs) -> bool:
        """
        Conferma l'entry del trade con controlli aggiuntivi.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # Controllo volatilità
        if last_candle['atr'] is not None and last_candle['atr'] > last_candle['close'] * 0.05:
            logger.info(f"Volatilità troppo alta per {pair}, skip trade")
            return False
        
        # Controllo volume
        if last_candle['volume_ratio'] < 0.8:
            logger.info(f"Volume troppo basso per {pair}, skip trade")
            return False
        
        return True

    def custom_stake_amount(self, pair: str, current_time: 'datetime', current_rate: float,
                           proposed_stake: float, min_stake: Optional[float], max_stake: Optional[float],
                           leverage: float, entry_tag: Optional[str], side: str, **kwargs) -> float:
        """
        Calcola il position size basato sulla volatilità.
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()
        
        # Position sizing dinamico basato su ATR
        if last_candle['atr'] is not None:
            volatility_factor = 1 - (last_candle['atr'] / last_candle['close'])
            adjusted_stake = proposed_stake * volatility_factor * self.max_position_size.value
        else:
            adjusted_stake = proposed_stake * self.max_position_size.value
        
        # Assicurati che sia dentro i limiti
        if min_stake:
            adjusted_stake = max(adjusted_stake, min_stake)
        if max_stake:
            adjusted_stake = min(adjusted_stake, max_stake)
        
        return adjusted_stake 