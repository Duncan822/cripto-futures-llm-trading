#!/usr/bin/env python3
"""
Background Agent Cooperativo: Versione cooperativa del background agent originale.
Sostituisce SOLO la generazione strategia con cooperazione tra LLM, mantenendo tutto il resto identico.
"""

import os
import time
import json
import logging
import schedule
import signal
import sys
import random
import threading
import queue
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Importa tutto dal background agent originale
from background_agent import (
    BackgroundAgent, StrategyMetadata, signal_handler,
    DRY_RUN_MANAGER_AVAILABLE, BACKTEST_MONITOR_AVAILABLE, LIVE_EXPORTER_AVAILABLE
)

# Importa i componenti cooperativi
from agents.generator import GeneratorAgent
from agents.strategy_converter import StrategyConverter
from agents.optimizer import OptimizerAgent
from freqtrade_utils import FreqtradeManager

# Importa il monitor cooperativo se disponibile
try:
    from cooperative_monitor import track_cooperative_session, log_cooperative_conversation, end_cooperative_session
    COOPERATIVE_MONITOR_AVAILABLE = True
except ImportError:
    COOPERATIVE_MONITOR_AVAILABLE = False
    print("⚠️ CooperativeMonitor non disponibile, monitoraggio cooperativo disabilitato")

# Importa le utility LLM
try:
    from llm_utils import query_ollama, query_ollama_fast, query_ollama_unlimited, query_ollama_cooperative
    LLM_UTILS_AVAILABLE = True
