import requests
from typing import List, Dict

def query_ollama(prompt: str, model: str = "mistral", timeout: int = 1800) -> str:
    """
    Invia un prompt all'istanza Ollama locale e restituisce la risposta.
    Ottimizzato per velocità e trading futures.

    Args:
        prompt: Il prompt da inviare al modello
        model: Il nome del modello da utilizzare
        timeout: Timeout in secondi (default: 1800 = 30 minuti)
    """
    url = "http://localhost:11434/api/generate"

    # Configurazioni ottimizzate per velocità
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,        # Più basso = più deterministico e veloce
            "top_p": 0.8,             # Più basso = più focalizzato
            "top_k": 40,              # Limita le scelte
            "num_predict": 1024,      # Ridotto per velocità
            "repeat_penalty": 1.1,    # Evita ripetizioni
            "num_ctx": 2048,          # Contesto ridotto per velocità
            "num_thread": 8,          # Usa più thread se disponibili
            "num_gpu": 1,             # Usa GPU se disponibile
            "num_batch": 512,         # Batch size ottimizzato
            "rope_freq_base": 10000,  # Parametri ROPE ottimizzati
            "rope_freq_scale": 0.5
        }
    }

    try:
        print(f"🤖 Invio richiesta a {model} (configurazione veloce)...")
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Risposta ricevuta da {model}")
        return result["response"]
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout per {model} dopo {timeout} secondi")
        raise
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore nella richiesta a {model}: {e}")
        raise

def query_ollama_fast(prompt: str, model: str = "phi3", timeout: int = 600) -> str:
    """
    Versione ultra-veloce per prompt semplici e decisioni rapide.
    Usa phi3 che è più veloce per operazioni semplici.
    """
    url = "http://localhost:11434/api/generate"

    # Configurazione ultra-veloce
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,        # Molto deterministico
            "top_p": 0.5,             # Molto focalizzato
            "num_predict": 512,       # Output molto breve
            "num_ctx": 1024,          # Contesto minimo
            "num_thread": 8,
            "num_batch": 256
        }
    }

    try:
        print(f"⚡ Invio richiesta veloce a {model}...")
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Risposta veloce ricevuta da {model}")
        return result["response"]
    except Exception as e:
        print(f"❌ Errore nella richiesta veloce a {model}: {e}")
        raise

def test_model_availability(model: str = "mistral") -> bool:
    """
    Testa se un modello è disponibile e risponde.

    Args:
        model: Il nome del modello da testare

    Returns:
        True se il modello è disponibile, False altrimenti
    """
    try:
        test_prompt = "Rispondi solo con 'OK'"
        result = query_ollama_fast(test_prompt, model, timeout=120)
        return "OK" in result.upper()
    except Exception as e:
        print(f"❌ Modello {model} non disponibile: {e}")
        return False

def get_available_models() -> List[str]:
    """
    Restituisce la lista dei modelli disponibili.

    Returns:
        Lista dei nomi dei modelli disponibili
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]
    except Exception as e:
        print(f"❌ Errore nel recupero modelli: {e}")
        return []

def get_model_speed_ranking() -> List[str]:
    """
    Restituisce i modelli ordinati per velocità (dal più veloce al più lento).

    Returns:
        Lista ordinata dei modelli per velocità
    """
    # phi3 è il più veloce, mistral è il più lento ma più accurato
    return ["phi3", "llama2", "mistral"]

def get_model_timeout_config() -> Dict[str, Dict[str, int]]:
    """
    Restituisce la configurazione dei timeout ottimali per ogni modello.
    Basato su test reali di velocità dei modelli.
    """
    return {
        "phi3": {
            "fast": 300,      # 5 minuti per prompt semplici
            "normal": 600,    # 10 minuti per prompt normali
            "complex": 900    # 15 minuti per prompt complessi
        },
        "llama2": {
            "fast": 600,      # 10 minuti per prompt semplici
            "normal": 1200,   # 20 minuti per prompt normali
            "complex": 1800   # 30 minuti per prompt complessi
        },
        "mistral": {
            "fast": 900,      # 15 minuti per prompt semplici
            "normal": 1800,   # 30 minuti per prompt normali
            "complex": 2700   # 45 minuti per prompt complessi
        }
    }

def get_optimal_timeout(model: str, prompt_complexity: str = "normal") -> int:
    """
    Calcola il timeout ottimale basato sul modello e sulla complessità del prompt.

    Args:
        model: Nome del modello LLM
        prompt_complexity: Complessità del prompt ("fast", "normal", "complex")

    Returns:
        Timeout in secondi
    """
    config = get_model_timeout_config()

    # Default per modelli sconosciuti
    if model not in config:
        return 1800  # 30 minuti di default

    return config[model].get(prompt_complexity, config[model]["normal"])

def estimate_prompt_complexity(prompt: str) -> str:
    """
    Stima la complessità di un prompt basandosi su vari fattori.

    Args:
        prompt: Il prompt da analizzare

    Returns:
        Complessità stimata ("fast", "normal", "complex")
    """
    # Fattori per determinare la complessità
    length = len(prompt)
    has_code = "def " in prompt or "class " in prompt or "import " in prompt
    has_instructions = prompt.count("Includi") + prompt.count("Genera") + prompt.count("Crea")

    if length < 200 and not has_code and has_instructions < 2:
        return "fast"
    elif length < 800 and has_instructions < 5:
        return "normal"
    else:
        return "complex"
