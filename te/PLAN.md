---
title: "Trace metals under basalt EW in upland soils: plan"
author: "Drafted 3 November 2026"
---

# Aim

Build a trace-element module for upland (aerated) SCEPTER and use it to show where basalt Ni, Cr, Cu, Zn, Cd and Pb actually go over 10 to 40 years in 3 temperate and 3 tropical soils, for several real basalts. The output is a short paper that replaces the box-model view of [Dupla et al. 2023](https://doi.org/10.1111/ejss.13343) with a mechanistic one.

Why Dupla is not enough:

- **Total content is mostly mixing arithmetic.** At 40 t/ha/yr into a 0 to 20 cm layer (about 2600 t soil/ha), the topsoil drifts toward rock composition whatever the weathering rate. Their inert and weathering scenarios differ by only a few years for Cu. The weathering chemistry hardly enters the headline result.
- **Leaching is applied once to the cumulative released pool** (their Eqs 4 and 5), not each year, so the released pool can never plateau. Applied yearly, their own 16.6%/yr Ni rate would cap released Ni near 6 years of input.
- **Leaching rates are from a pH 4.2 forest soil** (Tyler 1978), with no pH, sorption, organic matter or speciation dependence. Basalt raises pH, which changes all of these.
- **Dissolution is a flat 1%/yr** of rock mass, taken from a company website, with no mineral or host-phase dependence. Cr in chromite and Cu in sulphide behave nothing alike.
- **Regulation and risk are mixed up.** Limits are set on aqua-regia extractable totals, which they convert using soil, not fresh-rock, extractabilities. Toxicity depends on the labile and porewater pool, which they do not compute.
- **It fails its own test case.** Vienne et al. 2022 measured a soil Ni rise 48 times their estimate.

# Model design: SCEPTER-TE

Recommended build: a one-way coupled trace-element module inside upstream (cropland) SCEPTER, called after each converged time step. Trace metals sit at micromolar levels, so they do not feed back on pH or major cations. The module reads SCEPTER's local state (pH, pCO2, ionic strength, Ca and Mg, water flux, saturation, tillage mixing, per-mineral dissolution rates, Fe-oxide and SOM amounts) and solves its own transport and chemistry. This keeps the frozen paddy v25b code untouched and avoids re-tuning the main Newton solver. The chemistry is prototyped first in Python against PHREEQC, which also serves as the benchmark harness.

Processes, in build order:

1. **Release from host minerals.** Each metal is released in proportion to the dissolution rate of its host phase: olivine, clinopyroxene, plagioclase, glass, plus new accessory phases (magnetite and Cr-spinel, slow; Cu-Fe sulphide, fast oxidative dissolution).
2. **Aqueous speciation.** Hydrolysis, carbonate, sulphate and chloride complexes; Cr(III) and chromate.
3. **Cation exchange.** Same Gaines-Thomas scheme SCEPTER already uses for majors.
4. **Surface complexation on Fe oxides.** Dzombak and Morel diffuse-layer model on ferrihydrite and goethite (Ni, Cu, Zn, Cd, Pb, chromate), sites scaled to soil Fe-oxide content. Shared with the planned arsenic side paper.
5. **Organic-matter binding.** Generic humic binding (NICA-Donnan or WHAM-type parameters) for solid SOM and DOC; DOC transport carries Cu.
6. **Solubility caps.** Metal hydroxides and carbonates, Cr(OH)3.
7. **Cr redox.** Cr(III) oxidation by Mn oxides (prescribed per soil) and Cr(VI) reduction by Fe(II) and SOM.
8. **Plant uptake and offtake.** Transpiration-driven uptake with crop offtake, calibrated to grain and biomass concentrations.

Outputs per depth and year: total (HF-equivalent), aqua-regia extractable (residual rock counted by its own extractability), labile (exchangeable plus sorbed plus OM-bound), free-ion porewater concentration, leaching flux below the profile and crop offtake.

# Soils

Six soils spanning the controls that matter for metal mobility: pH, Fe oxides, organic matter, CEC and drainage. Values are approximate starting points; each will be pinned to a real ISRIC WoSIS profile.

| Soil | Setting | pH | SOC (%) | Clay (%) | Fe ox. (%) | CEC (cmol/kg) | MAT (°C) | Drainage (mm/yr) | Why it is in |
|---|---|---|---|---|---|---|---|---|---|
| T1 Luvisol loam | UK / NW Europe arable | 6.5 | 1.8 | 20 | 1.5 | 12 | 9.5 | 250 | UK trials (Kelland, Hillhouse rock) |
| T2 Mollisol silty clay loam | US Corn Belt | 6.2 | 2.5 | 30 | 1.5 | 20 | 11 | 300 | Upstream SCEPTER GMD24 setup, US deployment |
| T3 Acid sandy Cambisol/Podzol | N Europe | 5.0 | 1.5 | 5 | 0.3 | 4 | 8 | 350 | Worst case: low sorption, high leaching |
| P1 Ferralsol (Oxisol) | Brazil Cerrado | 5.0 | 1.5 | 50 | 9 | 5 | 23 | 600 | Fe-oxide rich, Brazil remineraliser market |
| P2 Acrisol (Ultisol) | SE Asia / India | 4.8 | 1.2 | 25 | 3 | 6 | 26 | 1000 | Acid, highly leached, wet tropics |
| P3 Vertisol | India Deccan | 7.8 | 0.8 | 50 | 2 | 45 | 26 | 150 | Alkaline smectitic contrast; Cr(VI) risk |

# Basalts and host minerals

Which mineral holds each metal decides how fast it is released, so each basalt needs both bulk trace-element data and a host-phase split. Bulk values will come from GEOROC and published analyses (not yet sourced).

| Basalt | Role | Mineralogy source |
|---|---|---|
| B1 Continental LIP mean | Like-for-like with Dupla | Generic tholeiite recipe from oxides |
| B2 Hillhouse dolerite (UK) | Kelland 2020 test, UK trials | SCEPTER recipe: labradorite 35%, augite 33%, forsterite 15%, analcime 7% |
| B3 Olivine-rich alkali basalt | High Ni and Cr worst case (Vienne 2022 type) | Recipe from oxides, high olivine |
| B4 Deccan or Paraná tholeiite | Tropical deployment rock, Cu-rich, low olivine | Recipe from oxides, glass-rich groundmass |

Host-phase split, set by mass balance against bulk rock:

- **Ni:** mostly olivine, then clinopyroxene and sulphide. Released fast.
- **Cr:** Cr-spinel and clinopyroxene. Spinel is close to inert, so much of the Cr should stay in residual rock.
- **Cu:** sulphide and glass or mesostasis, little in silicates. Sulphide oxidises quickly in aerated soil.
- **Zn:** magnetite, olivine and clinopyroxene. Partly slow.
- **Cd, Pb:** to be constrained (Cd largely follows Zn hosts; Pb in feldspar, glass and sulphide).

This split is the main way the model can depart from Dupla's single 1%/yr rate, and its uncertainty will be carried as a sensitivity range.

# Benchmarks and field tests

1. **Speciation and sorption vs PHREEQC.** Batch pH edges (pH 4 to 8) for each metal on ferrihydrite with the minteq.v4 / wateq4f diffuse-layer constants, plus exchange and humic binding. Target: free-ion and sorbed fractions within a few percent.
2. **Transport vs PHREEQC TRANSPORT.** A column with exchange plus surface complexation, as done for the ex11 cation-exchange baseline.
3. **Mass balance.** Released = sorbed + exchangeable + OM-bound + dissolved + leached + crop, to round-off.
4. **Kelland et al. 2020.** Hillhouse basalt, 100 t/ha, UK soil, sorghum mesocosm: soil and plant Ni, Cr, Cu.
5. **Vienne et al. 2022.** 50 t/ha basalt, potato mesocosm: soil Ni rise of 23 mg/kg, porewater and leachate Ni, no plant Ni rise.
6. **Reproduce Dupla.** With sorption off and their 1%/yr rate, the module should recover their curves, then show what changes as each process is switched on.

A literature check for newer field data (for example Ibrahim et al. 2025 on cropland metals) comes before the field tests.

# Runs and paper figures

Core matrix: 6 soils × 4 basalts × 3 doses (10, 20 and 40 t/ha/yr, annual) × 40 years = 72 runs, plus a one-off 50 t/ha case per soil. Each soil is first spun up to its target pH without basalt, as in the upstream GMD24 workflow. First timings: an upland spin-up takes about 25 s and a Hillhouse amendment about 40 s per 2 years on one core, so the matrix fits on 4 cores.

Figures for a compact paper:

1. **Schematic and Dupla comparison.** The module's processes, and Dupla's curves next to ours for the same scenario.
2. **40-year trajectories.** Ni and Cu per soil at 40 t/ha: total, aqua-regia extractable, labile and porewater, against regulatory and ecotoxicological thresholds.
3. **Time to threshold.** A soil × basalt heat map per metal and dose.
4. **Where the metal goes.** Budget split after 40 years: residual rock, sorbed on oxides, OM-bound, exchangeable, leached, crop.

Extended data: benchmark plots, host-phase sensitivity, Cr redox, Cd and Pb.

# Decisions (status 3 Nov 2026)

- **Soils:** the six above (agreed).
- **Basalts:** the four above; open: measured-TE rocks David wants added (UK quarries, Brazil remineralisers, Indian or Malaysian trial rocks).
- **Elements:** Ni, Cr, Cu, Zn, Cd and Pb (agreed).
- **Doses:** 10, 20 and 40 t/ha/yr for 40 years, plus a one-off 50 t/ha (agreed).
- **Coupling:** one-way module inside SCEPTER (agreed).
- **Target journal:** a short-format venue, e.g. Environ. Sci. Technol. Lett. or EJSS (agreed).
- **Code:** djbeerling-art/scepter, branch claude/project-thread-shu7fx; handoff note te/HANDOFF.md.

# Sources

- Dupla et al. 2023, Eur. J. Soil Sci. 74, e13343. https://doi.org/10.1111/ejss.13343
- Kanzaki et al. 2024, SCEPTER v1.0, Geosci. Model Dev. 17, 4515. https://doi.org/10.5194/gmd-17-4515-2024
- Plan doc (live): https://claude.ai/artifact/4V212c94Do8WZqrCrWxDZ9
