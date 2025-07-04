import os
import re
import shutil
import ast
from typing import Optional, Tuple, List

def get_class_name_from_file(file_path: str) -> Optional[str]:
    """Estrae il nome della classe dalla strategia."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'^class\s+(\w+)\(IStrategy\):', line)
            if match:
                return match.group(1)
    return None

def fix_class_name(file_path: str, correct_class_name: str) -> bool:
    """Corregge il nome della classe se non corrisponde al nome file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines: List[str] = f.readlines()
    new_lines: List[str] = []
    changed = False
    for line in lines:
        if line.strip().startswith('class ') and '(IStrategy)' in line:
            new_line = f'class {correct_class_name}(IStrategy):\n'
            if line != new_line:
                new_lines.append(new_line)
                changed = True
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
    return changed

def validate_python_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
    """Valida la sintassi Python del file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Errore di sintassi alla riga {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def postprocess_strategy(file_path: str, broken_dir: str = 'user_data/strategies_broken') -> bool:
    """Verifica e corregge nome classe, valida sintassi, sposta file non valido."""
    filename = os.path.basename(file_path)
    name_no_ext = filename.replace('.py', '')
    class_name = get_class_name_from_file(file_path)
    # Correggi nome classe se necessario
    if class_name != name_no_ext:
        fix_class_name(file_path, name_no_ext)
    # Valida sintassi
    valid, error = validate_python_syntax(file_path)
    if not valid:
        print(f"❌ {filename} non valido: {error}. Sposto in {broken_dir}")
        os.makedirs(broken_dir, exist_ok=True)
        shutil.move(file_path, os.path.join(broken_dir, filename))
        return False
    print(f"✅ {filename} valido e pronto all'uso.")
    return True 