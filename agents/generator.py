"""
Agente Generatore: genera nuove strategie di trading compatibili con Freqtrade.
Ottimizzato per futures volatili e velocità di risposta.
Approccio ibrido: generazione diretta + conversione testuale.
"""

from llm_utils import query_ollama, query_ollama_fast, get_model_speed_ranking, get_optimal_timeout, estimate_prompt_complexity
from .strategy_converter import StrategyConverter
import re

class GeneratorAgent:
    def __init__(self, default_model: str = "phi3"):
        self.default_model = default_model
        self.fast_models = get_model_speed_ranking()
        self.converter = StrategyConverter()

    def generate_strategy(self, prompt: str, model: str | None = None, timeout: int = None, use_hybrid: bool = True, strategy_name: str = None) -> str:
        """
        Genera una nuova strategia FreqTrade usando approccio ibrido.

        Args:
            prompt: Il prompt per la generazione
            model: Il modello da utilizzare (default: phi3 per velocità)
            timeout: Timeout in secondi (se None, viene calcolato automaticamente)
            use_hybrid: Se True, usa approccio ibrido (default: True)
            strategy_name: Nome della classe strategia (se None, viene estratto dal prompt)
        """
        model_to_use = model or self.default_model

        # Calcola timeout ottimale se non fornito
        if timeout is None:
            complexity = estimate_prompt_complexity(prompt)
            timeout = get_optimal_timeout(model_to_use, complexity)
            print(f"⏱️ Timeout calcolato automaticamente: {timeout}s per {model_to_use} ({complexity})")

        # Estrai il nome della strategia se non fornito
        if strategy_name is None:
            strategy_name = self._extract_strategy_name(prompt)

        if use_hybrid:
            return self._generate_hybrid_strategy(prompt, model_to_use, timeout, strategy_name)
        else:
            return self._generate_direct_strategy(prompt, model_to_use, timeout, strategy_name)

    def _generate_hybrid_strategy(self, prompt: str, model: str, timeout: int, strategy_name: str) -> str:
        """
        Approccio ibrido: prima prova generazione diretta, poi conversione testuale.
        """
        try:
            # Tentativo 1: Generazione diretta di codice
            print("🔄 Tentativo 1: Generazione diretta di codice...")
            direct_code = self._generate_direct_strategy(prompt, model, timeout // 2, strategy_name)

            # Valida il codice generato
            if self.converter.validate_and_fix_code(direct_code, strategy_name) != direct_code:
                print("⚠️ Codice diretto non valido, tentativo conversione testuale...")
                return self._generate_text_to_code_strategy(prompt, model, timeout // 2, strategy_name)
            else:
                print("✅ Codice diretto valido!")
                return direct_code

        except Exception as e:
            print(f"❌ Errore generazione diretta: {e}")
            print("🔄 Fallback: conversione testuale...")
            return self._generate_text_to_code_strategy(prompt, model, timeout, strategy_name)

    def _generate_direct_strategy(self, prompt: str, model: str, timeout: int, strategy_name: str) -> str:
        """
        Generazione diretta di codice FreqTrade.
        """
        # Ottimizza il prompt per generazione di codice
        code_prompt = self._optimize_code_prompt(prompt, strategy_name)

        try:
            if len(code_prompt) < 500:
                return query_ollama_fast(code_prompt, model, timeout=600)
            else:
                return query_ollama(code_prompt, model, timeout=timeout)
        except Exception as e:
            print(f"❌ Errore nella generazione diretta con {model}: {e}")
            raise

    def _generate_text_to_code_strategy(self, prompt: str, model: str, timeout: int, strategy_name: str) -> str:
        """
        Genera descrizione testuale e la converte in codice.
        """
        # Ottimizza il prompt per descrizione testuale
        text_prompt = self._optimize_text_prompt(prompt)

        try:
            # Genera descrizione testuale
            text_description = query_ollama_fast(text_prompt, model, timeout=600)

            # Converti in codice
            strategy_code = self.converter.convert_text_to_strategy(text_description, strategy_name)

            print("✅ Conversione testuale completata!")
            return strategy_code

        except Exception as e:
            print(f"❌ Errore nella conversione testuale: {e}")
            return self._get_default_strategy(strategy_name)

    def generate_futures_strategy(self, strategy_type: str = "volatility", use_hybrid: bool = True, strategy_name: str = None) -> str:
        """
        Genera una strategia specifica per futures volatili.

        Args:
            strategy_type: Tipo di strategia ("volatility", "scalping", "breakout", "momentum", "adaptive")
            use_hybrid: Se True, usa approccio ibrido (default: True)
            strategy_name: Nome della classe strategia (se None, viene generato automaticamente)
        """
        from prompts.improved_futures_prompts import (
            get_improved_scalping_prompt,
            get_improved_momentum_prompt,
            get_improved_breakout_prompt,
            get_improved_volatility_prompt,
            get_improved_adaptive_prompt
        )

        # Seleziona il prompt migliorato appropriato
        prompts = {
            "volatility": get_improved_volatility_prompt(),
            "scalping": get_improved_scalping_prompt(),
            "breakout": get_improved_breakout_prompt(),
            "momentum": get_improved_momentum_prompt(),
            "adaptive": get_improved_adaptive_prompt()
        }

        prompt = prompts.get(strategy_type, get_improved_volatility_prompt())

        # Genera nome strategia se non fornito
        if strategy_name is None:
            strategy_name = f"{strategy_type.capitalize()}Strategy"

        # Usa il modello più veloce disponibile
        fastest_model = self.fast_models[0] if self.fast_models else "phi3"

        try:
            print(f"🚀 Generazione strategia {strategy_type} con {fastest_model} (ibrido: {use_hybrid})...")
            return self.generate_strategy(prompt, fastest_model, timeout=1800, use_hybrid=use_hybrid, strategy_name=strategy_name)
        except Exception as e:
            print(f"❌ Errore nella generazione strategia {strategy_type}: {e}")
            return self._get_default_futures_strategy(strategy_type, strategy_name)

    def _extract_strategy_name(self, prompt: str) -> str:
        """
        Estrae il nome della strategia dal prompt.
        """
        # Cerca pattern comuni per il nome della strategia
        patterns = [
            r'strategia\s+(\w+)',
            r'strategy\s+(\w+)',
            r'(\w+)\s+strategy',
            r'(\w+)\s+strategia',
            r'crea\s+(\w+)',
            r'create\s+(\w+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                name = match.group(1).capitalize()
                # Assicurati che finisca con "Strategy"
                if not name.endswith("Strategy"):
                    name += "Strategy"
                return name

        # Fallback: usa un nome generico
        return "LLMStrategy"

    def _optimize_code_prompt(self, prompt: str, strategy_name: str) -> str:
        """
        Ottimizza il prompt per generazione diretta di codice.
        """
        if "genera una strategia" in prompt.lower():
            return f"""Crea una strategia Freqtrade completa per trading futures crypto volatili.
            Rispondi SOLO con codice Python valido che include:
            - Classe chiamata {strategy_name} che eredita da IStrategy
            - Metodi populate_indicators, populate_entry_trend, populate_exit_trend
            - Indicatori tecnici (RSI, EMA, MACD, Bollinger Bands, ATR)
            - Condizioni di entrata/uscita per long/short
            - Gestione volatilità e stop loss dinamici
            - Parametri ottimizzabili con IntParameter/DecimalParameter

            Focus su:
            - Movimenti importanti (breakout, momentum)
            - Operazioni bidirezionali (long/short)
            - Gestione volatilità (ATR, stop loss dinamici)
            - Indicatori tecnici (EMA, RSI, MACD, Volume)

            Rispondi SOLO con codice Python completo e valido.
            La classe DEVE chiamarsi {strategy_name}."""

        return prompt[:800]  # Limita la lunghezza del prompt

    def _optimize_text_prompt(self, prompt: str) -> str:
        """
        Ottimizza il prompt per generazione di descrizioni testuali.
        """
        if "genera una strategia" in prompt.lower():
            return """Descrivi una strategia di trading per futures crypto volatili.
            Includi:
            - Indicatori tecnici da utilizzare (RSI, EMA, MACD, Bollinger Bands, ATR)
            - Condizioni di entrata (quando comprare/vendere)
            - Condizioni di uscita (quando chiudere posizioni)
            - Gestione del rischio (stop loss, take profit)
            - Timeframe consigliato
            - Parametri di ottimizzazione

            Descrivi in linguaggio naturale, non codice.
            Focus su strategie per mercati volatili con operazioni long/short."""

        return prompt[:600]  # Prompt più breve per descrizioni

    def _generate_fallback_strategy(self, strategy_name: str = "LLMStrategy") -> str:
        """
        Genera una strategia di fallback semplice se il modello principale fallisce.
        """
        fallback_prompt = f"""Crea una strategia Freqtrade semplice per futures crypto.
        Usa EMA crossover e RSI. La classe deve chiamarsi {strategy_name}.
        Rispondi solo con codice Python."""

        # Prova con modelli sempre più veloci
        for model in self.fast_models:
            try:
                return query_ollama_fast(fallback_prompt, model, timeout=600)
            except Exception as e:
                print(f"❌ Fallback con {model} fallito: {e}")
                continue

        return self._get_default_strategy(strategy_name)

    def _get_default_strategy(self, strategy_name: str = "LLMStrategy") -> str:
        """
        Restituisce una strategia di default se tutto il resto fallisce.
        """
        return f'''
class {strategy_name}(IStrategy):
    minimal_roi = {{"0": 0.05}}
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
'''

    def _get_default_futures_strategy(self, strategy_type: str, strategy_name: str = None) -> str:
        """
        Restituisce una strategia futures di default.
        """
        if strategy_name is None:
            strategy_name = f"{strategy_type.capitalize()}Strategy"

        if strategy_type == "volatility":
            return f'''
class {strategy_name}(IStrategy):
    minimal_roi = {{"0": 0.03, "10": 0.02, "30": 0.01}}
    stoploss = -0.05
    timeframe = "5m"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['ema9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['ema9'] > dataframe['ema21']) &
            (dataframe['ema21'] > dataframe['ema50']) &
            (dataframe['rsi'] > 50),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['ema9'] < dataframe['ema21']) &
            (dataframe['ema21'] < dataframe['ema50']) &
            (dataframe['rsi'] < 50),
            'sell'] = 1
        return dataframe
'''
        else:
            return self._get_default_strategy(strategy_name)
