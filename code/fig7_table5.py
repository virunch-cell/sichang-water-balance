"""Fig. 7 and Table 5 with the baseline decade 2012-2021 taken from the same daily TMD record (option a').
No parameter is assumed: monthly means = mean over the 10 years of the monthly sums of daily rainfall.
Projection = file 05 (HadGEM-AO RCP4.5 monthly climatology, 21 years); annual totals per model/RCP = file 09."""
import csv, glob, numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f=glob.glob('../data_raw/459202*.csv')[0]
d=pd.read_csv(f,encoding='utf-8-sig',parse_dates=['Date']); d['y']=d.Date.dt.year; d['m']=d.Date.dt.month
mon=d.groupby(['y','m']).Rainfall.sum().unstack()          # year x month totals
dec=mon.loc[2012:2021]; base=dec.mean().values; ann=dec.sum(1).mean()
print('n days per year 2012-2021:',d[d.y.between(2012,2021)].groupby('y').size().tolist())
print('baseline decade monthly mean (mm):',np.round(base,1),'annual',round(ann,1))
proj=np.array([float(r['rainfall_mm']) for r in csv.DictReader(open('05_rcp45_projected_monthly.csv'))])
print('projection monthly',proj,'annual',proj.sum())
print('change %',np.round((proj/base-1)*100,1))
print('Nov-Apr: base',round(base[[10,11,0,1,2,3]].sum(),1),'proj',proj[[10,11,0,1,2,3]].sum(),'pct',round((proj[[10,11,0,1,2,3]].sum()/base[[10,11,0,1,2,3]].sum()-1)*100,1))
print('May-Oct: base',round(base[4:10].sum(),1),'proj',proj[4:10].sum(),'pct',round((proj[4:10].sum()/base[4:10].sum()-1)*100,1))
print('Table 5 (annual mm, deviation from %.1f mm):'%ann)
for r in csv.DictReader(open('09_gcm_bias.csv')):
    s=[]
    for k in ('RCP2.6','RCP4.5','RCP8.5'):
        v=float(r[k+'_mm']); s.append('%s %s (%+.1f%%)'%(k,format(int(v),','),(v/ann-1)*100))
    print(' ',r['model'],'|'.join(s))
pd.DataFrame({'month':range(1,13),'baseline_2012_2021_mm':base.round(1),'HadGEM_RCP4.5_mm':proj}).to_csv('../results/raw_output/fig7_baseline_decade.csv',index=False)
M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']; x=np.arange(12)
fig,ax=plt.subplots(figsize=(7,3.8)); w=.38
ax.plot(x,base,'o-',color='#4c72b0',lw=1.8,ms=5,label='Observed 2012-2021 (Ko Sichang, TMD)')
ax.plot(x,proj,'s--',color='#dd8452',lw=1.8,ms=5,label='Projected 2026-2046, HadGEM-AO RCP4.5 (21-year mean)')
ax.set_xticks(x); ax.set_xticklabels(M); ax.set_ylabel('Monthly rainfall (mm)'); ax.legend(frameon=False,fontsize=8)
for s in ('top','right'): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('../results/figures/Figure11_projection_vs_baseline.png',dpi=200); plt.savefig('../results/figures/Figure11_projection_vs_baseline.pdf')
