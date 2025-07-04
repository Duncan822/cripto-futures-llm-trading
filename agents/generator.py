"""
Agente Generatore: genera nuove strategie di trading compatibili con Freqtrade.
Ottimizzato per futures volatili e velocità di risposta.
Approccio a due stadi: generazione testuale + conversione in codice.
"""

from llm_utils import query_ollama, query_ollama_fast, get_model_speed_ranking, get_optimal_timeout, estimate_prompt_complexity
from .two_stage_generator import TwoStageGenerator
import re

class GeneratorAgent:
    def __init__(self, default_model: str = "phi3"):
        self.default_model = default_model
        self.fast_models = get_model_speed_ranking()
        self.two_stage_generator = TwoStageGenerator(
            text_model="phi3:mini",
            code_model="mistral:7b-instruct-q4_0"
        )

    def generate_strategy(self, prompt: str, model: str | None = None, timeout: int | None = None, use_hybrid: bool = True, strategy_name: str | None = None) -> str:
        """
        Genera una nuova strategia FreqTrade usando approccio a due stadi.
        
        Args:
            prompt: Il prompt per la generazione
            model: Il modello da utilizzare (default: phi3 per velocità)
            timeout: Timeout in secondi (ignorato nel sistema a due stadi)
            use_hybrid: Se True, usa approccio a due stadi (default: True)
            strategy_name: Nome della classe strategia (se None, viene estratto dal prompt)
        """
        # Estrai il nome della strategia se non fornito
        if strategy_name is None:
            strategy_name = self._extract_strategy_name(prompt)
        
        # Estrai il tipo di strategia dal prompt
        strategy_type = self._extract_strategy_type(prompt)
        
        print(f"🔄 Generazione strategia {strategy_type} con sistema a due stadi...")
        
        try:
            # Usa il sistema a due stadi
            result = self.two_stage_generator.generate_strategy(
                strategy_type=strategy_type,
                complexity="normal",
                style="technical",
                randomization=0.3,
                strategy_name=strategy_name
            )
            
            return result['code']
            
        except Exception as e:
            print(f"❌ Errore nel sistema a due stadi: {e}")
            print("🔄 Fallback al sistema legacy...")
            return self._generate_fallback_strategy(strategy_name)
    
    def _extract_strategy_type(self, prompt: str) -> str:
        """Estrae il tipo di strategia dal prompt."""
        strategy_types = ['volatility', 'scalping', 'momentum', 'breakout', 'adaptive']
        
        for strategy_type in strategy_types:
            if strategy_type in prompt.lower():
                return strategy_type
        
        return "volatility"  # Default
    
    def generate_adaptive_strategy(self, 
                                 strategy_type: str = "volatility",
                                 model: str | None = None,
                                 complexity: str = "normal",
                                 style: str = "technical",
                                 randomization: float = 0.3,
                                 use_hybrid: bool = True,
                                 strategy_name: str = None) -> str:
        """
        Genera una strategia usando il sistema di prompt adattivi.
        
        Args:
            strategy_type: Tipo di strategia ("volatility", "scalping", "breakout", "momentum", "adaptive")
            model: Il modello da utilizzare
            complexity: Livello di complessità ("simple", "normal", "complex")
            style: Stile del prompt ("technical", "creative", "conservative", "aggressive")
            randomization: Livello di randomizzazione (0.0-1.0)
            use_hybrid: Se True, usa approccio ibrido
            strategy_name: Nome della classe strategia
            
        Returns:
            Codice della strategia generata
        """
        try:
            from prompts.adaptive_prompt_generator import generate_adaptive_prompt
            
            # Genera prompt adattivo
            adaptive_prompt = generate_adaptive_prompt(
                strategy_type=strategy_type,
                model=model or self.default_model,
                complexity=complexity,
                style=style,
                randomization=randomization
            )
            
            print(f"🎯 Generazione strategia {strategy_type} con prompt adattivo:")
            print(f"   Modello: {model or self.default_model}")
            print(f"   Complessità: {complexity}")
            print(f"   Stile: {style}")
            print(f"   Randomizzazione: {randomization}")
            print(f"   Lunghezza prompt: {len(adaptive_prompt)} caratteri")
            
            # Genera strategia con prompt adattivo
            return self.generate_strategy(
                prompt=adaptive_prompt,
                model=model,
                timeout=None,  # Calcolato automaticamente
                use_hybrid=use_hybrid,
                strategy_name=strategy_name or f"{strategy_type.capitalize()}Strategy"
            )
            
        except ImportError:
            print("⚠️ Sistema prompt adattivi non disponibile, uso prompt standard")
            return self.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
        except Exception as e:
            print(f"❌ Errore nella generazione adattiva: {e}")
            return self.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
    
    def generate_simple_strategy(self, strategy_type: str = "volatility", model: str | None = None, strategy_name: str = None) -> str:
        """
        Genera una strategia semplice usando prompt adattivi.
        """
        return self.generate_adaptive_strategy(
            strategy_type=strategy_type,
            model=model,
            complexity="simple",
            style="technical",
            randomization=0.1,
            strategy_name=strategy_name
        )
    
    def generate_complex_strategy(self, strategy_type: str = "volatility", model: str | None = None, strategy_name: str = None) -> str:
        """
        Genera una strategia complessa usando prompt adattivi.
        """
        return self.generate_adaptive_strategy(
            strategy_type=strategy_type,
            model=model,
            complexity="complex",
            style="technical",
            randomization=0.2,
            strategy_name=strategy_name
        )
    
    def generate_random_strategy(self, strategy_type: str = "volatility", model: str | None = None, strategy_name: str = None) -> str:
        """
        Genera una strategia con prompt casuale usando prompt adattivi.
        """
        return self.generate_adaptive_strategy(
            strategy_type=strategy_type,
            model=model,
            complexity="normal",
            style="creative",
            randomization=0.9,
            strategy_name=strategy_name
        )
    
    def generate_strategy_ensemble(self, strategy_type: str = "volatility", models: list = None, strategy_name: str = None) -> str:
        """
        Genera un ensemble di strategie usando diversi prompt adattivi.
        
        Args:
            strategy_type: Tipo di strategia
            models: Lista di modelli da usare (se None, usa modelli veloci)
            strategy_name: Nome della classe strategia
            
        Returns:
            Strategia migliore dell'ensemble
        """
        if models is None:
            models = self.fast_models[:3]  # Usa i 3 modelli più veloci
        
        print(f"🎭 Generazione ensemble per {strategy_type} con {len(models)} modelli")
        
        strategies = []
        
        # Genera strategie con diversi approcci
        approaches = [
            ("simple", "technical", 0.1),
            ("normal", "creative", 0.5),
            ("complex", "aggressive", 0.3)
        ]
        
        for i, (complexity, style, randomization) in enumerate(approaches):
            model = models[i % len(models)]
            try:
                strategy = self.generate_adaptive_strategy(
                    strategy_type=strategy_type,
                    model=model,
                    complexity=complexity,
                    style=style,
                    randomization=randomization,
                    strategy_name=f"{strategy_name or strategy_type.capitalize()}Ensemble{i+1}"
                )
                strategies.append({
                    'model': model,
                    'complexity': complexity,
                    'style': style,
                    'randomization': randomization,
                    'code': strategy
                })
                print(f"✅ Strategia {i+1} generata con {model} ({complexity}, {style})")
            except Exception as e:
                print(f"❌ Errore con strategia {i+1}: {e}")
        
        if not strategies:
            print("❌ Nessuna strategia generata, fallback a strategia standard")
            return self.generate_futures_strategy(strategy_type, True, strategy_name)
        
        # Per ora restituisce la prima strategia valida
        # In futuro potrebbe fare una sintesi delle migliori
        print(f"🏆 Ensemble completato: {len(strategies)} strategie generate")
        return strategies[0]['code']
    
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
    
    def generate_futures_strategy(self, strategy_type: str = "volatility", use_hybrid: bool = True, strategy_name: str | None = None) -> str:
        """
        Genera una strategia specifica per futures crypto usando sistema a due stadi.
        
        Args:
            strategy_type: Tipo di strategia ("volatility", "scalping", "breakout", "momentum", "adaptive")
            use_hybrid: Se True, usa approccio a due stadi
            strategy_name: Nome della classe strategia
            
        Returns:
            Codice della strategia generata
        """
        if strategy_name is None:
            strategy_name = f"{strategy_type.capitalize()}Strategy"
        
        print(f"🚀 Generazione strategia futures {strategy_type} con sistema a due stadi...")
        
        try:
            # Usa il sistema a due stadi
            result = self.two_stage_generator.generate_strategy(
                strategy_type=strategy_type,
                complexity="normal",
                style="technical",
                randomization=0.3,
                strategy_name=strategy_name
            )
            
            return result['code']
            
        except Exception as e:
            print(f"❌ Errore nel sistema a due stadi: {e}")
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
'''
    
    def _get_default_futures_strategy(self, strategy_type: str, strategy_name: str) -> str:
        """
        Restituisce una strategia futures di default.
        """
            return self._get_default_strategy(strategy_name) 