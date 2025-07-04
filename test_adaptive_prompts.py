#!/usr/bin/env python3
"""
Test del Sistema di Prompt Adattivi
Dimostra la generazione di prompt dinamici, casuali e personalizzati.
"""

import sys
import os
sys.path.append('.')

from prompts.adaptive_prompt_generator import (
    generate_simple_prompt,
    generate_complex_prompt,
    generate_random_prompt,
    generate_adaptive_prompt,
    AdaptivePromptGenerator
)

def test_adaptive_prompts():
    """Testa il sistema di prompt adattivi."""
    print("🧪 TEST SISTEMA PROMPT ADATTIVI")
    print("=" * 60)
    
    # Modelli di test
    models = ["phi3:mini", "mistral:7b-instruct-q4_0", "cogito:8b"]
    strategy_types = ["scalping", "momentum", "breakout", "volatility", "adaptive"]
    
    print(f"📊 Modelli testati: {len(models)}")
    print(f"🎯 Tipi strategia: {len(strategy_types)}")
    print()
    
    # Test 1: Prompt Semplici
    print("🔹 TEST 1: PROMPT SEMPLICI")
    print("-" * 40)
    for strategy_type in strategy_types[:2]:  # Testa solo 2 tipi
        for model in models[:2]:  # Testa solo 2 modelli
            print(f"\n📋 {strategy_type.upper()} con {model}:")
            prompt = generate_simple_prompt(strategy_type, model)
            print(f"Lunghezza: {len(prompt)} caratteri")
            print(f"Prime 200 caratteri: {prompt[:200]}...")
    print()
    
    # Test 2: Prompt Complessi
    print("🔹 TEST 2: PROMPT COMPLESSI")
    print("-" * 40)
    for strategy_type in strategy_types[:2]:
        for model in models[:2]:
            print(f"\n📋 {strategy_type.upper()} con {model}:")
            prompt = generate_complex_prompt(strategy_type, model)
            print(f"Lunghezza: {len(prompt)} caratteri")
            print(f"Prime 200 caratteri: {prompt[:200]}...")
    print()
    
    # Test 3: Prompt Casuali
    print("🔹 TEST 3: PROMPT CASUALI")
    print("-" * 40)
    for i in range(3):  # Genera 3 prompt casuali
        strategy_type = strategy_types[i % len(strategy_types)]
        model = models[i % len(models)]
        print(f"\n🎲 Prompt casuale {i+1} ({strategy_type} con {model}):")
        prompt = generate_random_prompt(strategy_type, model)
        print(f"Lunghezza: {len(prompt)} caratteri")
        print(f"Contenuto completo:\n{prompt}")
    print()
    
    # Test 4: Prompt Adattivi Personalizzati
    print("🔹 TEST 4: PROMPT ADATTIVI PERSONALIZZATI")
    print("-" * 40)
    
    # Configurazioni personalizzate
    configs = [
        ("scalping", "phi3:mini", "simple", "conservative", 0.1),
        ("momentum", "mistral:7b-instruct-q4_0", "normal", "technical", 0.3),
        ("breakout", "cogito:8b", "complex", "aggressive", 0.5),
        ("volatility", "phi3:mini", "normal", "creative", 0.7),
    ]
    
    for i, (strategy_type, model, complexity, style, randomization) in enumerate(configs):
        print(f"\n🎯 Configurazione {i+1}:")
        print(f"   Strategia: {strategy_type}")
        print(f"   Modello: {model}")
        print(f"   Complessità: {complexity}")
        print(f"   Stile: {style}")
        print(f"   Randomizzazione: {randomization}")
        
        prompt = generate_adaptive_prompt(
            strategy_type=strategy_type,
            model=model,
            complexity=complexity,
            style=style,
            randomization=randomization
        )
        
        print(f"   Lunghezza: {len(prompt)} caratteri")
        print(f"   Anteprima: {prompt[:150]}...")
    print()
    
    # Test 5: Confronto Lunghezze
    print("🔹 TEST 5: CONFRONTO LUNGHEZZE")
    print("-" * 40)
    
    generator = AdaptivePromptGenerator()
    strategy_type = "scalping"
    model = "mistral:7b-instruct-q4_0"
    
    lengths = {}
    for complexity in ["simple", "normal", "complex"]:
        for randomization in [0.1, 0.5, 0.9]:
            prompt = generator.generate_adaptive_prompt(
                strategy_type=strategy_type,
                model=model,
                complexity=complexity,
                style="technical",
                randomization=randomization
            )
            key = f"{complexity}_{randomization}"
            lengths[key] = len(prompt)
    
    print("Lunghezze prompt (caratteri):")
    for key, length in lengths.items():
        complexity, randomization = key.split("_")
        print(f"   {complexity} + {randomization} random: {length}")
    
    print()
    
    # Test 6: Analisi Componenti
    print("🔹 TEST 6: ANALISI COMPONENTI")
    print("-" * 40)
    
    generator = AdaptivePromptGenerator()
    components = generator._get_strategy_components()
    
    print("Componenti disponibili per generazione casuale:")
    print(f"   Indicatori: {len(components['indicators'])}")
    print(f"   Timeframes: {len(components['timeframes'])}")
    print(f"   Livelli rischio: {len(components['risk_levels'])}")
    
    print("\nEsempi indicatori:", ", ".join(components['indicators'][:5]))
    print("Esempi timeframes:", ", ".join(components['timeframes'][:3]))
    print("Esempi rischio:", components['risk_levels'][0])
    
    print()
    print("✅ TEST COMPLETATO!")
    print("=" * 60)

