#!/usr/bin/env python3
"""
Script per validare tutte le strategie e identificare errori di codice
"""

import os
import ast
import importlib.util
import sys
import glob
from typing import List, Dict, Any

def validate_strategy_syntax(file_path: str) -> Dict[str, Any]:
    """Valida la sintassi di una strategia."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Verifica sintassi Python
        ast.parse(code)
        
        return {
            'valid': True,
            'syntax_error': None,
            'file_path': file_path
        }
    except SyntaxError as e:
        return {
            'valid': False,
            'syntax_error': f"Errore di sintassi alla riga {e.lineno}: {e.msg}",
            'file_path': file_path
        }
    except Exception as e:
        return {
            'valid': False,
            'syntax_error': f"Errore generico: {str(e)}",
            'file_path': file_path
        }

def validate_strategy_structure(file_path: str) -> Dict[str, Any]:
    """Valida la struttura della strategia FreqTrade."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Verifica elementi essenziali
        required_elements = [
            'class',
            'IStrategy',
            'populate_indicators',
            'populate_entry_trend',
            'populate_exit_trend'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in code:
                missing_elements.append(element)
        
        # Verifica che ci sia almeno una classe che eredita da IStrategy
        has_valid_class = False
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'IStrategy':
                            has_valid_class = True
                            break
        except:
            pass
        
        return {
            'valid': len(missing_elements) == 0 and has_valid_class,
            'missing_elements': missing_elements,
            'has_valid_class': has_valid_class,
            'file_path': file_path
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'file_path': file_path
        }

def validate_strategy_imports(file_path: str) -> Dict[str, Any]:
    """Valida gli import della strategia."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Verifica import essenziali
        required_imports = [
            'freqtrade.strategy',
            'pandas',
            'talib'
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in code:
                missing_imports.append(imp)
        
        return {
            'valid': len(missing_imports) == 0,
            'missing_imports': missing_imports,
            'file_path': file_path
        }
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'file_path': file_path
        }

def get_all_strategies() -> List[str]:
    """Ottiene tutte le strategie Python."""
    strategies_dir = "user_data/strategies"
    if not os.path.exists(strategies_dir):
        return []
    
    strategy_files = []
    for file_path in glob.glob(os.path.join(strategies_dir, "*.py")):
        filename = os.path.basename(file_path)
        if filename != "__init__.py" and not filename.startswith("_"):
            strategy_files.append(file_path)
    
    return strategy_files

def main():
    """Funzione principale."""
    print("🔍 VALIDAZIONE STRATEGIE")
    print("=" * 60)
    
    # Ottieni tutte le strategie
    strategy_files = get_all_strategies()
    print(f"📊 Strategie trovate: {len(strategy_files)}")
    
    if not strategy_files:
        print("❌ Nessuna strategia trovata!")
        return
    
    # Risultati
    valid_strategies = []
    invalid_strategies = []
    
    print(f"\n🔍 Validazione di {len(strategy_files)} strategie...")
    
    for i, file_path in enumerate(strategy_files, 1):
        strategy_name = os.path.basename(file_path)
        print(f"\n📊 Progresso: {i}/{len(strategy_files)}")
        print(f"🔍 Validazione: {strategy_name}")
        print("-" * 40)
        
        # Validazione sintassi
        syntax_result = validate_strategy_syntax(file_path)
        if not syntax_result['valid']:
            print(f"❌ Errore di sintassi: {syntax_result['syntax_error']}")
            invalid_strategies.append({
                'file': strategy_name,
                'error': 'syntax',
                'details': syntax_result['syntax_error']
            })
            continue
        
        # Validazione struttura
        structure_result = validate_strategy_structure(file_path)
        if not structure_result['valid']:
            print(f"❌ Errore di struttura:")
            if structure_result.get('missing_elements'):
                print(f"   Elementi mancanti: {structure_result['missing_elements']}")
            if not structure_result.get('has_valid_class'):
                print(f"   Classe IStrategy non trovata")
            invalid_strategies.append({
                'file': strategy_name,
                'error': 'structure',
                'details': structure_result
            })
            continue
        
        # Validazione import
        import_result = validate_strategy_imports(file_path)
        if not import_result['valid']:
            print(f"❌ Import mancanti: {import_result['missing_imports']}")
            invalid_strategies.append({
                'file': strategy_name,
                'error': 'imports',
                'details': import_result['missing_imports']
            })
            continue
        
        print(f"✅ Strategia valida!")
        valid_strategies.append(strategy_name)
    
    # Riepilogo finale
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO VALIDAZIONE")
    print("=" * 60)
    print(f"✅ Strategie valide: {len(valid_strategies)}")
    print(f"❌ Strategie con errori: {len(invalid_strategies)}")
    print(f"📈 Tasso di successo: {(len(valid_strategies)/(len(valid_strategies)+len(invalid_strategies))*100):.1f}%")
    
    if valid_strategies:
        print(f"\n✅ STRATEGIE VALIDE:")
        for strategy in valid_strategies:
            print(f"   - {strategy}")
    
    if invalid_strategies:
        print(f"\n❌ STRATEGIE CON ERRORI:")
        for strategy in invalid_strategies:
            print(f"   - {strategy['file']}: {strategy['error']}")
            if strategy.get('details'):
                print(f"     Dettagli: {strategy['details']}")
    
    # Salva report
    report_file = "strategy_validation_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("REPORT VALIDAZIONE STRATEGIE\n")
        f.write("=" * 50 + "\n")
        f.write(f"Strategie valide: {len(valid_strategies)}\n")
        f.write(f"Strategie con errori: {len(invalid_strategies)}\n")
        f.write(f"Tasso di successo: {(len(valid_strategies)/(len(valid_strategies)+len(invalid_strategies))*100):.1f}%\n\n")
        
        if valid_strategies:
            f.write("STRATEGIE VALIDE:\n")
            for strategy in valid_strategies:
                f.write(f"  - {strategy}\n")
        
        if invalid_strategies:
            f.write("\nSTRATEGIE CON ERRORI:\n")
            for strategy in invalid_strategies:
                f.write(f"  - {strategy['file']}: {strategy['error']}\n")
                if strategy.get('details'):
                    f.write(f"    Dettagli: {strategy['details']}\n")
    
    print(f"\n💾 Report salvato in: {report_file}")

if __name__ == "__main__":
    main() 