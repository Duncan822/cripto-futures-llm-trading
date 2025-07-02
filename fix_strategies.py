#!/usr/bin/env python3
"""
Script per correggere automaticamente i nomi delle classi nelle strategie FreqTrade.
Assicura che il nome della classe corrisponda al nome del file.
"""

import os
import re
import glob
from pathlib import Path

def fix_strategy_class_name(file_path: str) -> bool:
    """
    Corregge il nome della classe in una strategia per corrispondere al nome del file.

    Args:
        file_path: Percorso del file della strategia

    Returns:
        True se il file è stato modificato, False altrimenti
    """
    try:
        # Leggi il contenuto del file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Estrai il nome del file senza estensione
        file_name = Path(file_path).stem
        expected_class_name = file_name.replace('_', '').title()

        # Cerca la classe esistente
        class_pattern = r'class\s+(\w+)\s*\(IStrategy\)'
        match = re.search(class_pattern, content)

        if not match:
            print(f"⚠️ Nessuna classe IStrategy trovata in {file_path}")
            return False

        current_class_name = match.group(1)

        if current_class_name == expected_class_name:
            print(f"✅ {file_path}: nome classe già corretto ({current_class_name})")
            return False

        # Sostituisci il nome della classe
        old_class_declaration = f"class {current_class_name}(IStrategy)"
        new_class_declaration = f"class {expected_class_name}(IStrategy)"

        if old_class_declaration in content:
            content = content.replace(old_class_declaration, new_class_declaration)

            # Aggiorna anche il docstring se presente
            content = re.sub(
                rf'""".*?{current_class_name}.*?"""',
                f'"""{expected_class_name} - Strategia generata automaticamente"""',
                content,
                flags=re.DOTALL
            )

            # Scrivi il file corretto
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ {file_path}: corretto da {current_class_name} a {expected_class_name}")
            return True
        else:
            print(f"❌ {file_path}: impossibile trovare la dichiarazione della classe")
            return False

    except Exception as e:
        print(f"❌ Errore nel processare {file_path}: {e}")
        return False

def fix_all_strategies():
    """
    Corregge tutte le strategie nella directory user_data/strategies.
    """
    strategies_dir = "user_data/strategies"

    if not os.path.exists(strategies_dir):
        print(f"❌ Directory {strategies_dir} non trovata")
        return

    # Trova tutti i file .py nella directory delle strategie
    strategy_files = glob.glob(os.path.join(strategies_dir, "*.py"))

    if not strategy_files:
        print(f"❌ Nessuna strategia trovata in {strategies_dir}")
        return

    print(f"🔍 Trovate {len(strategy_files)} strategie da correggere...")

    fixed_count = 0
    for file_path in strategy_files:
        if fix_strategy_class_name(file_path):
            fixed_count += 1

    print(f"\n📊 Risultati:")
    print(f"   - Strategie processate: {len(strategy_files)}")
    print(f"   - Strategie corrette: {fixed_count}")
    print(f"   - Strategie già corrette: {len(strategy_files) - fixed_count}")

def validate_strategies():
    """
    Valida che tutte le strategie abbiano il nome della classe corretto.
    """
    strategies_dir = "user_data/strategies"

    if not os.path.exists(strategies_dir):
        print(f"❌ Directory {strategies_dir} non trovata")
        return

    strategy_files = glob.glob(os.path.join(strategies_dir, "*.py"))

    if not strategy_files:
        print(f"❌ Nessuna strategia trovata in {strategies_dir}")
        return

    print(f"🔍 Validazione di {len(strategy_files)} strategie...")

    valid_count = 0
    invalid_files = []

    for file_path in strategy_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_name = Path(file_path).stem
            expected_class_name = file_name.replace('_', '').title()

            class_pattern = r'class\s+(\w+)\s*\(IStrategy\)'
            match = re.search(class_pattern, content)

            if match:
                current_class_name = match.group(1)
                if current_class_name == expected_class_name:
                    print(f"✅ {file_name}: {current_class_name}")
                    valid_count += 1
                else:
                    print(f"❌ {file_name}: {current_class_name} (dovrebbe essere {expected_class_name})")
                    invalid_files.append(file_path)
            else:
                print(f"⚠️ {file_name}: nessuna classe IStrategy trovata")
                invalid_files.append(file_path)

        except Exception as e:
            print(f"❌ {file_name}: errore di lettura - {e}")
            invalid_files.append(file_path)

    print(f"\n📊 Risultati validazione:")
    print(f"   - Strategie valide: {valid_count}")
    print(f"   - Strategie da correggere: {len(invalid_files)}")

    if invalid_files:
        print(f"\n🔧 Strategie da correggere:")
        for file_path in invalid_files:
            print(f"   - {Path(file_path).name}")

def create_test_strategy():
    """
    Crea una strategia di test per verificare il funzionamento.
    """
    test_strategy = '''"""
TestStrategy - Strategia di test
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class TestStrategy(IStrategy):
    """
    Strategia di test per verificare il funzionamento.
    """

    minimal_roi = {
        "0": 0.05,
        "30": 0.025,
        "60": 0.015,
        "120": 0.01
    }

    stoploss = -0.02
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    timeframe = "5m"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola gli indicatori tecnici.
        """
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        dataframe.loc[
            (dataframe['rsi'] < 30) &
            (dataframe['ema_short'] > dataframe['ema_long']),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        dataframe.loc[
            (dataframe['rsi'] > 70) |
            (dataframe['ema_short'] < dataframe['ema_long']),
            'exit_long'] = 1
        return dataframe
'''

    # Crea directory se non esiste
    os.makedirs("user_data/strategies", exist_ok=True)

    # Scrivi la strategia di test
    with open("user_data/strategies/test_strategy.py", "w", encoding="utf-8") as f:
        f.write(test_strategy)

    print("✅ Strategia di test creata: user_data/strategies/test_strategy.py")

def main():
    """
    Menu principale per la gestione delle strategie.
    """
    print("🔧 Gestione Strategie FreqTrade")
    print("=" * 40)
    print("1. Correggi nomi delle classi")
    print("2. Valida strategie esistenti")
    print("3. Crea strategia di test")
    print("4. Correggi e valida")
    print("0. Esci")

    while True:
        choice = input("\nScegli un'opzione (0-4): ").strip()

        if choice == "0":
            print("👋 Arrivederci!")
            break
        elif choice == "1":
            print("\n🔧 Correzione nomi delle classi...")
            fix_all_strategies()
        elif choice == "2":
            print("\n🔍 Validazione strategie...")
            validate_strategies()
        elif choice == "3":
            print("\n📝 Creazione strategia di test...")
            create_test_strategy()
        elif choice == "4":
            print("\n🔧 Correzione e validazione...")
            fix_all_strategies()
            print("\n" + "=" * 40)
            validate_strategies()
        else:
            print("❌ Opzione non valida. Riprova.")

if __name__ == "__main__":
    main()
