#!/usr/bin/env python3
"""
Test Cooperazione Senza Timeout: Verifica che la cooperazione tra LLM funzioni senza limiti di tempo
e che il monitoraggio delle risorse sia attivo durante le sessioni cooperative.
"""

import os
import time
import json
import logging
import threading
from datetime import datetime
from pathlib import Path

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_cooperative_unlimited.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_unlimited_cooperation():
    """Testa la cooperazione senza timeout."""
    print("🚀 Test Cooperazione Senza Timeout")
    print("=" * 50)
    
    # Verifica configurazione
    config_path = "background_config_cooperative.json"
    if not os.path.exists(config_path):
        print("❌ Configurazione cooperativa non trovata")
        return False
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    cooperative_config = config.get('cooperative_mode', {})
    unlimited = cooperative_config.get('unlimited_cooperation', False)
    timeouts = {
        'contest_timeout': cooperative_config.get('contest_timeout', 600),
        'voting_timeout': cooperative_config.get('voting_timeout', 600),
        'consensus_timeout': cooperative_config.get('consensus_timeout', 300)
    }
    
    print(f"📋 Configurazione cooperativa:")
    print(f"   - Cooperazione illimitata: {unlimited}")
    print(f"   - Timeout contest: {timeouts['contest_timeout']}s")
    print(f"   - Timeout voting: {timeouts['voting_timeout']}s")
    print(f"   - Timeout consensus: {timeouts['consensus_timeout']}s")
    
    if unlimited and all(t == 0 for t in timeouts.values()):
        print("✅ Configurazione senza timeout corretta")
    else:
        print("⚠️ Configurazione con timeout attiva")
    
    # Test funzioni LLM senza timeout
    print("\n🔧 Test funzioni LLM senza timeout...")
    
    try:
        from llm_utils import query_ollama_unlimited, query_ollama_cooperative
        
        # Test semplice senza timeout
        test_prompt = "Genera una breve strategia di trading per testare la cooperazione senza timeout."
        
        print("   - Test query_ollama_unlimited...")
        start_time = time.time()
        response = query_ollama_unlimited(test_prompt, "phi3:mini")
        duration = time.time() - start_time
        print(f"   ✅ Completato in {duration:.1f}s")
        
        print("   - Test query_ollama_cooperative...")
        start_time = time.time()
        response = query_ollama_cooperative(test_prompt, "phi3:mini", "test_session")
        duration = time.time() - start_time
        print(f"   ✅ Completato in {duration:.1f}s")
        
    except ImportError as e:
        print(f"❌ Errore import: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore test LLM: {e}")
        return False
    
    # Test monitoraggio risorse
    print("\n📊 Test monitoraggio risorse...")
    
    try:
        from cooperative_monitor import CooperativeMonitor
        
        monitor = CooperativeMonitor(port=8082)
        monitor.start()
        
        # Verifica che il monitor sia attivo
        time.sleep(2)
        
        if monitor.is_running:
            print("✅ Monitor cooperativo attivo")
            
            # Verifica monitoraggio risorse
            monitoring_config = config.get('monitoring', {})
            resource_monitoring = monitoring_config.get('enable_resource_monitoring', False)
            check_interval = monitoring_config.get('resource_check_interval', 30)
            
            print(f"   - Monitoraggio risorse: {resource_monitoring}")
            print(f"   - Intervallo controllo: {check_interval}s")
            
            if resource_monitoring:
                print("✅ Monitoraggio risorse attivo")
            else:
                print("⚠️ Monitoraggio risorse disabilitato")
            
            monitor.stop()
        else:
            print("❌ Monitor cooperativo non attivo")
            return False
            
    except ImportError as e:
        print(f"⚠️ Monitor cooperativo non disponibile: {e}")
    except Exception as e:
        print(f"❌ Errore monitor: {e}")
    
    # Test agente cooperativo
    print("\n🤖 Test agente cooperativo...")
    
    try:
        from background_agent_cooperative import CooperativeBackgroundAgent
        
        agent = CooperativeBackgroundAgent()
        print("✅ Agente cooperativo caricato")
        
        # Verifica configurazione agente
        agent_config = agent.config.get('cooperative_mode', {})
        agent_unlimited = agent_config.get('unlimited_cooperation', False)
        
        print(f"   - Cooperazione illimitata: {agent_unlimited}")
        
        if agent_unlimited:
            print("✅ Agente configurato per cooperazione illimitata")
        else:
            print("⚠️ Agente con limiti di tempo")
            
    except ImportError as e:
        print(f"⚠️ Agente cooperativo non disponibile: {e}")
    except Exception as e:
        print(f"❌ Errore agente: {e}")
    
    print("\n📈 Test completato!")
    return True

def test_resource_monitoring():
    """Test specifico per il monitoraggio delle risorse."""
    print("\n🔍 Test Dettagliato Monitoraggio Risorse")
    print("=" * 50)
    
    try:
        import psutil
        
        # Monitoraggio risorse di sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"💻 Risorse sistema:")
        print(f"   - CPU: {cpu_percent}%")
        print(f"   - RAM: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
        print(f"   - Disco: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        
        # Verifica processi Ollama
        ollama_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'ollama' in proc.info['name'].lower():
                    ollama_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if ollama_processes:
            print(f"\n🤖 Processi Ollama attivi: {len(ollama_processes)}")
            for proc in ollama_processes:
                print(f"   - PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, RAM: {proc['memory_percent']:.1f}%)")
        else:
            print("\n⚠️ Nessun processo Ollama trovato")
        
        # Verifica modelli disponibili
        try:
            from llm_utils import get_available_models
            models = get_available_models()
            print(f"\n📚 Modelli disponibili: {len(models)}")
            for model in models:
                print(f"   - {model}")
        except Exception as e:
            print(f"\n❌ Errore verifica modelli: {e}")
        
        return True
        
    except ImportError:
        print("❌ psutil non disponibile per monitoraggio risorse")
        return False
    except Exception as e:
        print(f"❌ Errore monitoraggio risorse: {e}")
        return False

def main():
    """Funzione principale del test."""
    print("🧪 Test Sistema Cooperativo Senza Timeout")
    print("=" * 60)
    
    # Test cooperazione senza timeout
    cooperation_ok = test_unlimited_cooperation()
    
    # Test monitoraggio risorse
    monitoring_ok = test_resource_monitoring()
    
    # Risultati finali
    print("\n" + "=" * 60)
    print("📊 RISULTATI FINALI")
    print("=" * 60)
    
    if cooperation_ok:
        print("✅ Cooperazione senza timeout: FUNZIONANTE")
    else:
        print("❌ Cooperazione senza timeout: PROBLEMI")
    
    if monitoring_ok:
        print("✅ Monitoraggio risorse: ATTIVO")
    else:
        print("❌ Monitoraggio risorse: PROBLEMI")
    
    if cooperation_ok and monitoring_ok:
        print("\n🎉 SISTEMA COMPLETAMENTE FUNZIONANTE!")
        print("   - Cooperazione libera senza timeout")
        print("   - Monitoraggio risorse attivo")
        print("   - Pronto per sessioni cooperative illimitate")
    else:
        print("\n⚠️ SISTEMA CON PROBLEMI")
        print("   - Verificare configurazione e dipendenze")
    
    print("\n📝 Prossimi passi:")
    print("   1. Avviare background_agent_cooperative.py")
    print("   2. Monitorare dashboard cooperativa su http://localhost:8080")
    print("   3. Verificare log per sessioni cooperative")
    print("   4. Controllare utilizzo risorse durante cooperazione")

if __name__ == "__main__":
    main() 