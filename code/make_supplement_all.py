"""All Supplement tables and the Monte-Carlo figure in ONE Word file. No number is typed by hand:
every value is parsed from raw_output/*.txt, raw_output/*.csv, code/*.csv (inputs) or the constants in sc.py.
Run from this folder:   python3 make_supplement_all.py      ->  ../results/Supplement_tables_all.docx
Order of the whole chain: see README_run_order.md.   Numbering follows the order of first citation in the paper (S3-S6, S10-S12, S15, S17, S18; Figure S3)."""
import re, csv, sys
from docx import Document
from docx.shared import Pt, Cm

RAW = '../results/raw_output/'
def rd(f): return open(RAW + f, encoding='utf-8').read()
def csvrows(f): return list(csv.DictReader(open(f, encoding='utf-8')))
def arr(line): return [float(v) for v in re.search(r'\[(.*?)\]', line).group(1).split()]
mon = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
problems = []
def check(name, cond):
    print(('OK   ' if cond else 'FAIL ') + name)
    if not cond: problems.append(name)

# ---------- constants of the model (sc.py) ----------
sc = open('sc.py').read()
m = re.search(r'^CROOF,ETA,AROOF,ARES=([\d.]+),([\d.]+),([\d.]+)\.?,([\d.]+)\.?', sc, re.M)
CROOF, ETA, AROOF, ARES = float(m[1]), float(m[2]), float(m[3]), float(m[4])
m = re.search(r'^VTANK,VMAIN0,GW=([\d.]+)\.?,([\d.]+)\.?,([\d.]+)\.?', sc, re.M)
VTANK, VMAIN0, GW = float(m[1]), float(m[2]), float(m[3])
par = {r['parameter']: r for r in csvrows('08_parameters.csv')}
check('sc.py: eta = 0.90', ETA == 0.9)

# ---------- generator, persistence, seeds ----------
g = rd('generator_checks.txt').splitlines()
syn_mean = arr([l for l in g if l.startswith('monthly mean')][0])
syn_cv = arr([l for l in g if l.startswith('monthly CV')][0])
obs_cv = arr([l for l in g if l.startswith('observed monthly CV')][0])
mult_cv = arr([l for l in g if 'gamma multiplier CV' in l][0])
cva = float(re.search(r'CVA ([0-9.]+)', [l for l in g if 'CVA' in l][0]).group(1))
ann_cv = float(re.search(r'annual CV ([0-9.]+)', g[0]).group(1))
ann_mean = float(re.search(r'annual mean (\d+)', g[0]).group(1))
obs_mean = [float(r['rainfall_mm']) for r in csvrows('01_rainfall_observed_monthly.csv')]
e = rd('evap_rho_seed_checks.txt')
rho = re.findall(r'^rho ([0-9.]+) (\d+)', e, flags=re.M)
sl = re.search(r'\[([0-9, ]+)\] mean (\d+) sd (\d+)', e)
seeds = [int(v) for v in sl.group(1).split(',')]; smean, ssd = int(sl.group(2)), int(sl.group(3))
check('baseline robust catchment 188,713 (rho 0 = seed 1)', int(rho[0][1]) == 188713 and seeds[0] == 188713)

# ---------- pan coefficient (section A of evap_rho_seed_checks.txt) ----------
pan = re.findall(r'^Kp ([0-9.]+) annual (\d+) mm \| rel level ([0-9.]+) / const ([0-9.]+) \| with seasonal tourism level ([0-9.]+) / const ([0-9.]+) \| catch0\.90 level (\d+), level\+seasonal (\d+)', e, re.M)
check('four pan coefficients parsed', len(pan) == 4)
loss = int(re.search(r'level-dependent\): (\d+) m3/yr', e).group(1))
r080 = [p for p in pan if p[0] == '0.80'][0]
check('Kp 0.80 -> 0.865 / 0.832 / 0.834 / 0.807 and 287,362 / 457,094 (paper Sect. 4.6)',
      (r080[2], r080[3], r080[4], r080[5], r080[6], r080[7]) == ('0.865','0.832','0.834','0.807','287362','457094'))

# ---------- V and labour (sens_V.txt) ----------
vrows = []
for l in rd('sens_V.txt').splitlines()[1:]:
    t = l.replace('|', ' ').split()
    if len(t) < 11: continue
    vrows.append(dict(V=int(t[0]), lab=float(t[1]), ptot=int(t[4]), dem=int(t[5]), defi=int(t[6]),
                      days=float(t[7]), fail=int(t[8]), rob=int(t[9]), rel=float(t[10])))
