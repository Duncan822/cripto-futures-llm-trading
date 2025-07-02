 Crearemo una strategia Freqtrade per il trading di BTCUSDT a livello di 5 minuti con un trailing stop e una gestione del rischio integrata. Per questo esempio, utilizzeremo i seguenti parametri:

1. Pair: BTCUSDT
2. Intervalle: 5m
3. Trailing Stop: 0.5%
4. Gestione Rischio: 2% del portafoglio

Inizieremo creando il file di configurazione della nostra strategia (strategy.py):

```python
# strategy.py
from freqtrade.strategy import IStrategy
from pandas import concat
import talib.abstract as ta
from functools import reduce

class MyStrategy(IStrategy):
    minimal_roi = {
        "0": 0.5,
        "1": 0.2,
        "2": 0.1,
    }
    stoploss = -0.1
    timeframe = '5m'
    use_abs = True
    trailing_stop = 0.005
    initial_capital = 1000
    max_invested_per_trade = 2.0

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: Series) -> DataFrame:
        dataframe['RSI'] = ta.RSI(data=dataframe, timeperiod=14)
        dataframe['STOCHF'] = ta.STOCHFastSlow(fastk_param=5, fastd_param=3, slowk_param=3, slowd_param=3)
        return dataframe

    def analyze(self, datadict):
        for data in datadict:
            if data['type'] == 'bid':
                high = data['high']
                low = data['low']

                if not self.data_framed[self.timeframe].empty:
                    open_price = self.data_framed[self.timeframe]['open'].iloc[-1]
                    close_price = self.data_framed[self.timeframe]['close'].iloc[-1]

                    if (high - open_price) / open_price > 0.02 or (low - open_price) / open_price < -0.02:
                        if ta.RSI(self.data_framed, timeperiod=14).iloc[-1] < 30 and ta.STOCHF(self.data_framed, fastk_param=5, fastd_param=3, slowk_param=3, slowd_param=3).iloc[-1][0] > self.data_framed['STOCHF'].quantile(0.85)[-1]:
                            self.log('Buying at open price:', open_price)
                            self.buy_long(open_price, stoploss=self.stoploss, remove_sl = False)
```

Aggiungiamo anche un file d'esportazione per indicare l'intervallo di trading (trade_range.csv):

```
from datetime import datetime

start_date = datetime(2021, 1, 1)
end_date = datetime(2021, 12, 31)

with open('trade_range.csv', 'w') as file:
    file.write(f'timestamp,open,high,low,close,volume,close_time\n')
    for timestamp in (start_date + datetime.timedelta(minutes=x) for x in range(int((end_date - start_date).total_seconds() / 60))):
        file.write(f"{timestamp},{self.data['open']},{self.data['high']},{self.data['low']},{self.data['close']},{self.data['volume']},{timestamp}\n")
```

Infine, eseguiremo il seguente comando per iniziare a fare trading:

```bash
freqtrade train --strategy strategy.py --verbose --config config.json --hyperopt-config hyperopt_config.json --trade-range trade_range.csv
```