#!/usr/bin/env python3
"""
Test script per modelli LLM veloci ottimizzati per CPU
"""

import time
import json
import subprocess
import sys
from pathlib import Path

def test_ollama_model(model_name, test_prompt, max_tokens=100):
    """Testa un modello Ollama e misura le performance"""
    print(f"\n🧪 Testando modello: {model_name}")
    print("=" * 50)
    
    # Prompt di test per strategie trading
    prompt = f"""Genera una strategia di trading semplice per crypto futures.
Focus su: scalping, timeframe 5m, BTC/USDT.
Risposta breve ({max_tokens} token max): {test_prompt}"""
    
    start_time = time.time()
    
    try:
        # Comando Ollama
        cmd = [
            "ollama", "run", model_name,
            prompt
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # Timeout di 60 secondi
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            response = result.stdout.strip()
            tokens_approx = len(response.split())  # Approssimazione token
            
            print(f"✅ Successo!")
            print(f"⏱️  Tempo di risposta: {duration:.2f} secondi")
            print(f"📊 Token generati: ~{tokens_approx}")
            print(f"🚀 Velocità: ~{tokens_approx/duration:.1f} token/sec")
            print(f"💾 Memoria stimata: {get_model_memory_usage(model_name)}")
            
            print(f"\n📝 Risposta:")
            print("-" * 30)
            print(response[:200] + "..." if len(response) > 200 else response)
            
            return {
                "model": model_name,
                "success": True,
                "duration": duration,
                "tokens": tokens_approx,
                "speed": tokens_approx/duration if duration > 0 else 0,
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
        print(f"⏰ Timeout dopo 60 secondi")
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

def get_model_memory_usage(model_name):
    """Stima l'uso di memoria del modello"""
    memory_map = {
        "phi3:mini": "~2GB",
        "llama2:7b-chat-q4_0": "~4GB", 
        "mistral:7b-instruct-q4_0": "~4GB",
        "arcee-vylinh:3b": "~2GB"
    }
    return memory_map.get(model_name, "~3GB")

def check_available_models():
    """Controlla i modelli disponibili su Ollama"""
    print("🔍 Controllo modelli disponibili...")
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            models = []
            for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    if parts:
                        models.append(parts[0])
            
            print(f"📦 Modelli installati: {len(models)}")
            for model in models:
                print(f"  - {model}")
            
            return models
        else:
            print("❌ Errore nel controllo modelli")
            return []
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        return []

def main():
    """Funzione principale"""
    print("🚀 TEST MODELLI LLM VELOCI PER CPU")
    print("=" * 50)
    
    # Controlla modelli disponibili
    available_models = check_available_models()
    
    # Modelli da testare (in ordine di velocità)
    models_to_test = [
        "phi3:mini",
        "llama2:7b-chat-q4_0", 
        "mistral:7b-instruct-q4_0"
    ]
    
    # Filtra solo quelli disponibili
    models_to_test = [m for m in models_to_test if m in available_models]
    
    if not models_to_test:
        print("\n❌ Nessun modello veloce trovato!")
        print("💡 Installa i modelli con:")
        print("   ollama pull phi3:mini")
        print("   ollama pull llama2:7b-chat-q4_0")
        print("   ollama pull mistral:7b-instruct-q4_0")
        return
    
    print(f"\n🎯 Testando {len(models_to_test)} modelli...")
    
    # Prompt di test
    test_prompts = [
        "Strategia scalping BTC/USDT 5m",
        "Indicatori RSI e MACD per momentum",
        "Gestione rischio stop loss 2%"
    ]
    
    results = []
    
    for i, model in enumerate(models_to_test, 1):
        print(f"\n📊 Test {i}/{len(models_to_test)}")
        
        # Test con prompt diverso per ogni modello
        prompt = test_prompts[i % len(test_prompts)]
        result = test_ollama_model(model, prompt)
        results.append(result)
        
        # Pausa tra test
        if i < len(models_to_test):
            print("⏳ Pausa 5 secondi...")
            time.sleep(5)
    
    # Risultati finali
    print("\n" + "=" * 60)
    print("📊 RISULTATI FINALI")
    print("=" * 60)
    
    successful_results = [r for r in results if r["success"]]
    
    if successful_results:
        # Ordina per velocità
        successful_results.sort(key=lambda x: x["speed"], reverse=True)
        
        print(f"🏆 MIGLIORI PERFORMANCE:")
        for i, result in enumerate(successful_results, 1):
            print(f"{i}. {result['model']}")
            print(f"   🚀 Velocità: {result['speed']:.1f} token/sec")
            print(f"   ⏱️  Tempo: {result['duration']:.2f}s")
            print(f"   📊 Token: {result['tokens']}")
            print()
        
        # Salva risultati
        with open("fast_llm_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Risultati salvati in: fast_llm_test_results.json")
        
        # Raccomandazione
        best_model = successful_results[0]
        print(f"\n🎯 RACCOMANDAZIONE:")
        print(f"Usa '{best_model['model']}' per il tuo progetto!")
        print(f"Velocità: {best_model['speed']:.1f} token/sec")
        
    else:
        print("❌ Nessun test completato con successo")

if __name__ == "__main__":
    main() 