vrows.sort(key=lambda r: (r['V'], r['lab']))
vbase = [r for r in vrows if r['V'] == 900000 and r['lab'] == 0.5][0]
check('stress test: deficit 32,558, demand 402,851, Ptot 10,173, robust 188,713',
      (vbase['defi'], vbase['dem'], vbase['ptot'], vbase['rob']) == (32558, 402851, 10173, 188713))

# ---------- constant per-capita use (const_wp.txt) ----------
cw = re.findall(r'^(paper 0\.12/0\.10|constant [0-9.]+)\s+demand\s+(\d+)\s+deficit\s+(-?\d+)\s+robust catchment \(0\.90\)\s+(\d+)', rd('const_wp.txt'), re.M)
check('constant wp: 0.11 reproduces the paper demand', [c for c in cw if c[0] == 'constant 0.11'][0][1:] == ('402851', '32558', '141474'))

# ---------- RCP4.5 climatology ----------
rc = csvrows(RAW + 'fig7_baseline_decade.csv')
rb = [float(r['baseline_2012_2021_mm']) for r in rc]; rp = [float(r['HadGEM_RCP4.5_mm']) for r in rc]
rcp05 = [float(r['rainfall_mm']) for r in csvrows('05_rcp45_projected_monthly.csv')]
check('RCP4.5 climatology: table equals file 05', rp == rcp05)
d4 = re.search(r'robust catchment hist (\d+) ; RCP4.5 (\d+)\nreliability of 188713 design: hist ([0-9.]+) ; RCP4.5 ([0-9.]+)\nreliability of mean-year design 95,730: hist ([0-9.]+) ; RCP4.5 ([0-9.]+)', e)
check('RCP4.5 sensitivity parsed', d4 is not None)
f7 = rd('fig7_table5.txt')
chg = arr([l for l in f7.splitlines() if l.startswith('change %')][0])
ann_b = float(re.search(r'baseline decade monthly mean.*?annual ([0-9.]+)', f7).group(1))
ann_p = float(re.search(r'projection monthly.*?annual ([0-9.]+)', f7).group(1))
check('RCP4.5 table: annual 1,168.2 and 1,162.0', (ann_b, ann_p) == (1168.2, 1162.0))
# TMD pan
pm = csvrows('04b_evaporation_pan_TMD_monthly.csv')

# ---------- document ----------
d = Document(); st = d.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(10)
def table(cap, hdr, rows, note=None):
    d.add_paragraph(cap)
    t = d.add_table(rows=1, cols=len(hdr)); t.style = 'Table Grid'
    for i, h in enumerate(hdr): t.rows[0].cells[i].text = h
    for row in rows:
        c = t.add_row().cells
        for i, v in enumerate(row): c[i].text = str(v)
    if note: d.add_paragraph(note)
    d.add_paragraph()
f0 = lambda x: f'{x:,.0f}'

