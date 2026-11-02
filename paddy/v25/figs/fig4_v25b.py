# Fig 4 (v25b): evaluation against observations. Model values: v25b runs (runE25b.sh, runW25b.sh/runW25c.sh; w 0.15, slag granular
# 1-7 mm, Gong/Wang 2024 P80 50 um); slag production/oxidation from flood_y5slag_* gas budgets; AWD ratio is v22 (marked); ferric Fe gain from v25b flood_y5slag_8w0.15 vs y5slag_0 (column Fe(III) change placed in 0-0.15 m, BD 1.1).
# a: CH4 responses, calibration-informed comparisons separated from predictions; oxidation partitioning flagged.
# b: model/observed for baselines, water-management response, cation release, soil carbonate and Fe(III); misfits flagged.
import sys as _s; import os as _o; _s.path.insert(0,_o.path.dirname(_o.path.abspath(__file__))); import bigfont
import json,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
from matplotlib.lines import Line2D as L
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
B,S,K,F='#2a78d6','#e8622a','0.45','#c0392b'
fig,(a,b)=plt.subplots(2,1,figsize=(7.4,10.5),gridspec_kw={'height_ratios':[1.15,1]})
# (label, obs, model, colour, calibration-informed, kind) kind: e emission, p production, o oxidation
P=[('Wang 2014 2 t/ha',-27,-31,S,1,'e'),('Wang 2014 4 t/ha',-43,-38,S,1,'e'),('Wang 2014 8 t/ha',-49,-47,S,1,'e'),
   ('Gong 36 t/ha',-18,-36,B,1,'e'),('Park 10 wt%',-25,-15,B,0,'e'),('Park 20 wt%',-37,-26,B,0,'e'),
   ('prod. 2 t/ha',-16,-22,S,0,'p'),('prod. 4 t/ha',-33,-26,S,0,'p'),('prod. 8 t/ha',-41,-29,S,0,'p'),
   ('ox. 2 t/ha',0,-19,F,0,'o'),('ox. 2, 4, 8 t/ha',0,-21,F,0,'o'),('ox. 8 t/ha',0,-19,F,0,'o')]
off={'Wang 2014 2 t/ha':(8,-14),'Wang 2014 4 t/ha':(8,-4),'Wang 2014 8 t/ha':(8,-10),'Gong 36 t/ha':(8,-4),'Park 10 wt%':(6,4),'Park 20 wt%':(-70,8),
     'prod. 2 t/ha':(6,4),'prod. 4 t/ha':(4,8),'prod. 8 t/ha':(-60,-12),'ox. 2 t/ha':(8,-3),'ox. 2, 4, 8 t/ha':(8,-4),'ox. 8 t/ha':(8,-3)}
a.plot([-60,5],[-60,5],'--',c='0.55',lw=1); a.axhline(0,c='0.8',lw=1); a.axvline(0,c='0.8',lw=1)
for l,o,m,c,cal,k in P:
    if k=='o': a.scatter(o,m,s=60,marker='X',color=c,zorder=3)
    else: a.scatter(o,m,s=60 if cal else 55,marker='s' if cal else 'o',facecolor='white' if k=='p' else (K if cal else c),edgecolor=K if cal else c,lw=1.6,zorder=3)
    None if l in ('ox. 2 t/ha','ox. 8 t/ha') else a.annotate(l,(o,m),xytext=off[l],textcoords='offset points',fontsize=8.5,color=F if k=='o' else '0.3')
a.annotate('',(-18,-4.3),(-18,-36),arrowprops=dict(arrowstyle='-',ls=':',color=K)); a.scatter(-18,-4.3,s=40,marker='x',c=K,zorder=3)
a.annotate('Gong, Si feedback off (w = 0)',(-18,-4.3),xytext=(6,0),textcoords='offset points',fontsize=8.5,color='0.3')
a.annotate('Wang 2014 oxidation: observed ~constant,\nmodelled to fall 19–21% (disagrees)',(-1,-31),xytext=(12,-52),textcoords='data',fontsize=8,color=F,ha='right')
a.legend(handles=[L([],[],marker='s',ls='',mfc=K,mec=K,label='calibration-informed: w fitted (Wang 2014 slag, Gong)'),
    L([],[],marker='o',ls='',mfc=B,mec=B,label='prediction, basalt (Park)'),L([],[],marker='o',ls='',mfc=S,mec=S,label='steel slag (Wang 2014)'),
    L([],[],marker='o',ls='',mfc='white',mec=S,label='CH$_4$ production (in-situ C$_2$H$_2$)'),L([],[],marker='X',ls='',c=F,label='CH$_4$ oxidation')],loc='upper left',frameon=False,fontsize=8.5)
