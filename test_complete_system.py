#!/usr/bin/env python3
"""
Test completo del sistema con modelli LLM veloci
"""

import json
import time
import subprocess
from pathlib import Path

def test_ollama_models():
    """Testa i modelli Ollama disponibili"""
    print("🧪 TEST MODELLI OLLAMA")
    print("=" * 40)
    
    models = ["phi3:mini", "llama2:7b-chat-q4_0", "mistral:7b-instruct-q4_0"]
    results = {}
    
    for model in models:
        print(f"\n🎯 Testando {model}...")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                ["ollama", "run", model, "Ciao, rispondi solo con 'OK'"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Successo in {duration:.1f}s")
                results[model] = {"success": True, "duration": duration}
            else:
                print(f"❌ Errore: {result.stderr}")
                results[model] = {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout dopo 30s")
            results[model] = {"success": False, "error": "Timeout"}
        except Exception as e:
            print(f"❌ Errore: {e}")
            results[model] = {"success": False, "error": str(e)}
    
    return results

def test_background_agent():
    """Testa il Background Agent"""
    print("\n🤖 TEST BACKGROUND AGENT")
    print("=" * 40)
    
    # Controlla se è in esecuzione
    try:
        result = subprocess.run(
            ["./manage_background_agent.sh", "status"],
            capture_output=True,
            text=True
        )
        
        if "in esecuzione" in result.stdout or "running" in result.stdout:
            print("✅ Background Agent in esecuzione")
            return True
        else:
            print("❌ Background Agent non in esecuzione")
            return False
            
    except Exception as e:
        print(f"❌ Errore nel controllo: {e}")
        return False

def test_configuration():
    """Testa la configurazione"""
    print("\n⚙️ TEST CONFIGURAZIONE")
    print("=" * 40)
    
    config_file = Path("background_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print("✅ Configurazione caricata")
            print(f"📊 Modelli configurati: {config.get('models', [])}")
            print(f"⏱️  Intervallo generazione: {config.get('generation_interval', 'N/A')}s")
            print(f"🔄 Intervallo backtest: {config.get('backtest_interval', 'N/A')}s")
            
            # Controlla se usa modelli veloci
            models = config.get('models', [])
            fast_models = ["phi3:mini", "llama2:7b-chat-q4_0", "mistral:7b-instruct-q4_0"]
            
            if any(model in fast_models for model in models):
                print("✅ Configurazione ottimizzata per CPU")
                return True
            else:
                print("⚠️  Configurazione non ottimizzata per CPU")
                return False
                
        except Exception as e:
            print(f"❌ Errore nel caricamento configurazione: {e}")
            return False
    else:
        print("❌ File configurazione non trovato")
        return False

def test_strategies():
    """Testa le strategie esistenti"""
    print("\n📈 TEST STRATEGIE")
    print("=" * 40)
    
    strategies_dir = Path("strategies")
    if strategies_dir.exists():
        strategies = list(strategies_dir.glob("*.py"))
        print(f"📊 Strategie trovate: {len(strategies)}")
        
        for strategy in strategies[:3]:  # Mostra prime 3
            print(f"  - {strategy.name}")
        
        return len(strategies) > 0
    else:
        print("❌ Directory strategie non trovata")
        return False

def test_metadata():
    """Testa i metadati delle strategie"""
    print("\n📋 TEST METADATI")
    print("=" * 40)
    
    metadata_file = Path("strategies_metadata.json")
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            print(f"✅ Metadati caricati: {len(metadata)} strategie")
            
            for name, info in list(metadata.items())[:2]:
                print(f"  - {name}: {info.get('strategy_type', 'N/A')} ({info.get('model_used', 'N/A')})")
            
            return True
        except Exception as e:
            print(f"❌ Errore nel caricamento metadati: {e}")
            return False
    else:
        print("❌ File metadati non trovato")
        return False

def main():
    """Test completo del sistema"""
    print("🚀 TEST COMPLETO SISTEMA LLM VELOCE")
    print("=" * 50)
    
    results = {
        "ollama_models": test_ollama_models(),
        "background_agent": test_background_agent(),
        "configuration": test_configuration(),
        "strategies": test_strategies(),
        "metadata": test_metadata()
    }
    
    # Risultati finali
    print("\n" + "=" * 50)
    print("📊 RISULTATI FINALI")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"✅ Test superati: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 SISTEMA COMPLETAMENTE FUNZIONANTE!")
        print("\n💡 Il tuo sistema è pronto per:")
        print("   - Generazione automatica strategie")
        print("   - Backtesting automatico")
        print("   - Ottimizzazione con LLM veloci")
    else:
        print("⚠️  Alcuni test falliti")
        print("\n🔧 Prossimi passi:")
        for test_name, result in results.items():
            if not result:
                print(f"   - Risolvi problema: {test_name}")
    
    # Salva risultati
    with open("system_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Risultati salvati in: system_test_results.json")

if __name__ == "__main__":
    main() 