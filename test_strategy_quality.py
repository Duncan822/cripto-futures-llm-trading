#!/usr/bin/env python3
"""
Test della qualità pratica della strategia generata da cogito:8b
"""

import json
import re
import ast
import sys
from typing import Dict, List, Any, Optional

class StrategyQualityTester:
    def __init__(self):
        self.responses_file = "llm_strategy_responses_20250703_004302.json"
        
    def load_responses(self) -> Dict[str, Any]:
        """Carica le risposte degli LLM"""
        try:
            with open(self.responses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ File {self.responses_file} non trovato")
            return {}
    
    def extract_code_from_response(self, response: str) -> Optional[str]:
        """Estrae il codice Python dalla risposta"""
        # Cerca blocchi di codice Python
        code_patterns = [
            r'```python\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'class\s+\w+.*?:\s*\n(.*?)(?=\n\n|\nclass|\Z)',
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """Analizza la qualità del codice Python"""
        analysis = {
            "syntax_valid": False,
            "has_class_definition": False,
            "has_imports": False,
            "has_methods": False,
            "has_indicators": False,
            "has_risk_management": False,
            "has_entry_exit_logic": False,
            "has_parameters": False,
            "code_length": len(code),
            "error": None
        }
        
        if not code:
            analysis["error"] = "No code found"
            return analysis
        
        # Test sintassi
        try:
            ast.parse(code)
            analysis["syntax_valid"] = True
        except SyntaxError as e:
            analysis["error"] = f"Syntax error: {e}"
            return analysis
        
        # Analisi del contenuto
        code_lower = code.lower()
        
        # Controlla presenza di classi
        analysis["has_class_definition"] = "class " in code
        
        # Controlla import
        analysis["has_imports"] = any(imp in code for imp in [
            "import ", "from ", "freqtrade", "talib", "numpy", "pandas"
        ])
        
        # Controlla metodi
        analysis["has_methods"] = "def " in code
        
        # Controlla indicatori tecnici
        analysis["has_indicators"] = any(indicator in code_lower for indicator in [
            "rsi", "macd", "bollinger", "stochastic", "ichimoku", "volume", "ema", "sma"
        ])
        
        # Controlla gestione del rischio
        analysis["has_risk_management"] = any(risk_term in code_lower for risk_term in [
            "stop loss", "take profit", "position size", "risk", "drawdown", "volatility"
        ])
        
        # Controlla logica entry/exit
        analysis["has_entry_exit_logic"] = any(logic_term in code_lower for logic_term in [
            "entry", "exit", "buy", "sell", "long", "short", "signal"
        ])
        
        # Controlla parametri
        analysis["has_parameters"] = any(param_term in code_lower for param_term in [
            "parameter", "config", "setting", "option"
        ])
        
        return analysis
    
    def test_strategy_execution(self, code: str) -> Dict[str, Any]:
        """Testa l'esecuzione della strategia (simulazione)"""
        test_result = {
            "can_instantiate": False,
            "has_required_methods": False,
            "method_signatures_valid": False,
            "error": None
        }
        
        try:
            # Analizza il codice per trovare la classe principale
            tree = ast.parse(code)
            
            # Cerca la classe strategy
            strategy_class = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if any(base in str(node.bases) for base in ['Strategy', 'IStrategy']):
                        strategy_class = node
                        break
            
            if not strategy_class:
                test_result["error"] = "No strategy class found"
                return test_result
            
            # Controlla metodi richiesti
            required_methods = ['populate_indicators', 'populate_buy_trend', 'populate_sell_trend']
            found_methods = []
            
            for node in strategy_class.body:
                if isinstance(node, ast.FunctionDef):
                    found_methods.append(node.name)
            
            test_result["has_required_methods"] = all(method in found_methods for method in required_methods)
            
            # Controlla firme dei metodi
            valid_signatures = 0
            for method_name in required_methods:
                for node in strategy_class.body:
                    if isinstance(node, ast.FunctionDef) and node.name == method_name:
                        # Controlla se ha i parametri corretti
                        if len(node.args.args) >= 2:  # dataframe e metadata
                            valid_signatures += 1
                        break
            
            test_result["method_signatures_valid"] = valid_signatures == len(required_methods)
            test_result["can_instantiate"] = True
            
        except Exception as e:
            test_result["error"] = f"Execution test error: {e}"
        
        return test_result
    
    def calculate_practical_score(self, code_analysis: Dict[str, Any], execution_test: Dict[str, Any]) -> float:
        """Calcola un punteggio pratico per la strategia"""
        score = 0.0
        
        # Punteggio per sintassi valida
        if code_analysis["syntax_valid"]:
            score += 20
        
        # Punteggio per struttura
        if code_analysis["has_class_definition"]:
            score += 10
        if code_analysis["has_imports"]:
            score += 10
        if code_analysis["has_methods"]:
            score += 10
        
        # Punteggio per funzionalità
        if code_analysis["has_indicators"]:
            score += 15
        if code_analysis["has_risk_management"]:
            score += 15
        if code_analysis["has_entry_exit_logic"]:
            score += 15
        if code_analysis["has_parameters"]:
            score += 5
        
        # Punteggio per esecuzione
        if execution_test["can_instantiate"]:
            score += 10
        if execution_test["has_required_methods"]:
            score += 10
        if execution_test["method_signatures_valid"]:
            score += 10
        
        # Bonus per lunghezza del codice (max 10 punti)
        length_bonus = min(10, code_analysis["code_length"] // 500)
        score += length_bonus
        
        return min(100, score)
    
    def test_best_strategy(self) -> Dict[str, Any]:
        """Testa la strategia migliore (cogito:8b)"""
        print("🔍 Testando la strategia di cogito:8b...")
        
        responses = self.load_responses()
        if not responses:
            return {"error": "No responses found"}
        
        # Prendi la strategia di cogito:8b
        cogito_response = responses.get("cogito:8b", {})
        if not cogito_response:
            return {"error": "cogito:8b response not found"}
        
        response_text = cogito_response.get("response", "")
        if not response_text:
            return {"error": "Empty response from cogito:8b"}
        
        # Estrai il codice
        code = self.extract_code_from_response(response_text)
        if not code:
            return {"error": "No code found in cogito:8b response"}
        
        print(f"📝 Codice estratto: {len(code)} caratteri")
        
        # Analizza qualità del codice
        code_analysis = self.analyze_code_quality(code)
        print("🔍 Analisi codice completata")
        
        # Test esecuzione
        execution_test = self.test_strategy_execution(code)
        print("⚡ Test esecuzione completato")
        
        # Calcola punteggio pratico
        practical_score = self.calculate_practical_score(code_analysis, execution_test)
        
        # Risultati completi
        results = {
            "model": "cogito:8b",
            "code_length": len(code),
            "code_analysis": code_analysis,
            "execution_test": execution_test,
            "practical_score": practical_score,
            "code_preview": code[:500] + "..." if len(code) > 500 else code
        }
        
        return results
    
    def generate_practical_report(self, results: Dict[str, Any]) -> str:
        """Genera un report pratico dei risultati"""
        if "error" in results:
            return f"❌ Errore: {results['error']}"
        
        report = f"""
# REPORT TEST PRATICO STRATEGIA COGITO:8B
## Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 RISULTATI GENERALI
- **Modello**: {results['model']}
- **Lunghezza codice**: {results['code_length']} caratteri
- **Punteggio pratico**: {results['practical_score']}/100

## 🔍 ANALISI CODICE
- **Sintassi valida**: {'✅' if results['code_analysis']['syntax_valid'] else '❌'}
- **Classe definita**: {'✅' if results['code_analysis']['has_class_definition'] else '❌'}
- **Import presenti**: {'✅' if results['code_analysis']['has_imports'] else '❌'}
- **Metodi definiti**: {'✅' if results['code_analysis']['has_methods'] else '❌'}
- **Indicatori tecnici**: {'✅' if results['code_analysis']['has_indicators'] else '❌'}
- **Gestione rischio**: {'✅' if results['code_analysis']['has_risk_management'] else '❌'}
- **Logica entry/exit**: {'✅' if results['code_analysis']['has_entry_exit_logic'] else '❌'}
- **Parametri configurabili**: {'✅' if results['code_analysis']['has_parameters'] else '❌'}

## ⚡ TEST ESECUZIONE
- **Può essere istanziato**: {'✅' if results['execution_test']['can_instantiate'] else '❌'}
- **Metodi richiesti presenti**: {'✅' if results['execution_test']['has_required_methods'] else '❌'}
- **Firme metodi valide**: {'✅' if results['execution_test']['method_signatures_valid'] else '❌'}

## 📝 ANTEPRIMA CODICE
```
{results['code_preview']}
```

## 🎯 VALUTAZIONE PRATICA

### Punti di Forza:
"""
        
        strengths = []
        if results['code_analysis']['syntax_valid']:
            strengths.append("- Codice Python sintatticamente corretto")
        if results['code_analysis']['has_indicators']:
            strengths.append("- Include indicatori tecnici avanzati")
        if results['code_analysis']['has_risk_management']:
            strengths.append("- Implementa gestione del rischio")
        if results['code_analysis']['has_entry_exit_logic']:
            strengths.append("- Definisce logica di entry/exit")
        if results['execution_test']['has_required_methods']:
            strengths.append("- Ha i metodi richiesti da FreqTrade")
        
        report += "\n".join(strengths) if strengths else "- Nessun punto di forza identificato"
        
        report += "\n\n### Aree di Miglioramento:\n"
        
        improvements = []
        if not results['code_analysis']['syntax_valid']:
            improvements.append("- Correggere errori di sintassi")
        if not results['execution_test']['has_required_methods']:
            improvements.append("- Aggiungere metodi mancanti di FreqTrade")
        if not results['execution_test']['method_signatures_valid']:
            improvements.append("- Correggere firme dei metodi")
        if not results['code_analysis']['has_parameters']:
            improvements.append("- Aggiungere parametri configurabili")
        
        report += "\n".join(improvements) if improvements else "- Nessuna area di miglioramento critica"
        
        report += f"""

## 🏆 RACCOMANDAZIONE FINALE

**Punteggio**: {results['practical_score']}/100

"""
        
        if results['practical_score'] >= 80:
            report += "**✅ ECCELLENTE**: La strategia è pronta per il backtest con modifiche minime."
        elif results['practical_score'] >= 60:
            report += "**🟡 BUONO**: La strategia richiede alcune modifiche prima del backtest."
        elif results['practical_score'] >= 40:
            report += "**🟠 ACCETTABILE**: La strategia necessita di lavoro significativo."
        else:
            report += "**❌ INSUFFICIENTE**: La strategia richiede una riscrittura completa."
        
        return report

def main():
    """Funzione principale"""
    print("🚀 TEST PRATICO STRATEGIA COGITO:8B")
    print("=" * 50)
    
    tester = StrategyQualityTester()
    
    # Testa la strategia
    results = tester.test_best_strategy()
    
    # Genera report
    report = tester.generate_practical_report(results)
    
    # Salva report
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"practical_strategy_test_report_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Report salvato: {report_file}")
    print("\n" + "=" * 50)
    print("📊 REPORT PRATICO")
    print("=" * 50)
    print(report)

if __name__ == "__main__":
    main() 