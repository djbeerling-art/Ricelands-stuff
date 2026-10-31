---
title: "Why does basalt lower paddy methane? An experiment to discriminate the mechanisms"
subtitle: "Discussion brief, draft 31 October 2026"
author: "David Beerling (University of Sheffield)"
---

# 1. The question

Silicate amendments (steel slag, wollastonite, basalt) lower CH₄ emissions from flooded rice in most trials, typically by
15–40 % (Ali et al., 2008; Wang et al., 2014; Das et al., 2022; Lim et al., 2022; Gong et al., 2026). These amendments
also supply Fe(III), raise soil pH and release dissolved Si, and no experiment so far has separated these effects.
Silicon applied alone has lowered, raised or not changed CH₄ (Lou et al., 2019; Ku et al., 2020; Limmer et al., 2018).
Studies of Si and the rice-root barrier to radial O₂ loss disagree in sign (Fleck et al., 2011, stronger barrier;
Tong et al., 2024, weaker barrier).

We have built a process-based reactive-transport model of flooded rice soils (Riceland SCEPTER) that resolves CH₄
production, soil and rhizosphere oxidation, and plant, bubble and diffusive emission, coupled to Fe, S, N and
mineral weathering. In the model, three candidate mechanisms make different, testable predictions:

| Mechanism | What changes first | Signature in the CH₄ budget |
|---|---|---|
| A. Fe(III) supply from the amendment | More Fe(III) for Fe-reducing bacteria, which outcompete methanogens | Lower CH₄ production; emission routes scale down together |
| B. Si raises root O₂ release | More O₂ in the root zone; more CH₄ and Fe(II) oxidation | Lower production in year 1 (Fe(III) regenerated), lower plant flux, ebullition also falls |
| C. Si tightens the root barrier, lowering plant gas conductance | Less CH₄ enters roots | Plant flux falls but CH₄ builds up in porewater and escapes as bubbles; total emission does not fall, and can rise |

A first model result is that mechanism C cannot reproduce the observed decreases: in our reference simulation, halving
root gas conductance cut plant-mediated emission by ~55 kg CH₄ ha⁻¹ but raised ebullition by ~125 kg, because CH₄
kept out of the roots also escapes the oxidation it meets in the rhizosphere. Mechanisms A and B both can. Telling
A and B apart, and testing the C result, needs the budget terms measured separately, not just net flux.

# 2. Suggested design

**Stage 1: one-season pot or mesocosm factorial (fast, cheap, decisive for A vs B vs C).**

| Treatment | Purpose |
|---|---|
| Control | Baseline |
| Basalt (field-relevant dose, e.g. 10–20 t ha⁻¹ equivalent, known grain size) | The amendment of interest |
| Si only (silicic acid, K-silicate or amorphous silica; Si release matched to basalt) | Isolates the Si / plant pathway |
| Fe(III) only (ferrihydrite, matched to the basalt's reducible Fe) | Isolates the electron-acceptor pathway |
| Lime, matched to the basalt's pH change | Isolates the pH effect |

Continuously flooded, with planted and unplanted pots for each treatment (unplanted pots give production and
non-plant emission without root effects); n ≥ 4 (a recent 36 t ha⁻¹ basalt trial at n = 3 found −18 % that was
not significant).

**Stage 2: multi-season field trial (for the long-term claims).** Control, basalt at two doses, under continuous
flooding and AWD; at least three seasons with fallows. The model predicts that control CH₄ drifts upward as reducible
Fe(III) is lost from the plough layer, while basalt plots hold their Fe(III), and that alkalinity export lags rock
dissolution by four to five years.

# 3. Measurements, by priority

**Essential (they discriminate the mechanisms)**

- Net CH₄ and N₂O flux (closed chambers), whole season and fallow.
- Emission partitioning: chambers on intact vs clipped or removed plants (plant-mediated flux); bubble traps
  (ebullition); floodwater CH₄ gradient (diffusion).
- Porewater CH₄, Si, Fe²⁺, pH and DOC by depth (rhizons or peepers), at least fortnightly; porewater CH₄ gives the
  storage term.
- CH₄ production potential: anoxic, root-free incubations of soil sampled through the season.
- CH₄ oxidation: in-situ inhibitor (difluoromethane or acetylene) and/or δ¹³C-CH₄ to estimate the oxidised fraction.
- Reducible Fe: 0.5 M HCl-extractable Fe(II)/Fe(III) and oxalate Fe in the plough layer (and plough pan in the
  field) at the start and end of each season.

**Desirable (they test the root physiology directly)**

- Radial O₂ loss along individual roots (root-sleeving O₂ electrodes or microsensors), or planar O₂/pH optodes.
- Root porosity, root oxidase activity (α-naphthylamine oxidation), Fe plaque (DCB extraction).
- Exodermal suberin and lignin (barrier anatomy).
- Functional genes (mcrA, pmoA, Geobacter gltA), as in Das et al. (2022).

**For the carbon budget (field stage)**

- Exchangeable cations, soil carbonate, and drainage volume, alkalinity and DIC.

# 4. What each result would mean

| Observation | Supports |
|---|---|
| Fe-only reproduces most of the basalt CH₄ decrease; Si-only has little effect | A (Fe supply) |
| Si-only lowers CH₄; production falls; ROL and root oxidase rise | B (Si → root O₂) |
| Si-only or basalt lowers plant flux but ebullition rises and total does not fall | C (barrier), and model's redirection |
| Lime alone lowers or raises CH₄ | pH effect on methanogens or methanotrophs |
| Production unchanged but oxidised fraction rises | Oxidation-driven suppression |

# 5. Model predictions to test

[To be completed on 1 November from the model runs: predicted changes in production, soil and rhizosphere oxidation,
plant, bubble and diffusive emission for each treatment and mechanism, at two reference sites. With the group's soil
and rock data (below) we can run their site directly and record the predictions before the experiment starts.]

# 6. Data that would let us model the group's site

- Soil: pH, CEC and exchangeable cations, texture, organic C and N, oxalate and dithionite Fe, available Si.
- Rock: bulk chemistry (XRF), mineralogy (XRD) and particle-size distribution.
- Management: flooding and drainage schedule, N fertiliser, residue handling, temperature record.

# References

Ali, M. A., Lee, C. H., and Kim, P. J.: Biol. Fertil. Soils, 44, 597–604, 2008.
Das, S., Jena, S. N., Bhuiyan, M. S. I., Kim, G. W., and Kim, P. J.: J. Clean. Prod., 373, 133799, 2022.
Fleck, A. T., et al.: J. Exp. Bot., 62, 2001–2011, 2011.
Gong, X., et al.: J. Environ. Manage., 405, 129708, 2026.
Ku, H. H., et al.: Pedosphere, 30, 535–543, 2020.
Lim, J. Y., et al.: Sci. Total Environ., 806, 150961, 2022.
Limmer, M. A., et al.: Sci. Total Environ., 624, 1360–1368, 2018.
Lou, Y., et al.: Energy Sci. Eng., 7, 1784–1794, 2019.
Tong, S., et al.: Environ. Exp. Bot., 226, 105941, 2024.
Wang, W., et al.: Steel slag amendment reduces methane emission and increases rice productivity in subtropical paddy
fields in China, 2014.
