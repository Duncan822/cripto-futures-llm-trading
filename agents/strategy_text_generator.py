#!/usr/bin/env python3
"""
Generatore di descrizioni testuali di strategie
Prima fase: genera logica di trading in linguaggio naturale
"""

import random
from typing import Dict, List, Any, Optional
from llm_utils import query_ollama_fast

class StrategyTextGenerator:
    def __init__(self, default_model: str = "phi3:mini"):
        self.default_model = default_model
        
        # Template per diversi tipi di strategia
        self.strategy_templates = {
            "scalping": {
                "description": "Strategia di scalping per operazioni veloci su timeframe brevi",
                "indicators": ["RSI", "EMA", "MACD", "Bollinger Bands", "ATR"],
                "timeframe": "1m-5m",
                "roi_target": "0.5-2%",
                "stoploss": "1-3%"
            },
            "momentum": {
                "description": "Strategia di momentum per seguire trend forti",
                "indicators": ["MACD", "RSI", "ADX", "EMA", "Volume"],
                "timeframe": "15m-1h",
                "roi_target": "2-5%",
                "stoploss": "2-4%"
            },
            "volatility": {
                "description": "Strategia per mercati volatili con breakout",
                "indicators": ["Bollinger Bands", "ATR", "RSI", "Stochastic", "Volume"],
                "timeframe": "5m-15m",
                "roi_target": "1-3%",
                "stoploss": "1.5-3%"
            },
            "breakout": {
                "description": "Strategia di breakout per livelli di supporto/resistenza",
                "indicators": ["Bollinger Bands", "Pivot Points", "Volume", "RSI", "EMA"],
                "timeframe": "15m-1h",
                "roi_target": "3-8%",
                "stoploss": "2-4%"
            },
            "adaptive": {
                "description": "Strategia adattiva che cambia approccio in base al mercato",
                "indicators": ["RSI", "MACD", "Bollinger Bands", "ATR", "ADX"],
                "timeframe": "5m-1h",
                "roi_target": "1-5%",
                "stoploss": "1.5-3%"
            }
        }
    
    def generate_strategy_description(self, 
                                    strategy_type: str = "volatility",
                                    complexity: str = "normal",
                                    style: str = "technical",
                                    randomization: float = 0.3) -> str:
        """
        Genera una descrizione testuale di strategia.
        
        Args:
            strategy_type: Tipo di strategia
            complexity: Livello di complessità (simple, normal, complex)
            style: Stile del prompt (technical, creative, conservative, aggressive)
            randomization: Livello di randomizzazione (0.0-1.0)
            
        Returns:
            Descrizione testuale della strategia
        """
        
        template = self.strategy_templates.get(strategy_type, self.strategy_templates["volatility"])
        
        # Crea prompt per la generazione
        prompt = self._create_description_prompt(template, complexity, style, randomization)
        
        try:
            description = query_ollama_fast(prompt, self.default_model, timeout=300)
            return self._clean_description(description)
        except Exception as e:
            print(f"❌ Errore nella generazione descrizione: {e}")
            return self._generate_fallback_description(template, strategy_type)
    
    def _create_description_prompt(self, template: Dict[str, Any], complexity: str, style: str, randomization: float) -> str:
        """Crea il prompt per la generazione della descrizione."""
        
        complexity_levels = {
            "simple": "semplice con 2-3 indicatori base",
            "normal": "media con 3-4 indicatori e condizioni composite",
            "complex": "complessa con 4-5 indicatori, filtri di trend e gestione rischio avanzata"
        }
        
        style_descriptions = {
            "technical": "approccio tecnico tradizionale",
            "creative": "approccio creativo con combinazioni innovative",
            "conservative": "approccio conservativo con gestione rischio rigorosa",
            "aggressive": "approccio aggressivo per massimizzare i profitti"
        }
        
        # Aggiungi randomizzazione
        random_indicators = self._get_random_indicators(template["indicators"], randomization)
        random_timeframe = self._get_random_timeframe(template["timeframe"], randomization)
        
        prompt = f"""
Descrivi una strategia di trading per futures crypto {template['description']}.

REQUISITI:
- Complessità: {complexity_levels[complexity]}
- Stile: {style_descriptions[style]}
- Indicatori principali: {', '.join(random_indicators)}
- Timeframe: {random_timeframe}
- Target ROI: {template['roi_target']}
- Stoploss: {template['stoploss']}

DESCRIVI IN DETTAGLIO:
1. Indicatori tecnici da utilizzare e parametri
2. Condizioni di entrata (quando comprare/vendere)
3. Condizioni di uscita (quando chiudere posizioni)
4. Gestione del rischio (stop loss, take profit, trailing)
5. Filtri di trend o volatilità
6. Parametri di ottimizzazione consigliati

Usa linguaggio naturale, non codice. Sii specifico sui valori e le logiche.
"""
        
        return prompt
    
    def _get_random_indicators(self, base_indicators: List[str], randomization: float) -> List[str]:
        """Aggiunge indicatori casuali basati sul livello di randomizzazione."""
        all_indicators = [
            "RSI", "EMA", "SMA", "MACD", "Bollinger Bands", "ATR", "Stochastic", 
            "ADX", "CCI", "Williams %R", "Volume", "OBV", "Pivot Points", "Ichimoku"
        ]
        
        if randomization < 0.3:
            return base_indicators[:3]  # Pochi indicatori base
        elif randomization < 0.7:
            # Aggiungi alcuni indicatori casuali
            additional = random.sample([i for i in all_indicators if i not in base_indicators], 2)
            return base_indicators[:3] + additional
        else:
            # Molti indicatori casuali
            return random.sample(all_indicators, 4)
    
    def _get_random_timeframe(self, base_timeframe: str, randomization: float) -> str:
        """Genera timeframe casuali."""
        timeframes = ["1m", "3m", "5m", "15m", "30m", "1h", "4h"]
        
        if randomization < 0.5:
            return base_timeframe
        else:
            return random.choice(timeframes)
    
    def _clean_description(self, description: str) -> str:
        """Pulisce la descrizione generata."""
        # Rimuovi parti di codice se presenti
        lines = description.split('\n')
        cleaned_lines = []
        
        for line in lines:
            if not line.strip().startswith('```') and not line.strip().startswith('class'):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _generate_fallback_description(self, template: Dict[str, Any], strategy_type: str) -> str:
        """Genera una descrizione di fallback."""
        return f"""
Strategia di {strategy_type} per futures crypto.

INDICATORI:
- RSI (14): per identificare condizioni di ipercomprato/ipervenduto
- EMA (9, 21): per trend direction
- Bollinger Bands (20): per volatilità e breakout

CONDIZIONI DI ENTRATA:
- RSI < 30 (ipervenduto)
- EMA 9 > EMA 21 (trend positivo)
- Prezzo vicino alla banda inferiore di Bollinger

CONDIZIONI DI USCITA:
- RSI > 70 (ipercomprato)
- EMA 9 < EMA 21 (trend negativo)
- Prezzo tocca la banda superiore di Bollinger

GESTIONE RISCHIO:
- Stoploss: 2%
- Take profit: 3%
- Trailing stop: 1% dopo 1% di profitto

PARAMETRI OTTIMIZZABILI:
- RSI buy/sell levels
- EMA periods
- Bollinger Bands deviation
- ROI e stoploss values
"""

    def generate_multiple_descriptions(self, 
                                     strategy_type: str = "volatility",
                                     count: int = 3,
                                     complexity: str = "normal") -> List[str]:
        """Genera multiple descrizioni della stessa strategia."""
        descriptions = []
        
        for i in range(count):
            style = random.choice(["technical", "creative", "conservative", "aggressive"])
            randomization = random.uniform(0.2, 0.8)
            
            description = self.generate_strategy_description(
                strategy_type=strategy_type,
                complexity=complexity,
                style=style,
                randomization=randomization
            )
            
            descriptions.append(description)
        
        return descriptions

def main():
    """Test del generatore di descrizioni."""
    generator = StrategyTextGenerator()
    
    print("🧠 Test generatore descrizioni strategie...")
    
    # Test singola descrizione
    description = generator.generate_strategy_description(
        strategy_type="volatility",
        complexity="normal",
        style="technical"
    )
    
    print("\n📝 Descrizione generata:")
    print("="*50)
    print(description)
    print("="*50)
    
    # Test multiple descrizioni
    print("\n🔄 Generazione multiple descrizioni...")
    descriptions = generator.generate_multiple_descriptions("scalping", 2)
    
    for i, desc in enumerate(descriptions, 1):
        print(f"\n--- Descrizione {i} ---")
        print(desc[:200] + "..." if len(desc) > 200 else desc)

if __name__ == "__main__":
    main() 