#!/usr/bin/env python3
"""
Generatore a due stadi per strategie FreqTrade
Combina generazione testuale + conversione in codice
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from .strategy_text_generator import StrategyTextGenerator
from .freqtrade_code_converter import FreqTradeCodeConverter
from .strategy_postprocess import postprocess_strategy

class TwoStageGenerator:
    def __init__(self, 
                 text_model: str = "phi3:mini",
                 code_model: str = "mistral:7b-instruct-q4_0"):
        self.text_generator = StrategyTextGenerator(default_model=text_model)
        self.code_converter = FreqTradeCodeConverter(default_model=code_model)
        
    def generate_strategy(self, 
                         strategy_type: str = "volatility",
                         complexity: str = "normal",
                         style: str = "technical",
                         randomization: float = 0.3,
                         strategy_name: str = None) -> Dict[str, Any]:
        """
        Genera una strategia usando l'approccio a due stadi.
        
        Args:
            strategy_type: Tipo di strategia
            complexity: Livello di complessità
            style: Stile del prompt
            randomization: Livello di randomizzazione
            strategy_name: Nome della strategia
            
        Returns:
            Dizionario con descrizione e codice generato
        """
        
        if strategy_name is None:
            strategy_name = self._generate_strategy_name(strategy_type)
        
        print(f"🔄 Generazione strategia {strategy_type} con approccio a due stadi...")
        
        # Fase 1: Genera descrizione testuale
        print("📝 Fase 1: Generazione descrizione testuale...")
        description = self.text_generator.generate_strategy_description(
            strategy_type=strategy_type,
            complexity=complexity,
            style=style,
            randomization=randomization
        )
        
        # Fase 2: Converti in codice FreqTrade
        print("🔧 Fase 2: Conversione in codice FreqTrade...")
        code = self.code_converter.convert_description_to_code(
            description=description,
            strategy_name=strategy_name,
            strategy_type=strategy_type
        )
        
        # Salva la strategia
        file_path = self._save_strategy(strategy_name, code, description)
        
        return {
            'strategy_name': strategy_name,
            'strategy_type': strategy_type,
            'description': description,
            'code': code,
            'file_path': file_path,
            'generation_time': datetime.now().isoformat(),
            'approach': 'two_stage'
        }
    
    def generate_multiple_strategies(self,
                                   strategy_type: str = "volatility",
                                   count: int = 3,
                                   complexity: str = "normal") -> List[Dict[str, Any]]:
        """
        Genera multiple strategie dello stesso tipo.
        """
        strategies = []
        
        for i in range(count):
            strategy_name = f"{strategy_type.capitalize()}Strategy_{i+1}"
            
            strategy = self.generate_strategy(
                strategy_type=strategy_type,
                complexity=complexity,
                style="technical",
                randomization=0.3 + (i * 0.2),
                strategy_name=strategy_name
            )
            
            strategies.append(strategy)
            print(f"✅ Strategia {i+1}/{count} generata: {strategy_name}")
        
        return strategies
    
    def generate_strategy_ensemble(self,
                                 strategy_type: str = "volatility",
                                 count: int = 3) -> Dict[str, Any]:
        """
        Genera un ensemble di strategie diverse.
        """
        print(f"🎭 Generazione ensemble per {strategy_type}...")
        
        # Genera strategie con diversi approcci
        approaches = [
            ("simple", "technical", 0.2),
            ("normal", "creative", 0.5),
            ("complex", "aggressive", 0.8)
        ]
        
        strategies = []
        
        for i, (complexity, style, randomization) in enumerate(approaches):
            if i >= count:
                break
                
            strategy_name = f"{strategy_type.capitalize()}Ensemble_{i+1}"
            
            strategy = self.generate_strategy(
                strategy_type=strategy_type,
                complexity=complexity,
                style=style,
                randomization=randomization,
                strategy_name=strategy_name
            )
            
            strategies.append(strategy)
        
        return {
            'ensemble_type': strategy_type,
            'strategies': strategies,
            'generation_time': datetime.now().isoformat(),
            'approach': 'two_stage_ensemble'
        }
    
    def _generate_strategy_name(self, strategy_type: str) -> str:
        """Genera un nome di strategia valido."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_type = re.sub(r'[^a-zA-Z0-9]', '', strategy_type)
        return f"{clean_type.capitalize()}Strategy_{timestamp}"
    
    def _save_strategy(self, strategy_name: str, code: str, description: str) -> str:
        """Salva la strategia su file."""
        # Crea directory se non esiste
        strategies_dir = "user_data/strategies"
        os.makedirs(strategies_dir, exist_ok=True)
        
        # Salva codice
        file_path = os.path.join(strategies_dir, f"{strategy_name.lower()}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Salva descrizione
        desc_path = os.path.join(strategies_dir, f"{strategy_name.lower()}_description.txt")
        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(f"Strategia: {strategy_name}\n")
            f.write(f"Generata il: {datetime.now().isoformat()}\n")
            f.write(f"Approccio: Two-stage generation\n\n")
            f.write(description)
        
        # Post-processing automatico: valida e correggi la strategia
        print("🔧 Post-processing automatico della strategia...")
        is_valid = postprocess_strategy(file_path)
        
        if is_valid:
            print(f"✅ Strategia validata e salvata: {file_path}")
        else:
            print(f"❌ Strategia non valida, spostata in strategies_broken")
            # Se non valida, il file è già stato spostato da postprocess_strategy
            return ""
        
        return file_path
    
    def validate_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """
        Valida una strategia generata.
        """
        file_path = f"user_data/strategies/{strategy_name.lower()}.py"
        
        if not os.path.exists(file_path):
            return {'valid': False, 'error': 'File non trovato'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Verifica sintassi
            import ast
            ast.parse(code)
            
            # Verifica elementi essenziali
            required_elements = [
                'class',
                'IStrategy',
                'populate_indicators',
                'populate_entry_trend',
                'populate_exit_trend'
            ]
            
            missing_elements = [elem for elem in required_elements if elem not in code]
            
            if missing_elements:
                return {
                    'valid': False,
                    'error': f'Elementi mancanti: {missing_elements}'
                }
            
            return {
                'valid': True,
                'file_path': file_path,
                'code_length': len(code),
                'has_optimization_params': 'IntParameter' in code or 'DecimalParameter' in code,
                'has_risk_management': 'stoploss' in code and 'trailing_stop' in code
            }
            
        except SyntaxError as e:
            return {'valid': False, 'error': f'Errore di sintassi: {e}'}
        except Exception as e:
            return {'valid': False, 'error': f'Errore di validazione: {e}'}

def main():
    """Test del generatore a due stadi."""
    generator = TwoStageGenerator()
    
    print("🚀 Test generatore a due stadi...")
    
    # Test singola strategia
    print("\n📊 Test 1: Generazione singola strategia")
    strategy = generator.generate_strategy(
        strategy_type="volatility",
        complexity="normal",
        style="technical",
        strategy_name="TestTwoStageStrategy"
    )
    
    print(f"✅ Strategia generata: {strategy['strategy_name']}")
    print(f"📁 File: {strategy['file_path']}")
    
    # Validazione
    validation = generator.validate_strategy("TestTwoStageStrategy")
    print(f"🔍 Validazione: {'✅' if validation['valid'] else '❌'}")
    if not validation['valid']:
        print(f"   Errore: {validation['error']}")
    
    # Test multiple strategie
    print("\n📊 Test 2: Generazione multiple strategie")
    strategies = generator.generate_multiple_strategies("scalping", 2)
    
    for strategy in strategies:
        print(f"   ✅ {strategy['strategy_name']}")
    
    # Test ensemble
    print("\n📊 Test 3: Generazione ensemble")
    ensemble = generator.generate_strategy_ensemble("momentum", 2)
    
    print(f"   🎭 Ensemble generato con {len(ensemble['strategies'])} strategie")
    for strategy in ensemble['strategies']:
        print(f"      • {strategy['strategy_name']}")

if __name__ == "__main__":
    main() 