#!/usr/bin/env python3
"""
Script principale per eseguire il sistema corretto e ottimizzato di generazione strategie.
"""

import os
import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Importa tutti i moduli necessari
try:
    from agents.enhanced_generator import EnhancedGenerator
    from agents.code_fixer import fix_strategy_file
    from fix_all_strategies import fix_all_broken_strategies
    from test_complete_strategy_generation import StrategyGenerationTester
except ImportError as e:
    print(f"❌ Errore di importazione: {e}")
    print("Assicurati di essere nella directory del progetto")
    sys.exit(1)

def main():
    """
    Funzione principale che gestisce le operazioni del sistema.
    """
    parser = argparse.ArgumentParser(description="Sistema di generazione strategie corretto e ottimizzato")
    parser.add_argument("--action", choices=["fix", "test", "generate", "batch", "all"], 
                       default="all", help="Azione da eseguire")
    parser.add_argument("--strategy-type", default="volatility", 
                       help="Tipo di strategia da generare")
    parser.add_argument("--complexity", choices=["simple", "normal", "complex"], 
                       default="normal", help="Livello di complessità")
    parser.add_argument("--style", choices=["technical", "creative", "conservative", "aggressive"], 
                       default="technical", help="Stile della strategia")
    parser.add_argument("--count", type=int, default=3, 
                       help="Numero di strategie da generare nel batch")
    
    args = parser.parse_args()
    
    print("🚀 Sistema di Generazione Strategie Corretto e Ottimizzato")
    print("=" * 70)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Azione: {args.action}")
    print("=" * 70)
    
    if args.action == "fix" or args.action == "all":
        print("\n🔧 FASE 1: Correzione strategie esistenti")
        fix_all_broken_strategies()
        print("✅ Correzione completata\n")
    
    if args.action == "test" or args.action == "all":
        print("\n🧪 FASE 2: Test completo del sistema")
        tester = StrategyGenerationTester()
        tester.run_complete_test_suite()
        print("✅ Test completati\n")
    
    if args.action == "generate" or args.action == "all":
        print("\n🚀 FASE 3: Generazione strategia singola")
        generator = EnhancedGenerator()
        
        result = generator.generate_strategy_enhanced(
            strategy_type=args.strategy_type,
            complexity=args.complexity,
            style=args.style,
            randomization=0.3
        )
        
        if result['success']:
            print(f"✅ Strategia generata con successo!")
            print(f"   📝 Nome: {result['strategy_name']}")
            print(f"   📁 File: {result['file_path']}")
            print(f"   ⏱️ Tempo: {result['generation_time']:.2f}s")
            print(f"   🔧 Fix applicati: {result['fixes_applied']}")
            print(f"   📊 Approccio: {result['approach_used']}")
        else:
            print(f"❌ Generazione fallita: {result['error']}")
        
        print("✅ Generazione singola completata\n")
    
    if args.action == "batch" or args.action == "all":
        print("\n🎭 FASE 4: Generazione batch")
        generator = EnhancedGenerator()
        
        strategy_types = ["volatility", "scalping", "momentum", "breakout", "adaptive"][:args.count]
        
        batch_result = generator.generate_multiple_strategies_enhanced(
            strategy_types=strategy_types,
            complexity=args.complexity,
            style=args.style
        )
        
        print(f"✅ Batch completato!")
        print(f"   📊 Successi: {batch_result['successful_strategies']}/{batch_result['total_strategies']}")
        print(f"   📈 Tasso di successo: {batch_result['success_rate']:.1f}%")
        print(f"   ⏱️ Tempo totale: {batch_result['total_time']:.2f}s")
        print(f"   📋 Batch ID: {batch_result['batch_id']}")
        
        # Stampa statistiche del generatore
        generator.print_stats()
        print("✅ Batch completato\n")
    
    print("🎉 SISTEMA COMPLETATO!")
    print("=" * 70)
    print("📋 Riepilogo delle operazioni:")
    
    if args.action == "fix" or args.action == "all":
        print("   ✅ Correzione strategie esistenti")
    
    if args.action == "test" or args.action == "all":
        print("   ✅ Test completo del sistema")
    
    if args.action == "generate" or args.action == "all":
        print("   ✅ Generazione strategia singola")
    
    if args.action == "batch" or args.action == "all":
        print("   ✅ Generazione batch")
    
    print("\n💡 Suggerimenti per l'uso:")
    print("   • Controlla le strategie generate in user_data/strategies/")
    print("   • I report dei test sono in test_reports/")
    print("   • Per aiuto: python run_corrected_system.py --help")
    print("   • Per generare una strategia specifica: python run_corrected_system.py --action generate --strategy-type scalping")
    
    print("\n📚 Modalità di generazione disponibili:")
    print("   🔄 Sistema a due stadi (principale)")
    print("   🎯 Prompt adattivi")
    print("   📝 Generazione diretta")
    print("   🎭 Ensemble")
    print("   🔧 Correzione automatica integrata")

def run_quick_demo():
    """
    Esegue una demo rapida del sistema.
    """
    print("🎯 DEMO RAPIDA DEL SISTEMA")
    print("=" * 50)
    
    # 1. Correggi una strategia esistente
    print("\n1. 🔧 Test correzione automatica...")
    from agents.code_fixer import CodeFixer
    
    fixer = CodeFixer()
    problematic_code = """
class TestStrategy(IStrategy):
minimal_roi = {"0": 0.05}
stoploss = -0.02
timeframe = "5m"

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
return dataframe
"""
    
    result = fixer.fix_python_code(problematic_code)
    print(f"   ✅ Correzione: {'✅ OK' if result['is_valid'] else '❌ KO'}")
    print(f"   🔧 Fix applicati: {result['fix_count']}")
    
    # 2. Genera una strategia
    print("\n2. 🚀 Test generazione strategia...")
    generator = EnhancedGenerator()
    
    result = generator.generate_strategy_enhanced(
        strategy_type="volatility",
        complexity="simple",
        style="technical"
    )
    
    if result['success']:
        print(f"   ✅ Strategia generata: {result['strategy_name']}")
        print(f"   📁 File: {result['file_path']}")
        print(f"   ⏱️ Tempo: {result['generation_time']:.2f}s")
    else:
        print(f"   ❌ Generazione fallita: {result['error']}")
    
    # 3. Statistiche
    print("\n3. 📊 Statistiche generazione:")
    generator.print_stats()
    
    print("\n🎉 Demo completata!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_quick_demo()
    else:
        main()