except ImportError:
    LLM_UTILS_AVAILABLE = False
    print("⚠️ LLM utils non disponibili, generazione cooperativa limitata")

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_agent_cooperative.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CooperativeGeneratorAgent:
    """
    Agente di generazione cooperativa che sostituisce il GeneratorAgent standard.
    Utilizza cooperazione tra LLM per generare strategie migliori.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cooperative_config = config.get('cooperative_mode', {})
        self.model_selection = config.get('model_selection', {})
        
        # Modelli disponibili per cooperazione
        self.strategy_generators = self.model_selection.get('generation', ['cogito:8b', 'mistral:7b-instruct-q4_0', 'phi3:mini'])
        self.validators = self.model_selection.get('validation', ['cogito:8b', 'mistral:7b-instruct-q4_0'])
        self.optimizers = self.model_selection.get('optimization', ['cogito:8b'])
        
        # Configurazione cooperativa
        self.enable_cooperation = self.cooperative_config.get('enable_cooperation', True)
        self.use_llm_voting = self.cooperative_config.get('use_llm_voting', True)
        self.parallel_generation_count = self.cooperative_config.get('parallel_generation_count', 3)
        self.enable_contest_mode = self.cooperative_config.get('enable_contest_mode', True)
        
        # Fallback al generatore standard (ora usa sistema a due stadi)
        self.standard_generator = GeneratorAgent()
        
        # Importa il sistema a due stadi
        try:
            from agents.two_stage_generator import TwoStageGenerator
            self.two_stage_generator = TwoStageGenerator(
                text_model="phi3:mini",
                code_model="mistral:7b-instruct-q4_0"
            )
            self.two_stage_available = True
        except ImportError:
            self.two_stage_available = False
            logger.warning("⚠️ Sistema a due stadi non disponibile")
        
    def generate_futures_strategy(self, strategy_type: str, use_hybrid: bool = True, strategy_name: str | None = None) -> str:
        """
        Genera una strategia usando sistema a due stadi con cooperazione tra LLM.
        Fallback al generatore standard se la cooperazione non è disponibile.
        """
        # Usa sistema a due stadi se disponibile
        if self.two_stage_available:
            logger.info(f"🔄 Generazione {strategy_type} con sistema a due stadi...")
            try:
                result = self.two_stage_generator.generate_strategy(
                    strategy_type=strategy_type,
                    complexity="normal",
                    style="technical",
                    randomization=0.3,
                    strategy_name=strategy_name
                )
                return result['code']
            except Exception as e:
                logger.error(f"❌ Errore nel sistema a due stadi: {e}")
        
        # Fallback alla cooperazione se disponibile
        if self.enable_cooperation and LLM_UTILS_AVAILABLE:
            logger.info("🤝 Usando generazione cooperativa...")
            try:
                # Avvia sessione cooperativa se il monitor è disponibile
                session_id = ""
                if COOPERATIVE_MONITOR_AVAILABLE:
                    session_id = track_cooperative_session(
                        "cooperative_generation",
                        strategy_type,
                        self.strategy_generators
                    )
                
                logger.info(f"🤝 Generazione cooperativa per {strategy_type}")
                
                # Scegli il metodo di generazione cooperativa
                if self.enable_contest_mode and len(self.strategy_generators) >= 2:
                    return self._generate_with_contest(strategy_type, use_hybrid, strategy_name, session_id)
                elif self.use_llm_voting and len(self.strategy_generators) >= 2:
                    return self._generate_with_voting(strategy_type, use_hybrid, strategy_name, session_id)
                else:
                    return self._generate_with_consensus(strategy_type, use_hybrid, strategy_name, session_id)
                    
            except Exception as e:
                logger.error(f"❌ Errore nella generazione cooperativa: {e}")
                
                # Termina sessione cooperativa se attiva
                if session_id and COOPERATIVE_MONITOR_AVAILABLE:
                    end_cooperative_session(session_id, "failed", {"error": str(e)})
        
        # Fallback finale al generatore standard
        logger.info("🔄 Fallback al generatore standard")
        return self.standard_generator.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
    
    def _generate_with_contest(self, strategy_type: str, use_hybrid: bool, strategy_name: str, session_id: str) -> str:
        """Genera strategia usando contest tra LLM."""
        logger.info("🏁 Avvio contest tra LLM...")
        
        contest_results = []
        start_time = time.time()
        
        # Genera strategie in parallelo
        threads = []
        for i, model in enumerate(self.strategy_generators):
            thread = threading.Thread(
                target=self._generate_contest_entry,
                args=(model, strategy_type, use_hybrid, strategy_name, contest_results, session_id)
            )
            threads.append(thread)
            thread.start()
        
        # Aspetta tutti i thread
        for thread in threads:
            thread.join()
        
        # Valuta i risultati del contest
        if contest_results:
            best_strategy = self._evaluate_contest_results(contest_results, strategy_type)
            
            # Termina sessione cooperativa
            if session_id and COOPERATIVE_MONITOR_AVAILABLE:
                end_cooperative_session(session_id, "completed", {
                    "method": "contest",
                    "participants": len(contest_results),
                    "winner": best_strategy.get('model', 'unknown'),
                    "duration": time.time() - start_time
                })
            
            return best_strategy['code']
        else:
            # Fallback se nessun risultato
            if session_id and COOPERATIVE_MONITOR_AVAILABLE:
                end_cooperative_session(session_id, "failed", {"error": "Nessun risultato dal contest"})
            return self.standard_generator.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
    
    def _generate_contest_entry(self, model: str, strategy_type: str, use_hybrid: bool, 
                               strategy_name: str, results: List, session_id: str):
        """Genera una strategia per il contest."""
        try:
            logger.info(f"🤖 {model} partecipa al contest...")
            
            prompt = f"""Crea la MIGLIORE strategia Freqtrade per {strategy_type} trading su futures crypto.
Devi BATTERE gli altri LLM nel contest!

Requisiti:
- Strategia per {strategy_type} trading
- Su futures crypto volatili
- Codice Python completo e funzionante
- Gestione rischio avanzata
- Indicatori tecnici efficaci
- Logica di entrata/uscita chiara

