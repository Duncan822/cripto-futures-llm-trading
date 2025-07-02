"""
Prompt specializzati per strategie di trading futures volatili
"""

def get_futures_volatility_prompt() -> str:
    """
    Prompt per strategie futures che identificano movimenti importanti
    e fanno operazioni in entrambe le direzioni.
    """
    return """
Crea una strategia Freqtrade per trading futures crypto su mercati volatili.
La strategia deve:

1. IDENTIFICARE MOVIMENTI IMPORTANTI:
   - Breakout di supporti/resistenze
   - Volatilità improvvisa (ATR)
   - Momentum significativo (RSI, MACD)
   - Volume anomalo

2. OPERARE IN ENTRAMBE LE DIREZIONI:
   - Long su trend rialzista forte
   - Short su trend ribassista forte
   - Scalping su oscillazioni laterali

3. GESTIRE LA VOLATILITÀ:
   - Stop loss dinamici basati su ATR
   - Take profit multipli
   - Position sizing adattivo

4. INDICATORI TECNICI:
   - EMA 9, 21, 50 per trend
   - RSI per momentum e divergenze
   - MACD per segnali di inversione
   - Bollinger Bands per volatilità
   - ATR per stop loss dinamici
   - Volume per conferma

5. LOGICA DI TRADING:
   - Long: EMA9 > EMA21 > EMA50 + RSI > 50 + Volume alto
   - Short: EMA9 < EMA21 < EMA50 + RSI < 50 + Volume alto
   - Exit: RSI estremo (>70 long, <30 short) o inversione trend

Rispondi SOLO con il codice Python completo della strategia.
"""

def get_scalping_futures_prompt() -> str:
    """
    Prompt per strategie di scalping su futures volatili.
    """
    return """
Crea una strategia Freqtrade di scalping per futures crypto volatili.
La strategia deve:

1. TIMEFRAME BREVE:
   - Usa timeframe 1m o 5m
   - Entrate e uscite rapide
   - Profitti piccoli ma frequenti

2. INDICATORI VELOCI:
   - Stochastic RSI per segnali rapidi
   - EMA 5 e 13 per trend immediato
   - Williams %R per momentum
   - Volume per conferma

3. LOGICA SCALPING:
   - Long: Stoch RSI oversold + EMA5 > EMA13 + Volume spike
   - Short: Stoch RSI overbought + EMA5 < EMA13 + Volume spike
   - Exit: RSI estremo o inversione EMA

4. GESTIONE RISCHIO:
   - Stop loss stretto (0.5-1%)
   - Take profit rapido (1-2%)
   - Max 3 trade simultanei

Rispondi SOLO con il codice Python della strategia.
"""

def get_breakout_futures_prompt() -> str:
    """
    Prompt per strategie di breakout su futures.
    """
    return """
Crea una strategia Freqtrade per trading breakout su futures crypto.
La strategia deve:

1. IDENTIFICARE BREAKOUT:
   - Rottura Bollinger Bands
   - Breakout volume elevato
   - Consolidamento pre-breakout
   - Support/Resistance rotti

2. CONFERME:
   - Volume > 150% media
   - Momentum forte (RSI, MACD)
   - Trend direzionale chiaro

3. ENTRY/EXIT:
   - Long: Breakout sopra resistenza + Volume + Momentum
   - Short: Breakout sotto supporto + Volume + Momentum
   - Exit: Ritorno dentro range o trend reversal

4. INDICATORI:
   - Bollinger Bands (20,2)
   - Volume SMA
   - RSI (14)
   - MACD
   - ATR per stop loss

Rispondi SOLO con il codice Python della strategia.
"""

def get_momentum_futures_prompt() -> str:
    """
    Prompt per strategie di momentum su futures.
    """
    return """
Crea una strategia Freqtrade di momentum per futures crypto.
La strategia deve:

1. CATTURARE MOMENTUM:
   - RSI momentum divergenze
   - MACD crossover veloci
   - Price action forte
   - Volume momentum

2. DIRECTIONAL TRADING:
   - Long su momentum rialzista
   - Short su momentum ribassista
   - Evita mercati laterali

3. TIMING:
   - Entrata su pullback
   - Uscita su momentum esaurito
   - Trail stop su trend forte

4. INDICATORI:
   - RSI (14) per momentum
   - MACD (12,26,9) per trend
   - EMA 20,50 per direzione
   - Volume per conferma
   - ATR per volatilità

Rispondi SOLO con il codice Python della strategia.
"""

def get_adaptive_futures_prompt() -> str:
    """
    Prompt per strategia adattiva che cambia approccio in base al mercato.
    """
    return """
Crea una strategia Freqtrade ADATTIVA per futures crypto.
La strategia deve ADATTARSI a:

1. MERCATO TRENDY:
   - Usa trend following
   - EMA crossover
   - Hold posizioni più a lungo

2. MERCATO VOLATILE:
   - Usa scalping
   - Stop loss stretti
   - Take profit rapidi

3. MERCATO LATERALE:
   - Usa mean reversion
   - Bollinger Bands
   - Range trading

4. LOGICA ADATTIVA:
   - Calcola volatilità (ATR)
   - Identifica tipo di mercato
   - Cambia parametri automaticamente
   - Usa indicatori appropriati

5. GESTIONE RISCHIO:
   - Position sizing adattivo
   - Stop loss dinamici
   - Diversificazione temporale

Rispondi SOLO con il codice Python della strategia adattiva.
""" 