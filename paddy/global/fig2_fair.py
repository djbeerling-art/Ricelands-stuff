"""Science Fig. 2: FaIR effective radiative forcing (top) and temperature (bottom)
by component, for deployment 2026-2050 then stop (left) or hold year-25 rates to 2100 (right).
Stacked panels share the time axis (no dual y-axis)."""
import sys, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/fair/v25fr_final'
out = sys.argv[2] if len(sys.argv) > 2 else '/mnt/project-files/science_figs/fig2_fair'
dom = sys.argv[3] if len(sys.argv) > 3 else '150'
C = {'ch4': ('#2a78d6', 'CH$_4$'), 'n2o': ('#eb6834', 'N$_2$O'), 'co2': ('#1baf7a', 'CO$_2$ (CDR)'), 'all': ('#0b0b0b', 'All')}
plt.rcParams.update({'font.size': 7, 'axes.linewidth': 0.6, 'font.family': 'DejaVu Sans'})
fig, ax = plt.subplots(2, 2, figsize=(7.2, 4.6), sharex=True, sharey='row')
for j, case in enumerate(['stop', 'hold']):
    e = pd.read_csv(f'{d}/fr_{dom}_{case}_dERF.csv'); t = pd.read_csv(f'{d}/fr_{dom}_{case}_dT.csv')
    e = e[(e.year >= 2020) & (e.year <= 2100)]; t = t[(t.year >= 2020) & (t.year <= 2100)]
    for k, (col, lab) in C.items():
        lw = 1.6 if k == 'all' else 1.1
        a = ax[0, j]; a.fill_between(e.year, e[f'dERF_{k}_p05'], e[f'dERF_{k}_p95'], color=col, alpha=0.15, lw=0)
        a.plot(e.year, e[f'dERF_{k}'], color=col, lw=lw, label=lab)
        a = ax[1, j]; a.fill_between(t.year, t[f'dT_{k}_p05_mK'], t[f'dT_{k}_p95_mK'], color=col, alpha=0.15, lw=0)
        a.plot(t.year, t[f'dT_{k}_mK'], color=col, lw=lw, label=lab)
    for i in range(2):
        a = ax[i, j]; a.axhline(0, color='#52514e', lw=0.5)
        a.axvspan(2026, 2050, color='#f0efec', zorder=0)
        a.grid(axis='y', color='#e5e4e0', lw=0.4); a.spines[['top', 'right']].set_visible(False)
    ax[0, j].set_title(['Deployment 2026-2050, then stop', 'Year-25 rates held to 2100 (assumed)'][j], fontsize=7.5)
ax[0, 0].set_ylabel('$\\Delta$ERF (mW m$^{-2}$)'); ax[1, 0].set_ylabel('$\\Delta$T (mK)')
for a in ax[1]: a.set_xlabel('Year'); a.set_xlim(2020, 2100)
ax[0, 0].legend(frameon=False, loc='lower left', ncol=2)
for a, l in zip(ax.flat, 'ABCD'): a.text(-0.12, 1.04, l, transform=a.transAxes, fontweight='bold', fontsize=9)
# caption text goes in the figure legend (see fig2_fair_caption.txt)
fig.tight_layout()
for ext in ('png', 'pdf'): fig.savefig(f'{out}_{dom}.{ext}', dpi=300)
print('saved', out)
