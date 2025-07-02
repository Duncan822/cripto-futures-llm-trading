#!/usr/bin/env python3
"""
Test script per l'Optimizer Agent.
Testa l'ottimizzazione di strategie esistenti e mostra i risultati.
"""

import os
import sys
import json
from pathlib import Path

# Aggiungi il percorso del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.optimizer import OptimizerAgent, OptimizationResult

def load_strategy_code(file_path: str) -> str:
    """Carica il codice di una strategia da file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Errore nel caricamento strategia {file_path}: {e}")
        return ""

def load_strategies_metadata() -> dict:
    """Carica i metadati delle strategie."""
    try:
        with open('strategies_metadata.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Errore nel caricamento metadati: {e}")
        return {}

def simulate_backtest_results() -> dict:
    """Simula risultati di backtest per testing."""
    return {
        'total_return': 0.08,      # 8% rendimento
        'sharpe_ratio': 0.8,       # Sharpe ratio basso
        'max_drawdown': 0.12,      # Drawdown moderato
        'win_rate': 0.35,          # Win rate basso
        'total_trades': 15,        # Pochi trade
        'avg_trade_duration': 120  # 2 ore media
    }

def test_optimizer_with_existing_strategies():
    """Testa l'ottimizzatore con strategie esistenti."""
    print("🧪 TEST OPTIMIZER AGENT")
    print("=" * 50)
    
    # Carica metadati
    metadata = load_strategies_metadata()
    if not metadata:
        print("❌ Nessuna strategia trovata nei metadati")
        return
    
    # Inizializza ottimizzatore
    optimizer = OptimizerAgent(default_model="phi3")
    
    # Simula risultati backtest
    backtest_results = simulate_backtest_results()
    
    print(f"📊 Strategie trovate: {len(metadata)}")
    print(f"📈 Risultati backtest simulati: {backtest_results}")
    print()
    
    # Testa con la prima strategia
    strategy_name = list(metadata.keys())[0]
    strategy_info = metadata[strategy_name]
    
    print(f"🎯 Testando ottimizzazione per: {strategy_name}")
    print(f"📁 File: {strategy_info['file_path']}")
    print(f"📅 Generata: {strategy_info['generation_time']}")
    print()
    
    # Carica codice strategia
    strategy_code = load_strategy_code(strategy_info['file_path'])
    if not strategy_code:
        print("❌ Impossibile caricare il codice della strategia")
        return
    
    print("📝 Codice originale (prime 10 righe):")
    print("-" * 40)
    for i, line in enumerate(strategy_code.split('\n')[:10]):
        print(f"{i+1:2d}: {line}")
    print("...")
    print()
    
    # Esegui ottimizzazione
    print("🔧 Avvio ottimizzazione...")
    try:
        result = optimizer.optimize_strategy(
            strategy_code=strategy_code,
            backtest_results=backtest_results,
            strategy_name=strategy_name
        )
        
        # Mostra risultati
        print("✅ Ottimizzazione completata!")
        print()
        print(optimizer.get_optimization_summary(result))
        
        if result.success and result.improvements:
            print("\n📝 Codice ottimizzato (prime 15 righe):")
            print("-" * 40)
            
            # Mostra le modifiche principali
            if result.changes_made:
                print("🔍 MODIFICHE PRINCIPALI:")
                for change_type, changes in result.changes_made.items():
                    if changes:
                        print(f"  - {change_type}: {changes}")
                print()
            
            # Mostra il codice ottimizzato
            optimized_code = optimizer._apply_optimizations(
                strategy_code, result.improvements, strategy_name
            )
            
            for i, line in enumerate(optimized_code.split('\n')[:15]):
                print(f"{i+1:2d}: {line}")
            print("...")
            
            # Salva strategia ottimizzata
            optimized_file_path = strategy_info['file_path'].replace('.py', '_optimized.py')
            try:
                with open(optimized_file_path, 'w', encoding='utf-8') as f:
                    f.write(optimized_code)
                print(f"\n💾 Strategia ottimizzata salvata in: {optimized_file_path}")
            except Exception as e:
                print(f"❌ Errore nel salvataggio: {e}")
        
    except Exception as e:
        print(f"❌ Errore durante l'ottimizzazione: {e}")
        import traceback
        traceback.print_exc()

