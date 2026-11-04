# Regional observing-system simulation experiment (OSSE) for the riceland CH4 cut: could a TROPOMI-class analytical
# inversion detect it delta by delta? (David, 4 Nov 2026: "box-model + regional OSSE"; the global one is osse_box.py.)
# An analytical Bayesian inversion (as in the Integrated Methane Inversion, Varon et al. 2022), without a chemical
# transport model:
#   state  = rice CH4 emission and all other CH4 emission (wetlands, livestock, waste...) on each GRID-degree cell of the
#            delta box plus a MARGIN; prior errors are --sa_rice and --sa_other (fractional, uncorrelated). Rice and other
#            sources in the same cell can only be told apart through their priors, which is the real confounding.
#   obs    = daily super-observations on the same grid during the rice season (--days), each with
#            n = clear-sky fraction x cell area / pixel area soundings; error^2 = sigr^2/n + smod^2 (transport/model).
#            A free background offset each day is projected out (equivalent to solving for it with a flat prior).
#   Jacobian = Gaussian-plume column enhancement for each source cell under that day's wind, drawn at random
#            (direction uniform, speed lognormal with median --U); sigma_y = sqrt((W/2.5)^2 + (--spread * x)^2).
#   posterior error covariance S_hat = (sum_days K'^T So^-1 K' + Sa^-1)^-1, for one season; N seasons divide the
#   information-matrix term (not the prior) by 1/N.
# Detection tests, per region, for full adoption (before/after) and half-domain adoption (paired west vs east blocks):
#   before/after: signal = summed rice-emission change in the domain; error = sqrt(2) x posterior SD of the rice total
#                 (two independent inversions, before and after);
#   paired:       signal = fractional change in treated rice minus untreated (0 for untreated), error = posterior SD of
#                 (E_T/E_T0 - E_U/E_U0) from one inversion.
# z = signal/error; reported for the cut fractions in years 1, 5, 10 and 25, and the seasons of data needed for z >= 2.
# Rice control emission per cell: --ef_irr / --ef_rf kg CH4/ha/season (default: batch-1 control means 120/77) x area,
# or a per-cell table --cells_dch4=<csv: cell, ctrl_kg, d1, d5, d10, d25> (kg CH4/cell/season) when the merge is done.
# Cut fractions default to batch-1 global dCH4/control (13.4, 32.2, 44.3, 60.3% in yr 1, 5, 10, 25).
# Usage: python3 osse_regional.py <cells150.csv> <out prefix> [--grid=0.25] [--margin=1] [--U=4] [--sigr=12] [--smod=8]
#        [--pix=38.5] [--fclear=0.1] [--days=113] [--sa_rice=0.5] [--sa_other=0.5] [--other=1] [--spread=0.25]
#        [--regions=Mekong Delta;Bangladesh;...] [--seed=1] [--cells_dch4=...]
#        [--era5=era5_delta_monthly.csv --cal=cells_all_cal.csv [--qa=0.5]]: daily winds drawn from the ERA5 06 UTC
#        monthly climatology (2019-23) of the rice-season months (area-weighted planting day); soundings per day =
#        qa x (1 - cloud cover) x cell area / pixel area (qa = fraction of cloud-free scenes passing retrieval QA)
#   -> <prefix>_regional.csv, <prefix>_regional.png
import sys, numpy as np, pandas as pd

def opt(k, d=None):
    for a in sys.argv[1:]:
        if a.startswith(f'--{k}='): return a.split('=', 1)[1]
    return d

PPB = 28.96/16.04*1e9/1.0e4      # kg CH4 m-2 -> ppb column-average dry mole fraction (dry-air column 1e4 kg m-2)
REGIONS = {   # lon0, lon1, lat0, lat1 (same boxes as detect_ch4.py)
    'Mekong Delta': (104.5, 107.0, 8.5, 11.2), 'Red River Delta': (105.3, 107.0, 20.0, 21.5),
    'Central Plain, Thailand': (99.3, 101.3, 13.3, 16.5), 'Bangladesh': (88.0, 92.7, 20.7, 26.6),
    'West Bengal–Bihar': (84.0, 89.0, 21.5, 27.5), 'Java': (105.0, 114.6, -8.8, -5.8),
    'Central Luzon': (120.0, 121.5, 14.6, 16.3), 'Irrawaddy Delta': (94.3, 96.6, 15.5, 18.5),
    'Yangtze middle/lower': (111.0, 122.0, 27.5, 32.5), 'Punjab–Haryana': (73.8, 77.5, 28.5, 32.5),
}
CUTS = {1: 0.134, 5: 0.322, 10: 0.443, 25: 0.603}
ADOPT = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
YCUT, AD_ROWS, AREA, PLANT, MET = [], [], {}, {}, {}
norm = lambda r: ''.join(ch for ch in r.lower() if ch.isalnum())

