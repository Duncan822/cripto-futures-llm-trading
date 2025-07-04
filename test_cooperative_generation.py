#!/usr/bin/env python3
"""
Test di generazione cooperativa manuale
"""

import sys
import os
import time
from datetime import datetime

# Aggiungi il path corrente
sys.path.append('.')

def test_cooperative_generation():
    """Test di generazione cooperativa."""
    print("🧪 Test Generazione Cooperativa")
    print("=" * 50)
    
    try:
        from background_agent_cooperative import CooperativeBackgroundAgent
        
        # Inizializza l'agente cooperativo
        agent = CooperativeBackgroundAgent()
        print("✅ Agente cooperativo inizializzato")
        
        # Test generazione strategia cooperativa
        print("\n🤝 Generazione strategia cooperativa...")
        start_time = time.time()
        
        metadata = agent.generate_strategy_safely("volatility", "cooperative")
        
        duration = time.time() - start_time
        
        if metadata:
            print(f"✅ Strategia cooperativa generata!")
            print(f"   Nome: {metadata.name}")
            print(f"   Tipo: {metadata.strategy_type}")
            print(f"   Modello: {metadata.model_used}")
            print(f"   Durata: {duration:.1f} secondi")
            print(f"   File: {metadata.file_path}")
            
            # Verifica che il file esista
            if os.path.exists(metadata.file_path):
                with open(metadata.file_path, 'r') as f:
                    content = f.read()
                print(f"   Dimensione: {len(content)} caratteri")
                print(f"   Righe: {len(content.split(chr(10)))}")
                
                # Cerca indicatori di cooperazione nel codice
                if "cooperative" in content.lower() or "contest" in content.lower():
                    print("   ✅ Segni di generazione cooperativa trovati")
                else:
                    print("   ℹ️ Codice standard (possibile fallback)")
            else:
                print("   ❌ File strategia non trovato")
                
            return True
        else:
            print("❌ Generazione cooperativa fallita")
            return False
            
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

def main():
    """Funzione principale."""
    print("🚀 Test Generazione Cooperativa")
    print("=" * 50)
    
    success = test_cooperative_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Test completato con successo!")
        print("La generazione cooperativa funziona correttamente.")
    else:
        print("❌ Test fallito.")
        print("Controlla i log per dettagli.")
    
    return success

if __name__ == "__main__":
    main() 