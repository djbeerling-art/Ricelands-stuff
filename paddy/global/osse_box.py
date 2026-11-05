# Global observing-system simulation experiment (OSSE): could the riceland CH4 cut be detected and attributed in the
# global-mean atmospheric record? (David, 4 Nov 2026: box-model OSSE + regional OSSE.)
# One-box tropospheric CH4, dB/dt = E - B/tau with B = 2.75 Tg/ppb x X (annual steps). The riceland signal dX_rice(t) is
# the box response to the modelled dCH4 series (Mt CH4/yr, years 1..N from Y0, last rate held to --end).
# Noise: natural interannual variability as an AR(1) emission/sink anomaly (lag-1 --rho) sized so the growth-rate SD is
# --sgr ppb/yr (NOAA global growth rate 2000-2023: SD ~3-5 ppb/yr raw, less after removing ENSO/fire/OH-explained
# variance), passed through the same box, plus white annual-mean observation error --sobs ppb.
# Fingerprint inversion (generalised least squares, as in detection-attribution): X_obs = baseline + alpha*dX_rice + noise,
# with the counterfactual baseline either known (--poly=-1), an unknown offset (0), linear trend (1) or quadratic (2).
# For data up to year Y the posterior SD of alpha (sigma_a) follows analytically from the noise covariance, so the
# expected detection statistic is z = f/sigma_a for deployment fraction f. Reported: the first year z >= --z (2), i.e.
# 50% chance of a 2-sigma detection, and z >= z + 1.28 (90% chance).
# Usage: python3 osse_box.py <yearly.csv: year, dch4_mt> <out prefix> [--y0=2026] [--end=2100] [--tau=9.1] [--rho=0.5]
#        [--sobs=1] [--z=2] [--sgr=2,3,4] [--poly=-1,0,1,2] [--frac=0.5,1,2] [--scale=1]
#   --signal=<FaIR *_dT.csv>: use FaIR's dCH4_ch4_ppb as the signal (noise model unchanged)
#   --scale multiplies the dCH4 series (e.g. full-domain / modelled area); -> <prefix>_osse.csv, <prefix>_osse.png
import sys, numpy as np, pandas as pd
def opt(k, d):
    for a in sys.argv[1:]:
        if a.startswith(f'--{k}='): return a.split('=', 1)[1]
    return d
TGPPB = 2.75

def box(dE, tau):
    """ppb response of a one-box model to an annual emission series (Tg/yr)."""
    a, x, out = np.exp(-1/tau), 0., []
    for e in dE:
        x = x*a + e/TGPPB*tau*(1 - a); out.append(x)
    return np.array(out)

def noise_cov(m, sE, rho, tau, sobs):
    """Covariance (ppb^2) of the box response to AR(1) emission noise plus white observation error, first m years."""
    Ce = sE**2/(1 - rho**2)*rho**np.abs(np.subtract.outer(np.arange(m), np.arange(m)))
    a = np.exp(-1/tau); g = tau*(1 - a)/TGPPB
    i, j = np.indices((m, m)); G = np.where(i >= j, g*a**(i - j).clip(0), 0.)
    return G @ Ce @ G.T + sobs**2*np.eye(m)

def sigma_alpha(tm, t, poly, sE, rho, tau, sobs):
    out = np.full(len(tm), np.nan)
    for j in range(len(tm)):
        X = np.column_stack([t[:j+1]**p for p in range(poly + 1)] + [tm[:j+1]])
        if j + 1 <= X.shape[1] + 1: continue
        C = noise_cov(j + 1, sE, rho, tau, sobs)
        out[j] = np.sqrt(np.linalg.inv(X.T @ np.linalg.solve(C, X))[-1, -1])
    return out

def main(yf, prefix):
    y0, yend, tau, rho = int(opt('y0', 2026)), int(opt('end', 2100)), float(opt('tau', 9.1)), float(opt('rho', 0.5))
    sobs, z = float(opt('sobs', 1)), float(opt('z', 2))
    sgrs = [float(x) for x in opt('sgr', '2,3,4').split(',')]; polys = [int(x) for x in opt('poly', '-1,0,1,2').split(',')]
    fracs = [float(x) for x in opt('frac', '0.5,1,2').split(',')]; scale = float(opt('scale', 1))
    s = pd.read_csv(yf); years = np.arange(y0, yend + 1); N = len(years); t = (years - y0)/10.
    dE = scale*np.interp(np.arange(1, N + 1), s.year, s.dch4_mt, right=s.dch4_mt.iloc[-1])
    tm = box(dE, tau)
    if opt('signal', None):   # FaIR dCH4 concentration series (year, dCH4_ch4_ppb), replaces the one-box signal
        fs = pd.read_csv(opt('signal', None)).set_index('year')['dCH4_ch4_ppb']
        tm = scale*fs.reindex(years).values
    lab = {-1: 'known counterfactual', 0: 'unknown offset', 1: 'unknown linear trend', 2: 'unknown quadratic trend'}
    rows, curves = [], {}
    for sgr in sgrs:
        sE = sgr*TGPPB*np.sqrt(1 - rho**2)    # growth-rate anomaly ~ emission anomaly / 2.75
        for poly in polys:
            sa = sigma_alpha(tm, t, poly, sE, rho, tau, sobs); curves[(sgr, poly)] = 1/sa
            for f in fracs:
                zz = f/sa
                first = lambda thr: (int(years[np.nanargmax(zz >= thr)]) if np.nanmax(zz) >= thr else None)
                rows.append(dict(sgr_ppb_yr=sgr, baseline=lab[poly], fraction=f, dX_2050_ppb=round(f*tm[years == 2050][0], 1),
                                 z_2040=round(zz[years == 2040][0], 2), z_2050=round(zz[years == 2050][0], 2), z_2075=round(zz[years == 2075][0], 2),
                                 year_50pct=first(z), year_90pct=first(z + 1.28)))
    out = pd.DataFrame(rows); out.to_csv(f'{prefix}_osse.csv', index=False)
    print(f'tau {tau} yr, AR1 rho {rho}, obs error {sobs} ppb, scale {scale}; dX(2050) full deployment {tm[years == 2050][0]:.1f} ppb')
    print(out.to_string(index=False))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, len(sgrs), figsize=(4*len(sgrs), 3.6), sharey=True)
    for ax, sgr in zip(np.atleast_1d(axs), sgrs):
        for poly in polys: ax.plot(years, curves[(sgr, poly)], lw=1.6, label=lab[poly])
        ax.axhline(z, color='#888', lw=0.8, ls='--'); ax.set_title(f'growth-rate noise {sgr:g} ppb/yr', fontsize=9)
        ax.set_xlabel('Last year of record'); ax.spines[['top', 'right']].set_visible(False)
    np.atleast_1d(axs)[0].set_ylabel('Expected detection statistic z (full deployment)'); np.atleast_1d(axs)[0].legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(f'{prefix}_osse.png', dpi=160)

if __name__ == '__main__':
    main(*[a for a in sys.argv[1:] if not a.startswith('--')])