def region_grid(c, box, g, margin):
    a0, a1, b0, b1 = box
    lo = np.arange(a0 - margin, a1 + margin, g) + g/2; la = np.arange(b0 - margin, b1 + margin, g) + g/2
    LO, LA = np.meshgrid(lo, la); LO, LA = LO.ravel(), LA.ravel()
    inbox = (LO > a0) & (LO < a1) & (LA > b0) & (LA < b1)
    r = c[c.lon.between(a0 - margin, a1 + margin) & c.lat.between(b0 - margin, b1 + margin)]
    ix = ((r.lon.values - (a0 - margin))/g).astype(int); iy = ((r.lat.values - (b0 - margin))/g).astype(int)
    ok = (ix < len(lo)) & (iy < len(la))
    E = np.zeros(len(LO)); np.add.at(E, iy[ok]*len(lo) + ix[ok], r.ctrl_kg.values[ok])
    return LO, LA, inbox, E

def jacobian(LO, LA, g, U, theta, spread):
    """ppb at each receptor per (kg/s) from each source cell, for wind speed U (m/s) blowing towards angle theta."""
    km = 111.32e3; x0 = LO*np.cos(np.deg2rad(LA.mean()))*km; y0 = LA*km
    dx = x0[:, None] - x0[None, :]; dy = y0[:, None] - y0[None, :]          # receptor minus source
    ux, uy = np.cos(theta), np.sin(theta)
    xa = dx*ux + dy*uy; ya = -dx*uy + dy*ux                                  # along / across wind
    W = g*km*np.cos(np.deg2rad(LA.mean()))
    sy = np.sqrt((W/2.5)**2 + (spread*np.clip(xa, 0, None))**2)
    K = np.where(xa > -W/2, np.exp(-ya**2/(2*sy**2))/(np.sqrt(2*np.pi)*sy*U), 0.)
    return K*PPB                                                             # ppb per kg/s

