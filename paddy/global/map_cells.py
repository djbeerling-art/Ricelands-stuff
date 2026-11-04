# Cell maps for the global riceland EW paper: 5-arcmin rasters of per-cell values with Natural Earth land/borders.
# Helper used by map_domain.py and map_deltas.py. Land/borders: Natural Earth 1:50m geojson (nvkelso/natural-earth-vector).
import json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
RES = 1/12
EXTENTS = {'global': (-120, 155, -40, 55), 'asia': (60, 150, -12, 50)}

def raster(lon, lat, val):
    nx, ny = int(360/RES), int(180/RES)
    g = np.full((ny, nx), np.nan)
    ix = np.clip(((np.asarray(lon) + 180)/RES).astype(int), 0, nx-1); iy = np.clip(((90 - np.asarray(lat))/RES).astype(int), 0, ny-1)
    g[iy, ix] = val
    return g

def _polys(fn):
    for f in json.load(open(fn))['features']:
        g = f['geometry']; cs = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for p in cs:
            for ring in p: yield np.asarray(ring)

def base(ax, ne, ext, land='#efefec', edge='#b9b9b4'):
    for r in _polys(f'{ne}/ne_50m_land.geojson'): ax.fill(r[:, 0], r[:, 1], color=land, lw=0, zorder=0)
    for r in _polys(f'{ne}/ne_50m_admin_0_countries.geojson'): ax.plot(r[:, 0], r[:, 1], color=edge, lw=0.3, zorder=3)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect('equal')
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color('#cccccc'); s.set_linewidth(0.5)

def show(ax, g, **kw):
    return ax.imshow(g, extent=(-180, 180, -90, 90), origin='upper', interpolation='nearest', zorder=2, **kw)
