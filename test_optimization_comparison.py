#!/usr/bin/env python3
"""
Test di confronto tra diversi approcci di ottimizzazione:
1. LLM solo (phi3)
2. LLM avanzato (cogito:8b)
3. Hyperopt + LLM (combinato)
"""

import os
import sys
import json
import time
from datetime import datetime

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.optimizer import OptimizerAgent
from agents.hyperopt_optimizer import HyperoptLLMOptimizer

def test_llm_optimization_phi3():
    """Testa ottimizzazione con phi3."""
    print("🧪 Test Ottimizzazione LLM (phi3)...")
    
    optimizer = OptimizerAgent(default_model="phi3")
    
    # Strategia di test
    test_strategy = '''
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter

class TestStrategy(IStrategy):
    minimal_roi = {"0": 0.1}
    stoploss = -0.05
    timeframe = '5m'
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['sma'] = dataframe['close'].rolling(window=20).mean()
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['enter_long'] = (dataframe['close'] > dataframe['sma'])
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['exit_long'] = (dataframe['close'] < dataframe['sma'])
        return dataframe
'''
    
    backtest_results = {
        'total_return': 0.05,
        'sharpe_ratio': 0.8,
        'max_drawdown': 0.12,
        'win_rate': 0.35,
        'total_trades': 15
    }
    
    start_time = time.time()
    result = optimizer.optimize_strategy(test_strategy, backtest_results, "TestStrategy")
    end_time = time.time()
    
    print(f"✅ Completato in {end_time - start_time:.1f} secondi")
    print(f"   Miglioramenti: {len(result.improvements)}")
    print(f"   Successo: {result.success}")
    
    return result, end_time - start_time

def test_llm_optimization_cogito8b():
    """Testa ottimizzazione con cogito:8b."""
    print("\n🧪 Test Ottimizzazione LLM (cogito:8b)...")
    
    optimizer = OptimizerAgent(default_model="cogito:8b")
    
    # Stessa strategia di test
    test_strategy = '''
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter

class TestStrategy(IStrategy):
    minimal_roi = {"0": 0.1}
    stoploss = -0.05
    timeframe = '5m'
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['sma'] = dataframe['close'].rolling(window=20).mean()
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['enter_long'] = (dataframe['close'] > dataframe['sma'])
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['exit_long'] = (dataframe['close'] < dataframe['sma'])
        return dataframe
'''
    
    backtest_results = {
        'total_return': 0.05,
        'sharpe_ratio': 0.8,
        'max_drawdown': 0.12,
        'win_rate': 0.35,
        'total_trades': 15
    }
    
    start_time = time.time()
    result = optimizer.optimize_strategy(test_strategy, backtest_results, "TestStrategy")
    end_time = time.time()
    
    print(f"✅ Completato in {end_time - start_time:.1f} secondi")
    print(f"   Miglioramenti: {len(result.improvements)}")
    print(f"   Successo: {result.success}")
    
    return result, end_time - start_time

def test_hyperopt_llm_optimization():
    """Testa ottimizzazione combinata Hyperopt + LLM."""
    print("\n🧪 Test Ottimizzazione Hyperopt + LLM...")
    
    try:
        optimizer = HyperoptLLMOptimizer(default_model="cogito:8b")
        
        # Stessa strategia di test
        test_strategy = '''
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter

class TestStrategy(IStrategy):
    minimal_roi = {"0": 0.1}
    stoploss = -0.05
    timeframe = '5m'
    
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['sma'] = dataframe['close'].rolling(window=20).mean()
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['enter_long'] = (dataframe['close'] > dataframe['sma'])
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['exit_long'] = (dataframe['close'] < dataframe['sma'])
        return dataframe
'''
        
        backtest_results = {
            'total_return': 0.05,
            'sharpe_ratio': 0.8,
            'max_drawdown': 0.12,
            'win_rate': 0.35,
            'total_trades': 15
        }
        
        start_time = time.time()
        result = optimizer.optimize_strategy(test_strategy, backtest_results, "TestStrategy")
        end_time = time.time()
        
        print(f"✅ Completato in {end_time - start_time:.1f} secondi")
        print(f"   Miglioramenti LLM: {len(result.llm_improvements)}")
        print(f"   Successo Hyperopt: {result.hyperopt_result.success}")
        print(f"   Successo totale: {result.success}")
        
        return result, end_time - start_time
        
    except Exception as e:
        print(f"❌ Errore nel test Hyperopt + LLM: {e}")
        return None, 0