def run_region(name, c, a):
    g, margin = a['grid'], a['margin']
    LO, LA, inbox, E = region_grid(c, REGIONS[name], g, margin)
    a0, a1, b0, b1 = REGIONS[name]
    rb = c[c.lon.between(a0, a1) & c.lat.between(b0, b1)]
    if len(rb) and 'plant' in rb: PLANT[name] = float(np.average(rb.plant.fillna(150), weights=rb.area_irr + rb.area_rf + 1e-9))
    AREA[name] = (c.area_irr + c.area_rf)[c.lon.between(a0, a1) & c.lat.between(b0, b1)].sum()/1e6
    if E[inbox].sum() <= 0: return []
    m = len(LO); sec = a['days']*86400.
    rice = E/sec                                                             # kg/s during the season
    other = np.full(m, a['other']*rice[inbox].sum()/max(inbox.sum(), 1))    # uniform other sources, same mean density
    sa = np.concatenate([(a['sa_rice']*rice)**2, (a['sa_other']*np.maximum(other, 1e-12))**2])
    area = (g*111.32)**2*np.cos(np.deg2rad(LA))                              # km2
    nobs = a['fclear']*area/a['pix']
    so = a['sigr']**2/np.maximum(nobs, 1e-6) + a['smod']**2
    # spatially correlated retrieval/transport bias: one state element per BBLK-degree block, persistent over the season
    nb = int(round(a['bblk']/g)); bx = ((LO - LO.min())/g).astype(int)//nb; by = ((LA - LA.min())/g).astype(int)//nb
    bid = np.unique(by*1000 + bx, return_inverse=True)[1]; nbk = bid.max() + 1
    B = np.zeros((m, nbk)); B[np.arange(m), bid] = 1.
    n = 2*m + nbk
    sa = np.concatenate([sa, np.full(nbk, a['sbias']**2)])
    rng = np.random.default_rng(a['seed']); F = np.zeros((n, n)); w = 1/so
    met = MET.get(norm(name)) if MET else None
    for d in range(int(a['days'])):
        if met is None:
            U, th = a['U']*np.exp(0.5*rng.standard_normal()), rng.uniform(0, 2*np.pi)
        else:   # ERA5 06 UTC climatology for the season month: lognormal speed, von Mises direction
            mo = met.loc[min(int(((PLANT[name] + d) % 365)/30.42), 11) + 1]
            U = mo.ws_med*np.exp(np.log(mo.ws_p75/mo.ws_p25)/1.349*rng.standard_normal())
            R = min(np.hypot(mo.u, mo.v)/mo.ws_med, 0.95)
            kap = 2*R + R**3 + 5*R**5/6 if R < 0.53 else (-0.4 + 1.39*R + 0.43/(1 - R) if R < 0.85 else 1/(R**3 - 4*R**2 + 3*R))
            th = rng.vonmises(np.arctan2(mo.v, mo.u), kap)
            w = 1/(a['sigr']**2/np.maximum(a['qa']*(1 - mo.tcc)*area/a['pix'], 1e-6) + a['smod']**2)
        K = jacobian(LO, LA, g, max(U, 0.5), th, a['spread'])
        K = np.hstack([K, K, B])                                             # rice and other share transport; bias
        K = K - (w @ K)/w.sum()                                              # project out the daily background offset
        F += (K*w[:, None]).T @ K
    west = inbox & (LO < np.median(LO[inbox])); east = inbox & ~west
    ET0, EU0, ER0 = rice[west].sum(), rice[east].sum(), rice[inbox].sum()
    hr = np.concatenate([inbox*1., np.zeros(m + nbk)])                       # rice total in the box
    hp = np.concatenate([west/ET0 - east/EU0, np.zeros(m + nbk)])            # paired fractional contrast
    oth = lambda msk: np.concatenate([np.zeros(m), other*msk, np.zeros(nbk)])
    out = []
    for ns in (1, 3, 10):
        Sh = np.linalg.inv(F*ns + np.diag(1/np.maximum(sa, 1e-30)))
        A = Sh @ (F*ns)                                                      # averaging kernel
        sd_tot = np.sqrt(hr @ Sh @ hr); sd_pri = np.sqrt(hr @ (sa*hr)); sd_pair = np.sqrt(hp @ Sh @ hp)
        # natural year-to-year variability, averaged over ns seasons before and ns after:
        # rice (weather) and other sources leaking into the rice estimate through the averaging kernel
        leak = hr @ A @ oth(np.ones(m))                                      # kg/s of rice per 100% change in others
        var_ba = 2*(sd_tot**2 + ((a['iav_rice']*ER0)**2 + (a['iav_other']*leak)**2)/ns)
        lw, le = hp @ A @ oth(west | (~inbox & (LO < np.median(LO[inbox])))), hp @ A @ oth(east | (~inbox & (LO >= np.median(LO[inbox]))))
        var_p = sd_pair**2 + (2*a['iav_pair']**2 + a['iav_other']**2*(lw**2 + le**2))/ns
        for yr, f in CUTS.items():
            out.append(dict(region=name, seasons=ns, year=yr, cut=f, rice_Mt_season=E[inbox].sum()/1e9,
                            dXmax_ppb=np.nan, prior_sd_pct=100*sd_pri/ER0, post_sd_pct=100*sd_tot/ER0,
                            leak_other_pct=100*leak/ER0,
                            z_before_after=f*ER0/np.sqrt(var_ba), z_paired=f/np.sqrt(var_p),
                            z_ba_noiav=f*ER0/(np.sqrt(2)*sd_tot)))
    # adoption x time: treated block = a compact fraction `ad` of the delta's rice, one season of data in
    # year Y with that year's cut; before/after on the treated block total, paired = treated block vs the rest
    Sh = np.linalg.inv(F + np.diag(1/np.maximum(sa, 1e-30))); A = Sh @ F
    # treated block grows outward from the rice-weighted centre of the delta, cell by cell
    idx = np.nonzero(inbox & (rice > 0))[0]
    cx, cy = np.average(LO[idx], weights=rice[idx]), np.average(LA[idx], weights=rice[idx])
    idx = idx[np.argsort((LO[idx] - cx)**2*np.cos(np.deg2rad(cy))**2 + (LA[idx] - cy)**2)]
    cr = np.cumsum(rice[idx])/ER0
    for ad in ADOPT:
        T = np.zeros(m, bool); T[idx[:np.searchsorted(cr, ad - 1e-9) + 1]] = True
        Un = inbox & ~T; ET = rice[T].sum(); near = np.zeros(m, bool)                     # margin cells: split by
        d2 = lambda msk: ((LO[:, None] - LO[msk][None])**2 + (LA[:, None] - LA[msk][None])**2).min(1)
        near = ~inbox & (d2(T) <= (d2(Un) if Un.any() else np.inf))                        # nearest block
        hT = np.concatenate([T*1., np.zeros(m + nbk)])
        leakT = hT @ A @ oth(T | near)
        var_ba = 2*(hT @ Sh @ hT + (a['iav_rice']*ET)**2 + (a['iav_other']*leakT)**2)
        if Un.sum() > 0 and rice[Un].sum() > 0:
            hq = np.concatenate([T/ET - Un/rice[Un].sum(), np.zeros(m + nbk)])
            l1, l2 = hq @ A @ oth(T | near), hq @ A @ oth(Un | (~inbox & ~near))
            var_q = hq @ Sh @ hq + 2*a['iav_pair']**2 + a['iav_other']**2*(l1**2 + l2**2)
        else: var_q = np.inf
        for yr, f in enumerate(YCUT, 1):
            AD_ROWS.append(dict(region=name, adoption=ad, treated_Mha=E[T].sum()/E[inbox].sum()*AREA[name], year=yr, cut=f,
                                z_before_after=f*ET/np.sqrt(var_ba), z_paired=f/np.sqrt(var_q)))
    # peak column signal of the full-adoption cut in year 10, mean wind from the west
    K = jacobian(LO, LA, g, a['U'], 0., a['spread'])
    for o in out: o['dXmax_ppb'] = CUTS[o['year']]*np.abs(K @ rice).max()
    return out