def demonstrate_prompt_variations():
    """Dimostra le variazioni di prompt per lo stesso tipo di strategia."""
    print("🎭 DIMOSTRAZIONE VARIAZIONI PROMPT")
    print("=" * 60)
    
    strategy_type = "momentum"
    model = "cogito:8b"
    
    print(f"Strategia: {strategy_type}")
    print(f"Modello: {model}")
    print()
    
    # Variazione 1: Semplice e Tecnico
    print("📋 VARIAZIONE 1: SEMPLICE E TECNICO")
    print("-" * 40)
    prompt1 = generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity="simple",
        style="technical",
        randomization=0.1
    )
    print(f"Lunghezza: {len(prompt1)} caratteri")
    print(prompt1)
    print()
    
    # Variazione 2: Complesso e Creativo
    print("📋 VARIAZIONE 2: COMPLESSO E CREATIVO")
    print("-" * 40)
    prompt2 = generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity="complex",
        style="creative",
        randomization=0.5
    )
    print(f"Lunghezza: {len(prompt2)} caratteri")
    print(prompt2)
    print()
    
    # Variazione 3: Casuale
    print("📋 VARIAZIONE 3: CASUALE")
    print("-" * 40)
    prompt3 = generate_adaptive_prompt(
        strategy_type=strategy_type,
        model=model,
        complexity="normal",
        style="creative",
        randomization=0.9
    )
    print(f"Lunghezza: {len(prompt3)} caratteri")
    print(prompt3)
    print()
    
    # Confronto
    print("📊 CONFRONTO VARIAZIONI")
    print("-" * 40)
    print(f"Variazione 1 (Semplice): {len(prompt1)} caratteri")
    print(f"Variazione 2 (Complessa): {len(prompt2)} caratteri")
    print(f"Variazione 3 (Casuale): {len(prompt3)} caratteri")
    print()
    
    ratio = len(prompt2) / len(prompt1)
    print(f"Rapporto complesso/semplice: {ratio:.1f}x")
    print("✅ Dimostrazione completata!")

if __name__ == "__main__":
    print("🚀 AVVIO TEST SISTEMA PROMPT ADATTIVI")
    print("=" * 60)
    
    try:
        # Test principale
        test_adaptive_prompts()
        
        print("\n" + "=" * 60)
        
        # Dimostrazione variazioni
        demonstrate_prompt_variations()
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 TEST COMPLETATO CON SUCCESSO!") 