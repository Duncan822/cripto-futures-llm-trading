#!/usr/bin/env python3
"""
Script per correggere automaticamente tutte le strategie rotte.
"""

import os
import glob
from agents.code_fixer import fix_strategy_file

def fix_all_broken_strategies():
    """
    Corregge tutte le strategie rotte nella directory strategies.
    """
    print("🔧 Correzione automatica di tutte le strategie rotte...")
    
    # Trova tutti i file di strategia
    strategy_files = glob.glob("user_data/strategies/*.py")
    
    if not strategy_files:
        print("❌ Nessun file di strategia trovato in user_data/strategies/")
        return
    
    print(f"📁 Trovati {len(strategy_files)} file di strategia")
    
    fixed_count = 0
    error_count = 0
    
    for file_path in strategy_files:
        print(f"\n🔍 Controllo: {os.path.basename(file_path)}")
        
        # Controlla se il file è già valido
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Prova a compilare il codice
            import ast
            ast.parse(code)
            print(f"✅ Già valido: {os.path.basename(file_path)}")
            continue
            
        except SyntaxError:
            print(f"🔧 Correzione necessaria: {os.path.basename(file_path)}")
            
            # Correggi il file
            result = fix_strategy_file(file_path)
            
            if result['is_valid']:
                fixed_count += 1
                print(f"✅ Corretto con successo!")
                print(f"   Fix applicati: {result['fix_count']}")
            else:
                error_count += 1
                print(f"❌ Impossibile correggere: {result['error_msg']}")
        
        except Exception as e:
            print(f"❌ Errore durante la lettura di {file_path}: {e}")
            error_count += 1
    
    print(f"\n📊 Risultati:")
    print(f"   ✅ Strategie corrette: {fixed_count}")
    print(f"   ❌ Errori: {error_count}")
    print(f"   📁 Totale file controllati: {len(strategy_files)}")
    
    if fixed_count > 0:
        print("\n🎉 Correzione completata! Le strategie sono ora utilizzabili.")
    else:
        print("\n💡 Nessuna correzione necessaria.")

if __name__ == "__main__":
    fix_all_broken_strategies()