def main(cells_f, prefix):
    a = dict(grid=float(opt('grid', 0.25)), margin=float(opt('margin', 1)), U=float(opt('U', 4)),
             sigr=float(opt('sigr', 12)), smod=float(opt('smod', 8)), pix=float(opt('pix', 38.5)),
             fclear=float(opt('fclear', 0.1)), days=float(opt('days', 113)), sa_rice=float(opt('sa_rice', 0.5)),
             sa_other=float(opt('sa_other', 0.5)), other=float(opt('other', 1)), spread=float(opt('spread', 0.25)),
             seed=int(opt('seed', 1)), sbias=float(opt('sbias', 2)), bblk=float(opt('bblk', 1)),
             iav_rice=float(opt('iav_rice', 0.1)), iav_other=float(opt('iav_other', 0.15)), iav_pair=float(opt('iav_pair', 0.04)), qa=float(opt('qa', 0.5)))
    c = pd.read_csv(cells_f, usecols=['cell', 'lon', 'lat', 'area_irr', 'area_rf'])
    if opt('cells_dch4'):
        d = pd.read_csv(opt('cells_dch4')); c = c.merge(d, on='cell')
        tot = c.ctrl_kg.sum(); CUTS.update({y: -c[f'd{y}'].sum()/tot for y in CUTS})
    else:
        c['ctrl_kg'] = c.area_irr*float(opt('ef_irr', 120)) + c.area_rf*float(opt('ef_rf', 77))
    yc = pd.read_csv(opt('yearly', '/mnt/project-files/fair/v25fr_batch1/yearly_150.csv'))
    YCUT.extend((-yc.dch4_mt/yc.ctrl_ch4_mt).tolist())       # yearly fractional cut, years 1..25
    if opt('cells_dch4'): YCUT[:] = list(np.interp(np.arange(1, 26), list(CUTS), [CUTS[k] for k in CUTS]))
    if opt('cal'):
        cal = pd.read_csv(opt('cal'), usecols=['cell', 'plant_irr', 'plant_rf']); c = c.merge(cal, on='cell', how='left')
        c['plant'] = np.where(c.area_irr >= c.area_rf, c.plant_irr, c.plant_rf)
    if opt('era5'):
        e = pd.read_csv(opt('era5'))
        for r, g_ in e.groupby('region'): MET[norm(r)] = g_.set_index('m')
    names = opt('regions', ';'.join(REGIONS)).split(';')
    rows = []
    for n in names:
        rows += run_region(n, c, a); print(n, flush=True)
    out = pd.DataFrame(rows)
    yr = out.year.unique()
    # seasons needed for z >= 2 (information term scales with seasons; interpolate in log-log between 1, 3, 10)
    def need(r, col):
        s = out[(out.region == r.region) & (out.year == r.year)].sort_values('seasons')
        z = s[col].values; n = s.seasons.values
        if z[0] >= 2: return 1.
        if z[-1] < 2: return np.inf
        return float(np.exp(np.interp(np.log(2), np.log(z), np.log(n))))
    one = out[out.seasons == 1].copy()
    one['seasons_needed_before_after'] = one.apply(lambda r: need(r, 'z_before_after'), axis=1)
    one['seasons_needed_paired'] = one.apply(lambda r: need(r, 'z_paired'), axis=1)
    out = out.merge(one[['region', 'year', 'seasons_needed_before_after', 'seasons_needed_paired']], on=['region', 'year'])
    out.to_csv(f'{prefix}_regional.csv', index=False, float_format='%.3g')
    ad = pd.DataFrame(AD_ROWS); ad.to_csv(f'{prefix}_adoption.csv', index=False, float_format='%.3g')
    plot_adoption(ad, prefix)
    print(f'U {a["U"]} m/s, sigr {a["sigr"]} ppb, smod {a["smod"]} ppb, clear {a["fclear"]}, prior rice {a["sa_rice"]}, other {a["sa_other"]} x{a["other"]}')
    print(out[out.seasons == 1].round(2).to_string(index=False))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, col, t in zip(axs, ['z_before_after', 'z_paired'], ['Before/after, full adoption', 'Paired blocks, half treated']):
        s = out[(out.seasons == 1) & (out.rice_Mt_season > 0.1)].pivot(index='region', columns='year', values=col)
        s = s.loc[s[10].sort_values().index]
        for y, mk in zip(s.columns, 'o^sD'): ax.plot(s[y], s.index, mk, label=f'year {y}', ms=5)
        ax.axvline(2, color='#888', ls='--', lw=0.8); ax.set_title(t, fontsize=9); ax.set_xlabel('z, one season of TROPOMI data')
        ax.spines[['top', 'right']].set_visible(False)
    axs[0].legend(frameon=False, fontsize=8); fig.tight_layout(); fig.savefig(f'{prefix}_regional.png', dpi=160)