# 1 parameters
Kc = int(par['K_eff']['value'])
table('Table S3. Parameters of the water-balance model: symbol, meaning, unit, value and source.',
 ['Symbol', 'Meaning', 'Unit', 'Value', 'Source'],
 [['C_roof', 'Roof runoff coefficient', '-', f'{CROOF}', 'Midpoint of 0.75-0.95 for roofs (ASCE/WEF, 1992, Table 5.5)'],
  ['η', 'Rooftop collection (filter) efficiency', '-', f'{ETA}', 'Dudkiewicz and Ludwińska (2023)'],
  ['A_roof', 'Connected roof area', 'm²', f0(AROOF), 'Estimated, Sect. 3.2 (range 190,000-300,000 m²)'],
  ['C_ws', 'Area-weighted watershed runoff coefficient', '-', par['C_ws']['value'], 'Table S2'],
  ['A_ws', 'Contributing watershed area', 'm²', f0(float(par['A_ws']['value'])), 'GIS layer, Table S2'],
  ['A_res', 'Reservoir and pond surface at full level', 'm²', f0(ARES), 'Land-use layer, artificial water body (Table S1)'],
  ['V_tank', 'Capacity of household cisterns', 'm³', f0(VTANK), 'Table 1'],
  ['V_main', 'Capacity of the main system (reservoir, ponds, water bank)', 'm³', f0(VMAIN0), 'Table 1'],
  ['W_gw,max', 'Sustainable groundwater use', 'm³ month⁻¹', f0(GW), 'Table 1'],
  ['W_ext,max', 'Import by barge (PWA)', 'm³ day⁻¹', f0(float(par['PWA_daily']['value'])), 'Table 1'],
  ['w_p', 'Per-capita use, dry season (Nov-Apr) / wet season (May-Oct)', 'm³ person⁻¹ day⁻¹', '0.12 / 0.10', 'Kaosa-ard et al. (2001); RID manual (n.d.); Ko Si Chang Municipality (personal communication, January 2025)'],
  ['V', 'Visitors per year, current / stress test', 'yr⁻¹', f"{int(par['V_current']['value']):,} / {int(par['V_future']['value']):,}", 'Swangkong (2023); stress test is not a forecast'],
  ['-', 'Transient labour as a share of equivalent visitors', '-', par['labour_fraction']['value'], 'Assumption; sensitivity in Table S11'],
  ['CV_A', 'CV of the annual rainfall factor', '-', f'{cva:.4f}', 'Calibrated to the observed annual CV, Table S4'],
  ['CV_m', 'CV of the monthly gamma multiplier', '-', f'{min(mult_cv):.2f}-{max(mult_cv):.2f}', 'Set so that the monthly CV equals the observed CV, Table S4 and Figure S3'],
  ['K_pan', 'Class A pan to open-water coefficient', '-', par['pan_coefficient']['value'], 'Rittima et al. (2013); 0.70-0.85 tested, Table S17'],
  ['R*', 'Target long-run reliability of the robust design', '-', par['reliability_target']['value'], 'Design choice; 0.85 and 0.95 shown in Figure 6']],
 f'Combined constant K = C_ws·A_ws + A_res = {Kc:,} m² (computed with the unrounded C_ws).')

# 2-4 generator
table('Table S4. Parameters of the monthly rainfall generator: observed (Si Chang, 1985-2025) and synthetic (100,000-year) monthly rainfall.',
 ['Month', 'Observed mean (mm)', 'Observed CV', 'Multiplier CV', 'Synthetic mean (mm)', 'Synthetic CV'],
 [[mon[i], f'{obs_mean[i]:.1f}', f'{obs_cv[i]:.2f}', f'{mult_cv[i]:.3f}', f'{syn_mean[i]:.1f}', f'{syn_cv[i]:.2f}'] for i in range(12)],
 f'Multiplier CV: CV of the gamma multiplier applied to each month independently, set so that the synthetic monthly CV equals the observed CV. Observed data: Thai Meteorological Department. Annual factor: lognormal, mean 1, CV {cva:.2f}, shared by the 12 months of a year. Synthetic annual rainfall: mean {ann_mean:,.0f} mm, CV {ann_cv:.2f}.')
base = int(rho[0][1])
table('Table S5. Effect of year-to-year persistence (autocorrelation rho of the log annual factor) on the robust catchment (reliability 0.90, +20,000 m³).',
 ['rho', 'Robust catchment (m²)', 'Change from rho = 0 (%)'],
 [[r, f'{int(v):,}', ('0.0' if int(v) == base else f'{(int(v)/base-1)*100:+.1f}')] for r, v in rho])
table('Table S6. Robust catchment (reliability 0.90, 20,000 m³ of added storage) for six independent random samples. Sample 1 is the baseline used in the paper.',
 ['Sample', 'Robust catchment (m²)'], [[i+1, f'{v:,}'] for i, v in enumerate(seeds)],
 f'Mean {smean:,} m²; standard deviation {ssd:,} m² ({ssd/smean*100:.0f} %).')
d.add_picture('../results/figures/FigureS3_rainfall_multiplier_pdfs.png', width=Cm(15))
d.add_paragraph('Figure S3. Probability density functions of the rainfall multipliers: (a) lognormal annual factor (mean 1, CV %.2f); (b) gamma monthly multiplier (mean 1, CV %.2f-%.2f by month).' % (cva, min(mult_cv), max(mult_cv)))
d.add_paragraph()

