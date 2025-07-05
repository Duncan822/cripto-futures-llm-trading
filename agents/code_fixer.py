#!/usr/bin/env python3
"""
Modulo per correggere automaticamente i problemi di indentazione e sintassi
nel codice generato dai modelli LLM.
"""

import re
import ast
import textwrap
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CodeFixer:
    """
    Classe per correggere automaticamente i problemi comuni nel codice generato dai LLM.
    """
    
    def __init__(self):
        self.fixes_applied = []
        
    def fix_python_code(self, code: str) -> Dict[str, Any]:
        """
        Corregge automaticamente i problemi di indentazione e sintassi nel codice Python.
        
        Args:
            code: Il codice Python da correggere
            
        Returns:
            Dizionario con il codice corretto e le informazioni sui fix applicati
        """
        self.fixes_applied = []
        original_code = code
        
        # 1. Correzione dell'indentazione
        code = self._fix_indentation(code)
        
        # 2. Correzione di problemi sintattici comuni
        code = self._fix_syntax_issues(code)
        
        # 3. Correzione di problemi specifici Freqtrade
        code = self._fix_freqtrade_issues(code)
        
        # 4. Validazione finale
        is_valid, error_msg = self._validate_python_syntax(code)
        
        return {
            'original_code': original_code,
            'fixed_code': code,
            'is_valid': is_valid,
            'error_msg': error_msg,
            'fixes_applied': self.fixes_applied,
            'fix_count': len(self.fixes_applied)
        }
    
    def _fix_indentation(self, code: str) -> str:
        """
        Corregge i problemi di indentazione nel codice.
        """
        lines = code.split('\n')
        fixed_lines = []
        
        current_indent = 0
        in_class = False
        in_function = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Salta linee vuote
            if not stripped:
                fixed_lines.append('')
                continue
            
            # Determina il livello di indentazione necessario
            if stripped.startswith('class '):
                in_class = True
                current_indent = 0
                fixed_lines.append(stripped)
                self._add_fix(f"Fixed class indentation at line {i+1}")
                continue
            
            elif stripped.startswith('def '):
                in_function = True
                if in_class:
                    current_indent = 4  # Indentazione per metodi di classe
                else:
                    current_indent = 0  # Funzioni top-level
                fixed_lines.append(' ' * current_indent + stripped)
                self._add_fix(f"Fixed function indentation at line {i+1}")
                continue
            
            elif stripped.startswith(('return ', 'pass')):
                # Istruzioni di ritorno e pass dovrebbero essere indentate
                if in_function:
                    indent = current_indent + 4
                else:
                    indent = 4
                fixed_lines.append(' ' * indent + stripped)
                self._add_fix(f"Fixed return/pass indentation at line {i+1}")
                continue
            
            elif stripped.startswith('dataframe'):
                # Linee con dataframe dovrebbero essere indentate nei metodi
                if in_function:
                    indent = current_indent + 4
                else:
                    indent = 4
                fixed_lines.append(' ' * indent + stripped)
                self._add_fix(f"Fixed dataframe indentation at line {i+1}")
                continue
            
            elif stripped.startswith(('minimal_roi', 'stoploss', 'timeframe')):
                # Attributi di classe dovrebbero essere indentati
                if in_class:
                    indent = 4
                else:
                    indent = 0
                fixed_lines.append(' ' * indent + stripped)
                self._add_fix(f"Fixed class attribute indentation at line {i+1}")
                continue
            
            elif stripped.startswith('(') and i > 0 and 'dataframe.loc[' in lines[i-1]:
                # Continuazione di dataframe.loc
                if in_function:
                    indent = current_indent + 8  # Indentazione extra per continuazione
                else:
                    indent = 8
                fixed_lines.append(' ' * indent + stripped)
                self._add_fix(f"Fixed dataframe.loc continuation indentation at line {i+1}")
                continue
            
            elif stripped.startswith("'") and ('enter_long' in stripped or 'exit_long' in stripped):
                # Chiusura di dataframe.loc
                if in_function:
                    indent = current_indent + 8
                else:
                    indent = 8
                fixed_lines.append(' ' * indent + stripped)
                self._add_fix(f"Fixed dataframe assignment indentation at line {i+1}")
                continue
            
            else:
                # Mantieni l'indentazione originale se sembra corretta
                if line.startswith(' ' * 4) or line.startswith(' ' * 8):
                    fixed_lines.append(line)
                else:
                    # Default: usa indentazione appropriata
                    if in_function:
                        indent = current_indent + 4
                    elif in_class:
                        indent = 4
                    else:
                        indent = 0
                    fixed_lines.append(' ' * indent + stripped)
                    self._add_fix(f"Fixed general indentation at line {i+1}")
        
        return '\n'.join(fixed_lines)
    
    def _fix_syntax_issues(self, code: str) -> str:
        """
        Corregge problemi sintattici comuni.
        """
        # Correzione di import mancanti
        if 'import' not in code:
            code = self._add_missing_imports(code)
        
        # Correzione di parentesi non chiuse
        code = self._fix_parentheses(code)
        
        # Correzione di stringhe non chiuse
        code = self._fix_quotes(code)
        
        return code
    
    def _add_missing_imports(self, code: str) -> str:
        """
        Aggiunge import mancanti se necessario.
        """
        required_imports = [
            "import talib.abstract as ta",
            "import pandas as pd",
            "from pandas import DataFrame",
            "from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter"
        ]
        
        has_imports = any(imp.split()[1] in code for imp in required_imports)
        
        if not has_imports:
            imports_block = '\n'.join(required_imports) + '\n\n'
            code = imports_block + code
            self._add_fix("Added missing imports")
        
        return code
    
    def _fix_parentheses(self, code: str) -> str:
        """
        Corregge parentesi non bilanciate.
        """
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Conta parentesi aperte e chiuse
            open_parens = line.count('(')
            close_parens = line.count(')')
            
            # Se ci sono più parentesi aperte che chiuse, aggiungi le chiuse
            if open_parens > close_parens:
                missing_parens = open_parens - close_parens
                line = line + ')' * missing_parens
                self._add_fix(f"Fixed missing closing parentheses at line {i+1}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_quotes(self, code: str) -> str:
        """
        Corregge problemi con le virgolette.
        """
        # Correzione di virgolette non chiuse in modo basilare
        lines = code.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Conta virgolette singole e doppie
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            
            # Se numero dispari di virgolette, prova a correggere
            if single_quotes % 2 == 1 and "'" in line:
                # Trova l'ultima virgoletta e assicurati che sia chiusa
                if line.rstrip().endswith("'"):
                    pass  # Già chiusa
                else:
                    line = line + "'"
                    self._add_fix(f"Fixed unclosed single quote at line {i+1}")
            
            if double_quotes % 2 == 1 and '"' in line:
                if line.rstrip().endswith('"'):
                    pass  # Già chiusa
                else:
                    line = line + '"'
                    self._add_fix(f"Fixed unclosed double quote at line {i+1}")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_freqtrade_issues(self, code: str) -> str:
        """
        Corregge problemi specifici di Freqtrade.
        """
        # Assicurati che la classe erediti da IStrategy
        if 'class ' in code and 'IStrategy' not in code:
            code = re.sub(r'class (\w+):', r'class \1(IStrategy):', code)
            self._add_fix("Fixed class inheritance from IStrategy")
        
        # Correggi nomi di colonne dataframe
        code = re.sub(r"'enter_long'\]", "'enter_long']", code)
        code = re.sub(r"'exit_long'\]", "'exit_long']", code)
        
        # Assicurati che i metodi restituiscano dataframe
        if 'populate_indicators' in code and 'return dataframe' not in code:
            code = re.sub(r'(def populate_indicators.*?\n.*?)(\n\s*def|\n\s*$)', 
                         r'\1\n        return dataframe\2', code, flags=re.DOTALL)
            self._add_fix("Added missing return statement in populate_indicators")
        
        return code
    
    def _validate_python_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Valida la sintassi Python del codice.
        """
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _add_fix(self, description: str):
        """
        Aggiunge una descrizione del fix applicato.
        """
        self.fixes_applied.append(description)
        logger.info(f"Applied fix: {description}")

def fix_strategy_file(file_path: str) -> Dict[str, Any]:
    """
    Corregge un file di strategia esistente.
    
    Args:
        file_path: Percorso del file da correggere
        
    Returns:
        Dizionario con i risultati della correzione
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()
        
        fixer = CodeFixer()
        result = fixer.fix_python_code(original_code)
        
        if result['is_valid']:
            # Salva il codice corretto
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result['fixed_code'])
            
            print(f"✅ File corretto: {file_path}")
            print(f"   Fix applicati: {result['fix_count']}")
            for fix in result['fixes_applied']:
                print(f"   - {fix}")
        else:
            print(f"❌ Impossibile correggere {file_path}: {result['error_msg']}")
        
        return result
    
    except Exception as e:
        return {
            'is_valid': False,
            'error_msg': f"Error reading file: {str(e)}",
            'fixes_applied': [],
            'fix_count': 0
        }

def main():
    """Test del code fixer."""
    print("🔧 Testing CodeFixer...")
    
    # Test con codice problematico
    problematic_code = '''
class TestStrategy(IStrategy):
minimal_roi = {"0": 0.05}
stoploss = -0.02
timeframe = "5m"

def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
return dataframe

def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
dataframe.loc[
(dataframe['rsi'] < 30) &
(dataframe['ema_short'] > dataframe['ema_long']),
'enter_long'] = 1
return dataframe
'''
    
    fixer = CodeFixer()
    result = fixer.fix_python_code(problematic_code)
    
    print(f"✅ Valid: {result['is_valid']}")
    print(f"🔧 Fixes applied: {result['fix_count']}")
    
    if result['is_valid']:
        print("\n📝 Fixed code:")
        print(result['fixed_code'])
    else:
        print(f"\n❌ Error: {result['error_msg']}")

if __name__ == "__main__":
    main()