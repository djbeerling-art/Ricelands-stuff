# Fig 6 (v25b): reference site over ten years, 10 and 20 t basalt/ha/yr.
# (a, b) cumulative cation fate (treatment minus year-matched control); (c) annual PDA and calcite change;
# (d) plough-layer (0-0.20 m, thickness-weighted mean of cell pH) porewater pH at the end of flooding (last profile
# record before the pre-harvest drain, day 98 of 113, same time each year), control, 10 t and 20 t.
# Data: ../results/timeline_ref{10,20}.json (export_v25b.py), ../results/ph_plough_ref_summary.csv (ph_plough.py).
# Run from paddy/v25/figs: python3 fig6_ref10_v25b.py
import bigfont, json, csv, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
C = dict(pda='#1baf7a', cc='#9b59d0', ret='#c9c7c0', cat='#52514e')
fig, ax = plt.subplots(2, 2, figsize=(7.6, 6.6)); ax = ax.ravel()
for a, dose in zip(ax[:2], (10, 20)):
    R = json.load(open(f'../results/timeline_ref{dose}.json')); y = np.array([r['y'] for r in R])
    cat = np.cumsum([r['cat'] for r in R]); pda = np.cumsum([r['pda'] for r in R])
    cc = np.minimum(np.cumsum([r['cc'] for r in R]), np.maximum(cat - pda, 0))
    pda = np.maximum(pda, 0); cc = np.maximum(cc, 0); ret = cat - pda - cc
    a.stackplot(y, pda, cc, ret, colors=[C['pda'], C['cc'], C['ret']], edgecolor='white', lw=.6)
    a.plot(y, cat, c=C['cat'], lw=1.6)
    a.text(0.03, 0.97, f"line: cation release\n{cat[-1]:.0f} t CO$_2$ ha$^{{-1}}$ by year 10", transform=a.transAxes, ha='left', va='top', fontsize=8)
    for v, b, l in ((pda[-1], 0, 'PDA'), (cc[-1], pda[-1], 'calcite'), (ret[-1], pda[-1] + cc[-1], 'retained')):
        a.annotate(f'{l}\n{v:.1f}', (y[-1], b + v/2), xytext=(4, 0), textcoords='offset points', va='center', fontsize=7.5, linespacing=.9)
    a.set_xlim(1, 12.6); a.set_xticks(range(1, 11)); a.set_xlabel('Year'); a.set_ylabel('Cumulative (t CO$_2$ ha$^{-1}$)')
    a.set_title(f"{'ab'[dose//20]}  {dose} t ha$^{{-1}}$ yr$^{{-1}}$: cumulative cation fate", loc='left', fontsize=9)
    ax[2].plot(y, [r['pda'] for r in R], marker='o', ms=3, c=C['pda'], ls='-' if dose == 20 else '--', label=f'PDA, {dose} t')
    ax[2].plot(y, [r['cc'] for r in R], marker='s', ms=3, c=C['cc'], ls='-' if dose == 20 else '--', label=f'calcite change, {dose} t')
ax[2].axhline(0, c='#888', lw=.8); ax[2].set_xlabel('Year'); ax[2].set_ylabel('t CO$_2$ ha$^{-1}$ yr$^{-1}$')
ax[2].set_title('c  Annual inorganic C fluxes', loc='left', fontsize=9)
ax[2].legend(frameon=False, fontsize=7.5, ncol=2, handlelength=3, loc='upper left'); ax[2].set_ylim(top=ax[2].get_ylim()[1]*1.45)
P = list(csv.DictReader(open('../results/ph_plough_ref_summary.csv')))
for d, c, ls, mk, lab in (('0', '#52514e', ':', 'o', 'control'), ('10', '#d9822b', '--', 'o', '10 t ha$^{-1}$ yr$^{-1}$'), ('20', '#2a6fb0', '-', 'o', '20 t ha$^{-1}$ yr$^{-1}$')):
    r = [p for p in P if p['dose_t_ha'] == d]
    ax[3].plot([int(p['year']) for p in r], [float(p['ph_end_flood_0_20']) for p in r], c=c, ls=ls, marker=mk, ms=3, label=lab)
ax[3].set_xlabel('Year'); ax[3].set_ylabel('Porewater pH, 0–0.20 m')
ax[3].set_title('d  Plough-layer pH, end of flooding', loc='left', fontsize=9); ax[3].legend(frameon=False, fontsize=7.5, loc='best', handlelength=3)
for a in ax:
    a.grid(c='#ecebe7', lw=.6); a.set_axisbelow(True)
    if a is not ax[0] and a is not ax[1]: a.set_xlim(0.5, 10.5); a.set_xticks(range(1, 11))
fig.legend([Patch(color=C[k]) for k in ('pda', 'cc', 'ret')],
           ['Potentially durable alkalinity exported at the base (PDA = ALK − 2Fe(II) − 2NH$_4^+$)',
            'Soil carbonate (calcite; counted only up to cations not exported)',
            'Retained cations (exchange sites, porewater): potential only'], loc='lower center', ncol=1, frameon=False, fontsize=8)
fig.text(0.995, 0.005, 'SCEPTER-paddy v25b', ha='right', va='bottom', fontsize=6.5, color='#888')
fig.tight_layout(rect=(0, 0.1, 1, 1), h_pad=1.4, w_pad=1.2); fig.savefig('fig6_ref10_v25b.png')
