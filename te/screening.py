"""Mass-balance screening models for trace-element (TE) accumulation under ERW.

These are the total-concentration screens used in the literature to flag
regulatory risk. They are the comparators for the mechanistic SCEPTER-TE
results (same rock, soil, dose and years).

1. Dupla et al. (2023, Eur. J. Soil Sci. 74, e13343), Eqs. 1-6: three
   scenarios for total TE in the 0-20 cm layer after n annual applications.
   - 'minimal'  : 1 wt%/yr rock dissolution (Eqs. 1-4); released TE minus
                  annual leaching and crop export accumulates.
   - 'maximal'  : full dissolution in the year of application (Eq. 5).
   - 'inert'    : no dissolution; rock accumulates and dilutes/enriches (Eq. 6).
   Leaching fractions per year (Tyler 1978, pH 4.2, 1000 mm): Ni 0.166,
   Cu 0.049, Cr 0.026, Zn 0.098. Other metals are not given by Dupla
   (default 0, i.e. conservative); crop export as mg/kg soil per year (Table 1).
2. Full-release mixing screen: all TE in the applied rock is released
   instantly and stays in the mixing layer (no leaching, no crop export):
       C_final = C_soil0 + C_rock * app_rate * n_app / (depth * BD).

All concentrations are mg/kg (total, aqua-regia-like). Doses in t/ha.
"""
import numpy as np

DUPLA_LEACH = {'Ni': 0.166, 'Cu': 0.049, 'Cr': 0.026, 'Zn': 0.098}
DEPTH, BD_SOIL0, BD_ROCK, R_WEATH = 0.20, 1300.0, 2000.0, 0.01


def dupla(c_rock, c_soil0, dose_t_ha_yr, years, *, scenario='minimal', leach=0.0,
          crop_mg_kg_yr=0.0, depth=DEPTH, bd_soil0=BD_SOIL0, bd_rock=BD_ROCK,
          r_weath=R_WEATH):
    """Total TE (mg/kg) in the mixing layer after each year 1..years.
    Annual application at the start of each year. Returns an array."""
    vol = depth * 1.0                      # m3 soil per m2
    app = dose_t_ha_yr * 0.1               # kg rock / m2 / yr
    out = np.zeros(years)
    if scenario == 'inert':                # Eq. 6 (arithmetic-geometric sequence)
        f = app / (vol * bd_rock)          # volume fraction replaced per year
        for n in range(1, years + 1):
            out[n - 1] = c_rock + (c_soil0 - c_rock) * (1 - f) ** n
        return out
    if scenario == 'maximal':              # Eq. 5, fixed point of the yearly map
        keep = (1 - leach)
        c = c_soil0
        for n in range(1, years + 1):
            add = c_rock * app / (bd_soil0 * vol)
            c = c + add * keep - crop_mg_kg_yr
            out[n - 1] = c
        return out
    # minimal weathering, Eqs. 1-4 (rock volume displaces soil; BD changes)
    mass_rock = 0.0                        # undissolved rock kg/m2
    weathered = 0.0                        # net TE from weathered rock, mg/m2
    for n in range(1, years + 1):
        mass_rock = mass_rock + app                      # add this year's rock
        mass_rock_after = mass_rock * (1 - r_weath)
        released = c_rock * r_weath * mass_rock          # mg/m2 this year
        weathered = (weathered + released) * (1 - leach) - crop_mg_kg_yr * vol * bd_soil0
        weathered = max(weathered, 0.0)
        v_rock = mass_rock_after / bd_rock
        bd_n = (v_rock * bd_rock + (vol - v_rock) * bd_soil0) / vol
        nat = c_soil0 * (vol - v_rock) * bd_soil0 / (vol * bd_n)
        unw = c_rock * mass_rock_after / (vol * bd_n)
        out[n - 1] = nat + unw + weathered / (vol * bd_n)
        mass_rock = mass_rock_after
    return out


def full_release(c_rock, c_soil0, dose_t_ha, n_app, *, depth=0.2, bd=1250.0):
    """Instant full release, no losses: total TE (mg/kg) after n_app events."""
    return c_soil0 + c_rock * dose_t_ha * 0.1 * n_app / (depth * bd)


def years_to_limit(series, limit):
    """First year (1-based) at which a yearly series exceeds limit, or None."""
    i = np.nonzero(np.asarray(series) > limit)[0]
    return int(i[0]) + 1 if len(i) else None
