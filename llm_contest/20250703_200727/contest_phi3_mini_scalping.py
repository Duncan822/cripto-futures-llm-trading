
class ContestScalpingphi3_mini(IStrategy):
    minimal_roi = {"0": 0.05}
    stoploss = -0.1
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=10)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=30)
        return dataframe
    
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['ema_short'] > dataframe['ema_long']),
            'buy'] = 1
        return dataframe
    
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['ema_short'] < dataframe['ema_long']),
            'sell'] = 1
        return dataframe
