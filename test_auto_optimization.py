#!/usr/bin/env python3
"""
Test script per l'ottimizzazione automatica delle strategie.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from background_agent import BackgroundAgent
from agents.optimizer import OptimizerAgent

def test_optimization_agent():
    """Testa l'Optimizer Agent direttamente."""
    print("🧪 Test Optimizer Agent...")
    
    optimizer = OptimizerAgent()
    
    # Strategia di esempio per il test
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
    
    # Risultati di backtest simulati
    backtest_results = {
        'total_return': 0.05,  # 5% rendimento
        'sharpe_ratio': 0.8,
        'max_drawdown': 0.12,
        'win_rate': 0.35,
        'total_trades': 15
    }
    
    # Esegui ottimizzazione
    result = optimizer.optimize_strategy(test_strategy, backtest_results, "TestStrategy")
    
    print(f"✅ Ottimizzazione completata: {result.success}")
    print(f"   Miglioramenti: {len(result.improvements)}")
    for improvement in result.improvements:
        print(f"   - {improvement}")
    
    return result.success

def test_background_agent_optimization():
    """Testa l'ottimizzazione automatica nel Background Agent."""
    print("\n🧪 Test Background Agent con ottimizzazione...")
    
    agent = BackgroundAgent()
    
    # Mostra stato attuale
    status = agent.get_status()
    print(f"📊 Stato attuale:")
    print(f"   - Strategie totali: {status['total_strategies']}")
    print(f"   - Strategie validate: {status['validated_strategies']}")
    print(f"   - Strategie con backtest: {status['backtested_strategies']}")
    
    # Trova strategie che necessitano ottimizzazione
    min_score = agent.config.get('min_backtest_score', 0.1)
    strategies_to_optimize = []
    
    for name, metadata in agent.strategies_metadata.items():
        if (metadata.backtest_score is not None and 
            metadata.backtest_score < min_score and
            metadata.validation_status == 'validated'):
            strategies_to_optimize.append((name, metadata))
    
    print(f"\n🔧 Strategie che necessitano ottimizzazione: {len(strategies_to_optimize)}")
    
    if strategies_to_optimize:
        # Ordina per punteggio (peggiori prima)
        strategies_to_optimize.sort(key=lambda x: x[1].backtest_score)
        
        print("\n📋 Strategie da ottimizzare:")
        for name, metadata in strategies_to_optimize[:3]:
            print(f"   - {name}: score {metadata.backtest_score:.3f}")
        
        # Testa ottimizzazione automatica
        if strategies_to_optimize:
            test_strategy = strategies_to_optimize[0][0]
            print(f"\n🔧 Test ottimizzazione automatica per: {test_strategy}")
            
            success = agent.optimize_strategy_automatically(test_strategy)
            print(f"✅ Risultato: {'Successo' if success else 'Fallito'}")
    else:
        print("ℹ️ Nessuna strategia necessita ottimizzazione")

def test_optimization_config():
    """Testa la configurazione dell'ottimizzazione."""
    print("\n🧪 Test configurazione ottimizzazione...")
    
    config_file = "background_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        optimization_config = config.get('optimization', {})
        print(f"📋 Configurazione ottimizzazione:")
        print(f"   - Abilitata: {optimization_config.get('enable_hyperopt', False)}")
        print(f"   - Intervallo: {optimization_config.get('optimization_interval', 0)} secondi")
        print(f"   - Epochs: {optimization_config.get('hyperopt_epochs', 0)}")
        
        if optimization_config.get('enable_hyperopt', False):
            print("✅ Ottimizzazione automatica ABILITATA")
        else:
            print("❌ Ottimizzazione automatica DISABILITATA")
    else:
        print("❌ File di configurazione non trovato")

def main():
    """Funzione principale."""
    print("🚀 Test Ottimizzazione Automatica Strategie")
    print("=" * 50)
    
    # Test 1: Optimizer Agent
    test_optimization_agent()
    
    # Test 2: Configurazione
    test_optimization_config()
    
    # Test 3: Background Agent
    test_background_agent_optimization()
    
    print("\n" + "=" * 50)
    print("✅ Test completati!")

if __name__ == "__main__":
    main() 