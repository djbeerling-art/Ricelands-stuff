# Satellite detectability of riceland CH4 suppression (David, 2 Nov 2026: "how much riceland would need to be treated
# before satellites could detect CH4 emission suppression?"). A simple observing-system test for TROPOMI-class XCH4:
#   1. per-cell CH4 change (kg CH4/ha per season, negative = suppression) x rice area, spread over each cell's 113-d
#      season from its planting day -> monthly flux change on a GRID-degree grid (kg CH4 m-2 s-1);
#   2. for square windows of side L centred on each grid point, the steady-state column enhancement from a uniform
#      source of width L in wind U (box mass balance): dOmega = dF_mean * L / U, dXCH4 (ppb) = dOmega/OMEGA_AIR * Mair/MCH4;
#   3. noise: per month, random sounding error SIGR over N = days x (L^2 / pixel area) x clear-sky fraction soundings,
#      months combined by inverse variance, plus a systematic (regional bias) term SIGS that does not average down;
#   4. SNR = |signal| / noise at 100% adoption of the treated domain; minimum adoption for SNR >= 2 scales as 1/SNR.
# This is a screening estimate (no transport model, no wind direction, no background variability beyond SIGS), meant
# to map where and at what scale suppression could be seen; an inversion-based OSSE would refine it.
# Inputs: <cells.csv> (cell, lon, lat, area_irr, area_rf), <dch4.csv> (cell, regime, dch4_kg_ha [, plant]) or
#   --placeholder=<fraction cut> (uses EF x 113 d, IPCC 1.19 kg/ha/d continuous flooding, x0.55 rainfed/AWD), and
#   optionally --cal=<cells_all_cal.csv> for planting days, --clear=<csv: lon,lat,month,fclear> for clear-sky fractions.
# Usage: python3 detect_ch4.py <cells.csv> <dch4.csv|-> <out prefix> [--placeholder=0.25] [--cal=...] [--grid=0.25]
#        [--L=50,100,200,300,500] [--U=4] [--sigr=12] [--sigs=3] [--pix=38.5] [--fclear=0.3] [--snr=2]
#   -> <prefix>_grid.csv (lon, lat, area_ha, dF_season, SNR_L..., amin_L...), <prefix>_regions.csv, <prefix>.png
import sys, os
import numpy as np, pandas as pd
from scipy.ndimage import uniform_filter

def opt(k, d=None):
    for a in sys.argv[1:]:
        if a.startswith(f'--{k}='): return a.split('=', 1)[1]
    return d

OMEGA_AIR = 1.0e4            # dry-air column, kg m-2 (~1013 hPa / g)
PPB = 28.96/16.04*1e9/OMEGA_AIR   # kg CH4 m-2 -> ppb of column-average mole fraction
SEASON = 113
REGIONS = {   # lon0, lon1, lat0, lat1 (screening boxes for the summary table)
    'Mekong Delta': (104.5, 107.0, 8.5, 11.2), 'Red River Delta': (105.3, 107.0, 20.0, 21.5),
    'Central Plain, Thailand': (99.3, 101.3, 13.3, 16.5), 'Bangladesh': (88.0, 92.7, 20.7, 26.6),
    'West Bengal–Bihar': (84.0, 89.0, 21.5, 27.5), 'Java': (105.0, 114.6, -8.8, -5.8),
    'Central Luzon': (120.0, 121.5, 14.6, 16.3), 'Irrawaddy Delta': (94.3, 96.6, 15.5, 18.5),
    'Yangtze middle/lower': (111.0, 122.0, 27.5, 32.5), 'Punjab–Haryana': (73.8, 77.5, 28.5, 32.5),
}

