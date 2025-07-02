#!/usr/bin/env python3
"""
Script per testare la generazione di strategie futures volatili
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.generator import GeneratorAgent
from llm_utils import get_available_models

def test_futures_strategy_generation():
    """Testa la generazione di strategie futures"""
    print("🚀 Test Generazione Strategie Futures Volatili")
    print("=" * 60)

    # 1. Verifica modelli disponibili
    print("1. Verifica modelli disponibili...")
    available_models = get_available_models()
    if not available_models:
        print("❌ Nessun modello disponibile")
        return False

    print(f"✅ Modelli trovati: {', '.join(available_models)}")

    # 2. Inizializza generatore
    print("\n2. Inizializzazione generatore...")
    generator = GeneratorAgent()
    print(f"✅ Generatore inizializzato con modello: {generator.default_model}")

    # 3. Test generazione strategia volatilità
    print("\n3. Test generazione strategia volatilità...")
    try:
        strategy = generator.generate_futures_strategy("volatility")
        print("✅ Strategia volatilità generata con successo")
        print(f"📝 Lunghezza strategia: {len(strategy)} caratteri")
        print(f"📄 Anteprima: {strategy[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Errore nella generazione strategia volatilità: {e}")
        return False

def test_multiple_strategies():
    """Testa la generazione di multiple strategie"""
    print("\n🔄 Test Generazione Multiple Strategie")
    print("=" * 60)

    generator = GeneratorAgent()
    strategy_types = ["volatility", "scalping", "breakout", "momentum", "adaptive"]

    results = {}

    for strategy_type in strategy_types:
        print(f"\n📊 Generazione strategia {strategy_type}...")
        try:
            strategy = generator.generate_futures_strategy(strategy_type)
            results[strategy_type] = {
                "success": True,
                "length": len(strategy),
                "preview": strategy[:100]
            }
            print(f"✅ {strategy_type}: {len(strategy)} caratteri")
        except Exception as e:
            results[strategy_type] = {
                "success": False,
                "error": str(e)
            }
            print(f"❌ {strategy_type}: {e}")

    # Riepilogo risultati
    print("\n📈 Riepilogo Risultati:")
    print("-" * 40)
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    print(f"Strategie generate con successo: {successful}/{total}")

    for strategy_type, result in results.items():
        if result["success"]:
            print(f"✅ {strategy_type}: {result['length']} caratteri")
        else:
            print(f"❌ {strategy_type}: {result['error']}")

    return successful > 0

if __name__ == "__main__":
    print("🤖 Test Sistema Generazione Strategie Futures")
    print("=" * 60)

    # Test base
    success1 = test_futures_strategy_generation()

    if success1:
        # Test multiple strategie
        success2 = test_multiple_strategies()

        if success2:
            print("\n🎉 Tutti i test completati con successo!")
            print("Il sistema è pronto per generare strategie futures volatili.")
        else:
            print("\n⚠️  Alcuni test sono falliti, ma il sistema base funziona.")
    else:
        print("\n❌ Test base fallito. Verifica la configurazione.")

    print("\n💡 Prossimi passi:")
    print("1. Usa './manage_background_agent.sh start' per avviare il sistema")
    print("2. Usa './run_backtest.sh' per testare le strategie")
    print("3. Usa './run_hyperopt.sh' per ottimizzare parametri")

    sys.exit(0 if success1 else 1)
