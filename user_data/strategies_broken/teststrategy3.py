"""
Test Strategy
"""
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class teststrategy3(IStrategy):
    minimal_roi = {"0": 0.05}
    stoploss = -0.02
    
    def populate_indicators(self, dataframe, metadata):
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
    
    def populate_entry_trend(self, dataframe, metadata):
        dataframe.loc[dataframe['rsi'] < 30, 'enter_long'] = 1
        return dataframe
    
    def populate_exit_trend(self, dataframe, metadata):
        dataframe.loc[dataframe['rsi'] > 70, 'exit_long'] = 1
        return dataframe
        # Errore di sintassi: indentazione sbagliata
    def wrong_function(self):
    pass
