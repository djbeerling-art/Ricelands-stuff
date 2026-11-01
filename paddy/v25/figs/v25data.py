# v25b figure data: 10-yr year-round (season + fallow) budgets from ../results/ghg_phase_rows.csv
# (exact time-integrated fluxes, ghg_budget.py commit 482bad3b). Each treatment vs the year-matched control of the same set.
# GWP100: CH4 27, N2O 273 (per kg N2O; N2O-N x 44.01/28.01).
import os,numpy as np,pandas as pd
D=pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../results/ghg_phase_rows.csv'))
COL=dict(ch4='CH4 (kg/ha)',n2o='N2O (kg N/ha)',pda='potentially durable ALK (t CO2/ha)',alk='ALK export (t CO2/ha)',
         lat='lateral ALK (t CO2/ha)',cc='calcite (t CO2/ha)',cat='cation release (t CO2/ha)')
GCH4=27e-3; GN2O=273e-3*44.01/28.01      # t CO2e per kg CH4, per kg N2O-N
def rows(st,site,dose): return D[(D.set==st)&(D.site==site)&(D.dose_t_ha==dose)].sort_values(['year','phase'])
def years(st,site,dose):
    """per-year treatment-minus-control terms (t CO2 or CO2e /ha), season (s) and fallow (f) split for CH4"""
    b,c=rows(st,site,dose),rows(st,site,0); out=[]
    for y in range(1,11):
        B={p:b[(b.year==y)&(b.phase==p)].iloc[0] for p in ('season','fallow')}; C={p:c[(c.year==y)&(c.phase==p)].iloc[0] for p in ('season','fallow')}
        dd=lambda k: sum(B[p][COL[k]]-C[p][COL[k]] for p in B)
        out.append(dict(y=y,ch4s=(B['season'][COL['ch4']]-C['season'][COL['ch4']])*GCH4,ch4f=(B['fallow'][COL['ch4']]-C['fallow'][COL['ch4']])*GCH4,
            n2o=dd('n2o')*GN2O,pda=dd('pda'),alk=dd('alk'),lat=dd('lat'),cc=dd('cc'),cat=sum(B[p][COL['cat']] for p in B),
            ctl_ch4s=C['season'][COL['ch4']],trt_ch4s=B['season'][COL['ch4']],
            pct=100*(B['season'][COL['ch4']]/C['season'][COL['ch4']]-1)))
    return out
def totals(st,site,dose):
    Y=years(st,site,dose); t={k:sum(r[k] for r in Y) for k in ('ch4s','ch4f','n2o','pda','alk','cc','cat')}
    t['cc']=min(t['cc'],max(t['cat']-t['pda'],0)); t['ret']=t['cat']-t['pda']-t['cc']      # cumulative calcite cap
    t['ghg']=t['ch4s']+t['ch4f']+t['n2o']; t['net']=t['ghg']-t['pda']-t['cc']; t['netpot']=t['ghg']-t['cat']
    t['pct1']=Y[0]['pct']; t['pct10']=Y[-1]['pct']; return t
if __name__=='__main__':
    for st,site,dose in [('v25bb','ref',10),('v25bb','ref',20),('v25bb','refq1',10),('v25bb','refq1',20)]+[('v25bb',s,20) for s in ('rf189','irr061','irr043','rf184','irr092','rf151')]+[(s,'ref',d) for s in ('v25bbw0','v25bbw04') for d in (10,20)]:
        t=totals(st,site,dose); print(f"{st:9s}{site:7s}{dose:3d}",' '.join(f"{k}={v:7.2f}" for k,v in t.items()))
