# Reactive rock-Fe(III) test (Si root feedback off, w = 0), 1 Nov 2026

One season, exe scepter_paddy_v23, constants k_cal.in (krxn_calibrated_v22.in), from the settled validation states
(reference vc_rref_y7f; Gong/batch vc_r03_y7f; Wang slag dc7_p21_0_y7f). Extra ferrihydrite added to the rock with
--basfe3 (wt fraction of rock mass). Run script runFe25.sh; table fe25_table.py -> fe25_results.txt
(kg CH4/ha/season: production, emission = plant + ebullition + diffusion, soil and rhizosphere oxidation; Fe(III)
reduced = g2fe3 + g2gt + g2gr, mol Fe/m2).

Observed for comparison: Gong 36 t/ha -18 % (n.s.); Wang 2014 slag 4 t/ha -43 %; Ali et al. 2008 root-free incubations
of slag-amended soil, production -10 to -27 %; Park batches -25/-37 % (390/780 t/ha).

Reference site, 20 t/ha: OM storage gain over the season falls from 3.0 to 2.5 mol C/m2 with basalt (more OM decomposed),
g2ch4 3.53 -> 3.97 mol C/m2, g2fe3 1.79 -> 1.85.

## Diagnosis (runFe25b.sh): why basalt raises production with w = 0 (reference, 20 t/ha, one season)

| Case | Production | Emission | OM storage change (mol C/m2) |
|---|---|---|---|
| Standard | +12.5 % | -9.2 % | 3.00 -> 2.46 |
| No O2 inhibition of anaerobic pathways (--o2inh=1) | -0.2 % | -10.1 % | -4.29 -> -4.27 (OM pool drawn down) |
| No green-rust oxidation by O2 (groxy removed) | +8.1 % | -13.6 % | 3.02 -> 2.67 |

With basalt, O2 consumption by reduced Fe rises (green-rust oxidation 0.03 -> 0.35, Fe2+ oxidation 0.85 -> 1.02 mol O2/m2),
so root-zone O2 falls and O2 inhibition of anaerobic decomposition weakens. Green rust accounts for about a third of the rise.
Caveat: without O2 inhibition the OM pool is largely consumed, so that run is substrate-limited.

## O2-inhibition Ki sensitivity (runFe25c.sh; reference, 20 t/ha vs control, one season, constants not recalibrated)

| Ki (M) | Control production (kg CH4/ha) | Production change | Emission change |
|---|---|---|---|
| 2.5e-7 (standard) | 283 | +12.5 % | -9.2 % |
| 1e-6 | 478 | +5.1 % | -8.4 % |
| 5e-6 | 577 | +1.9 % | -9.4 % |
| off | 684 | -0.2 % | -10.1 % |

Weaker inhibition shrinks the basalt production rise but never turns it into the decrease seen in root-free experiments;
emission change stays ~-9 %. With Ki >= 1e-6 the control OM pool declines (not steady), so g2ch4 would need recalibrating.
