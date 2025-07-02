#!/bin/bash

# Crea ambiente virtuale se non esiste
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Ambiente virtuale creato in ./venv"
fi

# Attiva ambiente virtuale
source venv/bin/activate
echo "Ambiente virtuale attivato"

# Aggiorna pip
pip install --upgrade pip

# Installa requirements
pip install -r requirements.txt

# Aggiorna tutte le librerie installate
pip list --outdated --format=columns | tail -n +3 | awk '{print $1}' | xargs -r -n1 pip install -U

echo "Setup completato!"
