"""Fig. 2 split in two (R1): (a) monthly mean rainfall 1985-2025 from file 01; (b) monthly water demand, current and stress test, from file 03.
No value is assumed; both come from the CSV files. Output: ../results/figures/Figure02_rainfall_monthly.png/.pdf and ../results/figures/Figure04_demand_monthly.png/.pdf (final figure numbers to be set in the paper)."""
import csv, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rain=[float(r['rainfall_mm']) for r in csv.DictReader(open('01_rainfall_observed_monthly.csv'))]
dem=list(csv.DictReader(open('03_demand_monthly.csv')))
cur=[float(r['demand_current_m3']) for r in dem]; fut=[float(r['demand_future_m3']) for r in dem]
x=np.arange(12); lab=list('JFMAMJJASOND')
fig,ax=plt.subplots(figsize=(5.6,3.3))
ax.bar(x,rain,color='#6baed6',width=0.8)
ax.set_ylim(0,280); ax.set_ylabel('Monthly rainfall (mm)'); ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_xlabel('Month')
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('../results/figures/Figure02_rainfall_monthly.png',dpi=200); fig.savefig('../results/figures/Figure02_rainfall_monthly.pdf'); plt.close(fig)
fig,ax=plt.subplots(figsize=(5.6,3.3))
ax.plot(x,cur,'o-',color='#d62728',ms=4,lw=1.6,label='Current demand')
ax.plot(x,fut,'s--',color='#7b1fa2',ms=4,lw=1.6,label='Stress-test demand')
ax.set_ylim(0,45000); ax.set_ylabel('Monthly water demand (m$^3$)'); ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_xlabel('Month')
ax.legend(loc='lower center',fontsize=8,ncol=2,frameon=False)
for s in ('top','right'): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig('../results/figures/Figure04_demand_monthly.png',dpi=200); fig.savefig('../results/figures/Figure04_demand_monthly.pdf'); plt.close(fig)
print(rain); print(cur[0],cur[5],fut[0],fut[5])
