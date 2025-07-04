#!/usr/bin/env python3
"""
Script per eseguire backtest solo delle strategie valide
"""

import os
import json
import subprocess
import glob
from datetime import datetime
from typing import List, Dict, Set

def get_valid_strategies() -> List[str]:
    """Ottiene solo le strategie valide."""
    valid_strategies = [
        "volatilitystrategy_20250704_100639",
        "scalpingstrategy_mistral_7b_instruct_q4_0_20250704_092117", 
        "contest_cogito_8b_scalping",
        "testnewsystem",
        "ScalpingStrategy_improved_test",
        "testtimeoutoptimized",
        "volatilitystrategy_cooperative_20250703_184333",
        "testllmstrategy"
    ]
    return valid_strategies

def get_backtested_strategies() -> Set[str]:
    """Ottiene l'elenco delle strategie già backtestate."""
    backtest_dir = "user_data/backtest_results"
    if not os.path.exists(backtest_dir):
        return set()
    
    backtested = set()
    
    # Controlla i file .json di backtest
    for file_path in glob.glob(os.path.join(backtest_dir, "*.json")):
        if file_path.endswith('.meta.json'):
            continue
        
        filename = os.path.basename(file_path)
        if filename.startswith('backtest-'):
            # Estrai il nome della strategia dal filename
            strategy_name = filename.replace('backtest-', '').split('-')[0]
            backtested.add(strategy_name)
    
    return backtested

def run_backtest_for_strategy(strategy_name: str) -> bool:
    """Esegue il backtest per una singola strategia."""
    print(f"🔄 Esecuzione backtest per {strategy_name}...")
    
    # Comando per eseguire il backtest
    cmd = [
        "/home/dria10/.pyenv/versions/venv311/bin/freqtrade", "backtesting",
        "--strategy", strategy_name,
        "--timerange", "20240101-20241231",
        "--timeframe", "5m",
        "--pairs", "BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT",
        "--export", "trades",
        "--export-filename", f"user_data/backtest_results/backtest-{strategy_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ]
    
    print(f"📋 Comando: {' '.join(cmd)}")
    
    try:
        # Timeout di 10 minuti per backtest
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"✅ Backtest completato per {strategy_name}")
            return True
        else:
            print(f"❌ Errore backtest per {strategy_name}:")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout per backtest di {strategy_name}")
        return False
    except Exception as e:
        print(f"❌ Errore esecuzione per {strategy_name}: {e}")
        return False

def main():
    """Funzione principale."""
    print("🎯 BACKTEST STRATEGIE VALIDE")
    print("=" * 50)
    
    # Ottieni strategie valide
    valid_strategies = get_valid_strategies()
    print(f"📊 Strategie valide trovate: {len(valid_strategies)}")
    
    # Ottieni strategie già backtestate
    backtested_strategies = get_backtested_strategies()
    print(f"✅ Strategie già testate: {len(backtested_strategies)}")
    
    # Filtra strategie da testare
    strategies_to_test = [s for s in valid_strategies if s not in backtested_strategies]
    print(f"🔄 Strategie da testare: {len(strategies_to_test)}")
    
    if not strategies_to_test:
        print("🎉 Tutte le strategie valide sono già state testate!")
        return
    
    print("📋 Strategie da testare:")
    for i, strategy in enumerate(strategies_to_test, 1):
        print(f"   {i}. {strategy}")
    
    print(f"\n🚀 Inizio backtest di {len(strategies_to_test)} strategie...")
    
    # Esegui backtest
    successful = 0
    failed = 0
    
    for i, strategy in enumerate(strategies_to_test, 1):
        print(f"\n📊 Progresso: {i}/{len(strategies_to_test)}")
        print("-" * 40)
        
        if run_backtest_for_strategy(strategy):
            successful += 1
        else:
            failed += 1
    
    # Riepilogo finale
    print("\n" + "=" * 50)
    print("📊 RIEPILOGO FINALE")
    print("=" * 50)
    print(f"✅ Backtest completati con successo: {successful}")
    print(f"❌ Backtest falliti: {failed}")
    print(f"📈 Tasso di successo: {(successful/(successful+failed)*100):.1f}%")

if __name__ == "__main__":
    main() 