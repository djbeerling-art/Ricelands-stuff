# Temperature response of riceland enhanced weathering with FaIR v2 (David, 2 Nov 2026): a background emissions pathway
# (RCMIP SSP, default ssp245) plus the annual global changes from the riceland SCEPTER runs, added as separate
# perturbations so each component's temperature response can be compared, alone and combined:
#   ch4  avoided CH4 emissions        (column dch4_mt,  Mt CH4/yr; negative = avoided)
#   n2o  avoided N2O emissions        (column dn2o_mt,  Mt N2O/yr; negative = avoided)
#   co2  net atmospheric CO2 removal  (column dco2_gt,  Gt CO2/yr; negative = removal, already net of carbon sources,
#                                      downstream fate and deployment/transport emissions), applied to CO2 FFI
#   all  the three together
# Each perturbation run is differenced against the background run with the same climate configuration, so the
# reported dT, dERF and concentration changes are free of the background's own trajectory.
# Climate: --calib=<dir> uses the fair-calibrate constrained ensemble (calibrated_constrained_parameters.csv and
#   species_configs_properties.csv from Zenodo; Smith et al. 2024), giving the 5-95% range. Without it, one central
#   AR6-like configuration is used (for testing the pipeline only).
# Usage: python3 fair_ew.py <perturbations.csv> <out prefix> [--ssp=ssp245] [--end=2200] [--calib=<dir>] [--nmax=0]
#   perturbations.csv: year, dch4_mt, dn2o_mt, dco2_gt (missing years = 0)
#   -> <prefix>_dT.csv (year x component, median and 5/95% if an ensemble), <prefix>_detail.nc, <prefix>.png
import sys, os
import numpy as np, pandas as pd
from fair import FAIR
from fair.io import read_properties
from fair.interface import initialise, fill

def opt(k, d=None):
    for a in sys.argv[1:]:
        if a.startswith(f'--{k}='): return a.split('=', 1)[1]
    return d

COMP = {'ch4': ['dch4_mt'], 'n2o': ['dn2o_mt'], 'co2': ['dco2_gt'], 'all': ['dch4_mt', 'dn2o_mt', 'dco2_gt']}
SPEC = {'dch4_mt': 'CH4', 'dn2o_mt': 'N2O', 'dco2_gt': 'CO2 FFI'}   # FaIR units: Mt CH4, Mt N2O, Gt CO2 per yr

def background(ssp, end, species, props):
    """RCMIP inputs for one scenario (FaIR fills by scenario name, so read them once and copy)."""
    b = FAIR(ch4_method='thornhill2021')
    b.define_time(1750, end, 1); b.define_scenarios([ssp]); b.define_configs(['x'])
    b.define_species(species, props); b.allocate(); b.fill_from_rcmip()
    return b

