---
title: "Draft for Methods: CDR and net greenhouse-gas accounting (v25b)"
---

Note for authors: Fluxes *F* are phase totals (mol m^−2^); subscripts Fe, NH4, SO4 and NO3 denote Fe^2+^, NH~4~^+^, SO~4~^2−^ and NO~3~^−^. Insert as a new subsection, e.g. 2.8 (after 2.7 Verification), or as 2.6.3. Equation numbers are placeholders. Text with cyan highlight is rationale or interpretation drafted by Claude and must be reworded by the authors (GMD AI policy). Everything else states what the code (`paddy/ghg_budget.py`, commit 482bad3b; multi-year totals from `paddy/v25/export_v25b.py`) computes.

# 2.8 Carbon dioxide removal and net greenhouse-gas accounting

All terms are areal totals for one simulated phase (the rice season or the fallow) and are summed over phases and years. Each basalt run is compared with a control run (no basalt) that has the same soil, management and restart history; Δ denotes basalt minus control. Phase totals are taken from SCEPTER's running time integrals of each flux, not from the sampled output rates.

**Cation release (CDR potential).** The base-cation charge released by dissolution of the applied rock minerals *m* in a phase is

$$R = \sum_{m} \sum_{i} z_i \, \nu_{i,m} \, D_m$$

EQNUM:E1

where *D*~m~ (mol m^−2^) is the amount of mineral *m* dissolved, *ν*~i,m~ the moles of cation *i* per mole of mineral and *z*~i~ its charge (2 for Ca and Mg, 1 for Na and K). Calcite, Fe(III) oxide and inert material in the rock recipe are excluded from the sum. *R* is converted to CO~2~ at 1 mol CO~2~ per equivalent (44.01 g mol^−1^). The control has *R* = 0.

**Alkalinity export.** Alkalinity leaves the column by two routes: advection of carbonate alkalinity through the base of the column, *F*^base^~ALK~, and lateral floodwater discharge (Sect. 2.6.2), whose alkalinity is taken from the charge balance of the exported major ions:

$$F^{\mathrm{lat}}_{\mathrm{ALK}} = 2 F_{\mathrm{Ca}} + 2 F_{\mathrm{Mg}} + F_{\mathrm{Na}} + F_{\mathrm{K}} + 2 F_{\mathrm{Fe}} - 2 F_{\mathrm{SO4}} - F_{\mathrm{Cl}} - F_{\mathrm{NO3}}$$

EQNUM:E2

$$E_{\mathrm{ALK}} = F^{\mathrm{base}}_{\mathrm{ALK}} + F^{\mathrm{lat}}_{\mathrm{ALK}}$$

EQNUM:E3

**Potentially durable alkalinity (PDA).** Exported Fe^2+^ and NH~4~^+^ are subtracted, two equivalents each:

$$\mathrm{PDA} = E_{\mathrm{ALK}} - 2 \left( F^{\mathrm{base}}_{\mathrm{Fe}} + F^{\mathrm{lat}}_{\mathrm{Fe}} + F^{\mathrm{base}}_{\mathrm{NH4}} \right)$$

EQNUM:E4

The factor 2 corresponds to oxidation and precipitation of Fe(OH)~3~ (2 H^+^ per Fe) and to complete nitrification (2 H^+^ per NH~4~^+^) after the water leaves the column. [PDA is a diagnostic of export that could persist downstream; it is not a verified permanent removal.]{custom-style="Rationale"} Results are reported with PDA; gross *E*~ALK~ is given as an alternative.

**Soil carbonate.** *C*~cc~ is the net calcite precipitated in the column in a phase (mol m^−2^, 1 mol CO~2~ per mol). It is negative when calcite dissolves, including calcite carried in the rock.

**Realised inorganic CDR.** Over years 1 … *N*, with sums over all seasons and fallows,

$$\mathrm{CDR}_{\mathrm{real}}(N) = \sum \Delta \mathrm{PDA} + \min \left[ \sum \Delta C_{\mathrm{cc}} , \; \max \left( \sum R - \sum \Delta \mathrm{PDA} , \, 0 \right) \right]$$

EQNUM:E5

The extra calcite is counted only up to the cation charge released by the rock and not already exported. [Beyond that limit, calcite Ca and alkalinity come from the exchange complex and from Fe and sulfate reduction rather than from the rock, and this calcite redissolves on drainage.]{custom-style="Rationale"} For a single phase the same expression is applied to that phase's totals.

**Greenhouse-gas change.** Using GWP100 values from AR6 (27 for non-fossil CH~4~, 273 for N~2~O),

$$\Delta \mathrm{GHG} = 27 \, \Delta M_{\mathrm{CH4}} + 273 \times \frac{44.01}{28.01} \, \Delta M_{\mathrm{N2O}}$$

EQNUM:E6

where *M*~CH4~ is the CH~4~ emitted (diffusion across the surface, ebullition and the unoxidised part of plant transport) and *M*~N2O~ the N~2~O emitted as N (diffusion and plant transport), both in t ha^−1^.

**Net balances.** In t CO~2~e ha^−1^,

$$\mathrm{Net}_{\mathrm{real}}(N) = \sum \Delta \mathrm{GHG} - \mathrm{CDR}_{\mathrm{real}}(N)$$

EQNUM:E7

$$\mathrm{Net}_{\mathrm{pot}}(N) = \sum \Delta \mathrm{GHG} - \sum R$$

EQNUM:E8

Negative values are a net benefit. Net~pot~ treats all released cations as if they had been exported. [It is an upper bound on the inorganic CDR term, not removal achieved within the simulated period.]{custom-style="Rationale"} CO~2~ exchange between soil and atmosphere, changes in soil organic carbon, CO~2~ re-release from exported alkalinity downstream (all export is counted at 1 mol CO~2~ per equivalent), and emissions from rock mining, grinding and transport are not included in either balance.
