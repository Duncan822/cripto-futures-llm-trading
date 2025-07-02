#!/usr/bin/env python3
"""
Script per correggere le strategie esistenti con caratteri non validi nei nomi.
Rinomina i file e aggiorna i metadati, poi ottimizza le strategie con score basso.
"""

import os
import json
import shutil
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple

def fix_strategy_name(old_name: str) -> str:
    """Corregge il nome della strategia sostituendo caratteri non validi."""
    # Sostituisci caratteri non validi per Python (es: :, /, -) con _
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', old_name)
    return safe_name

def rename_strategy_files() -> Dict[str, str]:
    """
    Rinomina i file delle strategie con caratteri non validi.
    Restituisce un dizionario {vecchio_nome: nuovo_nome}
    """
    print("🔧 Rinominazione file strategie...")

    strategies_dir = "user_data/strategies"
    renamed_files = {}

    if not os.path.exists(strategies_dir):
        print("❌ Directory strategie non trovata")
        return renamed_files

    # Trova tutti i file .py nella directory strategie
    for filename in os.listdir(strategies_dir):
        if filename.endswith('.py') and ':' in filename:  # Solo file con caratteri non validi
            old_path = os.path.join(strategies_dir, filename)
            new_filename = fix_strategy_name(filename)
            new_path = os.path.join(strategies_dir, new_filename)

            if old_path != new_path:
                try:
                    shutil.move(old_path, new_path)
                    old_name = filename.replace('.py', '')
                    new_name = new_filename.replace('.py', '')
                    renamed_files[old_name] = new_name
                    print(f"  ✅ {old_name} → {new_name}")
                except Exception as e:
                    print(f"  ❌ Errore nel rinominare {filename}: {e}")

    print(f"📊 Rinominati {len(renamed_files)} file")
    return renamed_files

def update_metadata(renamed_files: Dict[str, str]):
    """Aggiorna i metadati delle strategie con i nuovi nomi."""
    print("\n📝 Aggiornamento metadati...")

    metadata_file = "strategies_metadata.json"
    if not os.path.exists(metadata_file):
        print("❌ File metadati non trovato")
        return

    try:
        with open(metadata_file, 'r') as f:
            data = json.load(f)

        # Aggiorna i nomi delle strategie
        updated_data = {}
        for old_name, strategy_data in data.items():
            if old_name in renamed_files:
                new_name = renamed_files[old_name]
                strategy_data['name'] = new_name
                strategy_data['file_path'] = strategy_data['file_path'].replace(
                    f"{old_name.lower()}.py",
                    f"{new_name.lower()}.py"
                )
                updated_data[new_name] = strategy_data
                print(f"  ✅ Metadati aggiornati: {old_name} → {new_name}")
            else:
                updated_data[old_name] = strategy_data

        # Salva i metadati aggiornati
        with open(metadata_file, 'w') as f:
            json.dump(updated_data, f, indent=2)

        print(f"📊 Metadati aggiornati per {len(renamed_files)} strategie")

    except Exception as e:
        print(f"❌ Errore nell'aggiornamento metadati: {e}")

def optimize_low_score_strategies():
    """Ottimizza le strategie con score basso o nullo."""
    print("\n🔧 Ottimizzazione strategie con score basso...")

    try:
        from background_agent import BackgroundAgent

        agent = BackgroundAgent()

        # Trova strategie da ottimizzare
        strategies_to_optimize = []
        for name, metadata in agent.strategies_metadata.items():
            if (metadata.backtest_score is None or
                metadata.backtest_score < 0.1) and \
                metadata.validation_status == 'validated':
                strategies_to_optimize.append((name, metadata))

        if not strategies_to_optimize:
            print("ℹ️ Nessuna strategia da ottimizzare trovata")
            return

        print(f"🎯 Trovate {len(strategies_to_optimize)} strategie da ottimizzare")

        # Ordina per priorità (cogito:8b prima)
        def get_priority(metadata):
            priority = 0
            model = metadata.model_used
            if 'cogito:8b' in model:
                priority += 10
            elif 'cogito:3b' in model:
                priority += 5
            elif 'mistral' in model:
                priority += 3
            return priority

        strategies_to_optimize.sort(key=lambda x: get_priority(x[1]), reverse=True)

        # Ottimizza le prime 5 strategie
        for i, (name, metadata) in enumerate(strategies_to_optimize[:5]):
            print(f"\n🔧 Ottimizzazione {i+1}/5: {name}")
            print(f"   Modello: {metadata.model_used}")
            print(f"   Score attuale: {metadata.backtest_score}")

            success = agent.optimize_strategy_automatically(name)
            if success:
                print(f"   ✅ Ottimizzazione completata")
            else:
                print(f"   ⚠️ Nessuna ottimizzazione necessaria")

        print(f"\n✅ Ottimizzazione completata per {min(5, len(strategies_to_optimize))} strategie")

    except Exception as e:
        print(f"❌ Errore nell'ottimizzazione: {e}")

def test_fixed_strategies():
    """Testa alcune strategie corrette per verificare il funzionamento."""
    print("\n🧪 Test strategie corrette...")

    try:
        from background_agent import BackgroundAgent

        agent = BackgroundAgent()

        # Trova strategie corrette (senza caratteri non validi)
        valid_strategies = []
        for name, metadata in agent.strategies_metadata.items():
            if ':' not in name and metadata.validation_status in ['validated', 'optimized']:
                valid_strategies.append((name, metadata))

        if not valid_strategies:
            print("ℹ️ Nessuna strategia valida trovata")
            return

        # Ordina per priorità
        def get_priority(metadata):
            priority = 0
            model = metadata.model_used
            if 'cogito_8b' in model:
                priority += 10
            elif 'cogito_3b' in model:
                priority += 5
            elif 'mistral' in model:
                priority += 3
            return priority

        valid_strategies.sort(key=lambda x: get_priority(x[1]), reverse=True)

        # Testa le prime 3 strategie
        for i, (name, metadata) in enumerate(valid_strategies[:3]):
            print(f"\n🧪 Test {i+1}/3: {name}")
            print(f"   Modello: {metadata.model_used}")
            print(f"   Status: {metadata.validation_status}")

            # Esegui backtest
            score = agent.backtest_strategy(name)
            if score is not None:
                print(f"   ✅ Backtest completato: score {score:.3f}")
            else:
                print(f"   ❌ Backtest fallito")

        print(f"\n✅ Test completati per {min(3, len(valid_strategies))} strategie")

    except Exception as e:
        print(f"❌ Errore nel test: {e}")

def main():
    """Funzione principale."""
    print("🚀 Correzione strategie esistenti")
    print("=" * 50)

    # 1. Rinomina file
    renamed_files = rename_strategy_files()

    if renamed_files:
        # 2. Aggiorna metadati
        update_metadata(renamed_files)

        # 3. Ottimizza strategie
        optimize_low_score_strategies()

        # 4. Testa strategie corrette
        test_fixed_strategies()

        print("\n" + "=" * 50)
        print("✅ Correzione completata!")
        print("\n💡 Prossimi passi:")
        print("   1. Riavvia il Background Agent: ./manage_background_agent.sh restart")
        print("   2. Monitora i backtest: ./manage_background_agent.sh backtest")
        print("   3. Controlla le strategie live: ./manage_background_agent.sh live-strategies")
    else:
        print("\nℹ️ Nessuna strategia da correggere trovata")
        print("   Le strategie esistenti sono già corrette")

if __name__ == "__main__":
    main()
