# Maps of the cumulative 2026-2050 (25-yr) changes at 20 t/ha/yr basalt, per hectare of harvested rice, from the
# per-archetype collect_chains output (arch_cum.csv: t CO2e/ha cumulative; negative ch4/n2o = cut, positive alk/cc = removal)
# and the cell -> archetype map (cell_map.csv: cell, regime, arch, area). Each cell shows the area-weighted mean of its
# irrigated and rainfed archetypes. Panels: avoided CH4 (season + fallow), avoided N2O, CDR as alkalinity (PDA), CDR as
# calcite, all as t CO2e/ha over 25 yr (GWP100: CH4 27, N2O 273), plotted as benefit (positive = less GHG in the air).
# Usage: python3 paddy/global/map_deltas.py <arch_cum.csv> <cell_map.csv> <natural earth dir> <out prefix> [--dose=20]
import sys, numpy as np, pandas as pd
sys.path.insert(0, 'paddy/global'); from map_cells import *
pos = [a for a in sys.argv[1:] if not a.startswith('--')]; opt = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--'))
af, cmf, ne, out = pos
a = pd.read_csv(af)
if 'dose' in a: a = a[a.dose == int(opt.get('dose', 20))]
a['ch4'] = a.ch4s + a.ch4f
cm = pd.read_csv(cmf); n_all = cm.arch.nunique()
cells = pd.read_csv('data/global/cells_all.csv', usecols=['cell', 'lon', 'lat'])
m = cm.merge(a[['arch', 'ch4', 'n2o', 'alk', 'cc']], on='arch', how='left')
done = m.dropna(subset=['ch4'])
V = {'ch4': ('Avoided CH$_4$', -1), 'n2o': ('Avoided N$_2$O', -1), 'alk': ('CDR as alkalinity', 1), 'cc': ('CDR as calcite', 1)}
w = done.assign(**{k: done[k]*s*done.area for k, (_, s) in V.items()}).groupby('cell')[list(V) + ['area']].sum()
for k in V: w[k] /= w.area
w = w.reset_index().merge(cells, on='cell')
pend = cm[~cm.cell.isin(w.cell)].drop_duplicates('cell').merge(cells, on='cell')
tot = {k: (done[k]*V[k][1]*done.area).sum()/1e6 for k in V}   # Mt CO2e (area in ha, values t/ha)
note = f'{a.arch.nunique()} of {n_all} archetypes, {done.area.sum()/1e6:.1f} of {cm.area.sum()/1e6:.1f} Mha' + ('' if pend.empty else '; grey = not yet collected')
for name, ext in EXTENTS.items():
    fig, axs = plt.subplots(2, 2, figsize=(13, 6.6) if name == 'global' else (12, 9.2))
    for ax, (k, (lab, _)) in zip(axs.flat, V.items()):
        base(ax, ne, ext)
        if not pend.empty: show(ax, raster(pend.lon, pend.lat, 1.), cmap=matplotlib.colors.ListedColormap(['#c9c9c4']))
        vmax = float(np.nanpercentile(w[k], 98)); vmin = min(0., float(np.nanpercentile(w[k], 2)))
        cmap = 'BrBG' if vmin < -0.05*vmax else 'Blues'
        if cmap == 'BrBG': vmin = -vmax
        im = show(ax, raster(w.lon, w.lat, w[k].values), cmap=cmap, vmin=vmin, vmax=vmax)
        cb = fig.colorbar(im, ax=ax, shrink=0.75, pad=0.01, extend='both' if cmap == 'BrBG' else 'max')
        cb.set_label('t CO$_2$e ha$^{-1}$ (2026–2050)', fontsize=8); cb.ax.tick_params(labelsize=7)
        ax.set_title(f'{lab}: {tot[k]:,.0f} Mt CO$_2$e', fontsize=10, loc='left')
    fig.suptitle(f'Cumulative 25-yr change, 20 t ha$^{{-1}}$ yr$^{{-1}}$ basalt vs untreated (positive = climate benefit); {note}', fontsize=9, x=0.01, ha='left')
    fig.tight_layout(); fig.savefig(f'{out}_{name}.png', dpi=200); plt.close(fig)
print(note); print({k: round(v) for k, v in tot.items()})
for k in V: print(k, 'cells < 0:', int((w[k] < 0).sum()), 'p2/p50/p98', np.nanpercentile(w[k], [2, 50, 98]).round(2))
