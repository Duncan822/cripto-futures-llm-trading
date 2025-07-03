#!/usr/bin/env python3
"""
Validazione della qualità della strategia generata da cogito:8b
"""

import json
import re
import ast
from typing import Dict, List, Any, Optional

class StrategyValidator:
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
        code_patterns = [
            r'```python\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        return None
    
    def analyze_strategy_structure(self, code: str) -> Dict[str, Any]:
        """Analizza la struttura della strategia"""
        analysis = {
            "class_name": None,
            "base_class": None,
            "methods": [],
            "parameters": [],
            "indicators": [],
            "risk_management": [],
            "entry_conditions": [],
            "exit_conditions": [],
            "imports": [],
            "code_quality": {}
        }
        
        try:
            tree = ast.parse(code)
            
            # Analizza import
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        analysis["imports"].append(f"{module}.{alias.name}")
            
            # Analizza classi
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis["class_name"] = node.name
                    
                    # Controlla classe base
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            analysis["base_class"] = base.id
                        elif isinstance(base, ast.Attribute):
                            analysis["base_class"] = f"{base.value.id}.{base.attr}"
                    
                    # Analizza metodi
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "args": [arg.arg for arg in item.args.args],
                                "docstring": ast.get_docstring(item) or ""
                            }
                            analysis["methods"].append(method_info)
                            
                            # Analizza contenuto del metodo
                            method_code = ast.unparse(item) if hasattr(ast, 'unparse') else str(item)
                            
                            # Cerca indicatori
                            if any(indicator in method_code.lower() for indicator in ['rsi', 'macd', 'bollinger', 'stochastic', 'ichimoku']):
                                analysis["indicators"].append(item.name)
                            
                            # Cerca gestione rischio
                            if any(risk_term in method_code.lower() for risk_term in ['stop', 'loss', 'risk', 'position', 'size']):
                                analysis["risk_management"].append(item.name)
                            
                            # Cerca condizioni entry/exit
                            if any(condition in method_code.lower() for condition in ['buy', 'sell', 'entry', 'exit']):
                                if 'buy' in method_code.lower():
                                    analysis["entry_conditions"].append(item.name)
                                if 'sell' in method_code.lower():
                                    analysis["exit_conditions"].append(item.name)
                    
                    # Analizza attributi di classe (parametri)
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    analysis["parameters"].append(target.id)
            
        except SyntaxError as e:
            analysis["code_quality"]["syntax_error"] = str(e)
        except Exception as e:
            analysis["code_quality"]["error"] = str(e)
        
        return analysis
    
    def calculate_completeness_score(self, analysis: Dict[str, Any]) -> float:
        """Calcola un punteggio di completezza"""
        score = 0.0
        
        # Punteggio per struttura base
        if analysis["class_name"]:
            score += 10
        if analysis["base_class"]:
            score += 10
        
        # Punteggio per metodi essenziali
        method_names = [m["name"] for m in analysis["methods"]]
        essential_methods = ['populate_indicators', 'populate_buy_trend', 'populate_sell_trend']
        for method in essential_methods:
            if method in method_names:
                score += 15
        
        # Punteggio per indicatori
        if analysis["indicators"]:
            score += 15
        
        # Punteggio per gestione rischio
        if analysis["risk_management"]:
            score += 15
        
        # Punteggio per condizioni entry/exit
        if analysis["entry_conditions"]:
            score += 10
        if analysis["exit_conditions"]:
            score += 10
        
        # Punteggio per parametri
        if analysis["parameters"]:
            score += 5
        
        return min(100, score)
    
    def compare_strategies(self) -> Dict[str, Any]:
        """Confronta le strategie di tutti i modelli"""
        print("🔍 Confrontando le strategie di tutti i modelli...")
        
        responses = self.load_responses()
        if not responses:
            return {"error": "No responses found"}
        
        comparison = {}
        
        for model_name, response_data in responses.items():
            print(f"📊 Analizzando {model_name}...")
            
            response_text = response_data.get("response", "")
            code = self.extract_code_from_response(response_text)
            
            if code:
                analysis = self.analyze_strategy_structure(code)
                completeness_score = self.calculate_completeness_score(analysis)
                
                comparison[model_name] = {
                    "code_length": len(code),
                    "completeness_score": completeness_score,
                    "class_name": analysis["class_name"],
                    "base_class": analysis["base_class"],
                    "methods_count": len(analysis["methods"]),
                    "indicators_count": len(analysis["indicators"]),
                    "risk_management_count": len(analysis["risk_management"]),
                    "entry_conditions_count": len(analysis["entry_conditions"]),
                    "exit_conditions_count": len(analysis["exit_conditions"]),
                    "parameters_count": len(analysis["parameters"]),
                    "has_essential_methods": all(method in [m["name"] for m in analysis["methods"]] 
                                               for method in ['populate_indicators', 'populate_buy_trend', 'populate_sell_trend']),
                    "analysis": analysis
                }
            else:
                comparison[model_name] = {
                    "error": "No code found"
                }
        
        return comparison
    
    def generate_comparison_report(self, comparison: Dict[str, Any]) -> str:
        """Genera un report di confronto"""
        if "error" in comparison:
            return f"❌ Errore: {comparison['error']}"
        
        # Ordina per punteggio di completezza
        sorted_models = sorted(
            [(name, data) for name, data in comparison.items() if "error" not in data],
            key=lambda x: x[1]["completeness_score"],
            reverse=True
        )
        
        report = f"""
# REPORT CONFRONTO STRATEGIE LLM
## Data: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🏆 RANKING PER COMPLETEZZA
"""
        
        for i, (model_name, data) in enumerate(sorted_models, 1):
            report += f"""
{i}. **{model_name}** - Score: {data['completeness_score']}/100
   - Classe: {data['class_name'] or 'N/A'} (Base: {data['base_class'] or 'N/A'})
   - Metodi: {data['methods_count']} (Essenziali: {'✅' if data['has_essential_methods'] else '❌'})
   - Indicatori: {data['indicators_count']}
   - Risk Management: {data['risk_management_count']}
   - Entry/Exit: {data['entry_conditions_count']}/{data['exit_conditions_count']}
   - Parametri: {data['parameters_count']}
   - Codice: {data['code_length']} caratteri
"""
        
        # Trova il migliore
        best_model = sorted_models[0] if sorted_models else None
        
        report += f"""
## 🎯 ANALISI DETTAGLIATA DEL MIGLIORE: {best_model[0] if best_model else 'N/A'}

"""
        
        if best_model:
            model_name, data = best_model
            analysis = data["analysis"]
            
            report += f"""
### Struttura Classe
- **Nome**: {analysis['class_name']}
- **Classe Base**: {analysis['base_class']}
- **Metodi Totali**: {len(analysis['methods'])}

### Metodi Implementati
"""
            
            for method in analysis["methods"]:
                report += f"- **{method['name']}**: {len(method['args'])} parametri\n"
            
            report += f"""
### Indicatori Tecnici
- {', '.join(analysis['indicators']) if analysis['indicators'] else 'Nessuno identificato'}

### Gestione del Rischio
- {', '.join(analysis['risk_management']) if analysis['risk_management'] else 'Nessuna implementata'}

### Condizioni di Trading
- **Entry**: {', '.join(analysis['entry_conditions']) if analysis['entry_conditions'] else 'Nessuna'}
- **Exit**: {', '.join(analysis['exit_conditions']) if analysis['exit_conditions'] else 'Nessuna'}

### Parametri Configurabili
- {', '.join(analysis['parameters']) if analysis['parameters'] else 'Nessuno'}
"""
        
        report += f"""
## 📊 STATISTICHE GENERALI
- **Modelli analizzati**: {len(comparison)}
- **Modelli con codice**: {len([d for d in comparison.values() if 'error' not in d])}
- **Punteggio medio**: {sum(d['completeness_score'] for d in comparison.values() if 'error' not in d) / len([d for d in comparison.values() if 'error' not in d]):.1f}/100

## 🏆 RACCOMANDAZIONI FINALI

### 🥇 MIGLIORE STRATEGIA: {best_model[0] if best_model else 'N/A'}
- **Punteggio**: {best_model[1]['completeness_score'] if best_model else 0}/100
- **Raccomandazione**: {'Pronto per implementazione con modifiche minime' if best_model and best_model[1]['completeness_score'] >= 80 else 'Richiede lavoro significativo'}

### 🎯 CRITERI DI SELEZIONE
1. **Completezza**: Presenza di tutti i metodi essenziali
2. **Indicatori**: Varietà di indicatori tecnici implementati
3. **Risk Management**: Gestione del rischio integrata
4. **Struttura**: Codice ben organizzato e leggibile
5. **Parametri**: Configurabilità per ottimizzazione

### 📈 PROSSIMI PASSI
1. Implementare la strategia del modello migliore
2. Correggere eventuali errori di sintassi
3. Aggiungere metodi mancanti se necessario
4. Testare con backtest su dati storici
5. Ottimizzare parametri per massimizzare performance
"""
        
        return report

def main():
    """Funzione principale"""
    print("🚀 CONFRONTO STRATEGIE LLM")
    print("=" * 50)
    
    validator = StrategyValidator()
    
    # Confronta strategie
    comparison = validator.compare_strategies()
    
    # Genera report
    report = validator.generate_comparison_report(comparison)
    
    # Salva report
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"strategy_comparison_report_{timestamp}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Report salvato: {report_file}")
    print("\n" + "=" * 50)
    print("📊 REPORT CONFRONTO")
    print("=" * 50)
    print(report)

if __name__ == "__main__":
    main() 