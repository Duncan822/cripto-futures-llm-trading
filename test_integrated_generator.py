#!/usr/bin/env python3
"""
Test del Generatore Integrato con Sistema di Prompt Adattivi
Dimostra la generazione di strategie con prompt dinamici, casuali e personalizzati.
"""

import sys
import os
sys.path.append('.')

from agents.generator import GeneratorAgent

def test_integrated_generator():
    """Testa il generatore integrato con prompt adattivi."""
    print("🧪 TEST GENERATORE INTEGRATO")
    print("=" * 60)
    
    # Inizializza generatore
    generator = GeneratorAgent(default_model="phi3:mini")
    
    print(f"🤖 Generatore inizializzato con modello: {generator.default_model}")
    print(f"📊 Modelli veloci disponibili: {len(generator.fast_models)}")
    print()
    
    # Test 1: Strategie Semplici
    print("🔹 TEST 1: STRATEGIE SEMPLICI")
    print("-" * 40)
    
    strategy_types = ["scalping", "momentum", "breakout"]
    
    for strategy_type in strategy_types:
        print(f"\n📋 Generazione strategia {strategy_type} semplice...")
        try:
            strategy_code = generator.generate_simple_strategy(
                strategy_type=strategy_type,
                model="phi3:mini",
                strategy_name=f"Simple{strategy_type.capitalize()}Strategy"
            )
            
            print(f"✅ Strategia {strategy_type} generata!")
            print(f"   Lunghezza codice: {len(strategy_code)} caratteri")
            print(f"   Contiene 'class': {'class' in strategy_code}")
            print(f"   Contiene 'IStrategy': {'IStrategy' in strategy_code}")
            
        except Exception as e:
            print(f"❌ Errore con {strategy_type}: {e}")
    
    print()
    
    # Test 2: Strategie Complesse
    print("🔹 TEST 2: STRATEGIE COMPLESSE")
    print("-" * 40)
    
    for strategy_type in strategy_types[:2]:  # Testa solo 2 per velocità
        print(f"\n📋 Generazione strategia {strategy_type} complessa...")
        try:
            strategy_code = generator.generate_complex_strategy(
                strategy_type=strategy_type,
                model="mistral:7b-instruct-q4_0",
                strategy_name=f"Complex{strategy_type.capitalize()}Strategy"
            )
            
            print(f"✅ Strategia {strategy_type} complessa generata!")
            print(f"   Lunghezza codice: {len(strategy_code)} caratteri")
            print(f"   Contiene parametri: {'IntParameter' in strategy_code or 'DecimalParameter' in strategy_code}")
            
        except Exception as e:
            print(f"❌ Errore con {strategy_type}: {e}")
    
    print()
    
    # Test 3: Strategie Casuali
    print("🔹 TEST 3: STRATEGIE CASUALI")
    print("-" * 40)
    
    for i in range(2):  # Genera 2 strategie casuali
        strategy_type = strategy_types[i]
        print(f"\n🎲 Generazione strategia {strategy_type} casuale...")
        try:
            strategy_code = generator.generate_random_strategy(
                strategy_type=strategy_type,
                model="cogito:8b",
                strategy_name=f"Random{strategy_type.capitalize()}Strategy"
            )
            
            print(f"✅ Strategia {strategy_type} casuale generata!")
            print(f"   Lunghezza codice: {len(strategy_code)} caratteri")
            
        except Exception as e:
            print(f"❌ Errore con {strategy_type}: {e}")
    
    print()
    
    # Test 4: Strategie Adattive Personalizzate
    print("🔹 TEST 4: STRATEGIE ADATTIVE PERSONALIZZATE")
    print("-" * 40)
    
    # Configurazioni personalizzate
    configs = [
        ("scalping", "phi3:mini", "simple", "conservative", 0.1),
        ("momentum", "mistral:7b-instruct-q4_0", "normal", "technical", 0.3),
        ("breakout", "cogito:8b", "complex", "aggressive", 0.5),
    ]
    
    for i, (strategy_type, model, complexity, style, randomization) in enumerate(configs):
        print(f"\n🎯 Configurazione {i+1}: {strategy_type} con {model}")
        try:
            strategy_code = generator.generate_adaptive_strategy(
                strategy_type=strategy_type,
                model=model,
                complexity=complexity,
                style=style,
                randomization=randomization,
                strategy_name=f"Adaptive{strategy_type.capitalize()}Strategy{i+1}"
            )
            
            print(f"✅ Strategia adattiva {i+1} generata!")
            print(f"   Lunghezza codice: {len(strategy_code)} caratteri")
            
        except Exception as e:
            print(f"❌ Errore con configurazione {i+1}: {e}")
    
    print()
    
    # Test 5: Ensemble di Strategie
    print("🔹 TEST 5: ENSEMBLE DI STRATEGIE")
    print("-" * 40)
    
    print("🎭 Generazione ensemble per scalping...")
    try:
        ensemble_strategy = generator.generate_strategy_ensemble(
            strategy_type="scalping",
            models=["phi3:mini", "mistral:7b-instruct-q4_0"],
            strategy_name="ScalpingEnsemble"
        )
        
        print(f"✅ Ensemble generato!")
        print(f"   Lunghezza codice: {len(ensemble_strategy)} caratteri")
        
    except Exception as e:
        print(f"❌ Errore con ensemble: {e}")
    
    print()
    print("✅ TEST COMPLETATO!")
    print("=" * 60)

