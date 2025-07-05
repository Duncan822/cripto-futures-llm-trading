#!/usr/bin/env python3
"""
Test completo per tutte le modalità di generazione strategie.
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Any
from agents.generator import GeneratorAgent
from agents.two_stage_generator import TwoStageGenerator
from agents.code_fixer import CodeFixer
from prompts.adaptive_prompt_generator import AdaptivePromptGenerator

class StrategyGenerationTester:
    """
    Classe per testare tutte le modalità di generazione strategie.
    """
    
    def __init__(self):
        self.generator = GeneratorAgent()
        self.two_stage_generator = TwoStageGenerator()
        self.code_fixer = CodeFixer()
        self.adaptive_prompt_generator = AdaptivePromptGenerator()
        self.test_results = []
        
    def run_complete_test_suite(self):
        """
        Esegue tutti i test per tutte le modalità di generazione.
        """
        print("🚀 Avvio test completo di tutte le modalità di generazione strategie")
        print("=" * 80)
        
        # Test 1: Sistema a due stadi
        print("\n📊 Test 1: Sistema a Due Stadi")
        self.test_two_stage_generation()
        
        # Test 2: Sistema di prompt adattivi
        print("\n📊 Test 2: Sistema di Prompt Adattivi")
        self.test_adaptive_prompt_generation()
        
        # Test 3: Generazione diretta
        print("\n📊 Test 3: Generazione Diretta")
        self.test_direct_generation()
        
        # Test 4: Generazione ensemble
        print("\n📊 Test 4: Generazione Ensemble")
        self.test_ensemble_generation()
        
        # Test 5: Generazione per tipologia
        print("\n📊 Test 5: Generazione per Tipologia")
        self.test_strategy_types()
        
        # Test 6: Generazione per complessità
        print("\n📊 Test 6: Generazione per Complessità")
        self.test_complexity_levels()
        
        # Test 7: Correzione automatica
        print("\n📊 Test 7: Correzione Automatica")
        self.test_code_fixing()
        
        # Genera report finale
        self.generate_test_report()
        
    def test_two_stage_generation(self):
        """
        Test del sistema a due stadi.
        """
        print("🔄 Test sistema a due stadi...")
        
        strategy_types = ["volatility", "scalping", "momentum", "breakout", "adaptive"]
        
        for strategy_type in strategy_types:
            print(f"   📈 Test {strategy_type}...")
            
            start_time = time.time()
            
            try:
                result = self.two_stage_generator.generate_strategy(
                    strategy_type=strategy_type,
                    complexity="normal",
                    style="technical",
                    randomization=0.3,
                    strategy_name=f"Test{strategy_type.capitalize()}TwoStage"
                )
                
                execution_time = time.time() - start_time
                
                # Valida il codice generato
                fix_result = self.code_fixer.fix_python_code(result['code'])
                
                test_result = {
                    'test_type': 'two_stage',
                    'strategy_type': strategy_type,
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'code_length': len(result['code']),
                    'fixes_needed': fix_result['fix_count'],
                    'file_path': result.get('file_path', ''),
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {strategy_type}: OK ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ {strategy_type}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {strategy_type}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'two_stage',
                    'strategy_type': strategy_type,
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def test_adaptive_prompt_generation(self):
        """
        Test del sistema di prompt adattivi.
        """
        print("🔄 Test sistema prompt adattivi...")
        
        test_configs = [
            ("volatility", "simple", "technical", 0.1),
            ("scalping", "normal", "creative", 0.5),
            ("momentum", "complex", "aggressive", 0.8),
            ("breakout", "normal", "conservative", 0.3),
            ("adaptive", "complex", "technical", 0.6)
        ]
        
        for strategy_type, complexity, style, randomization in test_configs:
            print(f"   📊 Test {strategy_type} ({complexity}, {style})...")
            
            start_time = time.time()
            
            try:
                result = self.generator.generate_adaptive_strategy(
                    strategy_type=strategy_type,
                    complexity=complexity,
                    style=style,
                    randomization=randomization,
                    strategy_name=f"Test{strategy_type.capitalize()}Adaptive"
                )
                
                execution_time = time.time() - start_time
                
                # Valida il codice generato
                fix_result = self.code_fixer.fix_python_code(result)
                
                test_result = {
                    'test_type': 'adaptive_prompt',
                    'strategy_type': strategy_type,
                    'complexity': complexity,
                    'style': style,
                    'randomization': randomization,
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'code_length': len(result),
                    'fixes_needed': fix_result['fix_count'],
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {strategy_type}: OK ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ {strategy_type}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {strategy_type}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'adaptive_prompt',
                    'strategy_type': strategy_type,
                    'complexity': complexity,
                    'style': style,
                    'randomization': randomization,
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def test_direct_generation(self):
        """
        Test della generazione diretta.
        """
        print("🔄 Test generazione diretta...")
        
        test_prompts = [
            ("Crea una strategia di scalping per futures crypto", "DirectScalpingStrategy"),
            ("Genera una strategia di momentum per trading volatili", "DirectMomentumStrategy"),
            ("Sviluppa una strategia di breakout per criptovalute", "DirectBreakoutStrategy")
        ]
        
        for prompt, strategy_name in test_prompts:
            print(f"   📝 Test: {strategy_name}...")
            
            start_time = time.time()
            
            try:
                result = self.generator.generate_strategy(
                    prompt=prompt,
                    use_hybrid=False,
                    strategy_name=strategy_name
                )
                
                execution_time = time.time() - start_time
                
                # Valida il codice generato
                fix_result = self.code_fixer.fix_python_code(result)
                
                test_result = {
                    'test_type': 'direct',
                    'strategy_name': strategy_name,
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'code_length': len(result),
                    'fixes_needed': fix_result['fix_count'],
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {strategy_name}: OK ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ {strategy_name}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {strategy_name}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'direct',
                    'strategy_name': strategy_name,
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def test_ensemble_generation(self):
        """
        Test della generazione ensemble.
        """
        print("🔄 Test generazione ensemble...")
        
        strategy_types = ["volatility", "momentum", "scalping"]
        
        for strategy_type in strategy_types:
            print(f"   🎭 Test ensemble {strategy_type}...")
            
            start_time = time.time()
            
            try:
                result = self.generator.generate_strategy_ensemble(
                    strategy_type=strategy_type,
                    strategy_name=f"Test{strategy_type.capitalize()}Ensemble"
                )
                
                execution_time = time.time() - start_time
                
                # Valida il codice generato
                fix_result = self.code_fixer.fix_python_code(result)
                
                test_result = {
                    'test_type': 'ensemble',
                    'strategy_type': strategy_type,
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'code_length': len(result),
                    'fixes_needed': fix_result['fix_count'],
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {strategy_type}: OK ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ {strategy_type}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {strategy_type}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'ensemble',
                    'strategy_type': strategy_type,
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def test_strategy_types(self):
        """
        Test di tutte le tipologie di strategie.
        """
        print("🔄 Test tipologie strategie...")
        
        strategy_types = ["volatility", "scalping", "momentum", "breakout", "adaptive"]
        
        for strategy_type in strategy_types:
            print(f"   📊 Test {strategy_type}...")
            
            start_time = time.time()
            
            try:
                result = self.generator.generate_futures_strategy(
                    strategy_type=strategy_type,
                    strategy_name=f"Test{strategy_type.capitalize()}Type"
                )
                
                execution_time = time.time() - start_time
                
                # Valida il codice generato
                fix_result = self.code_fixer.fix_python_code(result)
                
                test_result = {
                    'test_type': 'strategy_type',
                    'strategy_type': strategy_type,
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'code_length': len(result),
                    'fixes_needed': fix_result['fix_count'],
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {strategy_type}: OK ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ {strategy_type}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {strategy_type}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'strategy_type',
                    'strategy_type': strategy_type,
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def test_complexity_levels(self):
        """
        Test dei diversi livelli di complessità.
        """
        print("🔄 Test livelli di complessità...")
        
        complexity_tests = [
            ("simple", "volatility"),
            ("normal", "scalping"),
            ("complex", "momentum")
        ]
        
        for complexity, strategy_type in complexity_tests:
            print(f"   🎯 Test {complexity} ({strategy_type})...")
            
            start_time = time.time()
            
            try:
                if complexity == "simple":
                    result = self.generator.generate_simple_strategy(
                        strategy_type=strategy_type,
                        strategy_name=f"Test{complexity.capitalize()}Strategy"
                    )
                elif complexity == "complex":
                    result = self.generator.generate_complex_strategy(
                        strategy_type=strategy_type,
                        strategy_name=f"Test{complexity.capitalize()}Strategy"
                    )
                else:
                    result = self.generator.generate_adaptive_strategy(
                        strategy_type=strategy_type,
                        complexity=complexity,
                        strategy_name=f"Test{complexity.capitalize()}Strategy"
                    )
                
                execution_time = time.time() - start_time
                
                # Valida il codice generato
                fix_result = self.code_fixer.fix_python_code(result)
                
                test_result = {
                    'test_type': 'complexity',
                    'complexity': complexity,
                    'strategy_type': strategy_type,
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'code_length': len(result),
                    'fixes_needed': fix_result['fix_count'],
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {complexity}: OK ({execution_time:.2f}s)")
                else:
                    print(f"   ❌ {complexity}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {complexity}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'complexity',
                    'complexity': complexity,
                    'strategy_type': strategy_type,
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def test_code_fixing(self):
        """
        Test del sistema di correzione automatica.
        """
        print("🔄 Test correzione automatica...")
        
        # Codice problematico di esempio
        problematic_codes = [
            {
                'name': 'indentation_issue',
                'code': '''
class TestStrategy(IStrategy):
minimal_roi = {"0": 0.05}
stoploss = -0.02
timeframe = "5m"

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
return dataframe
'''
            },
            {
                'name': 'missing_imports',
                'code': '''
class TestStrategy(IStrategy):
    minimal_roi = {"0": 0.05}
    stoploss = -0.02
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe
'''
            },
            {
                'name': 'syntax_error',
                'code': '''
class TestStrategy(IStrategy):
    minimal_roi = {"0": 0.05}
    stoploss = -0.02
    timeframe = "5m"
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14
        return dataframe
'''
            }
        ]
        
        for test_case in problematic_codes:
            print(f"   🔧 Test {test_case['name']}...")
            
            start_time = time.time()
            
            try:
                fix_result = self.code_fixer.fix_python_code(test_case['code'])
                execution_time = time.time() - start_time
                
                test_result = {
                    'test_type': 'code_fixing',
                    'test_case': test_case['name'],
                    'success': fix_result['is_valid'],
                    'execution_time': execution_time,
                    'fixes_applied': fix_result['fix_count'],
                    'error': fix_result.get('error_msg', '')
                }
                
                self.test_results.append(test_result)
                
                if fix_result['is_valid']:
                    print(f"   ✅ {test_case['name']}: OK ({fix_result['fix_count']} fix)")
                else:
                    print(f"   ❌ {test_case['name']}: ERRORE - {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ {test_case['name']}: ECCEZIONE - {str(e)}")
                self.test_results.append({
                    'test_type': 'code_fixing',
                    'test_case': test_case['name'],
                    'success': False,
                    'execution_time': time.time() - start_time,
                    'error': str(e)
                })
    
    def generate_test_report(self):
        """
        Genera un report completo dei test.
        """
        print("\n📋 Generazione report dei test...")
        
        # Calcola statistiche
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - successful_tests
        
        avg_execution_time = sum(r.get('execution_time', 0) for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        # Raggruppa per tipo di test
        test_types = {}
        for result in self.test_results:
            test_type = result['test_type']
            if test_type not in test_types:
                test_types[test_type] = {'total': 0, 'success': 0, 'failed': 0}
            
            test_types[test_type]['total'] += 1
            if result['success']:
                test_types[test_type]['success'] += 1
            else:
                test_types[test_type]['failed'] += 1
        
        # Crea report
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                'avg_execution_time': avg_execution_time
            },
            'test_types': test_types,
            'detailed_results': self.test_results
        }
        
        # Salva report
        os.makedirs("test_reports", exist_ok=True)
        report_file = f"test_reports/strategy_generation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Stampa sommario
        print("\n" + "=" * 80)
        print("📊 REPORT FINALE DEI TEST")
        print("=" * 80)
        print(f"✅ Test completati: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"❌ Test falliti: {failed_tests}")
        print(f"⏱️ Tempo medio esecuzione: {avg_execution_time:.2f}s")
        
        print("\n📋 Risultati per tipo di test:")
        for test_type, stats in test_types.items():
            success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
            print(f"   {test_type}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n📄 Report dettagliato salvato in: {report_file}")
        
        if failed_tests > 0:
            print("\n⚠️ Errori principali:")
            for result in self.test_results:
                if not result['success'] and result.get('error'):
                    print(f"   - {result['test_type']}: {result['error']}")

def main():
    """
    Esegue il test completo del sistema di generazione strategie.
    """
    print("🚀 Avvio test completo del sistema di generazione strategie")
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = StrategyGenerationTester()
    tester.run_complete_test_suite()

if __name__ == "__main__":
    main()