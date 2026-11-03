# TE column vs PHREEQC TRANSPORT

20 cells, 60 shifts, pure advection; exchanger 0.1 mol + Hfo (11.0 g) per cell; acid soil solution (pH 5) flushed with Ca-Mg-HCO3 water (pH 7.5), no metal inflow.
PHREEQC 0.3 s, Python column 15.1 s.

| metal | pool | max abs err / scale | scale (mol) |
|---|---|---|---|
| Ni | total | 1.17e-06 | 0.000153 |
| Ni | exchange | 4.55e-06 | 0.000153 |
| Ni | dissolved | 4.58e-05 | 2e-06 |
| Ni | effluent (last cell) | 1.06e-05 | 7.34e-06 |
| Ni | mass left after 60 shifts | PHREEQC 0.930, Python 0.930 of initial | |
| Cu | total | 4.56e-07 | 0.000122 |
| Cu | exchange | 7.80e-06 | 0.000122 |
| Cu | dissolved | 3.38e-05 | 1e-06 |
| Cu | effluent (last cell) | 2.56e-05 | 1.31e-06 |
| Cu | mass left after 60 shifts | PHREEQC 0.984, Python 0.984 of initial | |

Worst error 4.58e-05: PASS