def demonstrate_strategy_generation():
    """Dimostra la generazione di una strategia completa."""
    print("🎯 DIMOSTRAZIONE GENERAZIONE STRATEGIA")
    print("=" * 60)
    
    generator = GeneratorAgent(default_model="phi3:mini")
    
    # Genera una strategia scalping adattiva
    print("📋 Generazione strategia scalping adattiva...")
    print("   Complessità: normal")
    print("   Stile: technical")
    print("   Randomizzazione: 0.3")
    print()
    
    try:
        strategy_code = generator.generate_adaptive_strategy(
            strategy_type="scalping",
            model="phi3:mini",
            complexity="normal",
            style="technical",
            randomization=0.3,
            strategy_name="DemoScalpingStrategy"
        )
        
        print("✅ Strategia generata con successo!")
        print(f"📏 Lunghezza codice: {len(strategy_code)} caratteri")
        print()
        
        # Mostra anteprima del codice
        print("📄 ANTEPRIMA CODICE:")
        print("-" * 40)
        lines = strategy_code.split('\n')
        for i, line in enumerate(lines[:20]):  # Prime 20 righe
            print(f"{i+1:2d}: {line}")
        
        if len(lines) > 20:
            print(f"... e altre {len(lines) - 20} righe")
        
        print()
        
        # Analisi del codice
        print("📊 ANALISI CODICE:")
        print("-" * 40)
        print(f"   Contiene classe: {'class' in strategy_code}")
        print(f"   Contiene IStrategy: {'IStrategy' in strategy_code}")
        print(f"   Contiene populate_indicators: {'populate_indicators' in strategy_code}")
        print(f"   Contiene populate_entry_trend: {'populate_entry_trend' in strategy_code}")
        print(f"   Contiene populate_exit_trend: {'populate_exit_trend' in strategy_code}")
        print(f"   Contiene parametri: {'IntParameter' in strategy_code or 'DecimalParameter' in strategy_code}")
        print(f"   Contiene ROI: {'minimal_roi' in strategy_code}")
        print(f"   Contiene stoploss: {'stoploss' in strategy_code}")
        
        print()
        print("✅ Dimostrazione completata!")
        
    except Exception as e:
        print(f"❌ Errore durante la generazione: {e}")
        import traceback
        traceback.print_exc()

def compare_prompt_methods():
    """Confronta i diversi metodi di generazione prompt."""
    print("🔄 CONFRONTO METODI PROMPT")
    print("=" * 60)
    
    generator = GeneratorAgent(default_model="phi3:mini")
    strategy_type = "momentum"
    
    print(f"Strategia: {strategy_type}")
    print(f"Modello: {generator.default_model}")
    print()
    
    methods = [
        ("Standard", lambda: generator.generate_futures_strategy(strategy_type)),
        ("Semplice", lambda: generator.generate_simple_strategy(strategy_type)),
        ("Complessa", lambda: generator.generate_complex_strategy(strategy_type)),
        ("Casuale", lambda: generator.generate_random_strategy(strategy_type)),
        ("Adattiva", lambda: generator.generate_adaptive_strategy(strategy_type, complexity="normal", style="technical", randomization=0.3)),
    ]
    
    results = []
    
    for method_name, method_func in methods:
        print(f"📋 Testando metodo: {method_name}")
        try:
            strategy_code = method_func()
            results.append({
                'method': method_name,
                'length': len(strategy_code),
                'success': True,
                'has_class': 'class' in strategy_code,
                'has_istrategy': 'IStrategy' in strategy_code,
                'has_parameters': 'IntParameter' in strategy_code or 'DecimalParameter' in strategy_code
            })
            print(f"   ✅ Successo - Lunghezza: {len(strategy_code)} caratteri")
        except Exception as e:
            results.append({
                'method': method_name,
                'length': 0,
                'success': False,
                'error': str(e)
            })
            print(f"   ❌ Fallito - Errore: {e}")
    
    print()
    print("📊 RISULTATI CONFRONTO:")
    print("-" * 40)
    print(f"{'Metodo':<12} {'Lunghezza':<10} {'Successo':<8} {'Classe':<6} {'IStrategy':<10} {'Parametri':<9}")
    print("-" * 60)
    
    for result in results:
        if result['success']:
            print(f"{result['method']:<12} {result['length']:<10} {'✅':<8} {str(result['has_class']):<6} {str(result['has_istrategy']):<10} {str(result['has_parameters']):<9}")
        else:
            print(f"{result['method']:<12} {'0':<10} {'❌':<8} {'N/A':<6} {'N/A':<10} {'N/A':<9}")
    
    print()
    print("✅ Confronto completato!")

if __name__ == "__main__":
    print("🚀 AVVIO TEST GENERATORE INTEGRATO")
    print("=" * 60)
    
    try:
        # Test principale
        test_integrated_generator()
        
        print("\n" + "=" * 60)
        
        # Dimostrazione generazione
        demonstrate_strategy_generation()
        
        print("\n" + "=" * 60)
        
        # Confronto metodi
        compare_prompt_methods()
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 TEST COMPLETATO CON SUCCESSO!") 