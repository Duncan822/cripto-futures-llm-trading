#!/usr/bin/env python3
"""
Script per testare diversi scenari di pulizia delle strategie.
Crea strategie di test con età e punteggi diversi per verificare la logica di pulizia.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, TypedDict

class TestScenario(TypedDict):
    should_be_removed: List[str]
    should_stay: List[str]
    expected_behavior: Dict[str, str]

def create_test_metadata():
    """Crea metadati di test con diversi scenari."""
    
    # Configurazione di test
    config = {
        'cleanup_old_strategies': True,
        'min_backtest_score': 0.1,
        'max_strategy_age_days': 30
    }
    
    # Salva configurazione di test
    with open('test_cleanup_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    # Crea strategie di test con diversi scenari
    current_time = datetime.now()
    
    test_strategies = {
        # Scenario 1: Strategia vecchia con buon punteggio (DOVREBBE essere rimossa per età)
        "OldGoodStrategy_phi3_20240501_120000": {
            "name": "OldGoodStrategy_phi3_20240501_120000",
            "file_path": "user_data/strategies/oldgoodstrategy_phi3_20240501_120000.py",
            "strategy_type": "volatility",
            "model_used": "phi3",
            "generation_time": (current_time - timedelta(days=35)).isoformat(),
            "validation_status": "validated",
            "backtest_score": 0.15,
            "last_backtest": (current_time - timedelta(days=30)).isoformat(),
            "is_active": False
        },
        
        # Scenario 2: Strategia nuova con punteggio basso (DOVREBBE essere rimossa per punteggio)
        "NewBadStrategy_llama2_20250629_140000": {
            "name": "NewBadStrategy_llama2_20250629_140000",
            "file_path": "user_data/strategies/newbadstrategy_llama2_20250629_140000.py",
            "strategy_type": "scalping",
            "model_used": "llama2",
            "generation_time": (current_time - timedelta(days=2)).isoformat(),
            "validation_status": "validated",
            "backtest_score": 0.05,
            "last_backtest": (current_time - timedelta(hours=1)).isoformat(),
            "is_active": False
        },
        
        # Scenario 3: Strategia vecchia con punteggio basso (DOVREBBE essere rimossa per entrambi)
        "OldBadStrategy_mistral_20250620_150000": {
            "name": "OldBadStrategy_mistral_20250620_150000",
            "file_path": "user_data/strategies/oldbadstrategy_mistral_20250620_150000.py",
            "strategy_type": "breakout",
            "model_used": "mistral",
            "generation_time": (current_time - timedelta(days=35)).isoformat(),
            "validation_status": "validated",
            "backtest_score": 0.05,
            "last_backtest": (current_time - timedelta(days=30)).isoformat(),
            "is_active": False
        },
        
        # Scenario 4: Strategia nuova con buon punteggio (NON dovrebbe essere rimossa)
        "NewGoodStrategy_phi3_20250629_150000": {
            "name": "NewGoodStrategy_phi3_20250629_150000",
            "file_path": "user_data/strategies/newgoodstrategy_phi3_20250629_150000.py",
            "strategy_type": "momentum",
            "model_used": "phi3",
            "generation_time": (current_time - timedelta(days=1)).isoformat(),
            "validation_status": "validated",
            "backtest_score": 0.12,
            "last_backtest": (current_time - timedelta(hours=2)).isoformat(),
            "is_active": False
        },
        
        # Scenario 5: Strategia senza backtest ma nuova (NON dovrebbe essere rimossa)
        "NewNoBacktestStrategy_llama2_20250629_160000": {
            "name": "NewNoBacktestStrategy_llama2_20250629_160000",
            "file_path": "user_data/strategies/newnobackteststrategy_llama2_20250629_160000.py",
            "strategy_type": "volatility",
            "model_used": "llama2",
            "generation_time": (current_time - timedelta(days=5)).isoformat(),
            "validation_status": "validated",
            "backtest_score": None,
            "last_backtest": None,
            "is_active": False
        },
        
        # Scenario 6: Strategia senza backtest ma vecchia (DOVREBBE essere rimossa per età)
        "OldNoBacktestStrategy_mistral_20250620_160000": {
            "name": "OldNoBacktestStrategy_mistral_20250620_160000",
            "file_path": "user_data/strategies/oldnobackteststrategy_mistral_20250620_160000.py",
            "strategy_type": "scalping",
            "model_used": "mistral",
            "generation_time": (current_time - timedelta(days=35)).isoformat(),
            "validation_status": "validated",
            "backtest_score": None,
            "last_backtest": None,
            "is_active": False
        },
        
        # Scenario 7: Strategia al limite di età con buon punteggio (NON dovrebbe essere rimossa)
        "BorderlineStrategy_phi3_20250629_170000": {
            "name": "BorderlineStrategy_phi3_20250629_170000",
            "file_path": "user_data/strategies/borderlinestrategy_phi3_20250629_170000.py",
            "strategy_type": "breakout",
            "model_used": "phi3",
            "generation_time": (current_time - timedelta(days=29)).isoformat(),
            "validation_status": "validated",
            "backtest_score": 0.11,
            "last_backtest": (current_time - timedelta(days=25)).isoformat(),
            "is_active": False
        },
        
        # Scenario 8: Strategia al limite di punteggio (NON dovrebbe essere rimossa)
        "BorderlineScoreStrategy_llama2_20250629_180000": {
            "name": "BorderlineScoreStrategy_llama2_20250629_180000",
            "file_path": "user_data/strategies/borderlinescorestrategy_llama2_20250629_180000.py",
            "strategy_type": "momentum",
            "model_used": "llama2",
            "generation_time": (current_time - timedelta(days=10)).isoformat(),
            "validation_status": "validated",
            "backtest_score": 0.1,  # Esattamente al limite
            "last_backtest": (current_time - timedelta(days=5)).isoformat(),
            "is_active": False
        }
    }
    
    # Salva metadati di test
    with open('test_cleanup_metadata.json', 'w') as f:
        json.dump(test_strategies, f, indent=2)
    
    return test_strategies

def analyze_test_scenarios():
    """Analizza gli scenari di test."""
    print("🧪 Test Scenari Pulizia Strategie")
    print("=" * 50)
    
    # Carica configurazione e metadati di test
    with open('test_cleanup_config.json', 'r') as f:
        config = json.load(f)
    
    with open('test_cleanup_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    current_time = datetime.now()
    min_score = config.get('min_backtest_score', 0.1)
    max_age_days = config.get('max_strategy_age_days', 30)
    
    print(f"\n📋 Configurazione Test:")
    print(f"   🧹 Pulizia abilitata: {config.get('cleanup_old_strategies', True)}")
    print(f"   📊 Punteggio minimo: {min_score}")
    print(f"   📅 Età massima (giorni): {max_age_days}")
    
    print(f"\n📊 Analisi {len(metadata)} Scenari di Test:")
    print("-" * 50)
    
    scenarios: TestScenario = {
        'should_be_removed': [],
        'should_stay': [],
        'expected_behavior': {
            'OldGoodStrategy_phi3_20240501_120000': '❌ RIMOSSA (età > 30 giorni)',
            'NewBadStrategy_llama2_20250629_140000': '❌ RIMOSSA (punteggio < 0.1)',
            'OldBadStrategy_mistral_20250620_150000': '❌ RIMOSSA (età + punteggio)',
            'NewGoodStrategy_phi3_20250629_150000': '✅ MANTENUTA (nessun criterio)',
            'NewNoBacktestStrategy_llama2_20250629_160000': '✅ MANTENUTA (età < 30 giorni)',
            'OldNoBacktestStrategy_mistral_20250620_160000': '❌ RIMOSSA (età > 30 giorni)',
            'BorderlineStrategy_phi3_20250629_170000': '✅ MANTENUTA (età = 29 giorni)',
            'BorderlineScoreStrategy_llama2_20250629_180000': '✅ MANTENUTA (punteggio = 0.1)'
        }
    }
    
    for name, strategy_data in metadata.items():
        generation_time_str = strategy_data['generation_time']
        if isinstance(generation_time_str, str):
            generation_time = datetime.fromisoformat(generation_time_str)
            age_days = (current_time - generation_time).days
        else:
            age_days = 0
            
        backtest_score = strategy_data.get('backtest_score')
        
        # Determina i criteri di rimozione
        old_age = age_days > max_age_days
        low_score = backtest_score is not None and backtest_score < min_score
        
        # Determina se verrà rimossa
        will_be_removed = old_age or low_score
        
        # Stampa informazioni strategia
        status_icon = "❌" if will_be_removed else "✅"
        expected = scenarios['expected_behavior'].get(name, '❓ Comportamento non definito')
        
        print(f"\n{status_icon} {name}")
        print(f"   📅 Età: {age_days} giorni (max: {max_age_days})")
        print(f"   📊 Punteggio: {backtest_score or 'N/A'} (min: {min_score})")
        print(f"   🎯 Comportamento atteso: {expected}")
        
        if old_age:
            print(f"   ⚠️  Criterio rimozione: Età ({age_days} > {max_age_days})")
        elif low_score:
            print(f"   ⚠️  Criterio rimozione: Punteggio basso ({backtest_score} < {min_score})")
        else:
            print(f"   ✅ Sicura: Nessun criterio soddisfatto")
        
        if will_be_removed:
            scenarios['should_be_removed'].append(name)
        else:
            scenarios['should_stay'].append(name)
    
    # Riepilogo
    print(f"\n📊 Riepilogo Test:")
    print("=" * 50)
    print(f"   📈 Strategie totali: {len(metadata)}")
    print(f"   ✅ Strategie che rimarranno: {len(scenarios['should_stay'])}")
    print(f"   ❌ Strategie che verranno rimosse: {len(scenarios['should_be_removed'])}")
    
    if scenarios['should_be_removed']:
        print(f"\n🗑️ Strategie che verranno rimosse:")
        print("-" * 30)
        for name in scenarios['should_be_removed']:
            expected = scenarios['expected_behavior'].get(name, '❓')
            print(f"   ❌ {name} - {expected}")
    
    if scenarios['should_stay']:
        print(f"\n✅ Strategie che rimarranno:")
        print("-" * 30)
        for name in scenarios['should_stay']:
            expected = scenarios['expected_behavior'].get(name, '❓')
            print(f"   ✅ {name} - {expected}")
    
    # Verifica correttezza
    print(f"\n🔍 Verifica Correttezza:")
    print("=" * 30)
    
    correct_count = 0
    total_count = len(metadata)
    
    for name, expected in scenarios['expected_behavior'].items():
        if name in metadata:
            will_be_removed = name in scenarios['should_be_removed']
            expected_removal = '❌ RIMOSSA' in expected
            
            if will_be_removed == expected_removal:
                correct_count += 1
                print(f"   ✅ {name}: Comportamento corretto")
            else:
                print(f"   ❌ {name}: Comportamento ERRATO")
                print(f"      Atteso: {expected}")
                print(f"      Attuale: {'❌ RIMOSSA' if will_be_removed else '✅ MANTENUTA'}")
    
    accuracy = (correct_count / total_count) * 100
    print(f"\n📊 Accuratezza: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    if accuracy == 100:
        print("🎉 Tutti i test sono passati!")
    else:
        print("⚠️  Alcuni test sono falliti!")

def cleanup_test_files():
    """Rimuove i file di test."""
    test_files = [
        'test_cleanup_config.json',
        'test_cleanup_metadata.json'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Rimosso: {file}")

if __name__ == "__main__":
    try:
        print("🧪 Creazione scenari di test...")
        test_strategies = create_test_metadata()
        
        print("📊 Analisi scenari...")
        analyze_test_scenarios()
        
        print("\n🧹 Pulizia file di test...")
        cleanup_test_files()
        
        print("\n✅ Test completato!")
        
    except Exception as e:
        print(f"❌ Errore nel test: {e}")
        cleanup_test_files() 