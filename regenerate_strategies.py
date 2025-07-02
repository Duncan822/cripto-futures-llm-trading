#!/usr/bin/env python3
"""
Script per rigenerare le strategie esistenti con parametri migliorati.
Risolve i problemi identificati nel backtest precedente.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, Any, List

def regenerate_strategies():
    """
    Rigenera le strategie esistenti con parametri migliorati.
    """
    print("🚀 Rigenerazione strategie con parametri migliorati")
    print("=" * 60)
    
    # Carica le strategie esistenti
    try:
        with open('strategies_metadata.json', 'r') as f:
            strategies = json.load(f)
    except FileNotFoundError:
        print("❌ File strategies_metadata.json non trovato")
        return
    
    print(f"📊 Trovate {len(strategies)} strategie da rigenerare")
    
    # Backup delle strategie esistenti
    backup_dir = f"strategies_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Sposta le strategie esistenti nel backup
    strategies_dir = "user_data/strategies"
    if os.path.exists(strategies_dir):
        for file in os.listdir(strategies_dir):
            if file.endswith('.py'):
                src = os.path.join(strategies_dir, file)
                dst = os.path.join(backup_dir, file)
                shutil.move(src, dst)
                print(f"  📦 Backup: {file}")
    
    # Genera nuove strategie con parametri migliorati
    from agents.generator import GeneratorAgent
    
    generator = GeneratorAgent()
    
    # Parametri migliorati per ogni tipo di strategia
    improved_params = {
        "scalping": {
            "timeframe": "15m",  # Invece di 5m
            "roi": {
                "0": 0.10,      # 10% invece di 5%
                "60": 0.05,     # 5% dopo 1 ora
                "120": 0.03,    # 3% dopo 2 ore
                "240": 0.02,    # 2% dopo 4 ore
                "480": 0.01     # 1% dopo 8 ore
            },
            "stoploss": -0.03,  # 3% invece di 2%
            "trailing_stop_positive": 0.02,
            "trailing_stop_positive_offset": 0.03,
            "indicators": ["RSI", "EMA", "MACD", "BBANDS", "VOLUME"]
        },
        "momentum": {
            "timeframe": "1h",   # Timeframe più lungo
            "roi": {
                "0": 0.15,      # 15% invece di 10%
                "120": 0.08,    # 8% dopo 2 ore
                "240": 0.05,    # 5% dopo 4 ore
                "480": 0.03,    # 3% dopo 8 ore
                "720": 0.02     # 2% dopo 12 ore
            },
            "stoploss": -0.04,  # 4% invece di 3%
            "trailing_stop_positive": 0.03,
            "trailing_stop_positive_offset": 0.04,
            "indicators": ["RSI", "EMA", "MACD", "STOCH", "ADX"]
        },
        "volatility": {
            "timeframe": "30m",  # Timeframe intermedio
            "roi": {
                "0": 0.12,      # 12% invece di 8%
                "90": 0.06,     # 6% dopo 1.5 ore
                "180": 0.04,    # 4% dopo 3 ore
                "360": 0.025,   # 2.5% dopo 6 ore
                "720": 0.015    # 1.5% dopo 12 ore
            },
            "stoploss": -0.035, # 3.5% invece di 2.5%
            "trailing_stop_positive": 0.025,
            "trailing_stop_positive_offset": 0.035,
            "indicators": ["BBANDS", "ATR", "RSI", "EMA", "VOLUME"]
        },
        "breakout": {
            "timeframe": "4h",   # Timeframe lungo per breakout
            "roi": {
                "0": 0.20,      # 20% invece di 15%
                "240": 0.10,    # 10% dopo 4 ore
                "480": 0.06,    # 6% dopo 8 ore
                "720": 0.04,    # 4% dopo 12 ore
                "1440": 0.025   # 2.5% dopo 24 ore
            },
            "stoploss": -0.05,  # 5% invece di 3%
            "trailing_stop_positive": 0.04,
            "trailing_stop_positive_offset": 0.05,
            "indicators": ["BBANDS", "SUPPORT_RESISTANCE", "VOLUME", "RSI", "EMA"]
        }
    }
    
    # Genera nuove strategie per ogni tipo
    for strategy_type, params in improved_params.items():
        print(f"\n🔧 Generazione strategia {strategy_type.upper()}")
        
        # Genera 2-3 strategie per tipo con parametri leggermente diversi
        for i in range(3):
            # Varia leggermente i parametri
            modified_params = params.copy()
            modified_params["roi"] = {
                k: v * (1 + (i - 1) * 0.1)  # ±10% variazione
                for k, v in params["roi"].items()
            }
            modified_params["stoploss"] = params["stoploss"] * (1 + (i - 1) * 0.1)
            
            try:
                strategy_name = f"{strategy_type.capitalize()}Strategy_improved_v{i+1}"
                generator.generate_futures_strategy(
                    strategy_type=strategy_type,
                    strategy_name=strategy_name
                )
                print(f"  ✅ Generata: {strategy_name}")
            except Exception as e:
                print(f"  ❌ Errore generazione {strategy_type}: {e}")
    
    # Aggiorna i metadati
    print(f"\n📝 Aggiornamento metadati...")
    
    # Rimuovi le strategie vecchie dai metadati
    old_strategies = list(strategies.keys())
    for strategy_name in old_strategies:
        del strategies[strategy_name]
    
    # Aggiungi le nuove strategie
    new_strategies = []
    for file in os.listdir(strategies_dir):
        if file.endswith('.py') and 'improved' in file:
            strategy_name = file.replace('.py', '')
            strategies[strategy_name] = {
                "created_at": datetime.now().isoformat(),
                "model_used": "improved_template",
                "strategy_type": strategy_name.split('_')[0].lower(),
                "validation_status": "pending",
                "backtest_score": None,
                "last_backtest": None,
                "optimization_status": "pending",
                "improvements": [
                    "ROI più conservativo",
                    "Stop loss più ampio", 
                    "Timeframe più lungo",
                    "Più indicatori tecnici",
                    "Filtri di trend",
                    "Stop loss dinamico"
                ]
            }
            new_strategies.append(strategy_name)
    
    # Salva i metadati aggiornati
    with open('strategies_metadata.json', 'w') as f:
        json.dump(strategies, f, indent=2)
    
    print(f"✅ Rigenerate {len(new_strategies)} strategie migliorate")
    print(f"📦 Backup delle strategie vecchie in: {backup_dir}")
    
    # Mostra le nuove strategie
    print(f"\n📋 Nuove strategie generate:")
    for strategy in new_strategies:
        print(f"  • {strategy}")
    
    print(f"\n💡 Prossimi passi:")
    print(f"   1. Testa le nuove strategie: ./manage_background_agent.sh backtest")
    print(f"   2. Ottimizza le migliori: ./manage_background_agent.sh optimize")
    print(f"   3. Monitora i risultati: ./manage_background_agent.sh status")

if __name__ == "__main__":
    regenerate_strategies() 