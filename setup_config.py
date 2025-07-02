#!/usr/bin/env python3
"""
Script per ricreare i file di configurazione Freqtrade mancanti.
"""

import os
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_config_json():
    """Crea il file config.json principale."""
    config = {
        "max_open_trades": 3,
        "stake_currency": "USDT",
        "stake_amount": 100,
        "tradable_balance_ratio": 0.99,
        "fiat_display_currency": "USD",
        "timeframe": "5m",
        "dry_run": True,
        "dry_run_wallet": 1000,
        "cancel_open_orders_on_exit": False,
        "trading_mode": "futures",
        "margin_mode": "isolated",
        "unfilledtimeout": {
            "entry": 10,
            "exit": 10,
            "exit_timeout_count": 0,
            "unit": "minutes"
        },
        "entry_pricing": {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1,
            "price_last_balance": 0.0,
            "check_depth_of_market": {
                "enabled": False,
                "bids_to_ask_delta": 1
            }
        },
        "exit_pricing": {
            "price_side": "same",
            "use_order_book": True,
            "order_book_top": 1
        },
        "exchange": {
            "name": "binance",
            "key": "",
            "secret": "",
            "ccxt_config": {
                "enableRateLimit": True,
                "options": {
                    "defaultType": "future"
                }
            },
            "ccxt_async_config": {
                "enableRateLimit": True,
                "rateLimit": 200
            },
            "pair_whitelist": [
                "BTC/USDT:USDT",
                "ETH/USDT:USDT",
                "BNB/USDT:USDT",
                "ADA/USDT:USDT",
                "SOL/USDT:USDT"
            ],
            "pair_blacklist": []
        },
        "pairlists": [
            {
                "method": "StaticPairList"
            }
        ],
        "edge": {
            "enabled": False,
            "process_throttle_secs": 3600,
            "calculate_since_number_of_days": 7,
            "capital_available_percentage": 0.5,
            "allowed_risk": 0.01,
            "stoploss_range_min": -0.01,
            "stoploss_range_max": -0.1,
            "stoploss_range_step": -0.01,
            "minimum_winrate": 0.60,
            "minimum_expectancy": 0.20,
            "min_trade_number": 10,
            "max_trade_duration_minute": 1440,
            "remove_pumps": False
        },
        "telegram": {
            "enabled": False,
            "token": "",
            "chat_id": ""
        },
        "api_server": {
            "enabled": False,
            "listen_ip_address": "0.0.0.0",
            "listen_port": 8080,
            "verbosity": "error",
            "enable_openapi": False,
            "jwt_secret_key": "",
            "CORS_origins": [],
            "username": "",
            "password": ""
        },
        "bot_name": "crypto-futures-llm-trading",
        "initial_state": "running",
        "force_entry_enable": False,
        "internals": {
            "process_throttle_secs": 5
        }
    }

    config_path = "user_data/config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    logger.info(f"✅ Config creato: {config_path}")
    return config_path

def create_hyperopt_config_json():
    """Crea il file hyperopt_config.json."""
    config = {
        "strategy": "LLMStrategy",
        "epochs": 100,
        "spaces": ["buy", "sell", "roi", "stoploss"],
        "timerange": "20240101-20241231",
        "timeframe": "5m",
        "max_open_trades": 3,
        "stake_amount": 100,
        "dry_run": True,
        "dry_run_wallet": 1000,
        "trading_mode": "futures",
        "margin_mode": "isolated",
        "exchange": {
            "name": "binance",
            "key": "",
            "secret": "",
            "ccxt_config": {
                "enableRateLimit": True,
                "options": {
                    "defaultType": "future"
                }
            },
            "pair_whitelist": [
                "BTC/USDT:USDT",
                "ETH/USDT:USDT",
                "BNB/USDT:USDT",
                "ADA/USDT:USDT",
                "SOL/USDT:USDT"
            ]
        },
        "hyperopt": {
            "loss": "SharpeHyperOptLoss",
            "min_trades": 10,
            "print_colorized": True,
            "print_json": False,
            "job_timeout": 180,
            "random_state": 42,
            "spaces": {
                "buy": {
                    "buy_rsi": "int",
                    "buy_macd_fast": "int",
                    "buy_macd_slow": "int",
                    "buy_macd_signal": "int"
                },
                "sell": {
                    "sell_rsi": "int"
                },
                "roi": {
                    "0": "float",
                    "30": "float",
                    "60": "float",
                    "120": "float"
                },
                "stoploss": "float"
            }
        }
    }

    config_path = "user_data/hyperopt_config.json"
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

    logger.info(f"✅ Hyperopt config creato: {config_path}")
    return config_path

def create_base_strategy():
    """Crea una strategia base per i test."""
    strategy_code = '''"""
LLMStrategy - Strategia base generata da LLM
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pandas import DataFrame
import talib.abstract as ta
import pandas_ta as pta
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from freqtrade.strategy.interface import IStrategy
from freqtrade.persistence import Trade
from freqtrade.enums import CandleType

logger = logging.getLogger(__name__)

class LLMStrategy(IStrategy):
    """
    Strategia base per trading futures crypto.
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

        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0, matype=0)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']

        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di entrata.
        """
        conditions = []

        # Condizione RSI
        conditions.append(dataframe['rsi'] < self.buy_rsi.value)

        # Condizione EMA
        conditions.append(dataframe['ema_short'] > dataframe['ema_long'])

        # Condizione MACD
        conditions.append(dataframe['macd'] > dataframe['macdsignal'])

        # Condizione Bollinger
        conditions.append(dataframe['close'] < dataframe['bb_lowerband'])

        # Condizione Volume
        conditions.append(dataframe['volume'] > dataframe['volume_mean'] * 1.5)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Definisce i segnali di uscita.
        """
        conditions = []

        # Condizione RSI
        conditions.append(dataframe['rsi'] > self.sell_rsi.value)

        # Condizione EMA
        conditions.append(dataframe['ema_short'] < dataframe['ema_long'])

        # Condizione MACD
        conditions.append(dataframe['macd'] < dataframe['macdsignal'])

        # Condizione Bollinger
        conditions.append(dataframe['close'] > dataframe['bb_upperband'])

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Stoploss dinamico basato sul profitto.
        """
        if current_profit > 0.02:
            return 0.01
        elif current_profit > 0.01:
            return 0.015
        else:
            return self.stoploss
'''

    strategy_path = "user_data/strategies/LLMStrategy.py"
    os.makedirs(os.path.dirname(strategy_path), exist_ok=True)

    with open(strategy_path, 'w') as f:
        f.write(strategy_code)

    logger.info(f"✅ Strategia base creata: {strategy_path}")
    return strategy_path

def create_directories():
    """Crea le directory necessarie."""
    directories = [
        "user_data",
        "user_data/strategies",
        "user_data/data",
        "user_data/backtest_results",
        "user_data/hyperopt_results",
        "user_data/logs"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Directory creata: {directory}")

def main():
    """Esegue la configurazione completa."""
    logger.info("🔧 Iniziando configurazione Freqtrade...")

    try:
        # Crea directory
        create_directories()

        # Crea file di configurazione
        create_config_json()
        create_hyperopt_config_json()

        # Crea strategia base
        create_base_strategy()

        logger.info("🎉 Configurazione completata con successo!")
        logger.info("📁 File creati:")
        logger.info("  - user_data/config.json")
        logger.info("  - user_data/hyperopt_config.json")
        logger.info("  - user_data/strategies/LLMStrategy.py")

        return True

    except Exception as e:
        logger.error(f"❌ Errore durante la configurazione: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