def main(cells_f, dch4_f, prefix):
    g = float(opt('grid', 0.25)); Ls = [float(x) for x in opt('L', '50,100,200,300,500').split(',')]
    U, sigr, sigs, pix = (float(opt(k, d)) for k, d in (('U', 4), ('sigr', 12), ('sigs', 3), ('pix', 38.5)))
    snr0 = float(opt('snr', 2))
    c = pd.read_csv(cells_f, usecols=['cell', 'lon', 'lat', 'area_irr', 'area_rf'])
    u = pd.concat([c.assign(regime='irr', area=c.area_irr), c.assign(regime='rf', area=c.area_rf)])
    u = u[u.area > 0][['cell', 'lon', 'lat', 'regime', 'area']]
    if opt('placeholder'):
        cut = float(opt('placeholder'))
        u['dch4_kg_ha'] = -cut*1.19*SEASON*np.where(u.regime == 'rf', 0.55, 1.0)
        src = f'placeholder: {cut:.0%} cut of IPCC EF'
    else:
        d = pd.read_csv(dch4_f); u = u.merge(d, on=['cell', 'regime'], how='inner'); src = dch4_f
    if 'plant' not in u:
        if opt('cal'):
            cal = pd.read_csv(opt('cal'), usecols=['cell', 'plant_irr', 'plant_rf'])
            u = u.merge(cal, on='cell', how='left')
            u['plant'] = np.where(u.regime == 'irr', u.plant_irr, u.plant_rf)
        else:
            u['plant'] = 150.
    u['plant'] = u.plant.fillna(150.)
    # monthly fraction of each unit's season (113 d from planting), by day of year
    doy = np.arange(365); mon = np.minimum((doy/30.42).astype(int), 11)
    on = ((doy[None, :] - u.plant.values[:, None]) % 365) < SEASON            # (units, 365)
    mfrac = np.stack([on[:, mon == m].mean(axis=1) for m in range(12)], 1)  # fraction of month in season
    # grid
    lon0, lat0 = -180., -60.
    ix = ((u.lon.values - lon0)/g).astype(int); iy = ((u.lat.values - lat0)/g).astype(int)
    nx, ny = int(360/g), int(140/g)
    lat_c = lat0 + (np.arange(ny) + 0.5)*g
    garea = (g*111.32e3)**2*np.cos(np.deg2rad(lat_c))[:, None]*np.ones((1, nx))   # m2
    rate = u.dch4_kg_ha.values*u.area.values/(SEASON*86400.)                         # kg/s while in season
    F = np.zeros((12, ny, nx)); A = np.zeros((ny, nx))
    for m in range(12):
        np.add.at(F[m], (iy, ix), rate*mfrac[:, m])
    np.add.at(A, (iy, ix), u.area.values)
    F /= garea[None]
    fclr = float(opt('fclear', 0.3)); C = np.full((12, ny, nx), fclr)
    if opt('clear'):
        cl = pd.read_csv(opt('clear'))
        C[cl.month.values - 1, ((cl.lat.values - lat0)/g).astype(int), ((cl.lon.values - lon0)/g).astype(int)] = cl.fclear.values
    out = pd.DataFrame()
    jj, ii = np.nonzero(A > 0)
    out['lon'] = lon0 + (ii + 0.5)*g; out['lat'] = lat_c[jj]; out['area_ha'] = A[jj, ii]
    out['dch4_t_season'] = (F.sum(0)*garea*30.42*86400/1e3)[jj, ii]
    for L in Ls:
        w = max(int(round(L/(g*111.32))), 1)                                  # window in grid cells (lat-scale)
        Fm = np.stack([uniform_filter(F[m], size=w, mode='constant') for m in range(12)])
        S = Fm*L*1e3/U*PPB                                                    # ppb per month
        nsound = 30.42*(L**2/pix)*np.stack([uniform_filter(C[m], size=w, mode='constant') for m in range(12)])
        var = sigr**2/np.maximum(nsound, 1e-9)
        act = np.abs(S) > 1e-6                                                # months with a signal
        wgt = np.where(act, 1/var, 0.)
        Sc = np.where(wgt.sum(0) > 0, (wgt*S).sum(0)/np.maximum(wgt.sum(0), 1e-30), 0.)
        sig = np.sqrt(np.where(wgt.sum(0) > 0, 1/np.maximum(wgt.sum(0), 1e-30), np.inf) + sigs**2)
        snr = np.abs(Sc)/sig
        out[f'dX_{L:.0f}km_ppb'] = Sc[jj, ii]; out[f'SNR_{L:.0f}km'] = snr[jj, ii]
        out[f'amin_{L:.0f}km'] = np.minimum(snr0/np.maximum(snr[jj, ii], 1e-9), 99)
        out[f'treated_Mha_{L:.0f}km'] = (uniform_filter(A, size=w, mode='constant')*w*w)[jj, ii]/1e6
    out.to_csv(f'{prefix}_grid.csv', index=False, float_format='%.4g')
    rows = []
    for name, (a0, a1, b0, b1) in REGIONS.items():
        r = out[(out.lon.between(a0, a1)) & (out.lat.between(b0, b1))]
        if r.empty: rows.append(dict(region=name, domain_Mha=0)); continue
        best = {f'best_SNR_{L:.0f}km': r[f'SNR_{L:.0f}km'].max() for L in Ls}
        amin = {f'min_adoption_{L:.0f}km': r[f'amin_{L:.0f}km'].min() for L in Ls}
        rows.append(dict(region=name, domain_Mha=r.area_ha.sum()/1e6, dX_200km_ppb=r.get('dX_200km_ppb', pd.Series([np.nan])).min(), **best, **amin))
    reg = pd.DataFrame(rows); reg.to_csv(f'{prefix}_regions.csv', index=False, float_format='%.3g')
    print(f'source: {src}; grid {g} deg, U {U} m/s, sigma random {sigr} ppb, systematic {sigs} ppb, clear-sky {opt("clear") or fclr}')
    print(reg.round(2).to_string(index=False))
    plot(out, Ls, prefix, snr0, src)

def plot(out, Ls, prefix, snr0, src):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    det = np.full(len(out), np.nan)
    for L in sorted(Ls, reverse=True):
        det = np.where(out[f'SNR_{L:.0f}km'] >= snr0, L, det)
    a = out[(out.lon > 60) & (out.lon < 150) & (out.lat > -12) & (out.lat < 45)]
    d = det[a.index]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.scatter(a.lon, a.lat, s=2, c='#dddddd', lw=0)
    cmap = plt.get_cmap('viridis_r', len(Ls))
    sc = ax.scatter(a.lon[~np.isnan(d)], a.lat[~np.isnan(d)], s=3, c=d[~np.isnan(d)], cmap=cmap,
                    vmin=min(Ls), vmax=max(Ls), lw=0)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8); cb.set_label('Smallest detectable window (km), 100% adoption')
    ax.set_title(f'TROPOMI-class detectability of CH4 suppression (SNR ≥ {snr0:g}); grey = not detectable ≤ {max(Ls):.0f} km\n{src}', fontsize=9)
    ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude'); ax.set_aspect('equal')
    fig.tight_layout(); fig.savefig(f'{prefix}.png', dpi=160)

if __name__ == '__main__':
    main(*[a for a in sys.argv[1:] if not a.startswith('--')])
