"""Reproduces the design values printed in the discussion paper (egusphere-2026-4005, July 2026)
with the model of this package (sc.simulate), using the inputs of the discussion paper.

Purpose: to show that the design values of the discussion paper were obtained by simulation
(bisection on the additional catchment), not by the mixed-integer program described in its Sect. 3.4.

Inputs of the discussion paper (changed in the revised manuscript):
  * monthly rainfall: the 2012-2021 means printed in the discussion paper (file 01_..._PAPER_2012_2021.csv)
  * filter efficiency eta = 0.80
  * watershed inflow to the main system: file 02 (140,020 m3/yr), i.e. K = mean(Wres / rainfall)
  * stochastic generator of the discussion paper: lognormal annual factor (CV 0.20) x independent
    gamma monthly multiplier (CV 0.35, the same in every month); evaluation sample generate(1500, seed=11)[50:]
Criteria (identical to the revised manuscript):
  * mean-year design: smallest additional catchment for which every month of the mean year is satisfactory
  * robust design: smallest additional catchment with a long-run reliability of at least 0.90
Run: python3 reproduce_discussion_paper.py   (about 1 min)
"""
import csv
import numpy as np
import sc

def col(fn, c): return np.array([float(r[c]) for r in csv.DictReader(open(fn))])

# ---- inputs of the discussion paper
MU_DP = col('01_rainfall_observed_monthly_PAPER_2012_2021.csv', 'rainfall_mm') / 1000.
WRES = col('02_watershed_runoff_monthly.csv', 'Wres_m3')
K_DP = (WRES / MU_DP).mean()
sc.ETA = 0.80          # sc.simulate reads the module-level ETA
DEM = sc.DEMF

def generate_dp(n, seed=11, cv_a=0.20, cv_m=0.35, mu=MU_DP):
    """Generator of the discussion paper (constant monthly CV)."""
    rng = np.random.default_rng(seed)
    s = np.sqrt(np.log(1 + cv_a**2))
    kappa = rng.lognormal(-s**2 / 2, s, n)
    k = 1 / cv_m**2
    return np.array([mu * kappa[y] * rng.gamma(k, 1 / k, 12) for y in range(n)])

def mean_year_design(dV, years=70):
    Pm = np.tile(MU_DP, (years, 1))
    lo, hi = 0., 600000.
    for _ in range(30):
        m = (lo + hi) / 2
        if sc.simulate(Pm, m, dV, K_DP, dem=DEM).sum() == 0: hi = m   # no import month at periodic steady state
        else: lo = m
    return hi

def robust_design(Pe, dV, target=0.90):
    lo, hi = 0., 600000.
    for _ in range(24):
        m = (lo + hi) / 2
        if sc.rel(Pe, m, dV, K_DP, dem=DEM) >= target: hi = m
        else: lo = m
    return (lo + hi) / 2

roof = sc.CROOF * sc.ETA * MU_DP.sum() * sc.AROOF
deficit = DEM.sum() - roof - WRES.sum() - 12 * sc.GW
Pe = generate_dp(1500, seed=11)[50:]
det0, det20 = mean_year_design(0.), mean_year_design(20000.)
rob20 = robust_design(Pe, 20000.)
rel_det, rel_rob = sc.rel(Pe, det20, 20000., K_DP, dem=DEM), sc.rel(Pe, rob20, 20000., K_DP, dem=DEM)

rows = [("Structural annual deficit (m3/yr)", 46432, deficit),
        ("Mean-year design, no added storage (m2)", 206500, det0),
        ("Mean-year design, +20,000 m3 (m2)", 93600, det20),
        ("Robust design, +20,000 m3 (m2)", 147400, rob20),
        ("Long-run reliability, mean-year design", 0.83, rel_det),
        ("Long-run reliability, robust design", 0.90, rel_rob)]
print("Discussion-paper inputs: annual rainfall %.1f mm, eta %.2f, K %.0f m2, watershed inflow %.0f m3/yr"
      % (MU_DP.sum() * 1000, sc.ETA, K_DP, WRES.sum()))
print("%-42s %12s %12s %8s" % ("Quantity", "Printed", "Reproduced", "Diff"))
for name, pub, val in rows:
    if pub < 1:
        print("%-42s %12.2f %12.3f %8s" % (name, pub, val, "%+.3f" % (val - pub)))
    else:
        print("%-42s %12s %12s %7.1f%%" % (name, format(pub, ','), format(round(val), ','), 100 * (val - pub) / pub))
print("REPRO det0 %d det20 %d rob20 %d" % (round(det0), round(det20), round(rob20)))
