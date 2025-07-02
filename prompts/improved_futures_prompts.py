"""
Prompt MIGLIORATI per strategie di trading futures crypto.
Risolvono i problemi identificati: over-trading, drawdown eccessivo, strategie troppo semplici.
"""

def get_improved_scalping_prompt() -> str:
    """
    Prompt migliorato per scalping con gestione rischio avanzata.
    """
    return """
Crea una strategia Freqtrade di SCALPING AVANZATO per futures crypto.
RISOLVI questi problemi: over-trading, drawdown eccessivo, stop loss troppo frequenti.

REQUISITI OBBLIGATORI:

1. TIMEFRAME E PARAMETRI:
   - Timeframe: 15m (NON 5m per ridurre rumore)
   - ROI: {"0": 0.10, "60": 0.05, "120": 0.03, "240": 0.02, "480": 0.01}
   - Stop loss: -0.03 (3% invece di 2%)
   - Trailing stop: True, positive: 0.02, offset: 0.03

2. INDICATORI TECNICI OBBLIGATORI:
   - RSI(14) per momentum
   - EMA(9) e EMA(21) per trend
   - MACD(12,26,9) per conferma
   - Bollinger Bands(20,2) per volatilità
   - Volume SMA(20) per conferma
   - ATR(14) per stop loss dinamico

3. LOGICA DI ENTRATA STRETTA (TUTTE le condizioni devono essere vere):
   - RSI < 25 (oversold)
   - EMA9 > EMA21 (trend positivo)
   - MACD > MACD_signal (momentum positivo)
   - Prezzo vicino alla banda inferiore di Bollinger
   - Volume > 120% della media
   - ATR > media ATR (volatilità sufficiente)

4. LOGICA DI USCITA:
   - RSI > 75 (overbought)
   - EMA9 < EMA21 (trend negativo)
   - MACD < MACD_signal (momentum negativo)
   - Prezzo vicino alla banda superiore di Bollinger

5. GESTIONE RISCHIO AVANZATA:
   - Max 2 trade simultanei (NON 3)
   - Stop loss dinamico basato su ATR
   - Position sizing basato su volatilità
   - Filtro per mercati troppo volatili

6. PARAMETRI OTTIMIZZABILI:
   - rsi_oversold = IntParameter(20, 35, default=25)
   - rsi_overbought = IntParameter(65, 80, default=75)
   - ema_short = IntParameter(5, 15, default=9)
   - ema_long = IntParameter(15, 30, default=21)

7. FUNZIONI OBBLIGATORIE:
   - custom_stoploss() per stop loss dinamico
   - confirm_trade_entry() per filtri aggiuntivi
   - populate_indicators() con tutti gli indicatori
   - populate_entry_trend() con logica multipla
   - populate_exit_trend() con logica multipla

ESEMPIO STRUTTURA:
```python
class ImprovedScalpingStrategy(IStrategy):
    minimal_roi = {"0": 0.10, "60": 0.05, "120": 0.03, "240": 0.02, "480": 0.01}
    stoploss = -0.03
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    timeframe = "15m"

    # Parametri ottimizzabili
    rsi_oversold = IntParameter(20, 35, default=25)
    rsi_overbought = IntParameter(65, 80, default=75)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Tutti gli indicatori obbligatori
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Logica multipla con TUTTE le condizioni
        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        # Stop loss dinamico
        return self.stoploss

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: datetime, entry_tag: Optional[str],
                           side: str, **kwargs) -> bool:
        # Filtri aggiuntivi
        return True
```

Rispondi SOLO con il codice Python completo e funzionante.
"""

def get_improved_momentum_prompt() -> str:
    """
    Prompt migliorato per momentum con gestione trend avanzata.
    """
    return """
Crea una strategia Freqtrade di MOMENTUM AVANZATO per futures crypto.
RISOLVI questi problemi: entrate premature, uscite troppo veloci, mancanza di trend filter.

REQUISITI OBBLIGATORI:

1. TIMEFRAME E PARAMETRI:
   - Timeframe: 1h (NON 5m per trend più chiari)
   - ROI: {"0": 0.15, "120": 0.08, "240": 0.05, "480": 0.03, "720": 0.02}
   - Stop loss: -0.04 (4% per trend più lunghi)
   - Trailing stop: True, positive: 0.03, offset: 0.04

2. INDICATORI TECNICI OBBLIGATORI:
   - RSI(14) per momentum
   - EMA(20), EMA(50), EMA(200) per trend multi-timeframe
   - MACD(12,26,9) per momentum
   - Stochastic(14,3,3) per timing
   - ADX(14) per forza del trend
   - Volume SMA(20) per conferma

3. LOGICA DI ENTRATA STRETTA:
   - ADX > 25 (trend forte)
   - EMA20 > EMA50 > EMA200 (trend rialzista)
   - RSI > 50 (momentum positivo)
   - MACD > MACD_signal (momentum confermato)
   - Stochastic non overbought
   - Volume > 150% media

4. LOGICA DI USCITA:
   - ADX < 20 (trend debole)
   - EMA20 < EMA50 (inversione trend)
   - RSI > 70 (overbought)
   - MACD < MACD_signal (momentum negativo)

5. GESTIONE RISCHIO:
   - Max 1 trade simultaneo per coppia
   - Stop loss basato su EMA200
   - Take profit multipli
   - Filtro per mercati laterali

6. PARAMETRI OTTIMIZZABILI:
   - adx_threshold = IntParameter(20, 35, default=25)
   - rsi_threshold = IntParameter(45, 65, default=50)
   - ema_short = IntParameter(15, 25, default=20)
   - ema_medium = IntParameter(40, 60, default=50)

Rispondi SOLO con il codice Python completo.
"""

