import subprocess
import os
import json
import logging
from typing import Dict, Optional, List
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreqtradeManager:
    def __init__(self, config_path: str = "user_data/config.json"):
        self.config_path = config_path
        self.user_data_dir = "user_data"
        self.strategies_dir = f"{self.user_data_dir}/strategies"
        self.data_dir = f"{self.user_data_dir}/data"
        self.logs_dir = f"{self.user_data_dir}/logs"
        self.backtest_results_dir = f"{self.user_data_dir}/backtest_results"
        self.hyperopt_results_dir = f"{self.user_data_dir}/hyperopt_results"
        
        # Individua il binario di Freqtrade. Se l'ambiente virtuale è attivo, usa il percorso locale,
        # altrimenti fallback sul comando globally installato.
        venv_path = os.environ.get("VIRTUAL_ENV")
        if venv_path and Path(venv_path, "bin", "freqtrade").exists():
            self._freqtrade_bin = str(Path(venv_path, "bin", "freqtrade"))
        else:
            # Fallback: assuming freqtrade is in PATH
            self._freqtrade_bin = "freqtrade"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist."""
        directories = [
            self.user_data_dir,
            self.strategies_dir,
            self.data_dir,
            self.logs_dir,
            self.backtest_results_dir,
            self.hyperopt_results_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_strategy(self, code: str, name: str) -> str:
        """
        Salva la strategia in user_data/strategies/{name}.py e restituisce il path.
        """
        strategy_path = f"{self.strategies_dir}/{name}.py"
        
        # Ensure the strategy directory exists
        os.makedirs(self.strategies_dir, exist_ok=True)
        
        with open(strategy_path, "w", encoding='utf-8') as f:
            f.write(code)
        
        logger.info(f"Strategia salvata in: {strategy_path}")
        return strategy_path
    
    def download_data(self, pairs: List[str], timeframe: str = "5m", 
                     timerange: str = "20240101-20241231") -> bool:
        """
        Scarica i dati storici per le coppie specificate.
        """
        try:
            cmd = [
                *self._cmd("download-data"),
                "--config", self.config_path,
                "--timeframe", timeframe,
                "--timerange", timerange,
                "--pairs", *pairs
            ]
            
            logger.info(f"Downloading data for pairs: {pairs}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Download completato con successo")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore nel download dati: {e}")
            logger.error(f"Output: {e.stdout}")
            logger.error(f"Error: {e.stderr}")
            return False
    
    def run_backtest(self, strategy_path: str, timerange: str = "20240101-20241231") -> Dict[str, float]:
        """
        Esegue il backtest Freqtrade e restituisce metriche chiave.
        """
        strategy_name = os.path.splitext(os.path.basename(strategy_path))[0]
        
        try:
            cmd = [
                *self._cmd("backtesting"),
                "--config", self.config_path,
                "--strategy", strategy_name,
                "--timerange", timerange,
                "--export", "trades",
                "--export-filename", f"{self.backtest_results_dir}/backtest_{strategy_name}.json"
            ]
            
            logger.info(f"Eseguendo backtest per strategia: {strategy_name}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse results from output
            output = result.stdout
            metrics = self._parse_backtest_output(output)
            
            logger.info(f"Backtest completato per {strategy_name}")
            return metrics
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore nel backtest: {e}")
            logger.error(f"Output: {e.stdout}")
            logger.error(f"Error: {e.stderr}")
            return {"profit": 0.0, "sharpe": 0.0, "trades": 0}
    
    def _parse_backtest_output(self, output: str) -> Dict[str, float]:
        """
        Parse the backtest output to extract key metrics.
        """
        metrics = {
            "profit": 0.0,
            "sharpe": 0.0,
            "trades": 0,
            "win_rate": 0.0,
            "max_drawdown": 0.0
        }
        
        try:
            # Look for key metrics in the output
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if "Total Profit" in line and "%" in line:
                    try:
                        # Extract percentage from line like "Total Profit: 12.34%"
                        parts = line.split(':')
                        if len(parts) > 1:
                            profit_str = parts[1].strip().replace('%', '').replace(',', '')
                            metrics["profit"] = float(profit_str)
                    except:
                        pass
                elif "Sharpe Ratio" in line:
                    try:
                        sharpe_str = line.split(':')[1].strip()
                        metrics["sharpe"] = float(sharpe_str)
                    except:
                        pass
                elif "Total Trades" in line:
                    try:
                        trades_str = line.split(':')[1].strip()
                        metrics["trades"] = int(trades_str)
                    except:
                        pass
                elif "Win Rate" in line and "%" in line:
                    try:
                        win_rate_str = line.split(':')[1].strip().replace('%', '')
                        metrics["win_rate"] = float(win_rate_str)
                    except:
                        pass
                elif "Max Drawdown" in line and "%" in line:
                    try:
                        drawdown_str = line.split(':')[1].strip().replace('%', '')
                        metrics["max_drawdown"] = float(drawdown_str)
                    except:
                        pass
                elif "Total Profit" in line and "USDT" in line:
                    # Alternative format: "Total Profit: 123.45 USDT"
                    try:
                        parts = line.split(':')
                        if len(parts) > 1:
                            profit_str = parts[1].strip().split()[0].replace(',', '')
                            metrics["profit"] = float(profit_str)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Errore nel parsing output backtest: {e}")
        
        return metrics
    
    def run_hyperopt(self, strategy_path: str, epochs: int = 100, 
                    timerange: str = "20240101-20241231") -> Dict[str, float]:
        """
        Esegue Hyperopt Freqtrade e restituisce le metriche della migliore strategia trovata.
        """
        strategy_name = os.path.splitext(os.path.basename(strategy_path))[0]
        
        try:
            cmd = [
                *self._cmd("hyperopt"),
                "--config", self.config_path,
                "--strategy", strategy_name,
                "--epochs", str(epochs),
                "--timerange", timerange,
                "--spaces", "buy", "sell", "roi", "stoploss",
                "--loss", "SharpeHyperOptLoss",
                "--export-filename", f"{self.hyperopt_results_dir}/hyperopt_{strategy_name}.json"
            ]
            
            logger.info(f"Eseguendo hyperopt per strategia: {strategy_name} con {epochs} epochs")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse hyperopt results
            metrics = self._parse_hyperopt_output(result.stdout)
            
            logger.info(f"Hyperopt completato per {strategy_name}")
            return metrics
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore in Hyperopt: {e}")
            logger.error(f"Output: {e.stdout}")
            logger.error(f"Error: {e.stderr}")
            return {"best_profit": 0.0, "best_params": {}}
    
    def _parse_hyperopt_output(self, output: str) -> Dict[str, float]:
        """
        Parse the hyperopt output to extract best results.
        """
        metrics = {
            "best_profit": 0.0,
            "best_sharpe": 0.0,
            "best_params": {}
        }
        
        try:
            lines = output.split('\n')
            for line in lines:
                if "Best result:" in line:
                    # Extract best profit from the line
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "profit:":
                                profit_str = parts[i+1].replace('%', '').replace(',', '')
                                metrics["best_profit"] = float(profit_str)
                                break
                    except:
                        pass
                elif "Best Sharpe:" in line:
                    try:
                        sharpe_str = line.split(':')[1].strip()
                        metrics["best_sharpe"] = float(sharpe_str)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Errore nel parsing output hyperopt: {e}")
        
        return metrics
    
    def list_strategies(self) -> List[str]:
        """
        Lista tutte le strategie disponibili.
        """
        strategies = []
        if os.path.exists(self.strategies_dir):
            for file in os.listdir(self.strategies_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    strategies.append(file[:-3])  # Remove .py extension
        return strategies
    
    def validate_strategy(self, strategy_path: str) -> bool:
        """
        Valida una strategia Freqtrade.
        """
        try:
            strategy_name = os.path.splitext(os.path.basename(strategy_path))[0]
            
            # Usa il comando list-strategies per validare
            cmd = [
                *self._cmd("list-strategies"),
                "--config", self.config_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Controlla se la strategia appare nella lista
            if strategy_name in result.stdout:
                logger.info("Strategia validata con successo")
                return True
            else:
                logger.error(f"Strategia {strategy_name} non trovata nella lista")
                return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore nella validazione strategia: {e}")
            return False

    def validate_python_syntax(self, code: str) -> str | None:
        """
        Controlla se il codice Python è sintatticamente valido.
        Restituisce None se valido, altrimenti una stringa con l'errore.
        """
        try:
            compile(code, '<string>', 'exec')
            return None
        except SyntaxError as e:
            return f"SyntaxError: {e}"
        except Exception as e:
            return f"Error: {e}"

    def auto_correct_strategy(self, code: str) -> str:
        """
        Tenta di correggere automaticamente errori comuni nelle strategie generate.
        Restituisce il codice corretto o una strategia template valida.
        """
        logger.info("🔧 Tentativo di auto-correzione della strategia...")
        
        # 1. Correzione sintattica di base
        corrected_code = self._fix_syntax_errors(code)
        
        # 2. Verifica se ora è sintatticamente valido
        if self.validate_python_syntax(corrected_code) is None:
            logger.info("✅ Auto-correzione sintattica riuscita")
            return corrected_code
        
        # 3. Se ancora non valido, prova correzioni più aggressive
        corrected_code = self._fix_common_patterns(corrected_code)
        
        if self.validate_python_syntax(corrected_code) is None:
            logger.info("✅ Auto-correzione avanzata riuscita")
            return corrected_code
        
        # 4. Se tutto fallisce, usa una strategia template valida
        logger.warning("⚠️ Auto-correzione fallita, uso strategia template")
        return self._get_template_strategy()
    
    def _fix_syntax_errors(self, code: str) -> str:
        """Corregge errori sintattici comuni."""
        # Rimuovi caratteri problematici all'inizio/fine
        code = code.strip()
        
        # Correggi stringhe non chiuse
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Conta le virgolette nella riga
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            
            # Se numero dispari di virgolette, aggiungi una virgoletta di chiusura
            if single_quotes % 2 == 1:
                line += "'"
            if double_quotes % 2 == 1:
                line += '"'
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_common_patterns(self, code: str) -> str:
        """Corregge pattern comuni nelle strategie generate."""
        # Assicurati che ci sia una classe principale
        if 'class' not in code:
            code = self._get_template_strategy()
            return code
        
        # Assicurati che ci siano i metodi richiesti
        required_methods = ['populate_indicators', 'populate_entry_trend', 'populate_exit_trend']
        missing_methods = []
        
        for method in required_methods:
            if method not in code:
                missing_methods.append(method)
        
        if missing_methods:
            # Aggiungi i metodi mancanti
            template_methods = self._get_missing_methods_template(missing_methods)
            code += '\n\n' + template_methods
        
        return code
    
    def _get_missing_methods_template(self, missing_methods: list) -> str:
        """Genera template per i metodi mancanti."""
        templates = {
            'populate_indicators': '''
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola gli indicatori tecnici.
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # EMA
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        
        return dataframe
''',
            'populate_entry_trend': '''
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        dataframe.loc[
            (dataframe['rsi'] < 30) & (dataframe['ema_short'] > dataframe['ema_long']),
            'enter_long'] = 1
        
        return dataframe
''',
            'populate_exit_trend': '''
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        dataframe.loc[
            (dataframe['rsi'] > 70) | (dataframe['ema_short'] < dataframe['ema_long']),
            'exit_long'] = 1
        
        return dataframe
'''
        }
        
        result = ""
        for method in missing_methods:
            if method in templates:
                result += templates[method]
        
        return result
    
    def _get_template_strategy(self) -> str:
        """Restituisce una strategia template valida."""
        return '''"""
