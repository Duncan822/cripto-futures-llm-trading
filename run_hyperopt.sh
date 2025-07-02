#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
freqtrade hyperopt --config user_data/config.json --strategy LLMStrategy --epochs 100 --spaces buy sell roi stoploss
