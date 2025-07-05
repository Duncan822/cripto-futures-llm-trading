#!/usr/bin/env python3
"""
Test specifico per il Code Fixer.
"""

from agents.code_fixer import CodeFixer

def test_code_fixer():
    """
    Test del code fixer con codice problematico.
    """
    
    # Codice problematico con errori di indentazione tipici
    problematic_code = '''
class TestStrategy(IStrategy):
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
'''

    print("🔧 Test del Code Fixer")
    print("=" * 50)
    
    fixer = CodeFixer()
    result = fixer.fix_python_code(problematic_code)
    
    print(f"✅ Codice valido: {result['is_valid']}")
    print(f"🔧 Fix applicati: {result['fix_count']}")
    
    if result['fixes_applied']:
        print("\n📋 Fix applicati:")
        for fix in result['fixes_applied']:
            print(f"   - {fix}")
    
    if result['is_valid']:
        print("\n🎉 Test completato con successo!")
        print("\n📝 Codice corretto:")
        print("=" * 50)
        print(result['fixed_code'])
    else:
        print(f"\n❌ Errore: {result['error_msg']}")
    
    return result['is_valid']

if __name__ == "__main__":
    success = test_code_fixer()
    if success:
        print("\n✅ TUTTI I TEST PASSATI!")
    else:
        print("\n❌ TEST FALLITI!")