def plot_adoption(ad, prefix):
    """Per delta: detection statistic (one season of data) against treated area and year since first application."""
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    regs = [r for r in ad.region.unique()]
    fig, axs = plt.subplots(2, len(regs), figsize=(2.3*len(regs), 5.2), sharex=True, sharey=True, squeeze=False)
    lev = [0, 1, 2, 3, 4, 6, 8]
    for j, r in enumerate(regs):
        s = ad[ad.region == r]
        for i, col in enumerate(['z_paired', 'z_before_after']):
            P = s.pivot(index='adoption', columns='year', values=col)
            ax = axs[i, j]; Z = np.nan_to_num(P.values, posinf=0)
            cs = ax.contourf(P.columns, 100*P.index, Z, levels=lev, cmap='Blues', extend='max')
            ax.contour(P.columns, 100*P.index, Z, levels=[2], colors='#c0392b', linewidths=1.4)
            if i == 0: ax.set_title(f'{r}\n({s.treated_Mha.max():.1f} Mha)', fontsize=8)
            if i == 1: ax.set_xlabel('Year of deployment', fontsize=8)
            ax.set_yscale('log'); ax.set_yticks([1, 3, 10, 30, 100], ['1', '3', '10', '30', '100']); ax.tick_params(labelsize=7)
    axs[0, 0].set_ylabel('Paired blocks\n% of delta rice treated', fontsize=8)
    axs[1, 0].set_ylabel('Before/after\n% of delta rice treated', fontsize=8)
    cb = fig.colorbar(cs, ax=axs, shrink=0.7, pad=0.01); cb.set_label('z (one season of TROPOMI data); red line z = 2', fontsize=8)
    fig.savefig(f'{prefix}_adoption.png', dpi=160, bbox_inches='tight')

if __name__ == '__main__':
    main(*[a for a in sys.argv[1:] if not a.startswith('--')])
