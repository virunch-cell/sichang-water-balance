#!/usr/bin/env bash
# Runs the whole pipeline of the paper from the input data to every number, figure and supplement table.
# Usage:  bash run_all.sh            (about 25-40 min on one CPU core; no GPU, no internet needed)
#         bash run_all.sh quick      (skips the slow frontier / sensitivity runs of Figs. 6, 9, 10 = run_figs.sh)
set -uo pipefail
cd "$(dirname "$0")/code"
R=../results/raw_output; F=../results/figures
mkdir -p "$R" "$F"
LOG=../results/run_log.txt; : > "$LOG"
fail=0
step() { name=$1; shift; echo "[$(date +%T)] $name" | tee -a "$LOG"
         if "$@" > "$R/$name.txt" 2>> "$LOG"; then echo "   ok" >> "$LOG"; else echo "   FAILED: $name" | tee -a "$LOG"; fail=1; fi; }
# 0. inputs derived from the daily rainfall record (checks of the monthly means and CVs in data files 01 and 10)
step cv_from_daily      python3 cv_from_daily.py
step calibrate_cva      python3 calibrate_cva.py
# 1. checks of the stochastic generator and of the design sample
step generator_checks   python3 generator_checks.py
step evap_rho_seed_checks python3 evap_rho_seed_checks.py
step sens_V             python3 sens_V.py
step const_wp           python3 const_wp.py
step failure_months_check python3 failure_months_check.py
step eta_check_0.8      python3 eta_check.py 0.8
step eta_check_0.9      python3 eta_check.py 0.9
# discussion-paper values reproduced with the discussion-paper inputs (shows that they were obtained by simulation)
step reproduce_discussion_paper python3 reproduce_discussion_paper.py
# 2. main tables: baseline RRV, mean-year and robust design, convergence, sensitivity, evaporation (Tables 3, 4, S7, S13, S14, S16)
step stageA             python3 run_all_staged.py new A
step stageB             python3 run_all_staged.py new B
step stageC             python3 run_all_staged.py new C
# 3. figures drawn from code
step fig2_split         python3 fig2_split.py
step fig5_flowchart     python3 fig5_flowchart.py
step fig7_table5        python3 fig7_table5.py
step fig9_fig10         python3 fig9_fig10.py
step fig_S_mc_pdfs      python3 fig_S_mc_pdfs.py
if [ "${1:-}" != "quick" ]; then step run_figs bash run_figs.sh; fi
# 4. supplement tables (reads only the files written above; stops if a value differs from the paper)
step make_supplement_all python3 make_supplement_all.py
# 5. comparison with the numbers printed in the paper
python3 verify_numbers.py | tee "$R/verify_numbers.txt" | tee -a "$LOG"
[ $fail -eq 0 ] && echo "ALL STEPS COMPLETED" | tee -a "$LOG" || echo "SOME STEPS FAILED - see results/run_log.txt" | tee -a "$LOG"
