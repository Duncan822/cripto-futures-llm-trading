#!/usr/bin/env python3
"""
Test rapido per modelli LLM veloci
"""

import subprocess
import time

def test_model_speed(model_name, prompt="Genera una strategia scalping BTC/USDT in una riga"):
    """Testa velocità di un modello"""
    print(f"\n🧪 Testando {model_name}...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["ollama", "run", model_name, prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            response = result.stdout.strip()
            print(f"✅ Successo in {duration:.1f}s")
            print(f"📝 Risposta: {response[:100]}...")
            return duration
        else:
            print(f"❌ Errore: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout dopo 30s")
        return None
    except Exception as e:
        print(f"❌ Errore: {e}")
        return None

def main():
    print("🚀 TEST RAPIDO MODELLI LLM")
    print("=" * 40)
    
    models = [
        "phi3:mini",
        "llama2:7b-chat-q4_0",
        "mistral:7b-instruct-q4_0"
    ]
    
    results = {}
    
    for model in models:
        duration = test_model_speed(model)
        if duration:
            results[model] = duration
    
    if results:
        print(f"\n📊 RISULTATI:")
        print("=" * 40)
        
        # Ordina per velocità
        sorted_results = sorted(results.items(), key=lambda x: x[1])
        
        for i, (model, duration) in enumerate(sorted_results, 1):
            print(f"{i}. {model}: {duration:.1f}s")
        
        fastest = sorted_results[0]
        print(f"\n🏆 Più veloce: {fastest[0]} ({fastest[1]:.1f}s)")
        
        if fastest[1] < 15:
            print("✅ Performance eccellente!")
        elif fastest[1] < 25:
            print("✅ Performance buona")
        else:
            print("⚠️  Performance lenta, considera ottimizzazioni")
    
    else:
        print("❌ Nessun modello ha funzionato")

if __name__ == "__main__":
    main() 