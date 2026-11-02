# Arsenic in Riceland SCEPTER: Step 1 (arsenic branch)

This adds trace arsenic to the paddy model. It is kept on a separate branch so the v1.0 GMD code is untouched. Runs
that do not list the arsenic species or reactions give bit-identical output to v1.0. That was checked on a flooded
column, apart from the two extra charge-balance columns in `ph.txt`.

## What is tracked

| Name | Kind | Meaning |
|---|---|---|
| `as3`, `as5` | solutes | dissolved As(III) (H3AsO3) and As(V). Both are trace: no charge, no aqueous complexes. Diffusivity is that of H4SiO4 for As(III) and of H2AsO4- for As(V) (Li and Gregory 1974). |
| `as3ad`, `as5ad` | solids | As(III) and As(V) sorbed on Fe(III) oxide. Molar weight 74.92 (As), so wt fractions are As contents. They react only through the extra reactions below. |
| `as3sp`, `as5sp` | reactions | sorption, relaxing towards the Si-competitive equilibrium (below) |
| `as5rd`, `as5ra` | reactions | microbial As(V) reduction, of dissolved and sorbed As(V). First order, O2-inhibited as `g2fe3`. |
| `as3ox`, `as3oa` | reactions | As(III) oxidation by O2, of dissolved and sorbed As(III). First order, Monod in O2(aq). |
| `as3up` | reaction | rice uptake of As(III) through Lsi1, competitive with Si (Ki = Km of `siup`). Root profile as `siup`. Placeholder constants. |

## Sorption equation (`as3sp`, `as5sp`)

```
sorbed_eq [mol m-3] = c [mol L-1] * K * ( f_site * 0.2 * amfe3 / (1 + KSi * cSi^n)  +  Sx )
log K   = a + b (pH-7) + c (pH-7)^2        log KSi = aS + bS (pH-7)
rate    = krxn1 * min(2 sat, 1) * (sorbed_eq - sorbed)
```

- 0.2 is the number of weak sites per mol Fe (Dzombak and Morel 1990).
- `f_site` comes from `as_sites.in` and defaults to 1. It scales the site density for aged or P- or OM-coated oxide.
- `Sx` (krxn2) is the Si-insensitive sites in mol m-3, standing for crystalline Fe, clays and OM. It defaults to 0 and is soil-specific.
- Sorbed As follows `amfe3`, so it is released as the ferrihydrite is reductively dissolved (`g2fe3`).
- The constants were fitted to the PHREEQC diffuse-layer model in `paddy/arsenic/` (`grid_phreeqc.py`, `fit_kd.py`). That model uses USGS `wateq4f.dat` HFO constants for arsenite, arsenate and phosphate, and Swedlund and Webster for Si. The grid has 882 points: pH 5–8, Si 0.02–2 mM, As 2–200 µM, ferrihydrite Fe 0.02–0.23 mol per L porewater, and P 0.01 mM. Fitted constants and fit quality:

| | a | b | c | aS | bS | n | RMSE (log10) | max error (log10) |
|---|---|---|---|---|---|---|---|---|
| As(III) | 5.1882 | -0.0224 | -0.0171 | 3.8028 | 0.0104 | 0.8685 | 0.012 | 0.058 |
| As(V) | 7.2189 | -1.0735 | -0.2022 | 9.3859 | 0.1815 | 1.9115 | 0.052 | 0.223 |

pH and Si are clamped to the fitted range. In the fitted model:

- Raising Si from 0.3 to 1.5 mM raises dissolved As(III) 3.57 times. The full DLM gives 3.6.
- Losing 80% of the ferrihydrite raises it 5 times.
- As(V) rises 54 times from pH 6 to 7.5.

## Assumptions to revisit

- As is trace relative to sites, so As(III) and As(V) do not compete with each other. Loading in the fit grid is below 5%.
- Si sorption is not removed from solution. Porewater Si comes from SCEPTER's own balance.
- There is no P, carbonate or DOC competition. SCEPTER carries no P. In the prototype, P at 0.1–3 mM changed As(III) little.
- The redox rate constants are provisional: `as5rd` 50 /yr and `as3ox` 1000 /yr with O2 half-saturation 2e-5 M. They are not calibrated.
- The `as3up` constants are placeholders: Vmax 5e-3 mol m-2 yr-1 and Km 30 µM.

## Running

```bash
python3 paddy/run_flooded_column.py <tag> <reactions> <yr> ... --as=<mg/kg>[:<ug/L irrigation>[:<As(V) fraction>]] \
    [--asx=<mol/m3>] [--assite=<fraction>]
```

