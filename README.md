# Code and data: water-scarcity risk and robust design for Si Chang Island

Code, input data and checks for the revised manuscript *Assessing dry-season water-scarcity risk on a tourism-exposed small island: a multi-source water-balance framework for Si Chang Island, Thailand* (NHESS, egusphere-2026-4005; the discussion paper was titled *Assessing and reducing dry-season water-scarcity risk on a tourism-exposed small island: a multi-source water-balance and robust-optimisation framework for Si Chang Island, Thailand*).

Figure and table numbers below are those of the revised manuscript. Script names keep the figure numbers of the discussion paper (e.g. `fig8_frontier.py` draws Figure 6); output figure files carry the numbers of the revised manuscript.

Everything needed to reproduce the numbers, figures and supplement tables that are computed from the model is in this folder. One command runs the whole pipeline and compares the results with the numbers printed in the paper.

## Run

    python3 -m pip install -r requirements.txt     # Python 3.10 or newer
    bash run_all.sh                                # about 25-40 min on one CPU core, no internet needed
    bash run_all.sh quick                          # skips the slow frontier/sensitivity runs of Figs. 6, 9 and 10

Output (all written to `results/`, nothing outside the folder is touched):

* `results/raw_output/` text and csv results of every step, and `verify_numbers.txt` (PASS/FAIL for each paper number),
* `results/figures/` the figures drawn by code (png and pdf),
* `results/Supplement_tables_all.docx` the supplement tables that are computed (captions are in the order of the paper),
* `results/run_log.txt` log of the run.

`run_all.sh` stops nothing on an error but prints `FAILED` for the step and the last line says whether all steps completed. All random numbers use fixed seeds, so results are identical on every run.

## What is where

    code/        model (sc.py), scripts, and the input data files 01-10 (csv)
    data_raw/    daily rainfall record of the Ko Sichang station, 1985-2025 (TMD) - see the note on data below
    results/     written by run_all.sh

Input data files (`code/`):

| file | content | source |
|---|---|---|
| `01_rainfall_observed_monthly.csv` | mean monthly rainfall 1985-2025 (mm) | daily record in `data_raw/` (Thai Meteorological Department, TMD) |
| `01_..._PAPER_2012_2021.csv` | mean monthly rainfall 2012-2021 (mm) as printed in the discussion paper | used only by `reproduce_discussion_paper.py`; the comparison with the projection (Fig. 11, Table S10) uses the 2012-2021 means recomputed from the daily record (`fig7_table5.py`) |
| `02_watershed_runoff_monthly.csv` | watershed runoff to the reservoir (m3) | runoff coefficient and watershed area (Table S2) |
| `03_demand_monthly.csv` | monthly demand, current case and stress test (m3) | Eqs. (1)-(2), inputs of Tables 2 and S3 |
| `04b_evaporation_pan_TMD_monthly.csv` | Class A pan evaporation, Chon Buri and Phatthaya, and open-water evaporation (Table S18) | TMD (2023) |
| `05_rcp45_projected_monthly.csv` | downscaled monthly rainfall 2026-2046, HadGEM-AO, RCP4.5 | downscaling by the authors (not part of this code) |
| `06_storage_inventory.csv`, `07_landuse.csv` | storage inventory (Table 1) and land use (Table S1) | island authorities, GIS land-use layer (Land Development Department) |
| `08_parameters.csv` | model parameters (Table S3) | see the table |
| `09_gcm_bias.csv` | annual rainfall of each downscaled GCM (Table S9) | downscaling by the authors |
| `10_rainfall_cv_monthly.csv` | observed coefficient of variation of monthly rainfall | `cv_from_daily.py` |

`04_evaporation_net_monthly.csv` is an older literature-based profile that the model no longer uses; it is kept only for completeness.

## Which script produces what

