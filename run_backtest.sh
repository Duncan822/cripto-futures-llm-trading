#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
freqtrade backtesting --config user_data/config.json --strategy LLMStrategy --timerange 20240101-20241231