- `--as` adds the species and the sorption and redox reactions. It puts the labile soil As in as sorbed As(V), the state of oxidised soil before flooding.
- To get uptake, list `as3up` together with `siup`.
- `paddy/arsenic/as_profile.py <run dir> <z>` prints pH, Si, As(III), As(V), amfe3 and sorbed As through time at depth z.

## First test: one flooded season, 0.3 m column, no spin-up (uncalibrated)

Setup: reference soil with 3 wt% amfe3 and 6 mg/kg labile As. Reactions: `fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4eb,fe2fs,fesox,g2o2,groxy,sidox`. Options: `--ch4 --n --kaol=0.05 --refsoil --gt=0.02 --season --k=paddy/krxn_calibrated_v25_cal.in --nz=15 --ztot=0.3`. Results at 10 cm after 0.3 yr:

| Run | pH | Si (µM) | As(III) (µM) | As(V) peak (µM) |
|---|---|---|---|---|
| control | 7.27 | 266 | 0.053 | 0.11 (day 7) |
| basalt 20 t/ha | 8.31 | 1333 | 0.210 (4.0×) | 2.9 (weeks 2–6) |
| 1 wt% amfe3 | 7.28 | 265 | 0.177 (3.3×) | 0.32 |

- Sorbed As(V) is reduced to As(III) over about six weeks after flooding.
- Si competition alone accounts for 3.5× of the 4.0× As(III) rise with basalt.
- The basalt pH rise also mobilises As(V) for a few weeks, before it is reduced.
- Column mass balance closes. Residuals are below 1e-11 mol m-2.
- Major-element chemistry with and without As differs by about 1%. That is solver path; As is trace.
- Plugging the basalt run into the competitive uptake ratio (Si Km 300 µM) gives 4.0 × (1 + 266/300)/(1 + 1333/300) = 1.39. That is a 39% rise in As(III) uptake.
- This is a smoke test, not a prediction. There was no spin-up, the basalt pH is above the fitted range, and the redox constants are uncalibrated.

## Calibration and response-map tools (2 Nov 2026)

- **Si-insensitive sites on goethite.** `as3sp` and `as5sp` add f_gt sites per mol goethite Fe (`gt`) to krxn2. f_gt defaults to 0.02 and is the second value in `as_sites.in`, set with `--assite=<f>:<fgt>`. Crystalline Fe (dithionite minus oxalate) is therefore the soil input for the Si-insensitive pool.
- **Pot tests.** Seyfferth & Fendorf 2012 Richvale and Hawi pots, run at the SI values (oxalate Fe, DCB Fe, As spike), give absolute porewater As(III) within about 3× without fitting. The digitised Fig. 1 is in `paddy/arsenic/seyfferth2012_fig1_digitised.csv`. Two problems remain: silica gel dissolves too slowly unless amsi is scaled (production uses `--kscale=...,amsi:30`), and `--refsoil` irrigation gives too high a pH for these pots.
- **Threshold test** (`paddy/arsenic/threshold_table.py`). It compares the porewater As ratio with the Si-inhibition threshold T = (1+Si_trt/Ki)/(1+Si_ctrl/Ki) at Ki = 300 µM. The grain As direction is right in 12 of 15 treatments. Steel slag (He 2020), the basalt analogue, lies above the threshold. Richvale silica gel lies on the threshold but grain As fell, which points to Si effects beyond competition.
- **Response-map sweep** (`paddy/arsenic/run_as_sweep.sh`). 27 soils (ferrihydrite × goethite × irrigation alkalinity) each get a spin-up, a settle, then control and 20 t/ha basalt chains. `as3up` runs in the season only (`XRSS` in `run_chain.sh`). `paddy/arsenic/as_sweep_summary.py` reports pH, Si, As(III), R_As, T, the competitive and simulated uptake ratios, and the class (suppress, mobilise or uncertain). Grain iAs is left empty until translocation is modelled.
- **Smoke test.** One soil (1.2% ferrihydrite, 2% goethite, reference irrigation; 1 settle year, 1 chain year) ran end to end. Basalt raised Si 7× but As(III) only 1.27×, against a threshold of 4.2. The uptake ratio was 0.26 simulated and 0.30 competitive, so the class is suppress. The goethite pool dominates As retention in this soil.

## Next

1. Calibrate `f_site`, `Sx` and the redox constants against porewater As time series. Candidates are Seyfferth & Fendorf 2012, He 2020 and Limmer 2020.
2. Run from the settled v25 states (Stanage).
3. Calibrate `as3up` and add OsABCC1 vacuolar sequestration for grain partitioning.
4. Step 2: the Dzombak and Morel diffuse-layer model in the code, verified against PHREEQC example 8.
