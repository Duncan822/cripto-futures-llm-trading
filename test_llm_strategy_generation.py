#!/usr/bin/env python3
"""
Test completo per valutare la qualità della generazione di strategie di trading
con tutti gli LLM disponibili nel sistema.
"""

import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests
from dataclasses import dataclass, asdict

@dataclass
class LLMTestResult:
    """Risultato del test per un singolo LLM"""
    model_name: str
    response_time: float
    response_length: int
    has_code: bool
    has_indicators: bool
    has_risk_management: bool
    has_entry_exit_rules: bool
    has_backtest_ready: bool
    quality_score: float
    response_text: str
    error: Optional[str] = None

class LLMStrategyTester:
    def __init__(self):
        self.models = [
            "cogito:8b",
            "cogito:3b", 
            "mistral:7b-instruct-q4_0",
            "phi3:mini",
            "llama2:7b-chat-q4_0",
            "mistral:latest",
            "phi3:latest",
            "llama2:latest"
        ]
        
        self.complex_strategy_prompt = """
Crea una strategia di trading avanzata per futures crypto che includa:

1. **ANALISI TECNICA MULTI-TIMEFRAME**:
   - Analisi su timeframe 1h, 4h e 1d
   - Combinazione di indicatori trend-following e mean-reversion
   - Identificazione di supporti/resistenze dinamici

2. **INDICATORI TECNICI AVANZATI**:
   - RSI con divergenze
   - MACD con signal line
   - Bollinger Bands con squeeze detection
   - Volume Profile
   - Ichimoku Cloud
   - Stochastic oscillator

3. **GESTIONE DEL RISCHIO**:
   - Position sizing dinamico basato su volatilità
   - Stop loss trailing
   - Take profit multipli
   - Correlation matrix per diversificazione
   - Maximum drawdown protection

4. **LOGICA DI ENTRY/EXIT**:
   - Entry su breakout di pattern consolidati
   - Exit su divergenze o reversal signals
   - Time-based exits
   - News event filters

5. **OPTIMIZATION PARAMETERS**:
   - Parametri ottimizzabili per backtest
   - Range di valori realistici
   - Constraints per evitare overfitting

6. **RISULTATI ATTESI**:
   - Sharpe ratio target > 1.5
   - Maximum drawdown < 15%
   - Win rate > 55%
   - Profit factor > 1.8

Genera il codice Python completo per FreqTrade con:
- Classe strategy completa
- Tutti i metodi necessari
- Configurazione degli indicatori
- Logica di trading dettagliata
- Commenti esplicativi
- Gestione degli errori

La strategia deve essere pronta per il backtest e deve gestire correttamente:
- Market conditions diverse
- Slippage e fees
- Risk management
- Portfolio diversification
"""

    def test_model_availability(self, model: str) -> bool:
        """Testa se un modello è disponibile"""
        try:
            test_prompt = "Rispondi solo con 'OK'"
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 10
                    }
                },
                timeout=30
            )
            return response.status_code == 200
        except:
            return False

    def query_llm(self, model: str, prompt: str, timeout: int = 1800) -> Tuple[Optional[str], float]:
        """Invia una query all'LLM"""
        try:
            print(f"🤖 Testando {model}...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "top_k": 40,
                        "num_predict": 2048,
                        "repeat_penalty": 1.1,
                        "num_ctx": 4096,
                        "num_thread": 8,
                        "num_gpu": 1,
                        "num_batch": 512
                    }
                },
                timeout=timeout
            )
            
            response.raise_for_status()
            result = response.json()
            response_time = time.time() - start_time
            
            print(f"✅ {model} completato in {response_time:.2f}s")
            return result["response"], response_time
            
        except Exception as e:
            print(f"❌ Errore con {model}: {e}")
            return None, 0.0

    def analyze_response_quality(self, response: str) -> Dict[str, Any]:
        """Analizza la qualità della risposta"""
        analysis = {
            "response_length": len(response),
            "has_code": False,
            "has_indicators": False,
            "has_risk_management": False,
            "has_entry_exit_rules": False,
            "has_backtest_ready": False,
            "quality_score": 0.0
        }
        
        if not response:
            return analysis
            
        # Controlla presenza di codice
        analysis["has_code"] = any(keyword in response for keyword in [
            "class ", "def ", "import ", "from ", "return ", "if __name__"
        ])
        
        # Controlla indicatori tecnici
        analysis["has_indicators"] = any(indicator in response.lower() for indicator in [
            "rsi", "macd", "bollinger", "stochastic", "ichimoku", "volume", "ema", "sma"
        ])
        
        # Controlla gestione del rischio
        analysis["has_risk_management"] = any(risk_term in response.lower() for risk_term in [
            "stop loss", "take profit", "position size", "risk", "drawdown", "volatility"
        ])
        
        # Controlla regole di entry/exit
        analysis["has_entry_exit_rules"] = any(rule_term in response.lower() for rule_term in [
            "entry", "exit", "buy", "sell", "long", "short", "signal"
        ])
        
        # Controlla se è pronto per backtest
        analysis["has_backtest_ready"] = all([
            analysis["has_code"],
            analysis["has_indicators"],
            analysis["has_risk_management"],
            analysis["has_entry_exit_rules"]
        ])
        
        # Calcola quality score (0-100)
        score = 0
        if analysis["has_code"]: score += 25
        if analysis["has_indicators"]: score += 20
        if analysis["has_risk_management"]: score += 20
        if analysis["has_entry_exit_rules"]: score += 20
        if analysis["has_backtest_ready"]: score += 15
        
        # Bonus per lunghezza (max 10 punti)
        length_bonus = min(10, analysis["response_length"] // 100)
        score += length_bonus
        
        analysis["quality_score"] = min(100, score)
        
        return analysis

    def run_comprehensive_test(self) -> List[LLMTestResult]:
        """Esegue il test completo su tutti i modelli"""
        results = []
        
        print("🚀 Iniziando test completo di generazione strategie...")
        print(f"📊 Modelli da testare: {len(self.models)}")
        print("=" * 80)
        
        for model in self.models:
            print(f"\n🔍 Testando {model}...")
            
            # Test disponibilità
            if not self.test_model_availability(model):
                print(f"❌ {model} non disponibile, saltando...")
                result = LLMTestResult(
                    model_name=model,
                    response_time=0,
                    response_length=0,
                    has_code=False,
                    has_indicators=False,
                    has_risk_management=False,
                    has_entry_exit_rules=False,
                    has_backtest_ready=False,
                    quality_score=0,
                    response_text="",
                    error="Model not available"
                )
                results.append(result)
                continue
            
            # Esegui query
            response, response_time = self.query_llm(model, self.complex_strategy_prompt)
            
            if response is None:
                result = LLMTestResult(
                    model_name=model,
                    response_time=0,
                    response_length=0,
                    has_code=False,
                    has_indicators=False,
                    has_risk_management=False,
                    has_entry_exit_rules=False,
                    has_backtest_ready=False,
                    quality_score=0,
                    response_text="",
                    error="Query failed"
                )
            else:
                # Analizza qualità
                analysis = self.analyze_response_quality(response)
                
                result = LLMTestResult(
                    model_name=model,
                    response_time=response_time,
                    response_length=analysis["response_length"],
                    has_code=analysis["has_code"],
                    has_indicators=analysis["has_indicators"],
                    has_risk_management=analysis["has_risk_management"],
                    has_entry_exit_rules=analysis["has_entry_exit_rules"],
                    has_backtest_ready=analysis["has_backtest_ready"],
                    quality_score=analysis["quality_score"],
                    response_text=response
                )
            
            results.append(result)
            
            # Mostra risultati parziali
            print(f"📈 {model}: Score {result.quality_score}/100, Tempo {result.response_time:.2f}s")
        
        return results

    def generate_report(self, results: List[LLMTestResult]) -> str:
        """Genera un report dettagliato dei risultati"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Statistiche generali
        successful_results = [r for r in results if r.error is None]
        avg_quality = statistics.mean([r.quality_score for r in successful_results]) if successful_results else 0
        avg_time = statistics.mean([r.response_time for r in successful_results]) if successful_results else 0
        
        # Ranking per qualità
        quality_ranking = sorted(successful_results, key=lambda x: x.quality_score, reverse=True)
        
        # Ranking per velocità
        speed_ranking = sorted(successful_results, key=lambda x: x.response_time)
        
        report = f"""
# REPORT TEST GENERAZIONE STRATEGIE TRADING
## Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## STATISTICHE GENERALI
- Modelli testati: {len(results)}
- Modelli con successo: {len(successful_results)}
- Qualità media: {avg_quality:.1f}/100
- Tempo medio: {avg_time:.2f}s

## RANKING PER QUALITÀ
"""
        
        for i, result in enumerate(quality_ranking, 1):
            report += f"""
{i}. **{result.model_name}** - Score: {result.quality_score}/100
   - Tempo: {result.response_time:.2f}s
   - Lunghezza: {result.response_length} caratteri
   - Codice: {'✅' if result.has_code else '❌'}
   - Indicatori: {'✅' if result.has_indicators else '❌'}
   - Risk Management: {'✅' if result.has_risk_management else '❌'}
   - Entry/Exit: {'✅' if result.has_entry_exit_rules else '❌'}
   - Backtest Ready: {'✅' if result.has_backtest_ready else '❌'}
"""
        
        report += f"""
## RANKING PER VELOCITÀ
"""
        
        for i, result in enumerate(speed_ranking, 1):
            report += f"{i}. **{result.model_name}** - {result.response_time:.2f}s (Score: {result.quality_score}/100)\n"
        
        report += f"""
## MODELLI CON ERRORI
"""
        
        for result in results:
            if result.error:
                report += f"- **{result.model_name}**: {result.error}\n"
        
        report += f"""
## RACCOMANDAZIONI

### 🥇 MIGLIORE QUALITÀ: {quality_ranking[0].model_name if quality_ranking else 'N/A'}
- Score: {quality_ranking[0].quality_score if quality_ranking else 0}/100
- Ideale per: Generazione strategie complesse e accurate

### ⚡ PIÙ VELOCE: {speed_ranking[0].model_name if speed_ranking else 'N/A'}
- Tempo: {speed_ranking[0].response_time if speed_ranking else 0:.2f}s
- Ideale per: Test rapidi e iterazioni veloci

### 🎯 BILANCIATO: 
- Cerca il miglior compromesso qualità/velocità
- Considera: {', '.join([r.model_name for r in quality_ranking[:3] if r.response_time < avg_time * 1.5])}

## CONCLUSIONI
- Il modello {quality_ranking[0].model_name if quality_ranking else 'N/A'} offre la migliore qualità
- Il modello {speed_ranking[0].model_name if speed_ranking else 'N/A'} è il più veloce
- Considera l'uso di modelli diversi per fasi diverse del processo di sviluppo
"""
        
        return report

    def save_results(self, results: List[LLMTestResult], report: str):
        """Salva i risultati su file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva report
        report_file = f"llm_strategy_test_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Salva risultati dettagliati
        results_file = f"llm_strategy_test_results_{timestamp}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(r) for r in results], f, indent=2, ensure_ascii=False)
        
        # Salva risposte complete
        responses_file = f"llm_strategy_responses_{timestamp}.json"
        responses_data = {}
        for result in results:
            if result.response_text:
                responses_data[result.model_name] = {
                    "response": result.response_text,
                    "quality_score": result.quality_score,
                    "response_time": result.response_time
                }
        
        with open(responses_file, 'w', encoding='utf-8') as f:
            json.dump(responses_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Risultati salvati:")
        print(f"   📄 Report: {report_file}")
        print(f"   📊 Dati: {results_file}")
        print(f"   📝 Risposte: {responses_file}")

def main():
    """Funzione principale"""
    print("🚀 TEST COMPLETO GENERAZIONE STRATEGIE TRADING")
    print("=" * 60)
    
    tester = LLMStrategyTester()
    
    # Esegui test
    results = tester.run_comprehensive_test()
    
    # Genera report
    report = tester.generate_report(results)
    
    # Salva risultati
    tester.save_results(results, report)
    
    # Mostra report
    print("\n" + "=" * 60)
    print("📊 REPORT FINALE")
    print("=" * 60)
    print(report)

if __name__ == "__main__":
    main() 