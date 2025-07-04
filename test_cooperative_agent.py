#!/usr/bin/env python3
"""
Test rapido del Background Agent Cooperativo
"""

import sys
import os
import time
import json
from datetime import datetime

# Aggiungi il path corrente
sys.path.append('.')

def test_cooperative_agent():
    """Test di base del background agent cooperativo."""
    print("🧪 Test Background Agent Cooperativo")
    print("=" * 50)
    
    try:
        # Test importazione
        print("1. Test importazione...")
        from background_agent_cooperative import CooperativeBackgroundAgent
        print("   ✅ Importazione riuscita")
        
        # Test configurazione
        print("2. Test configurazione...")
        config_file = "background_config_cooperative.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"   ✅ Configurazione caricata: {len(config)} sezioni")
            
            # Verifica sezione cooperativa
            if 'cooperative_mode' in config:
                print(f"   ✅ Modalità cooperativa: {config['cooperative_mode']}")
            else:
                print("   ⚠️ Sezione cooperative_mode mancante")
        else:
            print("   ❌ File configurazione non trovato")
            return False
        
        # Test inizializzazione
        print("3. Test inizializzazione...")
        agent = CooperativeBackgroundAgent(config_file)
        print("   ✅ Agente cooperativo inizializzato")
        
        # Test generatore cooperativo
        print("4. Test generatore cooperativo...")
        if hasattr(agent, 'cooperative_generator'):
            print(f"   ✅ Generatore cooperativo: {type(agent.cooperative_generator).__name__}")
            print(f"   ✅ Modelli disponibili: {agent.cooperative_generator.strategy_generators}")
        else:
            print("   ❌ Generatore cooperativo non trovato")
            return False
        
        # Test generazione nome strategia
        print("5. Test generazione nome...")
        strategy_name = agent.generate_unique_strategy_name("volatility", "cooperative")
        print(f"   ✅ Nome generato: {strategy_name}")
        
        # Test fallback (senza generare effettivamente)
        print("6. Test fallback...")
        if hasattr(agent.cooperative_generator, 'standard_generator'):
            print("   ✅ Fallback al generatore standard disponibile")
        else:
            print("   ⚠️ Fallback non configurato")
        
        print("\n🎉 Test completato con successo!")
        print("Il Background Agent Cooperativo è pronto per l'uso.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Errore di importazione: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

def test_llm_availability():
    """Test disponibilità modelli LLM."""
    print("\n🤖 Test disponibilità modelli LLM")
    print("=" * 40)
    
    try:
        from llm_utils import query_ollama_fast
        
        models_to_test = ["cogito:8b", "mistral:7b-instruct-q4_0", "phi3:mini"]
        
        for model in models_to_test:
            print(f"Test {model}...")
            try:
                # Test rapido con prompt semplice
                response = query_ollama_fast("Rispondi solo 'OK'", model, timeout=10)
                if response and len(response.strip()) > 0:
                    print(f"   ✅ {model}: Disponibile")
                else:
                    print(f"   ⚠️ {model}: Risposta vuota")
            except Exception as e:
                print(f"   ❌ {model}: {str(e)[:50]}...")
                
    except ImportError:
        print("   ⚠️ llm_utils non disponibile")
    except Exception as e:
        print(f"   ❌ Errore test LLM: {e}")

def main():
    """Funzione principale."""
    print("🚀 Test Background Agent Cooperativo")
    print("=" * 50)
    
    # Test principale
    success = test_cooperative_agent()
    
    # Test LLM se il test principale è riuscito
    if success:
        test_llm_availability()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Tutti i test completati con successo!")
        print("Il sistema cooperativo è pronto per l'uso.")
    else:
        print("❌ Alcuni test sono falliti.")
        print("Controlla la configurazione e le dipendenze.")
    
    return success

if __name__ == "__main__":
    main() 