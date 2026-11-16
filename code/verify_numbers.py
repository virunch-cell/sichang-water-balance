"""Compares the numbers produced by the pipeline (../results/raw_output) with the values printed in the paper.
Prints PASS/FAIL for each item and exits with status 1 if any fails.   Run after run_all.sh:   python3 verify_numbers.py"""
import re, csv, sys, os
R = '../results/raw_output/'
def rd(f): return open(R + f, encoding='utf-8').read() if os.path.exists(R + f) else ''
def has(text, pat): return re.search(pat, text) is not None
checks = []
def chk(label, ok): checks.append((label, bool(ok)))
A, B, C = rd('stageA.txt'), rd('stageB.txt'), rd('stageC.txt')
DP = rd('reproduce_discussion_paper.txt')
m = re.search(r'REPRO det0 (\d+) det20 (\d+) rob20 (\d+)', DP)
chk('Discussion paper (its inputs): mean-year design 206,500 / 93,600 m2 and robust design 147,400 m2 reproduced within 1 %',
    m is not None and abs(int(m.group(1))/206500-1) < .01 and abs(int(m.group(2))/93600-1) < .01 and abs(int(m.group(3))/147400-1) < .01)
# input data: annual demand of the current case and of the stress test (Table 2)
dm = list(csv.DictReader(open('03_demand_monthly.csv')))
chk('Table 2 / data file 03: annual demand, current case 328,244 m3', round(sum(float(r['demand_current_m3']) for r in dm)) == 328244)
chk('Table 2 / data file 03: annual demand, stress test 402,851-402,852 m3', round(sum(float(r['demand_future_m3']) for r in dm)) in (402851, 402852))
# Sect. 4.1 structural balance (stress test, eta = 0.90)
chk('Sect 4.1: rooftop potential 217,244; local supply 370,293; structural deficit 32,558 m3/yr', has(A, r'rooftop 217244 .*sum 370293 deficit 32558'))
# Table 3 baseline water balance and RRV (mean year)
chk('Table 3, current demand: used 186,071, spill 31,173, 3.3 import days, rel 0.92, res 1.00, vul 4,964', has(A, r"T6 cur \{'used': 186071, 'spill': 31173.*'imp_days': (np\.float64\()?3\.3.*'rel': 0\.92.*'res': 1\.0.*'vul': 4964"))
chk('Table 3, stress test: used 197,454, spill 19,790, 43.5 import days, rel 0.75, res 0.33, vul 21,769', has(A, r"T6 fut \{'used': 197454, 'spill': 19790.*43\.5.*'rel': 0\.75.*'res': 0\.33.*'vul': 21769"))
# Table 4 mean-year versus robust design
chk('Table 4: mean-year design 95,730 m2, reliability 0.835, 23 import days', has(A, r'T7 det 95730 rel 0\.835 imp d 23\.0'))
chk('Table 4: robust design 188,713 m2, reliability 0.900, 12.6 (~13) import days', has(A, r'T7 rob 188713 rel 0\.9 imp d 12\.6'))
chk('Fig. 6: mean-year design without added storage 224,835 m2', has(A, r'det dV=0: 224835'))
# Table S7 convergence (independent runs of N years)
for N, r, h in ((100,'0.881','0.019'),(250,'0.909','0.012'),(500,'0.898','0.009'),(1000,'0.908','0.006'),(1390,'0.903','0.005'),(2000,'0.904','0.004'),(3000,'0.906','0.003'),(5000,'0.904','0.003')):
    chk('Table S7: N = %d  reliability %s  half-width %s' % (N, r, h), has(A, r'\b%d %s %s' % (N, re.escape(r), re.escape(h))))
# Table S13 (deficit sensitivity) and S14 (robust catchment sensitivity)
for nm, row in (('Per-capita use','[-48013, -7727, 72843, 113128]'),('Roof area','[76006, 54282, 10833, -10891]'),('Runoff coefficient','[59711, 46135, 18981, 5404]'),('Tourism demand','[8150, 20354, 44762, 56966]'),('Groundwater yield','[36014, 34286, 30830, 29102]')):
    chk('Table S13: %s %s' % (nm, row), (nm + ' ' + row) in A.replace('  ', ' '))
