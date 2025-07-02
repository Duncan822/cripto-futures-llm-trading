
class MomentumStrategy_mistral:7b-instruct-q4_0_20250701_062543(IStrategy):
minimal_roi = {"0": 0.05}
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
