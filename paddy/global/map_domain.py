# Map of rice cells by distance to basic volcanics (full-resolution GLiM, cells_all_dist.csv dist_vb_full):
# 0-50, 50-150 (the 150 km run domain), 150-250 km, and rice beyond 250 km.
# Usage: python3 paddy/global/map_domain.py <natural earth dir> <out prefix>
import sys, numpy as np, pandas as pd
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
sys.path.insert(0, 'paddy/global'); from map_cells import *
ne, out = sys.argv[1:3]
c = pd.read_csv('data/global/cells_all.csv', usecols=['cell', 'lon', 'lat', 'iso3', 'area_irr', 'area_rf'])
c = c.merge(pd.read_csv('data/global/cells_all_dist.csv'), on='cell'); c['a'] = c.area_irr + c.area_rf
c = c[~c.iso3.isin(['COL', 'ECU'])]   # excluded from the run domain (extreme-rain Pacific coast)
band = np.digitize(c.dist_vb_full, [50, 150, 250], right=True)   # 0: <=50, 1: <=150, 2: <=250, 3: beyond
A = [c.a[band <= k].sum()/1e6 for k in range(3)]; tot = c.a.sum()/1e6
cols = ['#08306b', '#2f78b4', '#9cc6e2', '#c9c9c4']
labs = [f'≤ 50 km ({A[0]:.0f} Mha)', f'50–150 km (domain to 150 km: {A[1]:.0f} Mha)', f'150–250 km (to 250 km: {A[2]:.0f} Mha)', f'> 250 km ({tot - A[2]:.0f} Mha)']
g = raster(c.lon, c.lat, band)
for name, ext in EXTENTS.items():
    fig, ax = plt.subplots(figsize=(11, 5.2) if name == 'global' else (9, 6.4))
    base(ax, ne, ext)
    show(ax, g, cmap=ListedColormap(cols), norm=BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5], 4))
    ax.legend(handles=[Patch(color=k, label=l) for k, l in zip(cols, labs)], loc='lower left', fontsize=8, frameon=True,
              framealpha=0.9, edgecolor='none', title='Rice cells by distance to basalt', title_fontsize=8)
    ax.set_title(f'Ricelands within 250 km of basalt (full-resolution GLiM basic volcanics); {tot:.0f} Mha harvested rice shown', fontsize=9, loc='left')
    fig.tight_layout(); fig.savefig(f'{out}_{name}.png', dpi=200); plt.close(fig)
print(f'<=50 {A[0]:.1f}, <=150 {A[1]:.1f}, <=250 {A[2]:.1f} of {tot:.1f} Mha')
