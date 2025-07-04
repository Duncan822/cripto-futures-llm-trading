#!/usr/bin/env python3
"""
Test del post-processing automatico delle strategie
"""

import os
import sys
sys.path.append('agents')

from agents.strategy_postprocess import postprocess_strategy

def test_postprocessing():
    """Test del post-processing automatico."""
    print("🧪 TEST POST-PROCESSING AUTOMATICO")
    print("=" * 50)
    
    # Test 1: Strategia con nome classe corretto
    print("\n📝 Test 1: Strategia valida")
    test_code_1 = '''"""
Test Strategy
"""
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class teststrategy(IStrategy):
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
'''
    
    # Salva strategia di test
    test_file = "user_data/strategies/teststrategy.py"
    os.makedirs("user_data/strategies", exist_ok=True)
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code_1)
    
    # Test post-processing
    result = postprocess_strategy(test_file)
    print(f"✅ Risultato: {result}")
    
    # Test 2: Strategia con nome classe sbagliato
    print("\n📝 Test 2: Strategia con nome classe sbagliato")
    test_code_2 = '''"""
Test Strategy
"""
from freqtrade.strategy import IStrategy
import talib.abstract as ta

class WrongName(IStrategy):
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
'''
    
    # Salva strategia di test
    test_file_2 = "user_data/strategies/teststrategy2.py"
    with open(test_file_2, 'w', encoding='utf-8') as f:
        f.write(test_code_2)
    
    # Test post-processing
    result = postprocess_strategy(test_file_2)
    print(f"✅ Risultato: {result}")
    
    # Test 3: Strategia con errore di sintassi
    print("\n📝 Test 3: Strategia con errore di sintassi")
    test_code_3 = '''"""
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
'''
    
    # Salva strategia di test
    test_file_3 = "user_data/strategies/teststrategy3.py"
    with open(test_file_3, 'w', encoding='utf-8') as f:
        f.write(test_code_3)
    
    # Test post-processing
    result = postprocess_strategy(test_file_3)
    print(f"✅ Risultato: {result}")
    
    # Verifica file finali
    print("\n📁 Verifica file finali:")
    strategies_dir = "user_data/strategies"
    broken_dir = "user_data/strategies_broken"
    
    print(f"Strategie valide in {strategies_dir}:")
    for file in os.listdir(strategies_dir):
        if file.endswith('.py') and not file.startswith('_'):
            print(f"  ✅ {file}")
    
    if os.path.exists(broken_dir):
        print(f"\nStrategie non valide in {broken_dir}:")
        for file in os.listdir(broken_dir):
            if file.endswith('.py'):
                print(f"  ❌ {file}")
    
    print("\n🎉 Test completato!")

if __name__ == "__main__":
    test_postprocessing() 