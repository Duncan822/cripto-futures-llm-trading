import requests
import os
import subprocess
import time
from typing import Optional, Any, List
import sys

# Aggiungo il path della cartella strategies per import diretto
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../strategies'))
from llm_strategies_parser import save_llm_strategies

class OllamaAgent:
    def __init__(self, model: str = "mistral", base_url: Optional[str] = None, auto_start: bool = True):
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        if auto_start:
            self.ensure_ollama_running()

    def ensure_ollama_running(self, max_retries: int = 3, wait_sec: int = 2) -> bool:
        url = f"{self.base_url}/api/tags"
        for _ in range(max_retries):
            try:
                requests.get(url, timeout=1)
                return True
            except Exception:
                pass
            time.sleep(wait_sec)
        # Se non risponde, provo ad avviare Ollama
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Attendo che si avvii
            for _ in range(max_retries * 2):
                try:
                    requests.get(url, timeout=1)
                    return True
                except Exception:
                    time.sleep(wait_sec)
        except Exception as e:
            print(f"Errore nell'avvio automatico di Ollama: {e}")
        print("Ollama non è in ascolto e non è stato possibile avviarlo automaticamente.")
        return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None, stream: bool = False) -> Any:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        if system_prompt:
            payload["system"] = system_prompt
        response = requests.post(url, json=payload)
        response.raise_for_status()
        if stream:
            # Stream non implementato, placeholder
            return response.iter_lines()
        else:
            return response.json().get("response", "")

    def generate_multiple_strategies(self, symbol: str, timeframe: str = "1h", n: int = 3) -> List[str]:
        prompt = (
            f"Genera {n} strategie di trading diverse in Python per il future {symbol} su timeframe {timeframe}. "
            "Le strategie devono essere pensate per dati storici OHLCV e orientate a trading long/short. "
            "Restituisci solo il codice Python di ciascuna strategia, separando ogni strategia con una riga che inizi con '### STRATEGIA'. "
            "Le strategie devono essere semplici, ma diverse tra loro (es: medie mobili, breakout, rsi, ecc)."
        )
        risposta = self.generate(prompt)
        strategie = [s.strip() for s in risposta.split('### STRATEGIA') if s.strip()]
        return strategie

    def generate_and_save_strategies(self, symbol: str, timeframe: str = "1h", n: int = 3) -> List[str]:
        """
        Genera strategie tramite LLM e le salva come file Python in strategies/.
        Restituisce la lista dei percorsi dei file creati.
        """
        strategie = self.generate_multiple_strategies(symbol, timeframe, n)
        file_paths = save_llm_strategies(strategie)
        return file_paths

if __name__ == "__main__":
    agent = OllamaAgent()
    symbol = "BTC/USDT"
    file_paths = agent.generate_and_save_strategies(symbol, timeframe="1h", n=3)
    print("Strategie salvate:")
    for path in file_paths:
        print("-", path) 