def compare_optimization_methods():
    """Confronta i diversi metodi di ottimizzazione."""
    print("🚀 CONFRONTO METODI DI OTTIMIZZAZIONE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: LLM phi3
    try:
        result_phi3, time_phi3 = test_llm_optimization_phi3()
        results['phi3'] = {
            'result': result_phi3,
            'time': time_phi3,
            'improvements': len(result_phi3.improvements) if result_phi3.success else 0
        }
    except Exception as e:
        print(f"❌ Errore test phi3: {e}")
        results['phi3'] = {'error': str(e)}
    
    # Test 2: LLM cogito:8b
    try:
        result_cogito, time_cogito = test_llm_optimization_cogito8b()
        results['cogito8b'] = {
            'result': result_cogito,
            'time': time_cogito,
            'improvements': len(result_cogito.improvements) if result_cogito.success else 0
        }
    except Exception as e:
        print(f"❌ Errore test cogito:8b: {e}")
        results['cogito8b'] = {'error': str(e)}
    
    # Test 3: Hyperopt + LLM
    try:
        result_combined, time_combined = test_hyperopt_llm_optimization()
        if result_combined:
            results['hyperopt_llm'] = {
                'result': result_combined,
                'time': time_combined,
                'improvements': len(result_combined.llm_improvements) if result_combined.success else 0,
                'hyperopt_success': result_combined.hyperopt_result.success
            }
        else:
            results['hyperopt_llm'] = {'error': 'Test fallito'}
    except Exception as e:
        print(f"❌ Errore test Hyperopt + LLM: {e}")
        results['hyperopt_llm'] = {'error': str(e)}
    
    # Riepilogo
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO CONFRONTO")
    print("=" * 60)
    
    for method, data in results.items():
        print(f"\n🔧 {method.upper()}:")
        if 'error' in data:
            print(f"   ❌ Errore: {data['error']}")
        else:
            print(f"   ⏱️ Tempo: {data['time']:.1f} secondi")
            print(f"   🎯 Miglioramenti: {data['improvements']}")
            if method == 'hyperopt_llm' and 'hyperopt_success' in data:
                print(f"   ⚙️ Hyperopt: {'✅' if data['hyperopt_success'] else '❌'}")
    
    # Raccomandazione
    print("\n" + "=" * 60)
    print("💡 RACCOMANDAZIONE")
    print("=" * 60)
    
    if 'cogito8b' in results and 'error' not in results['cogito8b']:
        print("✅ RACCOMANDATO: cogito:8b per ottimizzazione")
        print("   - Più accurato di phi3")
        print("   - Analisi più approfondita")
        print("   - Suggerimenti migliori")
    elif 'phi3' in results and 'error' not in results['phi3']:
        print("✅ RACCOMANDATO: phi3 per ottimizzazione")
        print("   - Veloce e affidabile")
        print("   - Buon compromesso velocità/qualità")
    
    if 'hyperopt_llm' in results and 'error' not in results['hyperopt_llm']:
        print("\n🔧 OPZIONE AVANZATA: Hyperopt + LLM")
        print("   - Ottimizzazione numerica + logica")
        print("   - Più completo ma più lento")
        print("   - Ideale per strategie complesse")

def main():
    """Funzione principale."""
    compare_optimization_methods()

if __name__ == "__main__":
    main() 