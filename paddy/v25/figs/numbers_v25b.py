# v25b numbers for the manuscript (abstract, Sects 4.1-4.4), from ../results/ghg_phase_rows.csv via v25data.py
import numpy as np
from v25data import years,totals
W={'rf189':23.0,'irr061':21.8,'irr043':18.7,'rf184':14.1,'irr092':12.6,'rf151':9.7}
def tot2(st,site,dose,half=True):
    Y=years(st,site,dose); t={k:sum(r[k] for r in Y) for k in ('ch4s','ch4f','n2o','pda','alk','lat','cc','cat')}
    # cumulative cap check, year by year: calcite stores 1 mol CO2 per 2 eq of Ca/Mg -> cap = (R - PDA)/2
    cR=np.cumsum([r['cat'] for r in Y]); cP=np.cumsum([r['pda'] for r in Y]); cC=np.cumsum([r['cc'] for r in Y])
    t['cap_binds_half']=bool(np.any(cC>np.maximum(cR-cP,0)/2)); t['cap_binds_full']=bool(np.any(cC>np.maximum(cR-cP,0)))
    t['ch4']=t['ch4s']+t['ch4f']; t['ccC']=min(t['cc'],max(t['cat']-t['pda'],0)/(2 if half else 1))
    t['net']=t['ch4']+t['n2o']-t['pda']-t['ccC']; t['netpot']=t['ch4']+t['n2o']-t['cat']
    y1=Y[0]['ch4s']+Y[0]['ch4f']; t['ch4y1']=y1; t['netfix']=10*y1+t['n2o']-t['pda']-t['ccC']
    # cation fate on an equivalent basis (calcite = 2 eq per mol CO2)
    t['f_pda']=t['pda']/t['cat']; t['f_cc']=2*t['ccC']/t['cat']; t['f_ret']=1-t['f_pda']-t['f_cc']
    t['y']=Y; return t
R={}
for s in W: R[s]=tot2('v25bb',s,20)
print('site    net   netfix  ch4   n2o   pda   lat   cc   cat  f_pda f_cc f_ret  cap1/2 capfull')
for s,t in R.items(): print(f"{s:7s}{t['net']:6.1f}{t['netfix']:7.1f}{t['ch4']:6.1f}{t['n2o']:6.2f}{t['pda']:6.2f}{t['lat']:6.2f}{t['ccC']:6.2f}{t['cat']:6.1f}  {t['f_pda']:.2f} {t['f_cc']:.2f} {t['f_ret']:.2f}  {t['cap_binds_half']} {t['cap_binds_full']}")
aw=lambda k: sum(W[s]*R[s][k] for s in W)/sum(W.values())
print('AREA-WEIGHTED:',{k:round(aw(k),2) for k in ('net','netfix','netpot','ch4','n2o','pda','lat','ccC','cat','f_pda','f_cc','f_ret')})
for st,lab in (('v25bb','w0.15'),('v25bbw0','w0'),('v25bbw04','w0.4')):
  for d in (10,20):
    t=tot2(st,'ref',d); Y=t['y']
    print(f"\nref {lab} {d} t: net {t['net']:.1f} netfix {t['netfix']:.1f} netpot {t['netpot']:.1f} ch4 {t['ch4']:.2f} n2o {t['n2o']:.2f} pda {t['pda']:.2f} lat {t['lat']:.2f} cc {t['ccC']:.2f} cat {t['cat']:.1f} fate pda/cc/ret {t['f_pda']:.2f}/{t['f_cc']:.2f}/{t['f_ret']:.2f} cap1/2 {t['cap_binds_half']}")
    if st=='v25bb':
        print(' yr1: CH4 mitig (s+f) %.2f, realised CDR (pda+cc) %.2f, cation release %.2f; pct y1 %.1f'%(-t['ch4y1'],Y[0]['pda']+Y[0]['cc'],Y[0]['cat'],Y[0]['pct']))
        print(' yr10: CH4 saving full %.2f fixed %.2f; annual realised CDR %.2f'%(-(Y[9]['ch4s']+Y[9]['ch4f']),-t['ch4y1'],Y[9]['pda']+Y[9]['cc']))
        print(' annual CDR by year:',[round(r['pda']+r['cc'],2) for r in Y]); print(' annual PDA:',[round(r['pda'],2) for r in Y])
        print(' annual CH4 saving:',[round(-(r['ch4s']+r['ch4f']),2) for r in Y])
        print(' GWP* CH4 (4 x GWP100 sum), full %.1f fixed %.1f'%(-4*t['ch4'],-40*t['ch4y1']))
        print(' ctrl CH4 season', [round(r['ctl_ch4s'],1) for r in Y])
