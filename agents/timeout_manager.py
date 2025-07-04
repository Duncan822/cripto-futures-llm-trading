#!/usr/bin/env python3
"""
Gestore di timeout adattivo per il sistema a due stadi
Ottimizza i timeout basandosi su modello, complessità e performance storiche
"""

import time
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class TimeoutManager:
    def __init__(self, config_file: str = "timeout_config.json"):
        self.config_file = config_file
        self.performance_history = self._load_performance_history()
        
        # Timeout di base per diversi modelli
        self.base_timeouts = {
            "phi3:mini": 1200,      # 20 minuti
            "phi3": 1800,           # 30 minuti
            "mistral:7b-instruct-q4_0": 2400,  # 40 minuti
            "cogito:8b": 3000,      # 50 minuti
            "cogito:3b": 900,       # 15 minuti
            "llama3.2:3b": 1200,    # 20 minuti
            "llama3.2:8b": 2400,    # 40 minuti
        }
        
        # Moltiplicatori per complessità
        self.complexity_multipliers = {
            "simple": 0.7,
            "normal": 1.0,
            "complex": 1.5
        }
        
        # Moltiplicatori per fase
        self.phase_multipliers = {
            "text_generation": 0.8,    # Descrizione testuale più veloce
            "code_conversion": 1.2     # Conversione codice più lenta
        }
    
    def get_optimal_timeout(self, 
                          model: str, 
                          phase: str = "text_generation",
                          complexity: str = "normal",
                          strategy_type: str = "volatility") -> int:
        """
        Calcola il timeout ottimale basato su modello, fase e complessità.
        
        Args:
            model: Nome del modello LLM
            phase: Fase del processo (text_generation, code_conversion)
            complexity: Livello di complessità (simple, normal, complex)
            strategy_type: Tipo di strategia
            
        Returns:
            Timeout in secondi
        """
        
        # Timeout di base per il modello
        base_timeout = self.base_timeouts.get(model, 1800)
        
        # Applica moltiplicatori
        complexity_mult = self.complexity_multipliers.get(complexity, 1.0)
        phase_mult = self.phase_multipliers.get(phase, 1.0)
        
        # Calcola timeout base
        calculated_timeout = int(base_timeout * complexity_mult * phase_mult)
        
        # Aggiusta basandosi sulla performance storica
        adjusted_timeout = self._adjust_based_on_history(
            model, phase, strategy_type, calculated_timeout
        )
        
        # Limiti di sicurezza
        min_timeout = 600   # 10 minuti minimo
        max_timeout = 7200  # 2 ore massimo
        
        final_timeout = max(min_timeout, min(max_timeout, adjusted_timeout))
        
        print(f"⏱️ Timeout calcolato per {model} ({phase}): {final_timeout}s")
        return final_timeout
    
    def record_performance(self, 
                         model: str, 
                         phase: str,
                         strategy_type: str,
                         actual_time: float,
                         success: bool,
                         timeout_used: int):
        """
        Registra la performance per migliorare i timeout futuri.
        
        Args:
            model: Nome del modello
            phase: Fase del processo
            strategy_type: Tipo di strategia
            actual_time: Tempo effettivo impiegato
            success: Se l'operazione è riuscita
            timeout_used: Timeout utilizzato
        """
        
        key = f"{model}_{phase}_{strategy_type}"
        
        if key not in self.performance_history:
            self.performance_history[key] = {
                'times': [],
                'successes': [],
                'timeouts': [],
                'last_updated': datetime.now().isoformat()
            }
        
        # Aggiungi dati
        self.performance_history[key]['times'].append(actual_time)
        self.performance_history[key]['successes'].append(success)
        self.performance_history[key]['timeouts'].append(timeout_used)
        self.performance_history[key]['last_updated'] = datetime.now().isoformat()
        
        # Mantieni solo gli ultimi 20 record
        if len(self.performance_history[key]['times']) > 20:
            self.performance_history[key]['times'] = self.performance_history[key]['times'][-20:]
            self.performance_history[key]['successes'] = self.performance_history[key]['successes'][-20:]
            self.performance_history[key]['timeouts'] = self.performance_history[key]['timeouts'][-20:]
        
        # Salva
        self._save_performance_history()
        
        print(f"📊 Performance registrata: {model} ({phase}) - {actual_time:.1f}s - Successo: {success}")
    
    def _adjust_based_on_history(self, 
                                model: str, 
                                phase: str, 
                                strategy_type: str, 
                                base_timeout: int) -> int:
        """Aggiusta il timeout basandosi sulla performance storica."""
        
        key = f"{model}_{phase}_{strategy_type}"
        
        if key not in self.performance_history:
            return base_timeout
        
        history = self.performance_history[key]
        
        if not history['times']:
            return base_timeout
        
        # Calcola statistiche
        avg_time = sum(history['times']) / len(history['times'])
        success_rate = sum(history['successes']) / len(history['successes'])
        
        # Se il success rate è basso, aumenta il timeout
        if success_rate < 0.7:
            adjustment = 1.3  # +30%
        elif success_rate > 0.9:
            adjustment = 0.9  # -10%
        else:
            adjustment = 1.0
        
        # Se il tempo medio è molto più alto del timeout, aumenta
        if avg_time > base_timeout * 0.8:
            adjustment *= 1.2
        
        adjusted_timeout = int(base_timeout * adjustment)
        
        print(f"📈 Aggiustamento basato su storia: {base_timeout}s → {adjusted_timeout}s")
        return adjusted_timeout
    
    def get_model_recommendations(self) -> Dict[str, Any]:
        """Restituisce raccomandazioni sui modelli basate sulla performance."""
        
        recommendations = {}
        
        for key, history in self.performance_history.items():
            if not history['times']:
                continue
            
            model, phase, strategy_type = key.split('_', 2)
            
            avg_time = sum(history['times']) / len(history['times'])
            success_rate = sum(history['successes']) / len(history['successes'])
            
            if model not in recommendations:
                recommendations[model] = {
                    'phases': {},
                    'overall_success_rate': 0,
                    'overall_avg_time': 0
                }
            
            recommendations[model]['phases'][phase] = {
                'avg_time': avg_time,
                'success_rate': success_rate,
                'recommended_timeout': int(avg_time * 1.2)  # 20% di margine
            }
        
        # Calcola statistiche generali per modello
        for model, data in recommendations.items():
            phases = list(data['phases'].values())
            if phases:
                data['overall_success_rate'] = sum(p['success_rate'] for p in phases) / len(phases)
                data['overall_avg_time'] = sum(p['avg_time'] for p in phases) / len(phases)
        
        return recommendations
    
    def _load_performance_history(self) -> Dict[str, Any]:
        """Carica la storia delle performance da file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Errore nel caricamento performance history: {e}")
        
        return {}
    
    def _save_performance_history(self):
        """Salva la storia delle performance su file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Errore nel salvataggio performance history: {e}")
    
    def reset_performance_history(self):
        """Resetta la storia delle performance."""
        self.performance_history = {}
        self._save_performance_history()
        print("🔄 Performance history resettata")

# Istanza globale
timeout_manager = TimeoutManager()

def get_optimal_timeout(model: str, 
                       phase: str = "text_generation",
                       complexity: str = "normal",
                       strategy_type: str = "volatility") -> int:
    """Funzione helper per ottenere timeout ottimale."""
    return timeout_manager.get_optimal_timeout(model, phase, complexity, strategy_type)

def record_performance(model: str, 
                      phase: str,
                      strategy_type: str,
                      actual_time: float,
                      success: bool,
                      timeout_used: int):
    """Funzione helper per registrare performance."""
    timeout_manager.record_performance(model, phase, strategy_type, actual_time, success, timeout_used) 