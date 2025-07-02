#!/usr/bin/env python3
"""
Project Optimizer: Corregge, ottimizza e ordina automaticamente il progetto.
Elimina import duplicati, corregge problemi comuni e ottimizza la struttura.
"""

import os
import re
import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import subprocess

class ProjectOptimizer:
    """Ottimizzatore automatico del progetto."""

    def __init__(self):
        self.project_root = Path(".")
        self.python_files = []
        self.issues_found = []
        self.fixes_applied = []

    def scan_project(self):
        """Scansiona il progetto per trovare tutti i file Python."""
        print("🔍 Scansione del progetto...")

        for py_file in self.project_root.rglob("*.py"):
            if not self._should_skip_file(py_file):
                self.python_files.append(py_file)

        print(f"📊 Trovati {len(self.python_files)} file Python da analizzare")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Determina se un file dovrebbe essere saltato."""
        skip_patterns = [
            "__pycache__",
            ".git",
            "venv",
            "env",
            ".pytest_cache"
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def analyze_imports(self, file_path: Path) -> List[str]:
        """Analizza gli import di un file e trova duplicati/problemi."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST per analizzare import
            tree = ast.parse(content)

            imports = []
            import_from = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        import_from.append(f"{module}.{alias.name}")

            # Cerca duplicati
            import_counts = {}
            for imp in imports + import_from:
                import_counts[imp] = import_counts.get(imp, 0) + 1

            duplicates = [imp for imp, count in import_counts.items() if count > 1]
            if duplicates:
                issues.append(f"Import duplicati: {', '.join(duplicates)}")

            # Cerca import non utilizzati (analisi semplificata)
            used_names = set(re.findall(r'\b(\w+)\b', content))
            unused_imports = []

            for imp in imports:
                base_name = imp.split('.')[0]
                if base_name not in used_names and base_name not in ['os', 'sys', 'logging']:
                    unused_imports.append(imp)

            if unused_imports:
                issues.append(f"Possibili import non utilizzati: {', '.join(unused_imports[:3])}")

        except Exception as e:
            issues.append(f"Errore nell'analisi: {str(e)}")

        return issues

    def fix_import_issues(self, file_path: Path) -> bool:
        """Corregge i problemi di import in un file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Trova tutte le linee di import
            import_lines = []
            import_indices = []
            other_lines = []

            in_import_section = True
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith(('import ', 'from ')) and in_import_section:
                    import_lines.append(line)
                    import_indices.append(i)
                elif stripped == '' and in_import_section:
                    import_lines.append(line)
                    import_indices.append(i)
                elif stripped.startswith('#') and in_import_section:
                    import_lines.append(line)
                    import_indices.append(i)
                else:
                    if in_import_section and stripped:
                        in_import_section = False
                    other_lines.append((i, line))

            # Rimuovi duplicati preservando l'ordine
            seen_imports = set()
            cleaned_imports = []

            for line in import_lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    if stripped not in seen_imports:
                        seen_imports.add(stripped)
                        cleaned_imports.append(line)
                else:
                    cleaned_imports.append(line)

            # Riorganizza import: standard library, third party, local
            standard_libs = {
                'os', 'sys', 'time', 'json', 'logging', 'subprocess', 're',
                'datetime', 'pathlib', 'typing', 'dataclasses', 'threading',
                'queue', 'signal', 'ast', 'glob', 'shutil'
            }

            stdlib_imports = []
            thirdparty_imports = []
            local_imports = []

            for line in cleaned_imports:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue

                # Determina il tipo di import
                if stripped.startswith('from '):
                    module = stripped.split()[1].split('.')[0]
                else:
                    module = stripped.split()[1].split('.')[0]

                if module in standard_libs:
                    stdlib_imports.append(line)
                elif module in ['freqtrade', 'pandas', 'numpy', 'ccxt', 'requests', 'schedule', 'talib']:
                    thirdparty_imports.append(line)
                else:
                    local_imports.append(line)

            # Ricostruisci il file
            new_lines = []

            # Aggiungi shebang e docstring se presenti
            for i, line in enumerate(lines):
                if line.startswith('#!') or (i < 5 and '"""' in line):
                    new_lines.append(line)
                else:
                    break

            # Aggiungi import organizzati
            if stdlib_imports:
                new_lines.extend(stdlib_imports)
                new_lines.append('\n')

            if thirdparty_imports:
                new_lines.extend(thirdparty_imports)
                new_lines.append('\n')

            if local_imports:
                new_lines.extend(local_imports)
                new_lines.append('\n')

            # Aggiungi il resto del codice
            code_started = False
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not code_started:
                    if (not line.startswith(('#!', 'import ', 'from ')) and
                        not stripped == '' and
                        not ('"""' in line and i < 10)):
                        code_started = True
                        new_lines.append(line)
                elif code_started:
                    new_lines.append(line)

            # Scrivi il file ottimizzato
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            return True

        except Exception as e:
            print(f"❌ Errore nella correzione di {file_path}: {e}")
            return False

    def check_code_quality(self, file_path: Path) -> List[str]:
        """Controlla la qualità del codice e trova problemi comuni."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Controlla linee troppo lunghe
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
            if long_lines:
                issues.append(f"Linee troppo lunghe: {len(long_lines)} linee")

            # Controlla trailing whitespace
            trailing_ws = [i+1 for i, line in enumerate(lines) if line.rstrip() != line]
            if trailing_ws:
                issues.append(f"Trailing whitespace: {len(trailing_ws)} linee")

            # Controlla indentazione mista
            has_tabs = any('\t' in line for line in lines)
            has_spaces = any(line.startswith('    ') for line in lines)
            if has_tabs and has_spaces:
                issues.append("Indentazione mista (tab e spazi)")

            # Controlla TODO/FIXME
            todos = [i+1 for i, line in enumerate(lines) if re.search(r'(TODO|FIXME|XXX)', line, re.IGNORECASE)]
            if todos:
                issues.append(f"TODO/FIXME trovati: {len(todos)} occorrenze")

        except Exception as e:
            issues.append(f"Errore nell'analisi qualità: {str(e)}")

        return issues

    def fix_code_quality_issues(self, file_path: Path) -> bool:
        """Corregge problemi di qualità del codice."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Fix trailing whitespace
            lines = [line.rstrip() for line in lines]

            # Fix indentazione mista (converti tab in spazi)
            lines = [line.expandtabs(4) for line in lines]

            # Rimuovi linee vuote multiple consecutive
            cleaned_lines = []
            empty_count = 0

            for line in lines:
                if line.strip() == '':
                    empty_count += 1
                    if empty_count <= 2:  # Massimo 2 linee vuote consecutive
                        cleaned_lines.append(line)
                else:
                    empty_count = 0
                    cleaned_lines.append(line)

            # Scrivi il file pulito
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cleaned_lines))
                if cleaned_lines and not cleaned_lines[-1] == '':
                    f.write('\n')  # Assicurati che il file finisca con newline

            return True

        except Exception as e:
            print(f"❌ Errore nella pulizia di {file_path}: {e}")
            return False

    def optimize_project(self):
        """Esegue l'ottimizzazione completa del progetto."""
        print("🚀 Inizio ottimizzazione progetto...")

        self.scan_project()

        total_issues = 0
        total_fixes = 0

        for py_file in self.python_files:
            print(f"\n🔧 Analizzando {py_file}...")

            # Analizza import
            import_issues = self.analyze_imports(py_file)
            if import_issues:
                print(f"  📋 Import issues: {len(import_issues)}")
                for issue in import_issues:
                    print(f"    - {issue}")
                total_issues += len(import_issues)

                # Correggi import
                if self.fix_import_issues(py_file):
                    print(f"  ✅ Import corretti")
                    total_fixes += 1

            # Analizza qualità codice
            quality_issues = self.check_code_quality(py_file)
            if quality_issues:
                print(f"  📋 Qualità issues: {len(quality_issues)}")
                for issue in quality_issues:
                    print(f"    - {issue}")
                total_issues += len(quality_issues)

                # Correggi qualità
                if self.fix_code_quality_issues(py_file):
                    print(f"  ✅ Qualità migliorata")
                    total_fixes += 1

            if not import_issues and not quality_issues:
                print(f"  ✅ File già ottimizzato")

        print(f"\n📊 Risultati ottimizzazione:")
        print(f"   - File analizzati: {len(self.python_files)}")
        print(f"   - Issues trovati: {total_issues}")
        print(f"   - Correzioni applicate: {total_fixes}")

    def create_project_summary(self):
        """Crea un sommario dell'organizzazione del progetto."""
        summary = {
            'directories': {
                'docs/': 'Documentazione completa del progetto',
                'tests/': 'Test suite per tutte le componenti',
                'scripts/': 'Script di utilità e setup',
                'configs/': 'File di configurazione alternativi',
                'agents/': 'Agenti AI per generazione e ottimizzazione',
                'prompts/': 'Prompt specializzati per LLMs',
                'strategies/': 'Strategie di trading generate',
                'user_data/': 'Dati e configurazioni Freqtrade',
                'examples/': 'Esempi e template',
                'templates/': 'Template per strategie'
            },
            'main_files': {
                'background_agent.py': 'Agente principale del sistema',
                'freqtrade_utils.py': 'Utilità per Freqtrade',
                'dry_run_manager.py': 'Gestione dry run',
                'live_strategies_exporter.py': 'Esportazione strategie live',
                'backtest_monitor.py': 'Monitoraggio backtest',
                'llm_monitor.py': 'Monitoraggio LLM',
                'session_manager.py': 'Gestione sessioni',
                'requirements.txt': 'Dipendenze Python'
            },
            'key_scripts': {
                'manage_background_agent.sh': 'Gestione agente principale',
                'start_background_agent.sh': 'Avvio rapido agente',
                'manage_backtest_monitor.sh': 'Gestione monitoraggio',
                'manage_dry_run.sh': 'Gestione dry run',
                'quick_start.sh': 'Setup rapido sistema'
            }
        }

        with open('PROJECT_STRUCTURE.md', 'w', encoding='utf-8') as f:
            f.write("# Struttura Progetto Ottimizzata\n\n")
            f.write("## 📁 Directory\n\n")
            for dir_name, description in summary['directories'].items():
                f.write(f"- **{dir_name}**: {description}\n")

            f.write("\n## 🐍 File Python Principali\n\n")
            for file_name, description in summary['main_files'].items():
                f.write(f"- **{file_name}**: {description}\n")

            f.write("\n## 🔧 Script Chiave\n\n")
            for script_name, description in summary['key_scripts'].items():
                f.write(f"- **{script_name}**: {description}\n")

            f.write("\n## 🚀 Quick Start\n\n")
            f.write("```bash\n")
            f.write("# Setup iniziale\n")
            f.write("./scripts/setup_freqtrade.sh\n")
            f.write("./scripts/setup_ollama.sh\n\n")
            f.write("# Avvio sistema\n")
            f.write("./start_background_agent.sh\n\n")
            f.write("# Monitoraggio\n")
            f.write("./manage_background_agent.sh status\n")
            f.write("./manage_background_agent.sh logs\n")
            f.write("```\n")

        print("✅ Sommario struttura creato in PROJECT_STRUCTURE.md")

def main():
    """Funzione principale."""
    print("🔧 Project Optimizer - Crypto Futures LLM Trading System")
    print("=" * 60)

    optimizer = ProjectOptimizer()

    try:
        # Ottimizza il progetto
        optimizer.optimize_project()

        # Crea sommario
        optimizer.create_project_summary()

        print("\n✅ Ottimizzazione completata con successo!")
        print("\n📖 Controlla PROJECT_STRUCTURE.md per la struttura aggiornata")

    except KeyboardInterrupt:
        print("\n🛑 Ottimizzazione interrotta dall'utente")
    except Exception as e:
        print(f"\n❌ Errore durante l'ottimizzazione: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