| paper item | script | output |
|---|---|---|
| Table 3 baseline water balance and RRV; Table 4 mean-year and robust design; Table S7 convergence; Tables S13, S14, S16 | `run_all_staged.py` (runs `run_all.py` in three parts) | `raw_output/stageA.txt`, `stageB.txt`, `stageC.txt` |
| Sect. 4.1 structural deficit | `run_all_staged.py` | `stageA.txt` |
| Fig. 2 rainfall, Fig. 4 demand | `fig2_split.py` | `figures/Figure02_rainfall_monthly`, `Figure04_demand_monthly` |
| Fig. 3 flow chart | `fig5_flowchart.py` | `figures/Figure03_methods_flowchart` |
| Fig. 6 catchment-storage frontier | `fig8_frontier.py` (called by `run_figs.sh`) | `figures/Figure06_frontier`, `raw_output/fig8_frontier.csv` |
| Figs. 7 and 8 reservoir operation, years by import months | `fig9_fig10.py`, `failure_months_check.py` | `figures/Figure07_reservoir_operation`, `Figure08_annual_reliability` |
| Fig. 9 sensitivity, Fig. 10 evaporation and seasonal tourism | `fig11_fig12.py` (called by `run_figs.sh`) | `figures/Figure09_sensitivity`, `Figure10_evaporation_tourism` |
| Fig. 11 projected rainfall, Table S10 | `fig7_table5.py` | `figures/Figure11_projection_vs_baseline`, `raw_output/fig7_baseline_decade.csv` |
| Tables S4, S5, S6, S15, S17 (generator, persistence, seeds, RCP4.5, pan coefficient) | `generator_checks.py`, `evap_rho_seed_checks.py` | `raw_output/generator_checks.txt`, `evap_rho_seed_checks.txt` |
| Table S11 (visitors, labour), Table S12 (constant per-capita use) | `sens_V.py`, `const_wp.py` | `raw_output/sens_V.txt`, `const_wp.txt` |
| Fig. S3 probability density functions of the rainfall multipliers | `fig_S_mc_pdfs.py` | `figures/FigureS3_rainfall_multiplier_pdfs` |
| supplement tables S3-S6, S10-S12, S15, S17, S18 as a Word file | `make_supplement_all.py` | `Supplement_tables_all.docx` |
| design values of the discussion paper reproduced with its inputs (see below) | `reproduce_discussion_paper.py` | `raw_output/reproduce_discussion_paper.txt` |
| comparison with the paper | `verify_numbers.py` | `raw_output/verify_numbers.txt` |
| calibration of the annual-factor CV (0.1342); effect of the filter efficiency (0.8 vs 0.9) | `calibrate_cva.py`, `eta_check.py` | `raw_output/` |

Method in short: monthly two-subsystem water balance with carry-over (household cisterns and main system), reliability-resilience-vulnerability metrics, mean-year design by bisection on the added catchment (the smallest catchment for which every month of the mean year is satisfactory, i.e. no import month at periodic steady state), robust design by bisection to a long-run reliability of 0.90 on a stochastic rainfall sample (1,500 generated years, the first 50 discarded; the first 60 years of each run are spin-up, so 1,390 years are evaluated; seed 11), see Sect. 3 of the paper. The model itself is `sc.py` (`simulate`, `gen`, `mincat`).

## Design method of the discussion paper

Sect. 3.4 of the discussion paper described the mean-year design as a mixed-integer linear program and Sect. 3.5 the robust design as a two-stage formulation. The values printed there were, however, obtained by the simulation and bisection used in this package. `reproduce_discussion_paper.py` runs `sc.simulate` with the inputs of the discussion paper (2012-2021 rainfall as printed, eta = 0.80, inflow 140,020 m3/yr, generator with annual CV 0.20 and monthly CV 0.35) and the criteria of the revised manuscript, and reproduces the printed values: mean-year design 206,670 and 93,506 m2 (printed 206,500 and 93,600; ~0.1 %), robust design 148,069 m2 (printed 147,400; 0.5 %, within the Monte-Carlo sampling spread), structural deficit 46,430 m3/yr (printed 46,432). No optimisation solver is used anywhere in this package.

## Not included

* The neural-network downscaling of the CMIP5 models. Its output (files 05 and 09) is an input here. The correlation table (Table S8) comes from that step.
* Figures 1, 5, S1 and S2 (map, climate-evaluation scheme, field photograph, satellite image) and Tables 1, 2, S1, S2, S8 and S9 are inputs or descriptions, not model output.
* The land-use GIS layer.

## Data

The daily rainfall record (`data_raw/`) was provided by the Thai Meteorological Department on request and is cited in the paper. It is needed only for `cv_from_daily.py` and `fig7_table5.py`. Check the conditions of use before redistributing the file.

## Reproducibility notes

Python 3.10+ with numpy, pandas, scipy, matplotlib and python-docx (`requirements.txt`). Results were produced and checked with numpy 2.5, pandas 3.0, scipy 1.18, matplotlib 3.11 and Python 3.13. Warnings about future pandas versions may be printed and do not affect the results.

## Contact and licence

Corresponding author: Pinit Tanachaichoksirikun (pinit.ta@kmitl.ac.th). Licence: to be set by the authors before public deposit (the code and the TMD daily record may need different terms).
