# Upscaling validation: run randomly drawn individual cells through the full protocol as "truth" and compare with the
# response of the archetype each belongs to (assignment) or an emulator fitted to the archetypes (David, 31 Oct 2026).
# Draws --n (cell, regime) units with probability proportional to rice area (regime area within the cell), and writes
# them in archetypes.csv format, one singleton "archetype" per unit (id v<cell>_<regime>), with that cell's own soil,
# N, planting day and monthly climate, built exactly as archetypes_clim.py builds an archetype; plus the archetype the
# unit belongs to (from <archdir>/cell_map.csv).
# Usage: python3 validation_cells.py <cells.csv> <cal.csv> <forcing> <archdir> <outdir> [--n=100] [--seed=1] [--nmax=300]
#   -> outdir/validation.csv (arch, regime, ..., args, member_of), outdir/clim/baseline/v*.csv
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import archetypes_clim as ac

def main(cells_f, cal_f, forc_f, archdir, outdir):
    n, seed, nmax = int(ac.opt('n', 100)), int(ac.opt('seed', 1)), float(ac.opt('nmax', 300))
    cm = pd.read_csv(os.path.join(archdir, 'cell_map.csv'))
    rng = np.random.default_rng(seed)
    pick = cm.iloc[rng.choice(len(cm), size=n, replace=False, p=cm.area.values/cm.area.sum())]
    cells = pd.read_csv(cells_f); cal = pd.read_csv(cal_f)
    c = cells.merge(cal[['cell', 'plant_irr', 'plant_rf', 'gsl_irr', 'gsl_rf', 'nfert']], on='cell', how='left')
    c['nfert'] = c.nfert.fillna(120).clip(upper=nmax)
    if 'fe3' not in c:
        c['fe3'] = np.clip(ac.FE3_REF*c.clay/ac.CLAY_REF, 0.004, 0.03) if 'clay' in c else ac.FE3_REF
    forc = ac.read_forcing(forc_f)
    forc = forc[forc.cell.isin(pick.cell)]
    fcells, M = ac.monthly(forc)
    pos = pd.Series(np.arange(len(fcells)), index=fcells)
    recs, cmap = [], []
    for p in pick.itertuples():
        r = c[c.cell == p.cell].iloc[0]; reg = p.regime
        sow = r[f'plant_{reg}'] if np.isfinite(r[f'plant_{reg}']) else 150
        gsl = r[f'gsl_{reg}'] if np.isfinite(r[f'gsl_{reg}']) else ac.SEASON_D
        plant = (sow + max(gsl - ac.SEASON_D, 0)) % 365
        i = pos.loc[p.cell]
        cf = ac.climate_features(np.array([plant]), {k: v[[i]] for k, v in M.items()}).iloc[0]
        aid = f'v{p.cell}_{reg}'
        recs.append(dict(arch=aid, regime=reg, rock=r.rock, area=p.area, ncell=1, plant=plant,
                         ph=r.ph, cec=r.cec, soc=r.soc, fe3=r.fe3, nfert=r.nfert, clay=r.clay, **cf.to_dict(),
                         member_of=p.arch, cell=p.cell))
        cmap.append((p.cell, reg, aid, p.area))
    a = pd.DataFrame(recs)
    cmd = pd.DataFrame(cmap, columns=['cell', 'regime', 'arch', 'area'])
    os.makedirs(outdir, exist_ok=True)
    paths, _ = ac.write_clim(cmd, fcells, M, outdir, 'baseline')
    a['args'] = [ac.driver_args(r, paths[r.arch]) for r in a.itertuples()]
    a.to_csv(os.path.join(outdir, 'validation.csv'), index=False)
    print(f'{len(a)} validation units ({(a.regime == "irr").sum()} irrigated) from {a.member_of.nunique()} archetypes, '
          f'{a.cell.nunique()} cells -> {outdir}/validation.csv')

if __name__ == '__main__':
    main(*[x for x in sys.argv[1:] if not x.startswith('--')])
