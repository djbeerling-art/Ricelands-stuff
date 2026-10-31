# Run domain from all rice cells and full-resolution GLiM distances (David, 31 Oct 2026: basalt within 150 km,
# Colombia and Ecuador excluded, full-resolution GLiM vector instead of the 0.5-degree raster).
#   cells_all.csv       data/global/cells_all.csv (all 265,876 MapSPAM rice cells with soil; rock = placeholder)
#   cells_all_dist.csv  cell, dist_vb_full, dist_vbvi_full (km to the nearest 5-arcmin GLiM vb / vb+vi point,
#                       glim_basalt.py on the GLiM vector, all_touched)
# Rock recipe per cell: cells already in --keep (the older cells.csv) keep its recipe and dist_rock; the other cells take
#   the nearest GEOROC analysis in --rocks (lon, lat, rock); without --rocks, the recipe of the nearest --keep cell
#   (dist_rock = NaN). The original rocks.csv behind glb00-11 was not kept; rocks_georoc2026_nearestrecipe.csv
#   (GEOROC 2026 basalts, each assigned to the nearest existing recipe in normative space) stands in for new cells.
# Output has the cells.csv columns (dist_basalt = the chosen GLiM distance) for archetypes_clim.py / collect_chains.py.
# Usage: python3 make_domain.py <cells_all.csv> <cells_all_dist.csv> <out.csv> [--dmax=150] [--dcol=dist_vb_full]
#        [--exclude=COL,ECU] [--keep=data/global/cells.csv] [--rocks=<rocks.csv>]
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prep_cells import nearest, opt

def main(cells_f, dist_f, out_f):
    dmax = float(opt('dmax', 150)); dcol = opt('dcol', 'dist_vb_full')
    ex = [e for e in opt('exclude', 'COL,ECU').split(',') if e]
    c = pd.read_csv(cells_f).drop(columns=['rock', 'dist_basalt', 'dist_rock'], errors='ignore')
    c = c.merge(pd.read_csv(dist_f, usecols=['cell', dcol]), on='cell', how='left').rename(columns={dcol: 'dist_basalt'})
    c = c[(c.dist_basalt <= dmax) & ~c.iso3.isin(ex)].reset_index(drop=True)
    o = pd.read_csv(opt('keep', 'data/global/cells.csv'), usecols=['cell', 'lon', 'lat', 'rock', 'dist_rock'])
    c = c.merge(o[['cell', 'rock', 'dist_rock']], on='cell', how='left')
    new = c.rock.isna().values
    if opt('rocks', None):
        r = pd.read_csv(opt('rocks', None))
        d, i = nearest(c.lon.values[new], c.lat.values[new], r.lon.values, r.lat.values)
        c.loc[new, 'rock'] = r.rock.values[i]; c.loc[new, 'dist_rock'] = d
    else:
        _, i = nearest(c.lon.values[new], c.lat.values[new], o.lon.values, o.lat.values)
        c.loc[new, 'rock'] = o.rock.values[i]
    print(f'{new.sum()} cells new to the domain take their recipe from', opt('rocks', None) or 'the nearest kept cell')
    c['dist_basalt'] = c.dist_basalt.round(1); c['dist_rock'] = c.dist_rock.round(1)
    c.to_csv(out_f, index=False)
    a = c.area_irr + c.area_rf
    print(f'{len(c)} cells, {a.sum()/1e6:.1f} Mha within {dmax:.0f} km ({dcol}), excluding {ex} -> {out_f}')
    print('rock area share:', (a.groupby(c.rock).sum() / a.sum()).round(3).to_dict())

if __name__ == '__main__':
    main(*[a for a in sys.argv[1:] if not a.startswith('--')])
