#!/usr/bin/env python3
"""
Esempio di utilizzo dell'approccio ibrido per la generazione di strategie FreqTrade.
Dimostra entrambi i metodi: generazione diretta e conversione testuale.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.generator import GeneratorAgent
from agents.strategy_converter import StrategyConverter

def example_direct_generation():
    """Esempio di generazione diretta di codice."""
    print("=" * 60)
    print("🔄 ESEMPIO: Generazione Diretta di Codice")
    print("=" * 60)
    
    generator = GeneratorAgent(default_model="phi3")
    
    prompt = """
    Genera una strategia FreqTrade per trading di futures crypto che:
    - Usa RSI per identificare condizioni di ipercomprato/ipervenduto
    - Utilizza EMA crossover per confermare il trend
    - Include MACD per segnali di momentum
    - Ha stop loss dinamico basato su ATR
    - Supporta operazioni long e short
    - È ottimizzata per timeframe 5m
    """
    
    try:
        strategy_code = generator.generate_strategy(prompt, use_hybrid=False)
        print("✅ Strategia generata direttamente:")
        print(strategy_code[:500] + "..." if len(strategy_code) > 500 else strategy_code)
        
        # Salva la strategia
        with open("user_data/strategies/direct_generated_strategy.py", "w") as f:
            f.write(strategy_code)
        print("💾 Strategia salvata in user_data/strategies/direct_generated_strategy.py")
        
    except Exception as e:
        print(f"❌ Errore nella generazione diretta: {e}")

def example_text_to_code_conversion():
    """Esempio di conversione da testo a codice."""
    print("\n" + "=" * 60)
    print("🔄 ESEMPIO: Conversione Testo → Codice")
    print("=" * 60)
    
    converter = StrategyConverter()
    
    text_description = """
    Strategia di trading per futures crypto:
    
    Indicatori: RSI, EMA, MACD, Bollinger Bands, ATR
    
    Condizioni di entrata:
    - Entra long quando RSI è sotto 30 (ipervenduto) e EMA corta è sopra EMA lunga
    - Entra short quando RSI è sopra 70 (ipercomprato) e EMA corta è sotto EMA lunga
    - Conferma con MACD che deve essere sopra/basso la sua media
    
    Condizioni di uscita:
    - Esci long quando RSI sale sopra 70 o EMA crossover diventa negativo
    - Esci short quando RSI scende sotto 30 o EMA crossover diventa positivo
    
    Gestione rischio:
    - Stop loss del 2% fisso
    - Take profit del 5% con trailing stop
    - Timeframe 5 minuti per operazioni veloci
    """
    
    try:
        strategy_code = converter.convert_text_to_strategy(text_description)
        print("✅ Strategia convertita da testo:")
        print(strategy_code[:500] + "..." if len(strategy_code) > 500 else strategy_code)
        
        # Salva la strategia
        with open("user_data/strategies/text_converted_strategy.py", "w") as f:
            f.write(strategy_code)
        print("💾 Strategia salvata in user_data/strategies/text_converted_strategy.py")
        
    except Exception as e:
        print(f"❌ Errore nella conversione: {e}")

def example_hybrid_approach():
    """Esempio dell'approccio ibrido."""
    print("\n" + "=" * 60)
    print("🔄 ESEMPIO: Approccio Ibrido")
    print("=" * 60)
    
    generator = GeneratorAgent(default_model="phi3")
    
    prompt = """
    Crea una strategia di breakout per futures crypto che:
    - Identifica rotture di supporto/resistenza usando Bollinger Bands
    - Usa volume per confermare i breakout
    - Include gestione della volatilità con ATR
    - Ha stop loss dinamici e trailing stop
    - Supporta scalping su timeframe 1m
    """
    
    try:
        strategy_code = generator.generate_strategy(prompt, use_hybrid=True)
        print("✅ Strategia generata con approccio ibrido:")
        print(strategy_code[:500] + "..." if len(strategy_code) > 500 else strategy_code)
        
        # Salva la strategia
        with open("user_data/strategies/hybrid_strategy.py", "w") as f:
            f.write(strategy_code)
        print("💾 Strategia salvata in user_data/strategies/hybrid_strategy.py")
        
    except Exception as e:
        print(f"❌ Errore nell'approccio ibrido: {e}")

def example_code_validation():
    """Esempio di validazione e correzione del codice."""
    print("\n" + "=" * 60)
    print("🔄 ESEMPIO: Validazione e Correzione Codice")
    print("=" * 60)
    
    converter = StrategyConverter()
    
    # Codice con errori
    invalid_code = """
    class BadStrategy:
        def populate_indicators(self, dataframe):
            dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
            return dataframe
        
        def populate_entry_trend(self, dataframe):
            dataframe.loc[dataframe['rsi'] < 30, 'enter_long'] = 1
            return dataframe
    """
    
    print("📝 Codice originale (con errori):")
    print(invalid_code)
    
    try:
        fixed_code = converter.validate_and_fix_code(invalid_code)
        print("\n✅ Codice corretto:")
        print(fixed_code[:500] + "..." if len(fixed_code) > 500 else fixed_code)
        
    except Exception as e:
        print(f"❌ Errore nella correzione: {e}")

def example_futures_strategy():
    """Esempio di generazione di strategia futures specifica."""
    print("\n" + "=" * 60)
    print("🔄 ESEMPIO: Strategia Futures Specifica")
    print("=" * 60)
    
    generator = GeneratorAgent(default_model="phi3")
    
    try:
        # Genera strategia di volatilità
        strategy_code = generator.generate_futures_strategy("volatility", use_hybrid=True)
        print("✅ Strategia futures di volatilità:")
        print(strategy_code[:500] + "..." if len(strategy_code) > 500 else strategy_code)
        
        # Salva la strategia
        with open("user_data/strategies/futures_volatility_strategy.py", "w") as f:
            f.write(strategy_code)
        print("💾 Strategia salvata in user_data/strategies/futures_volatility_strategy.py")
        
    except Exception as e:
        print(f"❌ Errore nella generazione futures: {e}")

def main():
    """Esegue tutti gli esempi."""
    print("🚀 DEMO: Approccio Ibrido per Generazione Strategie FreqTrade")
    print("=" * 80)
    
    # Crea directory se non esiste
    os.makedirs("user_data/strategies", exist_ok=True)
    
    # Esegui esempi
    example_direct_generation()
    example_text_to_code_conversion()
    example_hybrid_approach()
    example_code_validation()
    example_futures_strategy()
    
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETATA!")
    print("📁 Le strategie generate sono state salvate in user_data/strategies/")
    print("\n📊 Confronto degli approcci:")
    print("1. Generazione Diretta: Veloce, ma può generare errori di sintassi")
    print("2. Conversione Testuale: Robusta, ma meno flessibile")
    print("3. Approccio Ibrido: Combina i vantaggi di entrambi")
    print("\n🎯 Raccomandazione: Usa l'approccio ibrido per la massima affidabilità!")

if __name__ == "__main__":
    main() 