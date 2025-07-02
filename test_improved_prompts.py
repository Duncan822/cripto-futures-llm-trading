#!/usr/bin/env python3
"""
Script per testare la generazione di strategie con i prompt migliorati.
Confronta le strategie vecchie vs nuove per vedere i miglioramenti.
"""

import os
import sys
from datetime import datetime

def test_improved_prompts():
    """
    Testa la generazione di strategie con i prompt migliorati.
    """
    print("🧪 Test generazione strategie con prompt migliorati")
    print("=" * 60)
    
    try:
        from agents.generator import GeneratorAgent
        from prompts.improved_futures_prompts import (
            get_improved_scalping_prompt,
            get_improved_momentum_prompt,
            get_improved_breakout_prompt,
            get_improved_volatility_prompt
        )
        
        generator = GeneratorAgent()
        
        # Testa ogni tipo di strategia
        strategy_types = [
            ("scalping", "ScalpingStrategy_improved_test"),
            ("momentum", "MomentumStrategy_improved_test"),
            ("breakout", "BreakoutStrategy_improved_test"),
            ("volatility", "VolatilityStrategy_improved_test")
        ]
        
        generated_strategies = []
        
        for strategy_type, strategy_name in strategy_types:
            print(f"\n🔧 Test generazione {strategy_type.upper()}")
            print("-" * 40)
            
            try:
                # Genera la strategia
                strategy_code = generator.generate_futures_strategy(
                    strategy_type=strategy_type,
                    strategy_name=strategy_name
                )
                
                # Salva la strategia
                strategy_file = f"user_data/strategies/{strategy_name}.py"
                with open(strategy_file, 'w') as f:
                    f.write(strategy_code)
                
                generated_strategies.append(strategy_name)
                print(f"  ✅ Generata: {strategy_name}")
                
                # Analizza la strategia generata
                analyze_strategy(strategy_code, strategy_type)
                
            except Exception as e:
                print(f"  ❌ Errore generazione {strategy_type}: {e}")
        
        print(f"\n📊 Risultati test:")
        print(f"  • Strategie generate: {len(generated_strategies)}/{len(strategy_types)}")
        print(f"  • File salvati in: user_data/strategies/")
        
        if generated_strategies:
            print(f"\n💡 Prossimi passi:")
            print(f"   1. Testa le strategie: ./manage_background_agent.sh backtest")
            print(f"   2. Confronta con le vecchie strategie")
            print(f"   3. Ottimizza le migliori")
        
    except ImportError as e:
        print(f"❌ Errore importazione: {e}")
        print("Assicurati che tutti i moduli siano disponibili")

def analyze_strategy(strategy_code: str, strategy_type: str):
    """
    Analizza una strategia generata per verificare i miglioramenti.
    """
    print(f"  📋 Analisi strategia {strategy_type}:")
    
    # Controlla parametri chiave
    checks = {
        "timeframe": False,
        "roi_conservative": False,
        "stoploss_conservative": False,
        "trailing_stop": False,
        "multiple_indicators": False,
        "custom_stoploss": False,
        "confirm_trade_entry": False,
        "optimizable_params": False
    }
    
    # Controlla timeframe
    if "timeframe = \"15m\"" in strategy_code or "timeframe = \"1h\"" in strategy_code or "timeframe = \"4h\"" in strategy_code:
        checks["timeframe"] = True
    
    # Controlla ROI conservativo
    if "0.10" in strategy_code or "0.15" in strategy_code or "0.20" in strategy_code:
        checks["roi_conservative"] = True
    
    # Controlla stop loss conservativo
    if "-0.03" in strategy_code or "-0.04" in strategy_code or "-0.05" in strategy_code:
        checks["stoploss_conservative"] = True
    
    # Controlla trailing stop
    if "trailing_stop = True" in strategy_code:
        checks["trailing_stop"] = True
    
    # Controlla indicatori multipli
    indicators = ["RSI", "EMA", "MACD", "BBANDS", "ATR", "Volume"]
    indicator_count = sum(1 for ind in indicators if ind in strategy_code)
    if indicator_count >= 4:
        checks["multiple_indicators"] = True
    
    # Controlla funzioni avanzate
    if "custom_stoploss" in strategy_code:
        checks["custom_stoploss"] = True
    
    if "confirm_trade_entry" in strategy_code:
        checks["confirm_trade_entry"] = True
    
    # Controlla parametri ottimizzabili
    if "IntParameter" in strategy_code or "DecimalParameter" in strategy_code:
        checks["optimizable_params"] = True
    
    # Mostra risultati
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"    {status} {check}")
    
    # Calcola score
    score = sum(checks.values()) / len(checks) * 100
    print(f"  📊 Score: {score:.1f}%")
    
    return score

def compare_with_old_strategies():
    """
    Confronta le nuove strategie con quelle vecchie.
    """
    print(f"\n🔄 Confronto con strategie vecchie")
    print("-" * 40)
    
    # Trova le strategie vecchie
    old_strategies = []
    if os.path.exists("strategies_backup_20250701_225941"):
        backup_dir = "strategies_backup_20250701_225941"
        for file in os.listdir(backup_dir):
            if file.endswith('.py'):
                old_strategies.append(file)
    
    if old_strategies:
        print(f"  📦 Strategie vecchie trovate: {len(old_strategies)}")
        for strategy in old_strategies[:3]:  # Mostra solo le prime 3
            print(f"    • {strategy}")
        
        print(f"\n💡 Differenze principali:")
        print(f"    • Timeframe: 5m → 15m/1h/4h")
        print(f"    • ROI: 5% → 10-20%")
        print(f"    • Stop loss: 2% → 3-5%")
        print(f"    • Indicatori: 1-2 → 5-6")
        print(f"    • Filtri: Nessuno → Multipli")
        print(f"    • Gestione rischio: Base → Avanzata")
    else:
        print(f"  ⚠️ Nessuna strategia vecchia trovata per confronto")

if __name__ == "__main__":
    test_improved_prompts()
    compare_with_old_strategies() 