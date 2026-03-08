#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 edge_model_v3.py
python3 strategy_selector_v3.py
python3 ticket_generator_v3.py
python3 result_feedback_v3.py
echo "v3 pipeline complete"
