#!/usr/bin/env python3
"""
Script per analizzare le strategie e prevedere quali verranno rimosse dalla pulizia.
Mostra lo stato attuale e le previsioni per la prossima pulizia.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, TypedDict

class StrategyInfo(TypedDict):
    name: str
    age_days: int
    backtest_score: float | None
    reason: str

class SafeStrategyInfo(TypedDict):
    name: str
    age_days: int
    backtest_score: float | None

def load_config() -> Dict[str, Any]:
    """Carica la configurazione del Background Agent."""
    config_file = "background_config.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        return {
            'cleanup_old_strategies': True,
            'min_backtest_score': 0.1,
            'max_strategy_age_days': 30
        }

def load_metadata() -> Dict[str, Any]:
    """Carica i metadati delle strategie."""
    metadata_file = "strategies_metadata.json"
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    else:
        return {}

def analyze_strategies():
    """Analizza le strategie e mostra le previsioni di pulizia."""
    config = load_config()
    metadata = load_metadata()

    print("🧹 Analisi Pulizia Strategie")
    print("=" * 50)

    # Mostra configurazione
    print(f"\n📋 Configurazione Pulizia:")
    print(f"   🧹 Pulizia abilitata: {config.get('cleanup_old_strategies', True)}")
    print(f"   📊 Punteggio minimo: {config.get('min_backtest_score', 0.1)}")
    print(f"   📅 Età massima (giorni): {config.get('max_strategy_age_days', 30)}")

    if not config.get('cleanup_old_strategies', True):
        print("\n✅ Pulizia disabilitata - nessuna strategia verrà rimossa")
        return

    if not metadata:
        print("\n📭 Nessuna strategia trovata")
        return

    current_time = datetime.now()
    min_score = config.get('min_backtest_score', 0.1)
    max_age_days = config.get('max_strategy_age_days', 30)

    print(f"\n📊 Analisi {len(metadata)} Strategie:")
    print("-" * 50)

    strategies_to_remove: List[StrategyInfo] = []
    strategies_safe: List[SafeStrategyInfo] = []

    for name, strategy_data in metadata.items():
        # Converti stringa datetime in oggetto datetime
        generation_time = datetime.fromisoformat(strategy_data['generation_time'])
        age_days = (current_time - generation_time).days
        backtest_score = strategy_data.get('backtest_score')

        # Determina i criteri di rimozione
        old_age = age_days > max_age_days
        low_score = backtest_score is not None and backtest_score < min_score

        # Determina se verrà rimossa
        will_be_removed = old_age or low_score

        # Stampa informazioni strategia
        status_icon = "❌" if will_be_removed else "✅"
        print(f"\n{status_icon} {name}")
        print(f"   📅 Età: {age_days} giorni (max: {max_age_days})")
        print(f"   📊 Punteggio: {backtest_score or 'N/A'} (min: {min_score})")
        print(f"   ✅ Validazione: {strategy_data.get('validation_status', 'N/A')}")
        print(f"   🔄 Attiva: {strategy_data.get('is_active', False)}")

        if old_age:
            print(f"   ⚠️  Criterio rimozione: Età ({age_days} > {max_age_days})")
        elif low_score:
            print(f"   ⚠️  Criterio rimozione: Punteggio basso ({backtest_score} < {min_score})")
        else:
            print(f"   ✅ Sicura: Nessun criterio soddisfatto")

        if will_be_removed:
            strategies_to_remove.append({
                'name': name,
                'age_days': age_days,
                'backtest_score': backtest_score,
                'reason': 'età' if old_age else 'punteggio'
            })
        else:
            strategies_safe.append({
                'name': name,
                'age_days': age_days,
                'backtest_score': backtest_score
            })

    # Riepilogo
    print(f"\n📊 Riepilogo:")
    print("=" * 50)
    print(f"   📈 Strategie totali: {len(metadata)}")
    print(f"   ✅ Strategie sicure: {len(strategies_safe)}")
    print(f"   ❌ Strategie da rimuovere: {len(strategies_to_remove)}")

    if strategies_to_remove:
        print(f"\n🗑️ Strategie che verranno rimosse:")
        print("-" * 30)
        for strategy in strategies_to_remove:
            reason_text = f"età ({strategy['age_days']} giorni)" if strategy['reason'] == 'età' else f"punteggio ({strategy['backtest_score']})"
            print(f"   ❌ {strategy['name']} - {reason_text}")

    if strategies_safe:
        print(f"\n✅ Strategie che rimarranno:")
        print("-" * 30)
        for strategy in strategies_safe:
            print(f"   ✅ {strategy['name']} - {strategy['age_days']} giorni, punteggio: {strategy['backtest_score'] or 'N/A'}")

    # Raccomandazioni
    print(f"\n💡 Raccomandazioni:")
    print("=" * 30)

    if strategies_to_remove:
        print(f"   ⚠️  {len(strategies_to_remove)} strategie verranno rimosse alla prossima pulizia")
        print(f"   💾 Considera di fare backup delle strategie importanti")
        print(f"   🔄 Esegui backtest per le strategie senza punteggio")
    else:
        print(f"   ✅ Nessuna strategia verrà rimossa")

    # Strategie senza backtest
    strategies_without_backtest = [s for s in metadata.values() if s.get('backtest_score') is None]
    if strategies_without_backtest:
        print(f"   📊 {len(strategies_without_backtest)} strategie senza backtest")
        print(f"   🔄 Esegui backtest per evitare rimozioni future")

    # Strategie vecchie ma con buon punteggio
    old_good_strategies = [s for s in metadata.values()
                          if (current_time - datetime.fromisoformat(s['generation_time'])).days > max_age_days * 0.8
                          and s.get('backtest_score', 0) >= min_score]
    if old_good_strategies:
        print(f"   ⏰ {len(old_good_strategies)} strategie si avvicinano al limite di età")
        print(f"   📅 Considera di aumentare max_strategy_age_days se necessario")

def simulate_cleanup():
    """Simula la pulizia per vedere cosa succederebbe."""
    print(f"\n🧪 Simulazione Pulizia")
    print("=" * 30)

    config = load_config()
    metadata = load_metadata()

    if not config.get('cleanup_old_strategies', True):
        print("   ✅ Pulizia disabilitata - nessuna simulazione necessaria")
        return

    current_time = datetime.now()
    min_score = config.get('min_backtest_score', 0.1)
    max_age_days = config.get('max_strategy_age_days', 30)

    strategies_to_remove: List[str] = []

    for name, strategy_data in metadata.items():
        generation_time = datetime.fromisoformat(strategy_data['generation_time'])
        age_days = (current_time - generation_time).days
        backtest_score = strategy_data.get('backtest_score')

        old_age = age_days > max_age_days
        low_score = backtest_score is not None and backtest_score < min_score

        if old_age or low_score:
            strategies_to_remove.append(name)

    if strategies_to_remove:
        print(f"   🗑️ Verrebbero rimosse {len(strategies_to_remove)} strategie:")
        for name in strategies_to_remove:
            print(f"      - {name}")

        # Calcola spazio liberato
        total_size = 0
        for name in strategies_to_remove:
            file_path = metadata[name]['file_path']
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)

        if total_size > 0:
            print(f"   💾 Spazio che verrebbe liberato: {total_size / 1024:.1f} KB")
    else:
        print(f"   ✅ Nessuna strategia verrebbe rimossa")

if __name__ == "__main__":
    try:
        analyze_strategies()
        simulate_cleanup()

        print(f"\n🔧 Comandi Utili:")
        print(f"   python analyze_cleanup.py          - Analisi completa")
        print(f"   ./manage_background_agent.sh status - Stato agente")
        print(f"   ./manage_background_agent.sh config - Modifica configurazione")

    except Exception as e:
        print(f"❌ Errore nell'analisi: {e}")
        print(f"💡 Assicurati di essere nella directory del progetto")
