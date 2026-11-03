"""Humic acid site amounts for the simplified WHAM Model VII surface in
te_extra.dat (Hum_aa-ad type A, Hum_ba-bd type B, Hum_sa/sb strong;
non-electrostatic)."""
NA = 3.4e-3          # mol type-A sites per g HA (Tipping et al. 2011)

PER_G = {**{f'Hum_a{c}': 0.901 * NA / 4 for c in 'abcd'},
         **{f'Hum_b{c}': NA / 8 for c in 'abcd'},
         'Hum_sa': 0.09 * NA, 'Hum_sb': 0.009 * NA}


def sites(g):
    """Surface master label -> mol sites for g grams of humic acid."""
    return {k: v * g for k, v in PER_G.items()}


def surface(g):
    from .solver import Surface
    return Surface(sites(g), area=0.0, mass=g, edl=False)
