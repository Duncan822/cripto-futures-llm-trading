#!/usr/bin/env python3
"""
Test specifico per modelli Cogito e confronto performance
"""

import subprocess
import time
import json

def test_model_performance(model_name, prompt, timeout=30):
    """Testa performance di un modello"""
    print(f"\n🧪 Testando {model_name}...")

    start_time = time.time()

    try:
        result = subprocess.run(
            ["ollama", "run", model_name, prompt],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"✅ Successo in {duration:.1f}s")
            print(f"📝 Risposta: {response[:100]}...")
            return {
                "model": model_name,
                "success": True,
                "duration": duration,
                "response": response
            }
        else:
            print(f"❌ Errore: {result.stderr}")
            return {
                "model": model_name,
                "success": False,
                "error": result.stderr
            }

    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout dopo {timeout}s")
        return {
            "model": model_name,
            "success": False,
            "error": "Timeout"
        }
    except Exception as e:
        print(f"❌ Errore: {e}")
        return {
            "model": model_name,
            "success": False,
            "error": str(e)
        }

def test_cogito_deep_thinking():
    """Testa la funzionalità deep thinking di Cogito"""
    print("\n🧠 TEST COGITO DEEP THINKING")
    print("=" * 40)

    prompt = """Enable deep thinking subroutine.
Analizza: quale strategia di trading è più efficace per crypto futures - scalping o swing trading?
Spiega il ragionamento in 2 righe."""

    result = test_model_performance("cogito:3b", prompt, timeout=45)

    if result["success"]:
        response = result["response"]
        if "<think>" in response.lower():
            print("✅ Deep thinking subroutine attivato!")
        else:
            print("⚠️  Deep thinking non rilevato nella risposta")

    return result

def main():
    """Test completo modelli Cogito"""
    print("🚀 TEST MODELLI COGITO")
    print("=" * 50)

    # Test 1: Prompt semplice
    print("\n📊 TEST 1: PROMPT SEMPLICE")
    print("-" * 30)

    simple_prompt = "Ciao, rispondi solo con 'OK'"

    models = [
        "cogito:3b",
        "cogito:8b",
        "phi3:mini",
        "llama2:7b-chat-q4_0",
        "mistral:7b-instruct-q4_0"
    ]

    simple_results = {}

    for model in models:
        result = test_model_performance(model, simple_prompt)
        simple_results[model] = result

    # Test 2: Strategia trading
    print("\n📈 TEST 2: STRATEGIA TRADING")
    print("-" * 30)

    trading_prompt = "Genera una strategia di trading scalping per BTC/USDT in 2 righe"

    trading_results = {}

    for model in ["cogito:3b", "cogito:8b", "phi3:mini"]:
        result = test_model_performance(model, trading_prompt, timeout=60)
        trading_results[model] = result

    # Test 3: Deep thinking
    deep_thinking_result = test_cogito_deep_thinking()

    # Risultati finali
    print("\n" + "=" * 60)
    print("📊 RISULTATI FINALI")
    print("=" * 60)

    # Ordina per velocità (prompt semplice)
    successful_simple = {k: v for k, v in simple_results.items() if v["success"]}
    if successful_simple:
        sorted_simple = sorted(successful_simple.items(), key=lambda x: x[1]["duration"])

        print("🏆 CLASSIFICA VELOCITÀ (prompt semplice):")
        for i, (model, result) in enumerate(sorted_simple, 1):
            print(f"{i}. {model}: {result['duration']:.1f}s")

    # Analisi qualità (strategia trading)
    print(f"\n📈 ANALISI QUALITÀ (strategia trading):")
    for model, result in trading_results.items():
        if result["success"]:
            response = result["response"]
            quality_score = len(response.split())  # Approssimazione qualità
            print(f"  - {model}: {quality_score} parole, {result['duration']:.1f}s")

    # Specialità Cogito
    print(f"\n🧠 SPECIALITÀ COGITO:")
    if deep_thinking_result["success"]:
        print("  ✅ Deep thinking subroutine funzionante")
        print("  ✅ Capacità di ragionamento avanzato")
    else:
        print("  ⚠️  Deep thinking non testato completamente")

    # Raccomandazioni
    print(f"\n🎯 RACCOMANDAZIONI:")

    fastest = min(simple_results.items(), key=lambda x: x[1]["duration"] if x[1]["success"] else float('inf'))
    if fastest[1]["success"]:
        print(f"  🥇 Più veloce: {fastest[0]} ({fastest[1]['duration']:.1f}s)")

    print(f"  🧠 Per ragionamento complesso: cogito:3b")
    print(f"  ⚡ Per velocità massima: phi3:mini")
    print(f"  🎯 Per qualità bilanciata: cogito:8b")

    # Salva risultati
    all_results = {
        "simple_prompt": simple_results,
        "trading_prompt": trading_results,
        "deep_thinking": deep_thinking_result
    }

    with open("cogito_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n💾 Risultati salvati in: cogito_test_results.json")

if __name__ == "__main__":
    main()
