---
title: "Draft for Methods: CDR and net greenhouse-gas accounting (v25b)"
---

*Insert as a new subsection, e.g. 2.8 (after 2.7 Verification), or as 2.6.3. Equation numbers are placeholders. Text with cyan highlight is rationale or interpretation drafted by Claude and must be reworded by the authors (GMD AI policy). Everything else states what the code (`paddy/ghg_budget.py`, commit 482bad3b; multi-year totals from `paddy/v25/export_v25b.py`) computes.*

# 2.8 Carbon dioxide removal and net greenhouse-gas accounting

All terms are areal totals for one simulated phase (the rice season or the fallow) and are summed over phases and years. Each basalt run is compared with a control run (no basalt) that has the same soil, management and restart history; $\Delta$ denotes basalt minus control. Phase totals are taken from SCEPTER's running time integrals of each flux, not from the sampled output rates.

**Cation release (CDR potential).** The base-cation charge released by dissolution of the applied rock minerals $m$ in a phase is

$$R = \sum_{m} \sum_{i \in \{\mathrm{Ca,Mg,Na,K}\}} z_i \, \nu_{i,m} \, D_m , \qquad (\mathrm{E1})$$

where $D_m$ (mol m$^{-2}$) is the amount of mineral $m$ dissolved, $\nu_{i,m}$ the moles of cation $i$ per mole of mineral and $z_i$ its charge (2 for Ca and Mg, 1 for Na and K). Calcite, Fe(III) oxide and inert material in the rock recipe are excluded from the sum. $R$ is converted to CO$_2$ at 1 mol CO$_2$ per equivalent (44.01 g mol$^{-1}$). The control has $R = 0$.

**Alkalinity export.** Alkalinity leaves the column by two routes: advection of carbonate alkalinity through the base of the column, $F_{\mathrm{ALK}}^{\mathrm{base}}$, and lateral floodwater discharge (Sect. 2.6.2), whose alkalinity is taken from the charge balance of the exported major ions:

$$F_{\mathrm{ALK}}^{\mathrm{lat}} = 2F_{\mathrm{Ca}} + 2F_{\mathrm{Mg}} + F_{\mathrm{Na}} + F_{\mathrm{K}} + 2F_{\mathrm{Fe^{2+}}} - 2F_{\mathrm{SO_4}} - F_{\mathrm{Cl}} - F_{\mathrm{NO_3}} , \qquad (\mathrm{E2})$$

$$E_{\mathrm{ALK}} = F_{\mathrm{ALK}}^{\mathrm{base}} + F_{\mathrm{ALK}}^{\mathrm{lat}} . \qquad (\mathrm{E3})$$

**Potentially durable alkalinity (PDA).** Exported Fe$^{2+}$ and NH$_4^+$ are subtracted, two equivalents each:

$$\mathrm{PDA} = E_{\mathrm{ALK}} - 2\left(F_{\mathrm{Fe^{2+}}}^{\mathrm{base}} + F_{\mathrm{Fe^{2+}}}^{\mathrm{lat}} + F_{\mathrm{NH_4^+}}^{\mathrm{base}}\right) . \qquad (\mathrm{E4})$$

The factor 2 corresponds to oxidation and precipitation of Fe(OH)$_3$ (2 H$^+$ per Fe) and to complete nitrification (2 H$^+$ per NH$_4^+$) after the water leaves the column. [PDA is a diagnostic of export that could persist downstream; it is not a verified permanent removal.]{custom-style="Rationale"} Results are reported with PDA; gross $E_{\mathrm{ALK}}$ is given as an alternative.

**Soil carbonate.** $C_{\mathrm{cc}}$ is the net calcite precipitated in the column in a phase (mol m$^{-2}$, 1 mol CO$_2$ per mol). It is negative when calcite dissolves, including calcite carried in the rock.

**Realised inorganic CDR.** Over years $1 \ldots N$, with sums over all seasons and fallows,

$$\mathrm{CDR}_{\mathrm{real}}(N) = \sum \Delta\mathrm{PDA} + \min\!\left[\sum \Delta C_{\mathrm{cc}},\; \max\!\left(\sum R - \sum \Delta\mathrm{PDA},\, 0\right)\right] . \qquad (\mathrm{E5})$$

The extra calcite is counted only up to the cation charge released by the rock and not already exported. [Beyond that limit, calcite Ca and alkalinity come from the exchange complex and from Fe and sulfate reduction rather than from the rock, and this calcite redissolves on drainage.]{custom-style="Rationale"} For a single phase the same expression is applied to that phase's totals.

**Greenhouse-gas change.** Using GWP100 values from AR6 (27 for non-fossil CH$_4$, 273 for N$_2$O),

$$\Delta\mathrm{GHG} = 27\,\Delta M_{\mathrm{CH_4}} + 273\,\frac{44.01}{28.01}\,\Delta M_{\mathrm{N_2O\text{-}N}} , \qquad (\mathrm{E6})$$

where $M_{\mathrm{CH_4}}$ is the CH$_4$ emitted (diffusion across the surface, ebullition and the unoxidised part of plant transport) and $M_{\mathrm{N_2O\text{-}N}}$ the N$_2$O–N emitted (diffusion and plant transport), both in t ha$^{-1}$.

**Net balances.** In t CO$_2$e ha$^{-1}$,

$$\mathrm{Net}_{\mathrm{real}}(N) = \sum \Delta\mathrm{GHG} - \mathrm{CDR}_{\mathrm{real}}(N) , \qquad (\mathrm{E7})$$

$$\mathrm{Net}_{\mathrm{pot}}(N) = \sum \Delta\mathrm{GHG} - \sum R . \qquad (\mathrm{E8})$$

Negative values are a net benefit. $\mathrm{Net}_{\mathrm{pot}}$ treats all released cations as if they had been exported. [It is an upper bound on the inorganic CDR term, not removal achieved within the simulated period.]{custom-style="Rationale"} CO$_2$ exchange between soil and atmosphere, changes in soil organic carbon, CO$_2$ re-release from exported alkalinity downstream (all export is counted at 1 mol CO$_2$ per equivalent), and emissions from rock mining, grinding and transport are not included in either balance.
