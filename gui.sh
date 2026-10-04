#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")"

if [[ -d ".venv" ]]; then
    source .venv/bin/activate
fi

cd "$(dirname "$(readlink -f "$0")")/src"
python3 main.py