Genera SOLO il codice Python della strategia, senza spiegazioni."""

            start_time = time.time()
            response = query_ollama_cooperative(prompt, model, session_id)
            duration = time.time() - start_time
            
            # Log della conversazione cooperativa
            if session_id and COOPERATIVE_MONITOR_AVAILABLE:
                log_cooperative_conversation(
                    session_id, model, "contestant", prompt, response, duration
                )
            
            # Valida e pulisci il codice
            converter = StrategyConverter()
            clean_code = converter.validate_and_fix_code(response, strategy_name or f"Contest{strategy_type}")
            
            results.append({
                'model': model,
                'code': clean_code,
                'duration': duration,
                'original_response': response
            })
            
            logger.info(f"🏁 {model} ha completato il contest ({duration:.1f}s)")
            
        except Exception as e:
            logger.error(f"❌ {model} ha fallito nel contest: {e}")
    
    def _evaluate_contest_results(self, results: List[Dict], strategy_type: str) -> Dict:
        """Valuta i risultati del contest e sceglie il migliore."""
        logger.info(f"📊 Valutazione {len(results)} strategie del contest...")
        
        # Criteri di valutazione
        best_strategy = None
        best_score = 0
        
        for result in results:
            code = result['code']
            model = result['model']
            
            # Calcola punteggio basato su criteri oggettivi
            score = self._calculate_strategy_score(code, strategy_type)
            
            logger.info(f"   {model}: punteggio {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_strategy = result
        
        if best_strategy:
            logger.info(f"🏆 Vincitore: {best_strategy['model']} (punteggio: {best_score:.2f})")
            return best_strategy
        else:
            # Fallback al primo risultato disponibile
            return results[0] if results else {}
    
    def _calculate_strategy_score(self, code: str, strategy_type: str) -> float:
        """Calcola un punteggio oggettivo per una strategia."""
        score = 0.0
        
        # Criteri di valutazione
        criteria = {
            'has_indicators': len(re.findall(r'ta\.', code)) * 2.0,
            'has_conditions': len(re.findall(r'dataframe\.loc', code)) * 1.5,
            'has_risk_management': len(re.findall(r'stoploss|stop_loss|max_open_trades', code)) * 2.0,
            'has_proper_structure': len(re.findall(r'class.*Strategy', code)) * 3.0,
            'has_buy_sell_logic': len(re.findall(r'def (buy|sell)', code)) * 2.0,
            'code_length': min(len(code.split('\n')), 100) * 0.1,
            'strategy_type_match': 5.0 if strategy_type.lower() in code.lower() else 0.0
        }
        
        score = sum(criteria.values())
        
        # Bonus per codice pulito
        if 'import' in code and 'class' in code and 'def' in code:
            score += 3.0
        
        return score
    
    def _generate_with_voting(self, strategy_type: str, use_hybrid: bool, strategy_name: str, session_id: str) -> str:
        """Genera strategia usando voting tra LLM."""
        logger.info("🗳️ Generazione con voting tra LLM...")
        
        # Genera strategie con tutti i modelli
        strategies = []
        for model in self.strategy_generators:
            try:
                strategy = self._generate_single_strategy(model, strategy_type, use_hybrid, strategy_name, session_id)
                if strategy:
                    strategies.append(strategy)
            except Exception as e:
                logger.error(f"❌ Errore con {model}: {e}")
        
        if not strategies:
            return self.standard_generator.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
        
        # Usa il modello più potente per la sintesi finale
        synthesis_model = self.strategy_generators[0]
        
        # Crea sintesi delle strategie
        synthesis_prompt = f"""Analizza queste strategie per {strategy_type} trading e crea la migliore versione combinata:

{chr(10).join([f"=== Strategia {i+1} (da {s['model']}) ===\n{s['code']}\n" for i, s in enumerate(strategies)])}

