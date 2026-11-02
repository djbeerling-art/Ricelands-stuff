# Fig 6 (v25b): reference site over ten years, 10 and 20 t basalt/ha/yr.
# (a, b) cumulative cation fate (treatment minus year-matched control); (c) annual PDA and calcite change;
# (e) year-10 pH depth profiles (end of flooding, 0-0.5 m; plough layer and pan shaded);
# (d) plough-layer (0-0.20 m, thickness-weighted mean of cell pH) porewater pH at the end of flooding (last profile
# record before the pre-harvest drain, day 98 of 113, same time each year), control, 10 t and 20 t.
# Data: ../results/timeline_ref{10,20}.json (export_v25b.py), ../results/ph_plough_ref_summary.csv, _year0.csv (year 0 = last settle season), _profile_y10.csv (ph_plough.py).
# Run from paddy/v25/figs: python3 fig6_ref10_v25b.py
import bigfont, json, csv, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
C = dict(pda='#1baf7a', cc='#9b59d0', ret='#c9c7c0', cat='#52514e')
fig, ax = plt.subplots(3, 2, figsize=(7.6, 9.6)); ax = ax.ravel()
for a, dose in zip(ax[:2], (10, 20)):
    R = json.load(open(f'../results/timeline_ref{dose}.json')); y = np.array([r['y'] for r in R])
    cat = np.cumsum([r['cat'] for r in R]); pda = np.cumsum([r['pda'] for r in R])
    # Eq. 17 equivalent basis: calcite C capped at half the unexported charge, drawn as charge (2 eq per mol)
    cc = np.minimum(np.cumsum([r['cc'] for r in R]), 0.5*np.maximum(cat - pda, 0))
    pda = np.maximum(pda, 0); cc = 2*np.maximum(cc, 0); ret = cat - pda - cc
    a.stackplot(y, pda, cc, ret, colors=[C['pda'], C['cc'], C['ret']], edgecolor='white', lw=.6)
    a.plot(y, cat, c=C['cat'], lw=1.6)
    a.text(0.03, 0.97, f"line: cation release\n{cat[-1]:.0f} t CO$_2$ ha$^{{-1}}$ by year 10", transform=a.transAxes, ha='left', va='top', fontsize=8)
    for v, b, l in ((pda[-1], 0, 'PDA'), (cc[-1], pda[-1], 'calcite (charge)'), (ret[-1], pda[-1] + cc[-1], 'retained')):
        a.annotate(f'{l}\n{v:.1f}', (y[-1], b + v/2), xytext=(4, 0), textcoords='offset points', va='center', fontsize=7.5, linespacing=.9)
    a.set_xlim(1, 12.6); a.set_xticks(range(1, 11)); a.set_xlabel('Year'); a.set_ylabel('Cumulative (t CO$_2$ ha$^{-1}$)')
    a.set_title(f"{'ab'[dose//20]}  {dose} t ha$^{{-1}}$ yr$^{{-1}}$: cumulative cation fate", loc='left', fontsize=9)
    ax[2].plot(y, [r['pda'] for r in R], marker='o', ms=3, c=C['pda'], ls='-' if dose == 20 else '--', label=f'PDA, {dose} t')
    ax[2].plot(y, [r['cc'] for r in R], marker='s', ms=3, c=C['cc'], ls='-' if dose == 20 else '--', label=f'calcite change, {dose} t')
ax[2].axhline(0, c='#888', lw=.8); ax[2].set_xlabel('Year'); ax[2].set_ylabel('t CO$_2$ ha$^{-1}$ yr$^{-1}$')
ax[2].set_title('c  Annual inorganic C fluxes', loc='left', fontsize=9)
ax[2].legend(frameon=False, fontsize=7.5, ncol=2, handlelength=3, loc='upper left'); ax[2].set_ylim(top=ax[2].get_ylim()[1]*1.45)
P = list(csv.DictReader(open('../results/ph_plough_ref_summary.csv')))
Y0 = list(csv.DictReader(open('../results/ph_plough_ref_year0.csv')))
ph0 = float(Y0[0]['ph_end_flood_0_20']) if Y0 else None
ph0b = float(Y0[0]['ph_end_flood_2_20']) if Y0 and 'ph_end_flood_2_20' in Y0[0] else None
TR = (('0', '#52514e', ':', 'control'), ('10', '#d9822b', '--', '10 t ha$^{-1}$ yr$^{-1}$'), ('20', '#2a6fb0', '-', '20 t ha$^{-1}$ yr$^{-1}$'))
for d, c, ls, lab in TR:
    r = [p for p in P if p['dose_t_ha'] == d]
    yy = [0]*(ph0 is not None) + [int(p['year']) for p in r]; pp = [ph0]*(ph0 is not None) + [float(p['ph_end_flood_0_20']) for p in r]
    ax[3].plot(yy, pp, c=c, ls=ls, marker='o', ms=3, label=lab)
    if 'ph_end_flood_2_20' in r[0]:
        ax[3].plot([0]*(ph0b is not None) + [int(p['year']) for p in r], [ph0b]*(ph0b is not None) + [float(p['ph_end_flood_2_20']) for p in r],
                   c=c, ls=ls, lw=0.8, alpha=0.55, marker='o', ms=2, mfc='white')
