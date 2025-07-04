#!/usr/bin/env python3
"""
Script per pulire il progetto eliminando file non necessari
"""

import os
import shutil
from typing import List, Set

def get_essential_files() -> Set[str]:
    """Restituisce l'elenco dei file essenziali del progetto."""
    return {
        # File di configurazione
        'background_config.json',
        'background_config_cooperative.json',
        'timeout_config.json',
        
        # File principali
        'background_agent.py',
        'background_agent_cooperative.py',
        'freqtrade_utils.py',
        'llm_utils.py',
        
        # Directory essenziali
        'agents/',
        'user_data/',
        'prompts/',
        
        # File di documentazione
        'README.md',
        'POST_PROCESSING_AUTOMATICO.md',
        'OTTIMIZZAZIONE_TIMEOUT.md',
        'AGGIORNAMENTO_SISTEMA_DUE_STADI.md',
        'confronto_approcci_generazione.md',
        
        # File di test essenziali
        'test_two_stage_system.py',
        'test_postprocessing.py',
        
        # File di utilità
        'backtest_valid_strategies.py',
        'validate_strategies.py',
        'analyze_broken_strategies.py',
        'strategies_problems_report.txt'
    }

def get_temp_files() -> List[str]:
    """Restituisce l'elenco dei file temporanei da rimuovere."""
    temp_patterns = [
        # File di test temporanei
        'teststrategy.py',
        'teststrategy2.py',
        'teststrategy3.py',
        
        # File di correzione temporanei
        'fix_strategy_names.py',
        'fix_strategy_indentation.py',
        'fix_function_indentation.py',
        'fix_all_indentation.py',
        
        # File di backtest temporanei
        'backtest_all_strategies.py',
        'monitor_backtest.py',
        
        # File di cache Python
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        
        # File di log temporanei
        '*.log',
        'background_agent_cooperative.log',
        
        # File di test vecchi
        'test_llm_strategy_generation.py',
        'test_strategy_quality.py',
        'cogito_strategy_fixed.py',
        'validate_strategy_quality.py',
        'final_llm_recommendations.md'
    ]
    
    files_to_remove = []
    for pattern in temp_patterns:
        if pattern.endswith('/'):
            # Directory
            if os.path.exists(pattern):
                files_to_remove.append(pattern)
        else:
            # File
            if os.path.exists(pattern):
                files_to_remove.append(pattern)
    
    return files_to_remove

def cleanup_project():
    """Pulisce il progetto rimuovendo file non necessari."""
    print("🧹 PULIZIA PROGETTO")
    print("=" * 50)
    
    # File temporanei da rimuovere
    temp_files = get_temp_files()
    
    print(f"📁 File temporanei trovati: {len(temp_files)}")
    
    removed_count = 0
    for file_path in temp_files:
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"🗑️  Rimosso directory: {file_path}")
            else:
                os.remove(file_path)
                print(f"🗑️  Rimosso file: {file_path}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Errore nel rimuovere {file_path}: {e}")
    
    # Rimuovi file __pycache__ ricorsivamente
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                print(f"🗑️  Rimosso cache: {cache_dir}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Errore nel rimuovere {cache_dir}: {e}")
    
    # Rimuovi file .pyc e .pyo
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️  Rimosso bytecode: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Errore nel rimuovere {file_path}: {e}")
    
    print(f"\n✅ Pulizia completata: {removed_count} elementi rimossi")
    
    # Mostra dimensione progetto
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except:
                pass
    
    print(f"📊 Progetto dopo pulizia:")
    print(f"   File: {file_count}")
    print(f"   Dimensione: {total_size / 1024 / 1024:.1f} MB")

def show_project_structure():
    """Mostra la struttura del progetto dopo la pulizia."""
    print("\n📁 STRUTTURA PROGETTO")
    print("=" * 50)
    
    essential_files = get_essential_files()
    
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            continue
        
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py') or file.endswith('.json') or file.endswith('.md'):
                print(f"{subindent}{file}")

if __name__ == "__main__":
    cleanup_project()
    show_project_structure() 