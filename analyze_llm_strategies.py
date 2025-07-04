#!/usr/bin/env python3
"""
Analizzatore delle strategie generate dagli LLM
Identifica punti deboli e aree di miglioramento
"""

import os
import re
import json
import ast
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

class LLMStrategyAnalyzer:
    def __init__(self):
        self.strategies_dir = "user_data/strategies"
        self.analysis_results = {}
        
    def analyze_all_strategies(self) -> Dict[str, Any]:
        """Analizza tutte le strategie generate dagli LLM."""
        print("🔍 Analisi delle strategie generate dagli LLM...")
        
        # Trova tutte le strategie
        strategy_files = self._find_strategy_files()
        print(f"📁 Trovate {len(strategy_files)} strategie")
        
        # Analizza ogni strategia
        for file_path in strategy_files:
            try:
                analysis = self._analyze_single_strategy(file_path)
                self.analysis_results[file_path] = analysis
            except Exception as e:
                print(f"❌ Errore nell'analisi di {file_path}: {e}")
        
        # Analisi aggregata
        aggregate_analysis = self._create_aggregate_analysis()
        
        return {
            'individual_strategies': self.analysis_results,
            'aggregate_analysis': aggregate_analysis,
            'recommendations': self._generate_recommendations(aggregate_analysis)
        }
    
    def _find_strategy_files(self) -> List[str]:
        """Trova tutti i file di strategia generati dagli LLM."""
        strategy_files = []
        
        if not os.path.exists(self.strategies_dir):
            return strategy_files
        
        for file in os.listdir(self.strategies_dir):
            if file.endswith('.py') and not file.startswith('__'):
                # Filtra strategie generate da LLM (contengono timestamp o nomi di modelli)
                if any(pattern in file.lower() for pattern in [
                    'llm', 'cogito', 'mistral', 'phi', 'cooperative', 'contest'
                ]) or re.search(r'\d{8}_\d{6}', file):
                    strategy_files.append(os.path.join(self.strategies_dir, file))
        
        return strategy_files
    
    def _analyze_single_strategy(self, file_path: str) -> Dict[str, Any]:
        """Analizza una singola strategia."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(file_path)
        
        analysis = {
            'filename': filename,
            'file_size': len(content),
            'lines_of_code': len(content.split('\n')),
            'syntax_valid': False,
            'class_name': None,
            'indicators_used': [],
            'entry_conditions': [],
            'exit_conditions': [],
            'risk_management': {},
            'optimization_params': [],
            'code_quality': {},
            'potential_issues': [],
            'strengths': [],
            'model_used': self._extract_model_name(filename),
            'strategy_type': self._extract_strategy_type(filename),
            'generation_date': self._extract_generation_date(filename)
        }
        
        # Analisi sintassi
        try:
            ast.parse(content)
            analysis['syntax_valid'] = True
        except SyntaxError as e:
            analysis['potential_issues'].append(f"Errore di sintassi: {e}")
        
        # Analisi del contenuto
        if analysis['syntax_valid']:
            self._analyze_strategy_content(content, analysis)
        
        return analysis
    
    def _analyze_strategy_content(self, content: str, analysis: Dict[str, Any]):
        """Analizza il contenuto della strategia."""
        # Estrai nome classe
        class_match = re.search(r'class\s+(\w+)', content)
        if class_match:
            analysis['class_name'] = class_match.group(1)
        
        # Analizza indicatori
        indicators = re.findall(r'ta\.(\w+)\(', content)
        analysis['indicators_used'] = list(set(indicators))
        
        # Analizza condizioni di entrata
        entry_patterns = [
            r"dataframe\.loc\[(.*?), 'enter_long'\] = 1",
            r"dataframe\['enter_long'\] = (.*?)",
        ]
        for pattern in entry_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            analysis['entry_conditions'].extend(matches)
        
        # Analizza condizioni di uscita
        exit_patterns = [
            r"dataframe\.loc\[(.*?), 'exit_long'\] = 1",
            r"dataframe\['exit_long'\] = (.*?)",
        ]
        for pattern in exit_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            analysis['exit_conditions'].extend(matches)
        
        # Analizza gestione del rischio
        if 'stoploss' in content:
            analysis['risk_management']['stoploss'] = True
        if 'trailing_stop' in content:
            analysis['risk_management']['trailing_stop'] = True
        if 'minimal_roi' in content:
            analysis['risk_management']['roi'] = True
        
        # Analizza parametri di ottimizzazione
        opt_params = re.findall(r'(\w+)\s*=\s*IntParameter|DecimalParameter', content)
        analysis['optimization_params'] = opt_params
        
        # Analizza qualità del codice
        analysis['code_quality'] = self._analyze_code_quality(content)
        
        # Identifica punti di forza e debolezza
        self._identify_strengths_weaknesses(content, analysis)
    
    def _analyze_code_quality(self, content: str) -> Dict[str, Any]:
        """Analizza la qualità del codice."""
        quality = {
            'has_docstrings': bool(re.search(r'""".*?"""', content, re.DOTALL)),
            'has_comments': len(re.findall(r'#.*', content)) > 0,
            'has_logging': 'logger' in content,
            'has_type_hints': bool(re.search(r':\s*(DataFrame|dict|str|int|float)', content)),
            'has_error_handling': bool(re.search(r'try:|except:', content)),
            'code_complexity': self._calculate_complexity(content)
        }
        return quality
    
    def _calculate_complexity(self, content: str) -> int:
        """Calcola la complessità del codice."""
        complexity = 0
        complexity += len(re.findall(r'if\s+', content))
        complexity += len(re.findall(r'for\s+', content))
        complexity += len(re.findall(r'while\s+', content))
        complexity += len(re.findall(r'and\s+', content))
        complexity += len(re.findall(r'or\s+', content))
        return complexity
    
    def _identify_strengths_weaknesses(self, content: str, analysis: Dict[str, Any]):
        """Identifica punti di forza e debolezza."""
        # Punti di forza
        if len(analysis['indicators_used']) > 2:
            analysis['strengths'].append("Usa multipli indicatori")
        if analysis['risk_management'].get('trailing_stop'):
            analysis['strengths'].append("Ha trailing stop")
        if analysis['optimization_params']:
            analysis['strengths'].append("Parametri ottimizzabili")
        if analysis['code_quality']['has_docstrings']:
            analysis['strengths'].append("Documentazione presente")
        
        # Punti deboli
        if len(analysis['indicators_used']) < 2:
            analysis['potential_issues'].append("Troppo pochi indicatori")
        if not analysis['risk_management'].get('stoploss'):
            analysis['potential_issues'].append("Manca stoploss")
        if not analysis['entry_conditions']:
            analysis['potential_issues'].append("Condizioni di entrata mancanti")
        if not analysis['exit_conditions']:
            analysis['potential_issues'].append("Condizioni di uscita mancanti")
        if analysis['code_quality']['code_complexity'] < 3:
            analysis['potential_issues'].append("Strategia troppo semplice")
        if analysis['code_quality']['code_complexity'] > 20:
            analysis['potential_issues'].append("Strategia troppo complessa")
    
    def _extract_model_name(self, filename: str) -> str:
        """Estrae il nome del modello dal filename."""
        models = ['cogito', 'mistral', 'phi', 'llama', 'cooperative']
        for model in models:
            if model in filename.lower():
                return model
        return "unknown"
    
    def _extract_strategy_type(self, filename: str) -> str:
        """Estrae il tipo di strategia dal filename."""
        types = ['scalping', 'volatility', 'momentum', 'breakout', 'adaptive']
        for strategy_type in types:
            if strategy_type in filename.lower():
                return strategy_type
        return "unknown"
    
    def _extract_generation_date(self, filename: str) -> str:
        """Estrae la data di generazione dal filename."""
        date_match = re.search(r'(\d{8}_\d{6})', filename)
        if date_match:
            return date_match.group(1)
        return "unknown"
    
    def _create_aggregate_analysis(self) -> Dict[str, Any]:
        """Crea un'analisi aggregata di tutte le strategie."""
        if not self.analysis_results:
            return {}
        
        aggregate = {
            'total_strategies': len(self.analysis_results),
            'syntax_valid_count': sum(1 for a in self.analysis_results.values() if a['syntax_valid']),
            'models_used': {},
            'strategy_types': {},
            'common_indicators': {},
            'common_issues': {},
            'quality_metrics': {
                'avg_complexity': 0,
                'has_docstrings': 0,
                'has_optimization': 0,
                'has_risk_management': 0
            }
        }
        
        # Analizza modelli e tipi
        for analysis in self.analysis_results.values():
            model = analysis['model_used']
            strategy_type = analysis['strategy_type']
            
            aggregate['models_used'][model] = aggregate['models_used'].get(model, 0) + 1
            aggregate['strategy_types'][strategy_type] = aggregate['strategy_types'].get(strategy_type, 0) + 1
        
        # Analizza indicatori comuni
        all_indicators = []
        for analysis in self.analysis_results.values():
            all_indicators.extend(analysis['indicators_used'])
        
        for indicator in all_indicators:
            aggregate['common_indicators'][indicator] = aggregate['common_indicators'].get(indicator, 0) + 1
        
        # Analizza problemi comuni
        all_issues = []
        for analysis in self.analysis_results.values():
            all_issues.extend(analysis['potential_issues'])
        
        for issue in all_issues:
            aggregate['common_issues'][issue] = aggregate['common_issues'].get(issue, 0) + 1
        
        # Calcola metriche di qualità
        total_complexity = sum(a.get('code_quality', {}).get('code_complexity', 0) for a in self.analysis_results.values())
        aggregate['quality_metrics']['avg_complexity'] = total_complexity / len(self.analysis_results) if self.analysis_results else 0
        
        aggregate['quality_metrics']['has_docstrings'] = sum(
            1 for a in self.analysis_results.values() if a.get('code_quality', {}).get('has_docstrings', False)
        )
        
        aggregate['quality_metrics']['has_optimization'] = sum(
            1 for a in self.analysis_results.values() if a.get('optimization_params', [])
        )
        
        aggregate['quality_metrics']['has_risk_management'] = sum(
            1 for a in self.analysis_results.values() if a.get('risk_management', {})
        )
        
        return aggregate
    
    def _generate_recommendations(self, aggregate_analysis: Dict[str, Any]) -> List[str]:
        """Genera raccomandazioni basate sull'analisi."""
        recommendations = []
        
        if not aggregate_analysis:
            return recommendations
        
        # Raccomandazioni basate sui problemi comuni
        if aggregate_analysis['common_issues']:
            most_common_issue = max(aggregate_analysis['common_issues'].items(), key=lambda x: x[1])
            recommendations.append(f"Problema più comune: {most_common_issue[0]} ({most_common_issue[1]} strategie)")
        
        # Raccomandazioni sulla qualità
        if aggregate_analysis['quality_metrics']['has_docstrings'] < aggregate_analysis['total_strategies'] * 0.5:
            recommendations.append("Migliorare la documentazione delle strategie")
        
        if aggregate_analysis['quality_metrics']['has_optimization'] < aggregate_analysis['total_strategies'] * 0.3:
            recommendations.append("Aggiungere più parametri ottimizzabili")
        
        if aggregate_analysis['quality_metrics']['has_risk_management'] < aggregate_analysis['total_strategies'] * 0.8:
            recommendations.append("Migliorare la gestione del rischio")
        
        # Raccomandazioni sui modelli
        if aggregate_analysis['models_used']:
            best_model = max(aggregate_analysis['models_used'].items(), key=lambda x: x[1])
            recommendations.append(f"Modello più utilizzato: {best_model[0]} ({best_model[1]} strategie)")
        
        # Raccomandazioni sugli indicatori
        if aggregate_analysis['common_indicators']:
            most_used_indicator = max(aggregate_analysis['common_indicators'].items(), key=lambda x: x[1])
            recommendations.append(f"Indicatore più utilizzato: {most_used_indicator[0]} ({most_used_indicator[1]} volte)")
        
        return recommendations
    
    def print_analysis_report(self, analysis: Dict[str, Any]):
        """Stampa un report dell'analisi."""
        print("\n" + "="*80)
        print("📊 REPORT ANALISI STRATEGIE LLM")
        print("="*80)
        
        if 'aggregate_analysis' in analysis:
            agg = analysis['aggregate_analysis']
            print(f"\n📈 STATISTICHE GENERALI:")
            print(f"   • Strategie totali: {agg['total_strategies']}")
            print(f"   • Strategie valide: {agg['syntax_valid_count']}")
            print(f"   • Tasso di successo: {agg['syntax_valid_count']/agg['total_strategies']*100:.1f}%")
            
            print(f"\n🤖 MODELLI UTILIZZATI:")
            for model, count in agg['models_used'].items():
                print(f"   • {model}: {count} strategie")
            
            print(f"\n📊 TIPI DI STRATEGIA:")
            for strategy_type, count in agg['strategy_types'].items():
                print(f"   • {strategy_type}: {count} strategie")
            
            print(f"\n📊 INDICATORI PIÙ UTILIZZATI:")
            sorted_indicators = sorted(agg['common_indicators'].items(), key=lambda x: x[1], reverse=True)
            for indicator, count in sorted_indicators[:5]:
                print(f"   • {indicator}: {count} volte")
            
            print(f"\n⚠️ PROBLEMI PIÙ COMUNI:")
            sorted_issues = sorted(agg['common_issues'].items(), key=lambda x: x[1], reverse=True)
            for issue, count in sorted_issues[:5]:
                print(f"   • {issue}: {count} strategie")
            
            print(f"\n📊 METRICHE DI QUALITÀ:")
            qm = agg['quality_metrics']
            print(f"   • Complessità media: {qm['avg_complexity']:.1f}")
            print(f"   • Con documentazione: {qm['has_docstrings']}/{agg['total_strategies']}")
            print(f"   • Con ottimizzazione: {qm['has_optimization']}/{agg['total_strategies']}")
            print(f"   • Con gestione rischio: {qm['has_risk_management']}/{agg['total_strategies']}")
        
        if 'recommendations' in analysis:
            print(f"\n💡 RACCOMANDAZIONI:")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n📋 DETTAGLI STRATEGIE INDIVIDUALI:")
        for file_path, strategy_analysis in analysis['individual_strategies'].items():
            print(f"\n   📄 {strategy_analysis['filename']}")
            print(f"      • Modello: {strategy_analysis['model_used']}")
            print(f"      • Tipo: {strategy_analysis['strategy_type']}")
            print(f"      • Sintassi valida: {'✅' if strategy_analysis['syntax_valid'] else '❌'}")
            print(f"      • Indicatori: {', '.join(strategy_analysis['indicators_used'][:3])}")
            if strategy_analysis['potential_issues']:
                print(f"      • Problemi: {', '.join(strategy_analysis['potential_issues'][:2])}")
            if strategy_analysis['strengths']:
                print(f"      • Punti di forza: {', '.join(strategy_analysis['strengths'][:2])}")

def main():
    analyzer = LLMStrategyAnalyzer()
    analysis = analyzer.analyze_all_strategies()
    analyzer.print_analysis_report(analysis)
    
    # Salva l'analisi in JSON
    with open('llm_strategies_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"\n💾 Analisi salvata in: llm_strategies_analysis.json")

if __name__ == "__main__":
    main() 