# 5 V and labour
table('Table S11. Sensitivity of the stress-test results to the number of visitors V and the share of transient labour.',
 ['V (yr⁻¹)', 'Labour share', 'P_tot (persons)', 'Demand (m³ yr⁻¹)', 'Balance (m³ yr⁻¹)', 'Import days, mean year', 'Months with import, mean year', 'Robust catchment (m²)', 'Reliability of 188,713 m² design'],
 [[f"{r['V']:,}", f"{r['lab']:.2f}", f"{r['ptot']:,}", f"{r['dem']:,}", f"{r['defi']:,}", f"{r['days']:.1f}", r['fail'], f"{r['rob']:,}", f"{r['rel']:.3f}"] for r in vrows],
 'Baseline stress test: V = 900,000 and labour share 0.50. Balance = annual demand minus local supply after groundwater (positive: structural deficit; negative: surplus). Robust catchment: additional catchment for reliability 0.90 at +20,000 m³; last column: long-run reliability of the baseline robust design (188,713 m²).')

# 6 constant per-capita use
table('Table S12. Effect of a constant per-capita use (the same value in both seasons) compared with the seasonal values used in the paper (0.12 and 0.10 m³ person⁻¹ day⁻¹). Balance as in Table S11.',
 ['Per-capita use', 'Demand (m³ yr⁻¹)', 'Balance (m³ yr⁻¹)', 'Robust catchment (m²)'],
 [[('0.12 (dry) / 0.10 (wet), paper' if c[0].startswith('paper') else c[0].split()[1]), f'{int(c[1]):,}', f'{int(c[2]):,}', f'{int(c[3]):,}'] for c in cw])

# 7 pan coefficient
table('Table S17. Sensitivity of the evaporation results to the pan coefficient (robust design 188,713 m², +20,000 m³).',
 ['Pan coefficient', 'Annual evaporation (mm)', 'Reliability, evaporation only (level / constant)', 'Reliability, with seasonal tourism (level / constant)', 'Catchment for 0.90 (m²), evaporation only', 'Catchment for 0.90 (m²), with seasonal tourism'],
 [[p[0], f'{int(p[1]):,}', f'{p[2]} / {p[3]}', f'{p[4]} / {p[5]}', f'{int(p[6]):,}', f'{int(p[7]):,}'] for p in pan],
 f'Baseline Kp 0.80. Mean annual loss, level-dependent: {loss:,} m³ yr⁻¹. Reliability: long-run reliability with level-dependent / constant evaporating area. Catchment: additional catchment that restores reliability 0.90 with level-dependent evaporation. Each is given without and with the seasonal tourism profile.')

# 8 pan data
table('Table S18. Monthly Class A pan evaporation at the two nearest stations with pan records (Thai Meteorological Department, 2023) and the open-water evaporation used in the model (pan mean × pan coefficient).',
 ['Month', 'Chon Buri (mm)', 'Phatthaya (mm)', 'Mean pan (mm)', 'Pan coefficient', 'Open-water evaporation (mm)'],
 [[r['month'], r['pan_chonburi_48459_mm'], r['pan_phatthaya_48461_mm'], r['pan_mean_mm'], r['pan_coefficient'], r['open_water_evaporation_mm']] for r in pm],
 f"Annual: mean pan {sum(float(r['pan_mean_mm']) for r in pm):,.0f} mm; open water {sum(float(r['open_water_evaporation_mm']) for r in pm):,.0f} mm.")

# 9-10 RCP4.5
table('Table S10. Monthly rainfall of the observed decade 2012-2021 (Thai Meteorological Department) and of the 21-year projection 2026-2046 (HadGEM-AO, RCP4.5, downscaled).',
 ['Month', 'Observed 2012-2021 (mm)', 'Projected 2026-2046 (mm)', 'Change (%)'],
 [[mon[i], f'{rb[i]:.1f}', f'{rp[i]:.0f}', f'{chg[i]:+.0f}'] for i in range(12)] +
 [['Year', f'{ann_b:.1f}', f'{ann_p:.0f}', f'{(ann_p/ann_b-1)*100:+.1f}']])
table('Table S15. Sensitivity case: stress-test demand driven by the projected RCP4.5 rainfall (single climate model, no change in variability) instead of the observed 1985-2025 climate.',
 ['Result', 'Observed climate', 'RCP4.5'],
 [['Robust catchment at +20,000 m³ (m²)', f'{int(d4[1]):,}', f'{int(d4[2]):,}'],
  ['Long-run reliability of the 188,713 m² design', d4[3], d4[4]],
  ['Long-run reliability of the mean-year design (95,730 m²)', d4[5], d4[6]]])

d.save('../results/Supplement_tables_all.docx')
print('saved ../results/Supplement_tables_all.docx;', 'problems:', problems if problems else 'none')
sys.exit(1 if problems else 0)