def main(pert_f, prefix):
    ssp, end = opt('ssp', 'ssp245'), int(opt('end', 2200))
    calib, nmax = opt('calib'), int(opt('nmax', 0))
    if calib:
        species, props = read_properties(os.path.join(calib, 'species_configs_properties.csv'))
        par = pd.read_csv(os.path.join(calib, 'calibrated_constrained_parameters.csv'), index_col=0)
        if nmax: par = par.iloc[:nmax]
        configs = list(par.index.astype(str))
    else:
        species, props = read_properties(); configs = ['central']
    b = background(ssp, end, species, props)
    scen = ['base'] + list(COMP)
    f = FAIR(ch4_method='thornhill2021')
    f.define_time(1750, end, 1); f.define_scenarios(scen); f.define_configs(configs)
    f.define_species(species, props); f.allocate()
    for s in scen:   # same background inputs in every scenario and configuration
        for v in ('emissions', 'concentration', 'forcing'):
            getattr(f, v).loc[dict(scenario=s)] = getattr(b, v).sel(scenario=ssp, config='x').values[:, None, :]
    # perturbations: annual values at FaIR timepoints (year + 0.5)
    p = pd.read_csv(pert_f).set_index('year').reindex(np.floor(f.timepoints).astype(int)).fillna(0)
    for c, cols in COMP.items():
        for col in cols:
            if col in p:
                f.emissions.loc[dict(scenario=c, specie=SPEC[col])] += p[col].values[:, None]
    if calib:
        f.override_defaults(os.path.join(calib, 'calibrated_constrained_parameters.csv'))
    else:
        f.fill_species_configs()
        fill(f.climate_configs['ocean_heat_capacity'], [8, 14, 100])
        fill(f.climate_configs['ocean_heat_transfer'], [1.1, 1.6, 0.9])
        fill(f.climate_configs['deep_ocean_efficacy'], 1.1)
        fill(f.climate_configs['gamma_autocorrelation'], 2.0)
        fill(f.climate_configs['forcing_4co2'], 8.0)
        fill(f.climate_configs['stochastic_run'], False)
    initialise(f.concentration, f.species_configs['baseline_concentration'])
    for v in (f.forcing, f.temperature, f.cumulative_emissions, f.airborne_emissions): initialise(v, 0)
    f.run(progress=False)
    T = f.temperature.sel(layer=0)                           # (timebounds, scenario, config)
    dT = T - T.sel(scenario='base')
    dF = f.forcing_sum - f.forcing_sum.sel(scenario='base')
    dC = f.concentration.sel(specie=['CO2', 'CH4', 'N2O']) - f.concentration.sel(scenario='base', specie=['CO2', 'CH4', 'N2O'])
    yrs = f.timebounds.astype(int)
    out = {'year': yrs}
    for c in COMP:
        x = dT.sel(scenario=c).values                         # (time, config)
        out[f'dT_{c}_mK'] = np.median(x, axis=1)*1e3
        if x.shape[1] > 1:
            out[f'dT_{c}_p05_mK'] = np.percentile(x, 5, axis=1)*1e3; out[f'dT_{c}_p95_mK'] = np.percentile(x, 95, axis=1)*1e3
    df = pd.DataFrame(out)
    df.to_csv(f'{prefix}_dT.csv', index=False, float_format='%.4g')
    import xarray as xr
    xr.Dataset({'dT': dT.drop_vars('layer', errors='ignore'), 'dERF': dF, 'dconc': dC}).sel(scenario=list(COMP)).to_netcdf(f'{prefix}_detail.nc')
    plot(df, p, prefix, ssp)
    yr0 = p.index[(p != 0).any(axis=1)].min()
    for y in [yr0 + 10, yr0 + 20, yr0 + 50, yr0 + 100]:
        if y in df.year.values:
            r = df[df.year == y].iloc[0]
            print(f'{y}: ' + ', '.join(f'{c} {r[f"dT_{c}_mK"]:+.2f} mK' for c in COMP))
    print(f'-> {prefix}_dT.csv, {prefix}_detail.nc, {prefix}.png ({len(configs)} configs, background {ssp})')

def plot(df, p, prefix, ssp):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    col = {'ch4': '#2a7f62', 'n2o': '#c08a1e', 'co2': '#3b5ba5', 'all': '#222222'}
    lab = {'ch4': 'avoided CH$_4$', 'n2o': 'avoided N$_2$O', 'co2': 'net CO$_2$ removal', 'all': 'combined'}
    yr0 = p.index[(p != 0).any(axis=1)].min(); d = df[df.year >= yr0 - 5]
    fig, ax = plt.subplots(figsize=(7, 4))
    for c in COMP:
        ax.plot(d.year, d[f'dT_{c}_mK'], color=col[c], lw=2.2 if c == 'all' else 1.6, label=lab[c])
        if f'dT_{c}_p05_mK' in d:
            ax.fill_between(d.year, d[f'dT_{c}_p05_mK'], d[f'dT_{c}_p95_mK'], color=col[c], alpha=0.15, lw=0)
    ax.axhline(0, color='#888', lw=0.8)
    ax.set_ylabel('Temperature change vs background (mK)'); ax.set_xlabel('Year')
    ax.set_title(f'FaIR response to riceland EW perturbations ({ssp} background)', fontsize=10)
    ax.legend(frameon=False, fontsize=9); ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(); fig.savefig(f'{prefix}.png', dpi=160)

if __name__ == '__main__':
    main(*[a for a in sys.argv[1:] if not a.startswith('--')])