def test_optimizer_analysis():
    """Testa solo l'analisi delle strategie."""
    print("🔍 TEST ANALISI STRATEGIE")
    print("=" * 40)
    
    # Carica una strategia
    metadata = load_strategies_metadata()
    if not metadata:
        print("❌ Nessuna strategia trovata")
        return
    
    strategy_name = list(metadata.keys())[0]
    strategy_info = metadata[strategy_name]
    strategy_code = load_strategy_code(strategy_info['file_path'])
    
    if not strategy_code:
        print("❌ Impossibile caricare il codice")
        return
    
    # Inizializza ottimizzatore
    optimizer = OptimizerAgent()
    
    # Simula risultati
    backtest_results = simulate_backtest_results()
    
    # Testa analisi
    print(f"📊 Analizzando: {strategy_name}")
    analysis = optimizer._analyze_strategy_performance(strategy_code, backtest_results)
    
    print("\n📈 RISULTATI ANALISI:")
    print(f"  - Total Return: {analysis['total_return']:.4f}")
    print(f"  - Sharpe Ratio: {analysis['sharpe_ratio']:.4f}")
    print(f"  - Max Drawdown: {analysis['max_drawdown']:.4f}")
    print(f"  - Win Rate: {analysis['win_rate']:.4f}")
    print(f"  - Total Trades: {analysis['total_trades']}")
    
    print("\n🚨 PROBLEMI IDENTIFICATI:")
    for issue in analysis.get('issues', []):
        print(f"  - {issue}")
    
    print("\n💡 OPPORTUNITÀ DI OTTIMIZZAZIONE:")
    for opportunity in analysis.get('optimization_opportunities', []):
        print(f"  - {opportunity}")
    
    print("\n🔧 INDICATORI UTILIZZATI:")
    for indicator in analysis.get('indicators_used', []):
        print(f"  - {indicator}")
    
    print("\n📝 CONDIZIONI DI ENTRATA:")
    print(f"  - Numero: {len(analysis.get('entry_conditions', []))}")
    
    print("\n📝 CONDIZIONI DI USCITA:")
    print(f"  - Numero: {len(analysis.get('exit_conditions', []))}")

def test_optimization_suggestions():
    """Testa la generazione di suggerimenti di ottimizzazione."""
    print("💡 TEST SUGGERIMENTI OTTIMIZZAZIONE")
    print("=" * 50)
    
    # Carica strategia
    metadata = load_strategies_metadata()
    if not metadata:
        print("❌ Nessuna strategia trovata")
        return
    
    strategy_name = list(metadata.keys())[0]
    strategy_info = metadata[strategy_name]
    strategy_code = load_strategy_code(strategy_info['file_path'])
    
    if not strategy_code:
        print("❌ Impossibile caricare il codice")
        return
    
    # Inizializza ottimizzatore
    optimizer = OptimizerAgent()
    
    # Simula risultati
    backtest_results = simulate_backtest_results()
    
    # Analizza strategia
    analysis = optimizer._analyze_strategy_performance(strategy_code, backtest_results)
    
    # Genera suggerimenti
    print("🧠 Generazione suggerimenti di ottimizzazione...")
    try:
        suggestions = optimizer._generate_optimization_suggestions(
            strategy_code, backtest_results, analysis
        )
        
        print(f"✅ Generati {len(suggestions)} suggerimenti:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
            
    except Exception as e:
        print(f"❌ Errore nella generazione suggerimenti: {e}")
        # Testa suggerimenti basati su regole
        print("\n🔄 Fallback a suggerimenti basati su regole...")
        rule_suggestions = optimizer._generate_rule_based_suggestions(analysis)
        for i, suggestion in enumerate(rule_suggestions, 1):
            print(f"  {i}. {suggestion}")

def main():
    """Funzione principale."""
    print("🚀 TEST OPTIMIZER AGENT")
    print("=" * 60)
    print()
    
    # Verifica che Ollama sia disponibile
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama disponibile")
        else:
            print("⚠️ Ollama non risponde correttamente")
    except Exception as e:
        print(f"⚠️ Ollama non disponibile: {e}")
        print("   I test useranno solo suggerimenti basati su regole")
    
    print()
    
    # Menu di test
    while True:
        print("Scegli un test:")
        print("1. Test completo ottimizzatore")
        print("2. Test solo analisi strategie")
        print("3. Test suggerimenti ottimizzazione")
        print("4. Tutti i test")
        print("0. Esci")
        
        choice = input("\nScelta: ").strip()
        
        if choice == "1":
            test_optimizer_with_existing_strategies()
        elif choice == "2":
            test_optimizer_analysis()
        elif choice == "3":
            test_optimization_suggestions()
        elif choice == "4":
            test_optimizer_analysis()
            print("\n" + "="*60 + "\n")
            test_optimization_suggestions()
            print("\n" + "="*60 + "\n")
            test_optimizer_with_existing_strategies()
        elif choice == "0":
            break
        else:
            print("❌ Scelta non valida")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main() 