a.set(xlim=(-60,14),ylim=(-60,5),xlabel='Observed change (%)',ylabel='Model change (%)')
a.set_title('a  CH$_4$ response to amendments (dashed: 1:1)',loc='left'); a.grid(c='0.93')
aw=[0.675,0.680,0.723,0.599]; T=0.55/0.71  # v22 fig47_v22.json awd_ratio; IPCC 2019; T=0.55/0.71   # IPCC 2019: multiple vs single drainage
# (group, label, model, obs, model upper or None, calibration-informed, misfit)
R=[('Baseline CH$_4$','Wang 2014 control (mg m$^{-2}$ h$^{-1}$)',1.93,3.11,None,0,0,'1.93 vs 3.11'),
   ('Baseline CH$_4$','Gong control (kg ha$^{-1}$)',46,52,None,1,0,'46 vs 52'),
   ('Water management','AWD/flooded CH$_4$, 4 archetypes, v22\n(vs IPCC 0.55/0.71 = 0.77)',min(aw),T,max(aw),0,0,f'{min(aw):.2f}–{max(aw):.2f} vs 0.77 (v22)'),
   ('Cation release','Uchibayashi Na, 100 t/ha',4.8,4.6,None,1,0,'4.8 vs 4.6'),
   ('Cation release','Uchibayashi Mg, 100 t/ha',11.0,6.5,None,1,1,'11.0 vs 6.5 (olivine)'),
   ('Soil carbonate','Wang 2024 inorganic C gain\n0–20 cm (t CO$_2$ ha$^{-1}$)',0.10,1.20,None,0,1,'0.10 vs 1.20'),
   ('Fe(III)','Wang 2014 ferric Fe gain, 8 t/ha',0.84,5.6,None,0,1,'0.84 vs 5.6 g kg$^{-1}$')]
y=np.arange(len(R))[::-1]
for yi,(g,l,m,o,m2,cal,bad,t) in zip(y,R):
    r=m/o; c=F if bad else (K if cal else B); mk='s' if cal else 'o'
    if m2: b.barh(yi,m2/o-r,left=r,height=0.42,color=c,alpha=0.3)
    b.plot([1,r],[yi,yi],c=c,lw=2); b.scatter(r,yi,s=55,color=c,marker=mk,zorder=3)
    if m2: b.scatter(m2/o,yi,s=55,color=c,marker=mk,zorder=3)
    b.annotate(t,(max(1,r,m2/o if m2 else 0),yi),xytext=(8,-3),textcoords='offset points',fontsize=8.5,color=c if bad else '0.3')
grp=[R[i][0] for i in range(len(R))]
for g in dict.fromkeys(grp):
    ii=[yy for yy,gg in zip(y,grp) if gg==g]; b.annotate(g,(0.052,max(ii)+0.38),fontsize=8.5,fontweight='bold',color='0.35')
b.axvline(1,ls='--',c='0.55',lw=1); b.set_xscale('log'); b.set_xlim(0.05,8); b.set_ylim(-0.6,len(R)-0.2)
b.set_xticks([0.1,0.25,0.5,1,2,4]); b.set_xticklabels(['0.1','0.25','0.5','1','2','4'])
b.set_yticks(y); b.set_yticklabels([r[1] for r in R],fontsize=8.5); b.set_xlabel('Model / observed (log scale)')
b.legend(handles=[L([],[],marker='o',ls='',c=B,label='prediction'),L([],[],marker='s',ls='',c=K,label='calibration-informed'),L([],[],marker='o',ls='',c=F,label='disagreement (development target)')],
    loc='upper center',bbox_to_anchor=(0.3,-0.13),ncol=2,frameon=False,fontsize=8.5)
b.set_title('b  Baselines, water, cations, carbonate and Fe(III)',loc='left'); b.grid(c='0.93',axis='x')
fig.text(0.99,0.005,'v25b',ha='right',fontsize=9,color='0.4'); fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'fig4_eval_v25b.png'),dpi=200)
