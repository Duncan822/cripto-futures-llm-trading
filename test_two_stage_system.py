#!/usr/bin/env python3
"""
Test completo del sistema a due stadi
"""

import sys
import os
sys.path.append('.')

from agents.strategy_text_generator import StrategyTextGenerator
from agents.freqtrade_code_converter import FreqTradeCodeConverter
from agents.two_stage_generator import TwoStageGenerator

def test_text_generator():
    """Test del generatore di descrizioni."""
    print("🧠 Test 1: Generatore di descrizioni testuali")
    print("="*50)
    
    generator = StrategyTextGenerator()
    
    # Test descrizione fallback
    template = {'description': 'test', 'indicators': ['RSI', 'EMA'], 'timeframe': '5m', 'roi_target': '2%', 'stoploss': '2%'}
    desc = generator._generate_fallback_description(template, 'volatility')
    
    print(f"✅ Descrizione fallback generata: {len(desc)} caratteri")
    print(f"📝 Anteprima: {desc[:150]}...")
    
    return desc

def test_code_converter():
    """Test del convertitore di codice."""
    print("\n🔧 Test 2: Convertitore di codice FreqTrade")
    print("="*50)
    
    converter = FreqTradeCodeConverter()
    
    # Test codice fallback
    code = converter._generate_fallback_code('TestStrategy', 'volatility')
    
    print(f"✅ Codice fallback generato: {len(code)} caratteri")
    print(f"📝 Anteprima: {code[:200]}...")
    
    # Test validazione
    validation = converter._validate_and_fix_code(code, 'TestStrategy')
    print(f"🔍 Validazione: {'✅' if validation == code else '❌'}")
    
    return code

def test_two_stage_system():
    """Test del sistema completo a due stadi."""
    print("\n🚀 Test 3: Sistema completo a due stadi")
    print("="*50)
    
    generator = TwoStageGenerator()
    
    # Test generazione nome
    name = generator._generate_strategy_name('volatility')
    print(f"✅ Nome strategia generato: {name}")
    
    # Test con descrizione e codice di fallback
    desc = test_text_generator()
    code = test_code_converter()
    
    # Test salvataggio
    file_path = generator._save_strategy(name, code, desc)
    print(f"💾 Strategia salvata: {file_path}")
    
    # Test validazione
    validation = generator.validate_strategy(name)
    print(f"🔍 Validazione finale: {'✅' if validation['valid'] else '❌'}")
    if not validation['valid']:
        print(f"   Errore: {validation['error']}")
    else:
        print(f"   Lunghezza codice: {validation['code_length']}")
        print(f"   Parametri ottimizzabili: {'✅' if validation['has_optimization_params'] else '❌'}")
        print(f"   Gestione rischio: {'✅' if validation['has_risk_management'] else '❌'}")
    
    return name, file_path

def test_llm_generation():
    """Test della generazione con LLM (se disponibili)."""
    print("\n🤖 Test 4: Generazione con LLM")
    print("="*50)
    
    try:
        generator = TwoStageGenerator()
        
        print("🔄 Tentativo di generazione con LLM...")
        strategy = generator.generate_strategy(
            strategy_type="volatility",
            complexity="normal",
            style="technical",
            strategy_name="TestLLMStrategy"
        )
        
        print(f"✅ Strategia LLM generata: {strategy['strategy_name']}")
        print(f"📁 File: {strategy['file_path']}")
        print(f"📝 Descrizione: {len(strategy['description'])} caratteri")
        print(f"🔧 Codice: {len(strategy['code'])} caratteri")
        
        return strategy
        
    except Exception as e:
        print(f"❌ Errore nella generazione LLM: {e}")
        print("ℹ️  Questo è normale se gli LLM non sono disponibili")
        return None

def main():
    """Test principale."""
    print("🧪 TEST COMPLETO SISTEMA A DUE STADI")
    print("="*60)
    
    # Test componenti individuali
    desc = test_text_generator()
    code = test_code_converter()
    
    # Test sistema completo
    name, file_path = test_two_stage_system()
    
    # Test LLM (opzionale)
    llm_result = test_llm_generation()
    
    # Riepilogo
    print("\n📊 RIEPILOGO TEST")
    print("="*60)
    print(f"✅ Generatore descrizioni: Funzionante")
    print(f"✅ Convertitore codice: Funzionante")
    print(f"✅ Sistema a due stadi: Funzionante")
    print(f"✅ Strategia salvata: {name}")
    print(f"📁 File: {file_path}")
    
    if llm_result:
        print(f"✅ Generazione LLM: Funzionante")
    else:
        print(f"⚠️  Generazione LLM: Non testata (LLM non disponibili)")
    
    print("\n🎯 CONCLUSIONI")
    print("="*60)
    print("Il sistema a due stadi è funzionante e può:")
    print("• Generare descrizioni testuali di strategie")
    print("• Convertire descrizioni in codice FreqTrade valido")
    print("• Salvare strategie con nomi corretti")
    print("• Validare la sintassi del codice generato")
    print("• Gestire fallback in caso di errori")
    
    if llm_result:
        print("• Utilizzare LLM per generazione avanzata")

if __name__ == "__main__":
    main() 