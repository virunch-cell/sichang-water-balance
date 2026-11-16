"""Calibrate CVA (CV of the lognormal annual factor) so that the realised CV of annual totals
equals the observed 0.231 (Ko Sichang, 1985-2025), given the monthly means and monthly CVs in the input files."""
import numpy as np, csv
col=lambda fn,c:[float(r[c]) for r in csv.DictReader(open(fn))]
mu=np.array(col('01_rainfall_observed_monthly.csv','rainfall_mm')); OBS=np.array(col('10_rainfall_cv_monthly.csv','cv_monthly_1985_2025'))
TARGET=0.231
def ann(c,n=40000):
    cvm=np.sqrt((1+OBS**2)/(1+c**2)-1); k=1/cvm**2; rng=np.random.default_rng(5); sg=np.sqrt(np.log(1+c**2))
    kap=np.exp(rng.standard_normal(n)*sg-sg**2/2); tot=(mu*rng.gamma(k,1/k,(n,12))).sum(1)*kap; return tot.std()/tot.mean()
lo,hi=0.01,0.3
for _ in range(30):
    m=(lo+hi)/2
    if ann(m)<TARGET: lo=m
    else: hi=m
print('CVA = %.4f ; realised annual CV = %.3f'%((lo+hi)/2,ann((lo+hi)/2)))