LLMStrategy - Strategia template valida
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, IntParameter
from freqtrade.persistence import Trade

logger = logging.getLogger(__name__)

class LLMStrategy(IStrategy):
    """
    Strategia template per trading futures crypto.
    """
    
    # Parametri di base
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
    
    # Parametri ottimizzabili
    buy_rsi = IntParameter(20, 40, default=30, space="buy")
    sell_rsi = IntParameter(60, 80, default=70, space="sell")
    
    # Timeframe
    timeframe = "5m"
    
    # Indicatori
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Popola gli indicatori tecnici.
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # EMA
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=21)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        dataframe.loc[
            (dataframe['rsi'] < self.buy_rsi.value) & 
            (dataframe['ema_short'] > dataframe['ema_long']) &
            (dataframe['macd'] > dataframe['macdsignal']),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        dataframe.loc[
            (dataframe['rsi'] > self.sell_rsi.value) | 
            (dataframe['ema_short'] < dataframe['ema_long']) |
            (dataframe['macd'] < dataframe['macdsignal']),
            'exit_long'] = 1
        
        return dataframe
'''

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def _cmd(self, *args: str) -> List[str]:
        """Costruisce il comando completo per Freqtrade con path corretto."""
        return [self._freqtrade_bin, *args]
    
    def _run_command(self, cmd: List[str]) -> Optional[str]:
        """Esegue un comando e restituisce l'output."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Errore nell'esecuzione comando {' '.join(cmd)}: {e}")
            logger.error(f"Output: {e.stdout}")
            logger.error(f"Error: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"Errore generico nell'esecuzione comando: {e}")
            return None

# Legacy functions for backward compatibility
def save_strategy(code: str, name: str) -> str:
    """Legacy function - use FreqtradeManager.save_strategy instead."""
    manager = FreqtradeManager()
    return manager.save_strategy(code, name)

def run_backtest(strategy_path: str) -> Dict[str, float]:
    """Legacy function - use FreqtradeManager.run_backtest instead."""
    manager = FreqtradeManager()
    return manager.run_backtest(strategy_path)

def run_hyperopt(strategy_path: str, epochs: int = 20) -> Dict[str, float]:
    """Legacy function - use FreqtradeManager.run_hyperopt instead."""
    manager = FreqtradeManager()
    return manager.run_hyperopt(strategy_path, epochs) 