def get_improved_breakout_prompt() -> str:
    """
    Prompt migliorato per breakout con gestione falsi segnali.
    """
    return """
Crea una strategia Freqtrade di BREAKOUT AVANZATO per futures crypto.
RISOLVI questi problemi: falsi breakout, entrate premature, mancanza di conferma.

REQUISITI OBBLIGATORI:

1. TIMEFRAME E PARAMETRI:
   - Timeframe: 4h (per breakout significativi)
   - ROI: {"0": 0.20, "240": 0.10, "480": 0.06, "720": 0.04, "1440": 0.025}
   - Stop loss: -0.05 (5% per breakout)
   - Trailing stop: True, positive: 0.04, offset: 0.05

2. INDICATORI TECNICI OBBLIGATORI:
   - Bollinger Bands(20,2) per range
   - Support/Resistance dinamici
   - Volume SMA(20) per conferma
   - RSI(14) per momentum
   - EMA(50) per trend
   - ATR(14) per volatilità

3. LOGICA DI ENTRATA STRETTA:
   - Consolidamento pre-breakout (BB squeeze)
   - Volume > 200% media al breakout
   - RSI > 60 per breakout rialzista
   - Prezzo > resistenza + 0.5% conferma
   - ATR > media ATR (volatilità sufficiente)

4. LOGICA DI USCITA:
   - Ritorno dentro il range
   - Volume calante
   - RSI estremo
   - Inversione trend

5. GESTIONE RISCHIO:
   - Max 1 trade simultaneo
   - Stop loss sotto supporto/resistenza
   - Take profit basato su ATR
   - Filtro per mercati troppo volatili

Rispondi SOLO con il codice Python completo.
"""

def get_improved_volatility_prompt() -> str:
    """
    Prompt migliorato per volatilità con gestione rischio avanzata.
    """
    return """
Crea una strategia Freqtrade di VOLATILITÀ AVANZATA per futures crypto.
RISOLVI questi problemi: perdite in mercati laterali, stop loss troppo frequenti.

REQUISITI OBBLIGATORI:

1. TIMEFRAME E PARAMETRI:
   - Timeframe: 30m (intermedio)
   - ROI: {"0": 0.12, "90": 0.06, "180": 0.04, "360": 0.025, "720": 0.015}
   - Stop loss: -0.035 (3.5%)
   - Trailing stop: True, positive: 0.025, offset: 0.035

2. INDICATORI TECNICI OBBLIGATORI:
   - ATR(14) per volatilità
   - Bollinger Bands(20,2) per range
   - RSI(14) per momentum
   - EMA(20) per trend
   - Volume SMA(20) per conferma
   - Volatility Ratio (ATR/EMA)

3. LOGICA DI ENTRATA STRETTA:
   - Volatilità > 150% media
   - RSI < 30 (oversold) o > 70 (overbought)
   - Prezzo ai bordi delle Bollinger Bands
   - Volume > 130% media
   - Trend direzionale chiaro

4. LOGICA DI USCITA:
   - Volatilità normalizzata
   - RSI ritorno a livelli normali
   - Prezzo centro Bollinger Bands
   - Volume calante

5. GESTIONE RISCHIO:
   - Position sizing basato su volatilità
   - Stop loss dinamico basato su ATR
   - Max 2 trade simultanei
   - Filtro per mercati troppo volatili

Rispondi SOLO con il codice Python completo.
"""

def get_improved_adaptive_prompt() -> str:
    """
    Prompt migliorato per strategia adattiva con machine learning.
    """
    return """
Crea una strategia Freqtrade ADATTIVA AVANZATA per futures crypto.
La strategia deve CAMBIARE APPROCCIO automaticamente in base al mercato.

REQUISITI OBBLIGATORI:

1. TIMEFRAME E PARAMETRI:
   - Timeframe: 1h (per analisi macro)
   - ROI: {"0": 0.15, "120": 0.08, "240": 0.05, "480": 0.03, "720": 0.02}
   - Stop loss: -0.04
   - Trailing stop: True, positive: 0.03, offset: 0.04

2. CLASSIFICAZIONE MERCATO:
   - TRENDY: ADX > 25, EMA20 > EMA50
   - VOLATILE: ATR > 150% media, RSI estremo
   - LATERALE: ADX < 20, BB squeeze

3. STRATEGIE PER TIPO MERCATO:
   - TRENDY: Trend following con EMA crossover
   - VOLATILE: Scalping con stop loss stretti
   - LATERALE: Mean reversion con Bollinger Bands

4. INDICATORI OBBLIGATORI:
   - ADX(14) per forza trend
   - ATR(14) per volatilità
   - Bollinger Bands(20,2) per range
   - EMA(20,50) per trend
   - RSI(14) per momentum
   - Volume SMA(20) per conferma

5. LOGICA ADATTIVA:
   - Calcola tipo di mercato ogni 4 ore
   - Cambia parametri automaticamente
   - Usa indicatori appropriati
   - Adatta position sizing

6. GESTIONE RISCHIO:
   - Stop loss adattivo per tipo mercato
   - Position sizing basato su volatilità
   - Max 1 trade simultaneo
   - Filtri per transizioni di mercato

Rispondi SOLO con il codice Python completo.
"""
