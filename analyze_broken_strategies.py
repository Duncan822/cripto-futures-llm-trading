#!/usr/bin/env python3
"""
Analizza i problemi delle strategie non valide
"""

import os
import re
import ast
from typing import Dict, List, Tuple

def analyze_strategy_problems(file_path: str) -> Dict[str, any]:
    """Analizza i problemi di una singola strategia."""
    filename = os.path.basename(file_path)
    problems = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Problema 1: Nome classe con caratteri non validi
        class_match = re.search(r'class\s+(\w+)\(IStrategy\):', content)
        if class_match:
            class_name = class_match.group(1)
            if not class_name.replace('_', '').isalnum():
                problems.append(f"Nome classe con caratteri non validi: {class_name}")
        
        # Problema 2: Indentazione mancante
        in_class = False
        in_function = False
        expected_indent = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Trova dichiarazione classe
            if stripped.startswith('class ') and '(IStrategy)' in stripped:
                in_class = True
                expected_indent = 4
                continue
            
            # Trova dichiarazione funzione
            if in_class and stripped.startswith('def '):
                in_function = True
                expected_indent = 8
                continue
            
            # Controlla indentazione
            if in_class and stripped and not stripped.startswith('#'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent < expected_indent:
                    problems.append(f"Indentazione mancante alla riga {i}: '{stripped}'")
        
        # Problema 3: Sintassi Python
        try:
            ast.parse(content)
        except SyntaxError as e:
            problems.append(f"Errore di sintassi alla riga {e.lineno}: {e.msg}")
        except Exception as e:
            problems.append(f"Errore generico: {str(e)}")
        
        return {
            'filename': filename,
            'problems': problems,
            'problem_count': len(problems)
        }
        
    except Exception as e:
        return {
            'filename': filename,
            'problems': [f"Errore nell'analisi: {str(e)}"],
            'problem_count': 1
        }

def main():
    """Analizza tutte le strategie non valide."""
    print("🔍 ANALISI STRATEGIE NON VALIDE")
    print("=" * 50)
    
    broken_dir = "user_data/strategies_broken"
    if not os.path.exists(broken_dir):
        print("❌ Directory strategies_broken non trovata")
        return
    
    # Trova tutte le strategie non valide
    broken_files = []
    for file in os.listdir(broken_dir):
        if file.endswith('.py'):
            broken_files.append(os.path.join(broken_dir, file))
    
    print(f"📊 Strategie non valide trovate: {len(broken_files)}")
    
    # Analizza ogni strategia
    all_problems = []
    problem_types = {}
    
    for file_path in broken_files:
        analysis = analyze_strategy_problems(file_path)
        all_problems.append(analysis)
        
        print(f"\n📝 {analysis['filename']}:")
        if analysis['problems']:
            for problem in analysis['problems']:
                print(f"   ❌ {problem}")
                
                # Categorizza i problemi
                if "indentazione" in problem.lower():
                    problem_types['indentazione'] = problem_types.get('indentazione', 0) + 1
                elif "nome classe" in problem.lower():
                    problem_types['nome_classe'] = problem_types.get('nome_classe', 0) + 1
                elif "sintassi" in problem.lower():
                    problem_types['sintassi'] = problem_types.get('sintassi', 0) + 1
                else:
                    problem_types['altro'] = problem_types.get('altro', 0) + 1
        else:
            print("   ✅ Nessun problema rilevato")
    
    # Riepilogo
    print("\n" + "=" * 50)
    print("📊 RIEPILOGO PROBLEMI")
    print("=" * 50)
    
    for problem_type, count in problem_types.items():
        print(f"🔧 {problem_type.replace('_', ' ').title()}: {count}")
    
    total_problems = sum(problem_types.values())
    print(f"\n📈 Totale problemi: {total_problems}")
    
    # Salva report
    with open("strategies_problems_report.txt", "w", encoding="utf-8") as f:
        f.write("REPORT PROBLEMI STRATEGIE NON VALIDE\n")
        f.write("=" * 50 + "\n\n")
        
        for analysis in all_problems:
            f.write(f"📝 {analysis['filename']}:\n")
            for problem in analysis['problems']:
                f.write(f"   ❌ {problem}\n")
            f.write("\n")
        
        f.write("RIEPILOGO:\n")
        for problem_type, count in problem_types.items():
            f.write(f"🔧 {problem_type.replace('_', ' ').title()}: {count}\n")
    
    print(f"\n💾 Report salvato in: strategies_problems_report.txt")

if __name__ == "__main__":
    main() 