Crea una strategia unificata che combini i migliori elementi di tutte le strategie.
Genera SOLO il codice Python finale, senza spiegazioni."""

        try:
            final_strategy = query_ollama_cooperative(synthesis_prompt, synthesis_model, session_id)
            
            # Valida il codice finale
            converter = StrategyConverter()
            clean_code = converter.validate_and_fix_code(final_strategy, strategy_name or f"Voting{strategy_type}")
            
            return clean_code
            
        except Exception as e:
            logger.error(f"❌ Errore nella sintesi: {e}")
            # Fallback alla migliore strategia individuale
            return strategies[0]['code']
    
    def _generate_with_consensus(self, strategy_type: str, use_hybrid: bool, strategy_name: str, session_id: str) -> str:
        """Genera strategia usando consenso tra LLM."""
        logger.info("🤝 Generazione con consenso tra LLM...")
        
        # Raccolta idee da tutti i modelli
        ideas = []
        for model in self.strategy_generators:
            try:
                idea = self._collect_strategy_idea(model, strategy_type, session_id)
                if idea:
                    ideas.append(idea)
            except Exception as e:
                logger.error(f"❌ Errore con {model}: {e}")
        
        if not ideas:
            return self.standard_generator.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
        
        # Sintesi consensuale
        synthesis_model = self.strategy_generators[0]
        all_ideas_text = "\n\n".join([f"=== {idea['model']} ===\n{idea['idea']}" for idea in ideas])
        
        synthesis_prompt = f"""Analizza queste idee per una strategia {strategy_type}:

{all_ideas_text}

Crea una strategia Freqtrade completa che implementi il consenso tra queste idee.
Genera SOLO il codice Python della strategia."""

        try:
            consensus_strategy = query_ollama_cooperative(synthesis_prompt, synthesis_model, session_id)
            
            # Valida il codice
            converter = StrategyConverter()
            clean_code = converter.validate_and_fix_code(consensus_strategy, strategy_name or f"Consensus{strategy_type}")
            
            return clean_code
            
        except Exception as e:
            logger.error(f"❌ Errore nella sintesi consensuale: {e}")
            return self.standard_generator.generate_futures_strategy(strategy_type, use_hybrid, strategy_name)
    
    def _generate_single_strategy(self, model: str, strategy_type: str, use_hybrid: bool, 
                                 strategy_name: str, session_id: str) -> Optional[Dict]:
        """Genera una singola strategia con un modello."""
        try:
            prompt = f"""Crea una strategia Freqtrade per {strategy_type} trading su futures crypto.

Requisiti:
- Strategia per {strategy_type} trading
- Su futures crypto volatili
- Codice Python completo e funzionante
- Gestione rischio
- Indicatori tecnici appropriati

Genera SOLO il codice Python della strategia."""

            start_time = time.time()
            response = query_ollama_cooperative(prompt, model, session_id)
            duration = time.time() - start_time
            
            # Log della conversazione cooperativa
            if session_id and COOPERATIVE_MONITOR_AVAILABLE:
                log_cooperative_conversation(
                    session_id, model, "generator", prompt, response, duration
                )
            
            # Valida il codice
            converter = StrategyConverter()
            clean_code = converter.validate_and_fix_code(response, strategy_name or f"Single{strategy_type}")
            
            return {
                'model': model,
                'code': clean_code,
                'duration': duration
            }
            
        except Exception as e:
            logger.error(f"❌ Errore con {model}: {e}")
            return None
    
    def _collect_strategy_idea(self, model: str, strategy_type: str, session_id: str) -> Optional[Dict]:
        """Raccoglie un'idea strategica da un modello."""
        try:
            prompt = f"""Descrivi 3 idee chiave per una strategia di trading {strategy_type} su futures crypto:
1. Indicatori tecnici da usare
2. Condizioni di entrata/uscita 
3. Gestione del rischio

Rispondi in modo conciso e pratico."""

            start_time = time.time()
            response = query_ollama_fast(prompt, model, timeout=300)
            duration = time.time() - start_time
            
            # Log della conversazione cooperativa
            if session_id and COOPERATIVE_MONITOR_AVAILABLE:
                log_cooperative_conversation(
                    session_id, model, "idea_collector", prompt, response, duration
                )
            
            return {
                'model': model,
                'idea': response,
                'duration': duration
            }
            
        except Exception as e:
            logger.error(f"❌ Errore con {model}: {e}")
            return None