ax[3].plot([], [], c='#888', lw=0.8, alpha=0.7, marker='o', ms=2, mfc='white', label='0.02–0.20 m (excl. top cell)')
ax[3].set_xlabel('Year'); ax[3].set_ylabel('Porewater pH, 0–0.20 m')
ax[3].set_title('d  Plough-layer pH, end of flooding', loc='left', fontsize=9)
H3, L3 = ax[3].get_legend_handles_labels()
Z = list(csv.DictReader(open('../results/ph_plough_ref_profile_y10.csv')))
e = ax[4]
e.axhspan(0, 0.20, color='#f2efe6', zorder=0); e.axhspan(0.20, 0.24, color='#d9d4c5', zorder=0)
for d, c, ls, lab in TR:
    r = [z for z in Z if z['dose_t_ha'] == d]
    zz = np.array([float(z['z_m']) for z in r]); pp = np.array([float(z['ph']) for z in r]); XM = 7.9
    e.plot(np.minimum(pp, XM), zz, c=c, ls=ls, marker='o', ms=2.5, label=lab)
    if pp[0] > XM:
        e.plot([XM], [zz[0]], marker='>', ms=5, c=c, clip_on=False)
        e.text(XM - 0.05, 0.33 if d == '10' else 0.37, f'top cell (0–0.02 m) pH {pp[0]:.1f}', ha='right', va='center', fontsize=7, color=c)
e.set_xlim(4.9, 7.9); e.set_ylim(0.5, 0); e.set_ylabel('Depth (m)'); e.set_xlabel('Porewater pH')
e.text(0.02, 0.10, 'plough layer', transform=e.get_yaxis_transform(), ha='left', va='center', fontsize=7.5, color='#6b6658')
e.text(0.02, 0.22, 'plough pan', transform=e.get_yaxis_transform(), ha='left', va='center', fontsize=7.5, color='#6b6658')
e.set_title('e  pH profiles at year 10, end of flooding', loc='left', fontsize=9)
ax[3].set_xlim(-0.5, 10.5); ax[3].set_xticks(range(0, 11)); ax[2].set_xlim(0.5, 10.5); ax[2].set_xticks(range(1, 11))
for a in ax[:5]:
    a.grid(c='#ecebe7', lw=.6); a.set_axisbelow(True)
ax[5].axis('off'); ax[5].legend(H3, ['control (d, e)', '10 t ha$^{-1}$ yr$^{-1}$ (d, e)', '20 t ha$^{-1}$ yr$^{-1}$ (d, e)', 'd: thin lines, 0.02–0.20 m\n(excluding the top cell)'], loc='upper left', bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=7.5, handlelength=3)
fig.legend([Patch(color=C[k]) for k in ('pda', 'cc', 'ret')],
           ['Potentially durable alkalinity (PDA) exported\nat the base and by lateral discharge\n(PDA = ALK − 2Fe(II) − 2NH$_4^+$)',
            'Soil carbonate (calcite, 2 eq per mol;\ncalcite C capped at half the\nunexported charge)',
            'Retained cations (exchange sites,\nporewater): potential only'], loc='center', bbox_to_anchor=(0.76, 0.10), ncol=1, frameon=False, fontsize=7.5)
fig.text(0.995, 0.005, 'SCEPTER-paddy v25b', ha='right', va='bottom', fontsize=6.5, color='#888')
fig.tight_layout(h_pad=1.4, w_pad=1.2); fig.savefig('fig6_ref10_v25b.png')
