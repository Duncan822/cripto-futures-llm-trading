#!/usr/bin/env python3
"""
Generatore migliorato con correzione automatica integrata.
"""

import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from .generator import GeneratorAgent
from .code_fixer import CodeFixer
from .strategy_postprocess import postprocess_strategy

class EnhancedGenerator(GeneratorAgent):
    """
    Generatore migliorato con correzione automatica integrata e ottimizzazioni.
    """
    
    def __init__(self, default_model: str = "phi3"):
        super().__init__(default_model)
        self.code_fixer = CodeFixer()
        self.generation_stats = {
            'total_generated': 0,
            'successful_generations': 0,
            'auto_fixed': 0,
            'failed_generations': 0,
            'avg_generation_time': 0.0,
            'avg_fixes_per_strategy': 0.0
        }
        
    def generate_strategy_enhanced(self, 
                                 strategy_type: str = "volatility",
                                 complexity: str = "normal",
                                 style: str = "technical",
                                 randomization: float = 0.3,
                                 strategy_name: Optional[str] = None,
                                 max_retries: int = 3) -> Dict[str, Any]:
        """
        Genera una strategia con correzione automatica e retry intelligente.
        
        Args:
            strategy_type: Tipo di strategia
            complexity: Livello di complessità
            style: Stile del prompt
            randomization: Livello di randomizzazione
            strategy_name: Nome della strategia
            max_retries: Numero massimo di tentativi
            
        Returns:
            Dizionario con risultati della generazione
        """
        if strategy_name is None:
            strategy_name = self._generate_strategy_name(strategy_type)
        
        print(f"🚀 Generazione strategia migliorata: {strategy_name}")
        print(f"   Tipo: {strategy_type} | Complessità: {complexity} | Stile: {style}")
        
        start_time = time.time()
        attempts = []
        
        for attempt in range(max_retries):
            print(f"\n🔄 Tentativo {attempt + 1}/{max_retries}")
            
            try:
                # Genera strategia con approccio ottimizzato
                if attempt == 0:
                    # Primo tentativo: usa sistema a due stadi
                    raw_code = self._generate_with_two_stage(
                        strategy_type, complexity, style, randomization, strategy_name
                    )
                elif attempt == 1:
                    # Secondo tentativo: usa prompt adattivi
                    raw_code = self._generate_with_adaptive_prompts(
                        strategy_type, complexity, style, randomization, strategy_name
                    )
                else:
                    # Ultimo tentativo: usa generazione diretta semplificata
                    raw_code = self._generate_with_fallback(
                        strategy_type, strategy_name
                    )
                
                # Applica correzione automatica
                print("   🔧 Applicazione correzione automatica...")
                fix_result = self.code_fixer.fix_python_code(raw_code)
                
                attempt_info = {
                    'attempt': attempt + 1,
                    'approach': ['two_stage', 'adaptive_prompts', 'fallback'][attempt],
                    'raw_code_length': len(raw_code),
                    'fixes_applied': fix_result['fix_count'],
                    'is_valid': fix_result['is_valid'],
                    'error': fix_result.get('error_msg', '')
                }
                
                attempts.append(attempt_info)
                
                if fix_result['is_valid']:
                    print(f"   ✅ Strategia valida! Fix applicati: {fix_result['fix_count']}")
                    
                    # Salva strategia
                    file_path = self._save_enhanced_strategy(
                        strategy_name, fix_result['fixed_code'], 
                        strategy_type, complexity, style, attempts
                    )
                    
                    # Aggiorna statistiche
                    self._update_stats(True, time.time() - start_time, fix_result['fix_count'])
                    
                    return {
                        'success': True,
                        'strategy_name': strategy_name,
                        'strategy_type': strategy_type,
                        'complexity': complexity,
                        'style': style,
                        'code': fix_result['fixed_code'],
                        'file_path': file_path,
                        'generation_time': time.time() - start_time,
                        'attempts': attempts,
                        'fixes_applied': fix_result['fix_count'],
                        'approach_used': attempt_info['approach']
                    }
                else:
                    print(f"   ❌ Strategia non valida: {fix_result['error_msg']}")
                    
            except Exception as e:
                print(f"   ❌ Errore nel tentativo {attempt + 1}: {str(e)}")
                attempts.append({
                    'attempt': attempt + 1,
                    'approach': ['two_stage', 'adaptive_prompts', 'fallback'][attempt],
                    'is_valid': False,
                    'error': str(e)
                })
        
        # Tutti i tentativi falliti
        print(f"\n❌ Fallimento dopo {max_retries} tentativi")
        self._update_stats(False, time.time() - start_time, 0)
        
        return {
            'success': False,
            'strategy_name': strategy_name,
            'strategy_type': strategy_type,
            'generation_time': time.time() - start_time,
            'attempts': attempts,
            'error': 'Max retries exceeded'
        }
    
    def _generate_with_two_stage(self, strategy_type: str, complexity: str, 
                               style: str, randomization: float, strategy_name: str) -> str:
        """
        Genera con sistema a due stadi.
        """
        print("   📝 Approccio: Sistema a due stadi")
        result = self.two_stage_generator.generate_strategy(
            strategy_type=strategy_type,
            complexity=complexity,
            style=style,
            randomization=randomization,
            strategy_name=strategy_name
        )
        return result['code']
    
    def _generate_with_adaptive_prompts(self, strategy_type: str, complexity: str,
                                      style: str, randomization: float, strategy_name: str) -> str:
        """
        Genera con prompt adattivi.
        """
        print("   🎯 Approccio: Prompt adattivi")
        return self.generate_adaptive_strategy(
            strategy_type=strategy_type,
            complexity=complexity,
            style=style,
            randomization=randomization,
            strategy_name=strategy_name
        )
    
    def _generate_with_fallback(self, strategy_type: str, strategy_name: str) -> str:
        """
        Genera con approccio fallback semplificato.
        """
        print("   🔄 Approccio: Fallback semplificato")
        return self.generate_futures_strategy(
            strategy_type=strategy_type,
            use_hybrid=False,
            strategy_name=strategy_name
        )
    
    def _save_enhanced_strategy(self, strategy_name: str, code: str, 
                              strategy_type: str, complexity: str, style: str,
                              attempts: List[Dict]) -> str:
        """
        Salva strategia con metadati completi.
        """
        # Crea directory se non esiste
        strategies_dir = "user_data/strategies"
        os.makedirs(strategies_dir, exist_ok=True)
        
        # Salva codice
        file_path = os.path.join(strategies_dir, f"{strategy_name.lower()}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Salva metadati
        metadata = {
            'strategy_name': strategy_name,
            'strategy_type': strategy_type,
            'complexity': complexity,
            'style': style,
            'generation_time': datetime.now().isoformat(),
            'generator': 'enhanced_generator',
            'attempts': attempts,
            'success': True
        }
        
        metadata_path = os.path.join(strategies_dir, f"{strategy_name.lower()}_metadata.json")
        import json
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Post-processing automatico
        print("   🔧 Post-processing automatico...")
        is_valid = postprocess_strategy(file_path)
        
        if not is_valid:
            print(f"   ⚠️ Post-processing fallito, ma strategia comunque salvata")
        
        return file_path
    
    def _update_stats(self, success: bool, generation_time: float, fixes_applied: int):
        """
        Aggiorna le statistiche di generazione.
        """
        self.generation_stats['total_generated'] += 1
        
        if success:
            self.generation_stats['successful_generations'] += 1
            if fixes_applied > 0:
                self.generation_stats['auto_fixed'] += 1
        else:
            self.generation_stats['failed_generations'] += 1
        
        # Aggiorna medie
        total = self.generation_stats['total_generated']
        self.generation_stats['avg_generation_time'] = (
            (self.generation_stats['avg_generation_time'] * (total - 1) + generation_time) / total
        )
        
        if success:
            successful = self.generation_stats['successful_generations']
            self.generation_stats['avg_fixes_per_strategy'] = (
                (self.generation_stats['avg_fixes_per_strategy'] * (successful - 1) + fixes_applied) / successful
            )
    
    def generate_multiple_strategies_enhanced(self, 
                                            strategy_types: List[str],
                                            complexity: str = "normal",
                                            style: str = "technical") -> Dict[str, Any]:
        """
        Genera multiple strategie con il sistema migliorato.
        """
        print(f"🚀 Generazione batch di {len(strategy_types)} strategie")
        
        results = []
        start_time = time.time()
        
        for i, strategy_type in enumerate(strategy_types):
            print(f"\n📊 Strategia {i+1}/{len(strategy_types)}: {strategy_type}")
            
            strategy_name = f"Enhanced{strategy_type.capitalize()}Strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            result = self.generate_strategy_enhanced(
                strategy_type=strategy_type,
                complexity=complexity,
                style=style,
                randomization=0.3 + (i * 0.1),  # Varia randomizzazione
                strategy_name=strategy_name
            )
            
            results.append(result)
            
            if result['success']:
                print(f"   ✅ {strategy_type}: Completata")
            else:
                print(f"   ❌ {strategy_type}: Fallita")
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r['success'])
        
        batch_result = {
            'batch_id': f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'total_strategies': len(strategy_types),
            'successful_strategies': successful,
            'failed_strategies': len(strategy_types) - successful,
            'success_rate': successful / len(strategy_types) * 100,
            'total_time': total_time,
            'avg_time_per_strategy': total_time / len(strategy_types),
            'results': results
        }
        
        print(f"\n📊 Batch completato:")
        print(f"   ✅ Successi: {successful}/{len(strategy_types)} ({batch_result['success_rate']:.1f}%)")
        print(f"   ⏱️ Tempo totale: {total_time:.2f}s")
        print(f"   📈 Tempo medio per strategia: {batch_result['avg_time_per_strategy']:.2f}s")
        
        return batch_result
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Restituisce le statistiche di generazione.
        """
        stats = self.generation_stats.copy()
        if stats['total_generated'] > 0:
            stats['success_rate'] = (stats['successful_generations'] / stats['total_generated']) * 100
            stats['auto_fix_rate'] = (stats['auto_fixed'] / stats['successful_generations']) * 100 if stats['successful_generations'] > 0 else 0
        else:
            stats['success_rate'] = 0
            stats['auto_fix_rate'] = 0
        
        return stats
    
    def print_stats(self):
        """
        Stampa le statistiche di generazione.
        """
        stats = self.get_generation_stats()
        
        print("\n📊 STATISTICHE GENERAZIONE")
        print("=" * 50)
        print(f"📈 Totale generate: {stats['total_generated']}")
        print(f"✅ Successi: {stats['successful_generations']} ({stats['success_rate']:.1f}%)")
        print(f"❌ Fallimenti: {stats['failed_generations']}")
        print(f"🔧 Auto-corrette: {stats['auto_fixed']} ({stats['auto_fix_rate']:.1f}%)")
        print(f"⏱️ Tempo medio: {stats['avg_generation_time']:.2f}s")
        print(f"🛠️ Fix medi per strategia: {stats['avg_fixes_per_strategy']:.1f}")
    
    def _generate_strategy_name(self, strategy_type: str) -> str:
        """
        Genera un nome di strategia unico.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_type = re.sub(r'[^a-zA-Z0-9]', '', strategy_type)
        return f"Enhanced{clean_type.capitalize()}Strategy_{timestamp}"

def main():
    """
    Test del generatore migliorato.
    """
    print("🚀 Test del generatore migliorato")
    
    generator = EnhancedGenerator()
    
    # Test singola strategia
    print("\n📊 Test 1: Generazione singola strategia")
    result = generator.generate_strategy_enhanced(
        strategy_type="volatility",
        complexity="normal",
        style="technical"
    )
    
    if result['success']:
        print(f"✅ Strategia generata: {result['strategy_name']}")
        print(f"   File: {result['file_path']}")
        print(f"   Tempo: {result['generation_time']:.2f}s")
        print(f"   Approccio: {result['approach_used']}")
        print(f"   Fix applicati: {result['fixes_applied']}")
    else:
        print(f"❌ Generazione fallita: {result['error']}")
    
    # Test batch
    print("\n📊 Test 2: Generazione batch")
    batch_result = generator.generate_multiple_strategies_enhanced(
        strategy_types=["scalping", "momentum", "breakout"],
        complexity="normal",
        style="technical"
    )
    
    # Stampa statistiche
    generator.print_stats()

if __name__ == "__main__":
    main()