class CooperativeBackgroundAgent(BackgroundAgent):
    """
    Background Agent Cooperativo che sostituisce solo la generazione strategia.
    Mantiene tutto il resto identico al background agent originale.
    """
    
    def __init__(self, config_path: str = "background_config_cooperative.json"):
        # Carica configurazione cooperativa
        self.cooperative_config = self._load_config(config_path)
        
        # Inizializza il generatore cooperativo
        self.cooperative_generator = CooperativeGeneratorAgent(self.cooperative_config)
        
        # Chiama il costruttore del background agent originale
        super().__init__(config_path)
        
        # Sostituisce il generatore standard con quello cooperativo
        self.generator = self.cooperative_generator
        
        logger.info("🤖 Background Agent Cooperativo inizializzato")
        logger.info(f"   Modelli generazione: {self.cooperative_generator.strategy_generators}")
        logger.info(f"   Modelli validazione: {self.cooperative_generator.validators}")
        logger.info(f"   Cooperazione abilitata: {self.cooperative_generator.enable_cooperation}")
    
    def generate_strategy_safely(self, strategy_type: str, model: str) -> Optional[StrategyMetadata]:
        """
        Override della generazione strategia per usare il generatore cooperativo.
        Mantiene tutto il resto identico al metodo originale.
        """
        try:
            # Genera nome univoco
            strategy_name = self.generate_unique_strategy_name(strategy_type, model)
            file_name = f"{strategy_name.lower()}.py"
            file_path = f"user_data/strategies/{file_name}"
            
            # Controlla se esiste già
            if os.path.exists(file_path):
                logger.warning(f"File {file_path} esiste già, generando nuovo nome...")
                strategy_name = self.generate_unique_strategy_name(strategy_type, model)
                file_name = f"{strategy_name.lower()}.py"
                file_path = f"user_data/strategies/{file_name}"
            
            logger.info(f"🤝 Generazione cooperativa: {strategy_name} per {strategy_type}")
            
            # Usa il generatore cooperativo
            strategy_code = self.cooperative_generator.generate_futures_strategy(
                strategy_type=strategy_type,
                use_hybrid=True,
                strategy_name=strategy_name
            )
            
            # Validazione automatica (identica all'originale)
            if self.auto_validation:
                strategy_code = self.converter.validate_and_fix_code(strategy_code, strategy_name)
            
            # Salva la strategia (identico all'originale)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(strategy_code)
            
            # Crea metadati (identico all'originale)
            metadata = StrategyMetadata(
                name=strategy_name,
                file_path=file_path,
                strategy_type=strategy_type,
                model_used=f"cooperative({model})",  # Indica che è stata generata cooperativamente
                generation_time=datetime.now(),
                validation_status="validated" if self.auto_validation else "generated"
            )
            
            # Salva metadati (identico all'originale)
            self.strategies_metadata[strategy_name] = metadata
            self._save_metadata()
            
            logger.info(f"✅ Strategia cooperativa {strategy_name} generata e salvata")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Errore nella generazione cooperativa {strategy_type}: {e}")
            return None


def main():
    """Funzione principale per avviare l'agente cooperativo."""
    # Registra i gestori di segnale
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Avvia l'agente cooperativo
    agent = CooperativeBackgroundAgent()
    print('🤖 Background Agent Cooperativo avviato')
    agent.start()
    
    try:
        while agent.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        print('🛑 Arresto agente cooperativo')
        agent.stop()


if __name__ == "__main__":
    main() 