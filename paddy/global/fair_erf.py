# Effective radiative forcing change per perturbation from fair_ew.py's <prefix>_detail.nc (dERF = total ERF of the
# perturbed run minus background, same config; the CH4 run includes CH4's indirect ozone and stratospheric-water terms).
# Usage: python3 fair_erf.py <prefix> [<prefix> ...] -> <prefix>_dERF.csv (mW m-2: median, p05, p95) and <prefix>_dERF.png
import sys, numpy as np, pandas as pd, xarray as xr
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
COL = {'ch4': '#2a7f62', 'n2o': '#c08a1e', 'co2': '#3b5ba5', 'all': '#222222'}
LAB = {'ch4': 'avoided CH$_4$', 'n2o': 'avoided N$_2$O', 'co2': 'net CO$_2$ removal', 'all': 'combined'}
for p in sys.argv[1:]:
    F = xr.open_dataset(f'{p}_detail.nc').dERF*1e3
    out = {'year': F.timebounds.values.astype(int)}
    for c in COL:
        x = F.sel(scenario=c).values
        out[f'dERF_{c}'], out[f'dERF_{c}_p05'], out[f'dERF_{c}_p95'] = np.median(x, 1), np.percentile(x, 5, 1), np.percentile(x, 95, 1)
    d = pd.DataFrame(out); d.to_csv(f'{p}_dERF.csv', index=False, float_format='%.4g')
    d = d[d.year >= 2020]
    fig, ax = plt.subplots(figsize=(7, 4))
    for c in COL:
        ax.plot(d.year, d[f'dERF_{c}'], color=COL[c], lw=2.2 if c == 'all' else 1.6, label=LAB[c])
        ax.fill_between(d.year, d[f'dERF_{c}_p05'], d[f'dERF_{c}_p95'], color=COL[c], alpha=0.15, lw=0)
    ax.axhline(0, color='#888', lw=0.8); ax.set_ylabel('Effective radiative forcing change (mW m$^{-2}$)'); ax.set_xlabel('Year')
    ax.legend(frameon=False, fontsize=9); ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(); fig.savefig(f'{p}_dERF.png', dpi=160); plt.close(fig)
    print(p, 'done')
