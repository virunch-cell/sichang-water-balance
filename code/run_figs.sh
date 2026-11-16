#!/bin/bash
# regenerates the data behind Figs. 8, 11 and 12 (about 10-15 min) and then draws them
cd "$(dirname "$0")"
python3 fig8_frontier.py calc 0 10000 20000 40000 80000
python3 fig11_fig12.py calc11 "Per-capita use" "Tourism demand" "Roof area" "Runoff coefficient" "Groundwater yield"
python3 fig11_fig12.py calc12
python3 fig8_frontier.py plot
python3 fig11_fig12.py plot
echo ALLDONE