for nm, row in (('Per-capita use','[21507, 86763, 370545, 613199]'),('Tourism demand','[121457, 149400, 236668, 291388]'),('Roof area','[242350, 214582, 165338, 142883]'),('Runoff coefficient','[219336, 204025, 173402, 158090]'),('Groundwater yield','[191630, 190254, 187290, 186169]')):
    chk('Table S14: %s %s' % (nm, row), (nm + ' ' + row) in B.replace('  ', ' '))
# Table S16 evaporation and seasonal tourism; catchment for 0.90 and RCP4.5 / rho / pan (Sects. 4.5 and 4.6)
for nm, u, s in (('none','0.9','0.867'),('level','0.865','0.834'),('const','0.832','0.807')):
    chk('Table S16: %s evaporation  uniform %s  seasonal %s' % (nm, u, s), has(C, r'%s uniform %s seasonal %s' % (nm, re.escape(u), re.escape(s))))
chk('Sect. 4.6: catchment for 0.90 with evaporation and seasonal tourism 457,094 m2', has(C, r'457094'))
chk('Sect. 4.6: catchment for 0.90 with evaporation only 287,362 m2', has(C, r'evap 287362'))
chk('Sect. 4.5 / Table S15: RCP4.5 robust catchment 130,974 m2', has(C, r'RCP4\.5 130974'))
chk('Table S5: rho = 0.5 gives 189,580 m2', has(C, r'rho\.5 189580'))
# Fig. 6 frontier
fr = open(R + 'fig8_frontier.csv').read() if os.path.exists(R + 'fig8_frontier.csv') else ''
for dv, v in ((0,'388282'),(10000,'265286'),(20000,'188713'),(40000,'126659'),(80000,'89364')):
    chk('Fig. 6 frontier: added storage %d m3 -> robust (0.90) %s m2' % (dv, v), has(fr, r'^%d,\d+,%s,' % (dv, v)) or has(fr, r'(?m)^%d,\d+,%s' % (dv, v)))
# Figs. 7 and 8 (failure months) and Table S6 / S4 / S17
F9 = rd('fig9_fig10.txt')
chk('Figs. 7-8: robust design, 1,390 years, long-run reliability 0.9, 63 % of years with at most one import month', has(F9, r'robust dA 188713\.0 years 1390 long-run rel 0\.9 .*>=11/12 0\.632'))
chk('Figs. 7-8: mean-year design, long-run reliability 0.835, 42 % of years with at most one import month', has(F9, r'mean-year dA 95730\.0 years 1390 long-run rel 0\.835 .*>=11/12 0\.419'))
E_ = rd('evap_rho_seed_checks.txt')
chk('Table S6: baseline (seed 11) and mean of six samples 180,078 m2', has(E_, r'188713') and has(E_, r'180078'))
chk('Table S17: pan coefficient 0.80 -> reliability 0.865 / 0.832 (level / constant)', has(E_, r'0\.865') and has(E_, r'0\.832'))
G = rd('generator_checks.txt')
chk('Table S4 / Sect. 3.7: generator mean 1,160 mm, annual CV 0.231, annual factor CV 0.1342, lag-1 autocorrelation ~0', has(G, r'annual mean 1160 mm, realised annual CV 0\.231') and has(G, r'CVA 0\.1342') and has(G, r'autocorr of annual totals 0\.00'))
S = rd('make_supplement_all.txt')
chk('Supplement tables: internal consistency checks passed ("problems: none")', has(S, r'problems: none'))
w = max(len(c[0]) for c in checks)
for label, ok in checks: print(('PASS  ' if ok else 'FAIL  ') + label)
n_ok = sum(ok for _, ok in checks)
print('\n%d of %d checks passed' % (n_ok, len(checks)))
sys.exit(0 if n_ok == len(checks) else 1)
