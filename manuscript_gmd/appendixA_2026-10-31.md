---
title: "Appendix A: Process rate laws, parameters and model inputs (Riceland SCEPTER v1.0)"
---

This appendix lists every process added to SCEPTER for flooded rice soils, with the rate law, stoichiometry, parameter values and units used in all simulations in this paper. Values are those of the frozen production version: executable v22 (commit 162913a) with calibration file `paddy/krxn_calibrated_v22.in`, and v23 (commit 267a856) for the verification in Fig. 3. The two differ only in the carbon-closure fix described in Sect. A9. Where the code default differs from the calibrated value, the calibrated value is given and the default is noted.

# A1 Notation and units

| Quantity | Unit | Notes |
|---|---|---|
| Time | yr (365 d) | |
| Depth *z* | m, positive downward | |
| Solids (OM `g2`, minerals, urea) | mol m⁻³ bulk soil | |
| Aqueous species [X] | mol L⁻¹ pore water | storage term φ *S*~w~ 1000 [X] (mol m⁻³ bulk) |
| Gases | partial pressure *p* (atm) | total = gas phase + dissolved (*K*~H~ *p*) |
| Reaction rates *R* | mol m⁻³ bulk yr⁻¹ | per mol of reaction extent |
| Plant and root fluxes | mol m⁻² yr⁻¹ | distributed over the root profile (Sect. A5) |

φ is porosity, *S*~w~ water saturation and *K*~H~ Henry's constant (mol L⁻¹ atm⁻¹). For the reactions that consume organic matter (OM), one mol of extent is one mol of CH~2~O consumed, so v~max~ is a rate of OM loss. The following modifiers recur:

$$\mathrm{M}(X,K)=\frac{X}{X+K},\qquad \mathrm{I}(X,K_i)=\frac{K_i}{X+K_i},\qquad f_{\mathrm{sat}}=\min(2S_\mathrm{w},1).$$

Every OM-consuming reaction carries M(g2, 100 mol m⁻³). Every anaerobic pathway carries an O~2~ inhibition term *f*~O2~ = I([O~2~], 2.5 × 10⁻⁷ M) and the saturation factor *f*~sat~. The Fe(III), SO~4~²⁻ and CH~4~ pathways also carry a nitrate inhibition term *f*~NO3~ = I([NO~3~⁻], 1.13 × 10⁻⁴ M) (Maggi et al., 2008).

SCEPTER has no redox equilibrium: every electron transfer in Tables A1 and A2 is kinetic. Each table therefore gives two forms of every reaction. The **reference reaction** is the chemically balanced equation (elements and charge), written with H⁺ and H~2~O, and defines what the process is. The **species advanced by the model** are the components whose totals the reaction operator changes, per mol of extent, exactly as coded in `scepter.f90`. H⁺ and H~2~O are not transported components in SCEPTER, so they do not appear in the second column. Protons are nonetheless conserved: pH is solved in every Newton iteration from the charge balance of all total concentrations, including the exchanger, so the proton consumption of, for example, Fe(III) reduction (8 H⁺ per CH~2~O) is recovered from the Fe²⁺ and dissolved inorganic carbon (DIC) that the reaction adds. Total ammonia (NH~3~ + NH~4~⁺) and DIC are each one component. In addition to the coefficients shown, every reaction that consumes OM releases *n*~c~ = 0.03 mol NH~3~ per mol CH~2~O (`--n2c=0.03`); this N is omitted from the balanced forms for clarity.

# A2 Carbon, iron and sulfur reactions

**Table A1.** Carbon, iron and sulfur reactions. Fe~pool~ = amfe3 + 2 *f*~gr~ gr (mol m⁻³), the Fe(III) available to reducers, with green-rust bioavailability *f*~gr~ = 1. Species names: g2 = OM (CH~2~O), amfe3 = ferrihydrite, gt = goethite, gr = green rust Fe~3~(OH)~8~, sid = siderite, fes = FeS; aqueous totals Fe(II), SO~4~, HS, Fe(III); gases O~2~, CO~2~ (DIC), CH~4~.

| Reaction | Reference reaction (balanced) | Species advanced by the model (per mol extent) | Rate law (mol m⁻³ yr⁻¹) | Parameters |
|---|---|---|---|---|
| `g2o2` aerobic respiration | CH~2~O + O~2~ → CO~2~ + H~2~O | −1 g2, −1 O~2~, +1 CO~2~ | v M(g2) M([O~2~], 5 × 10⁻⁶ M) | v = 300 yr⁻¹ |
| `g2fe3` ferrihydrite reduction | CH~2~O + 4 Fe(OH)~3~ + 8 H⁺ → CO~2~ + 4 Fe²⁺ + 11 H~2~O | −1 g2, −4 amfe3, +4 Fe(II), +1 CO~2~ | v M(g2) M(Fe~pool~, 100) *f*~O2~ *f*~NO3~ *f*~sat~ | v = 300 yr⁻¹ (code default 200) |
| `g2gr` green-rust reduction | CH~2~O + 2 Fe~3~(OH)~8~ + 12 H⁺ → CO~2~ + 6 Fe²⁺ + 15 H~2~O | −1 g2, −2 gr, +6 Fe(II), +1 CO~2~ | shares the `g2fe3` rate through Fe~pool~ | *f*~gr~ = 1.0 |
| `g2gt` goethite reduction | CH~2~O + 4 FeOOH + 8 H⁺ → CO~2~ + 4 Fe²⁺ + 7 H~2~O | −1 g2, −4 gt, +4 Fe(II), +1 CO~2~ | v M(g2) M(gt, 100) *f*~O2~ *f*~NO3~ *f*~sat~ | v = 10 yr⁻¹ (Roden and Zachara, 1996) |
| `g2so4` sulfate reduction | CH~2~O + ½ SO~4~²⁻ + ½ H⁺ → CO~2~ + ½ HS⁻ + H~2~O | −1 g2, −½ SO~4~, +½ HS, +1 CO~2~ | v M(g2) M([SO~4~²⁻], 10⁻⁴ M) *f*~O2~ *f*~NO3~ *f*~sat~ | v = 300 yr⁻¹ (code default 100) |
| `g2ch4` methanogenesis | CH~2~O → ½ CH~4~ + ½ CO~2~ | −1 g2, +½ CH~4~, +½ CO~2~ | v M(g2) I(Fe~pool~, 30) I([SO~4~²⁻], 10⁻⁴ M) *f*~O2~ *f*~NO3~ *f*~sat~ | v = 1860 yr⁻¹ (calibrated); *K*~i,Fe~ = 30 mol m⁻³ |
| `ch4o2` methanotrophy | CH~4~ + 2 O~2~ → CO~2~ + 2 H~2~O | −1 CH~4~, −2 O~2~, +1 CO~2~ | v M([CH~4~], 5 × 10⁻⁶ M) M([O~2~], 2 × 10⁻⁵ M) | v = 500 mol m⁻³ yr⁻¹ |
| `fe2o2` Fe(II) oxygenation | Fe²⁺ + ¼ O~2~ + H⁺ → Fe³⁺ + ½ H~2~O | −1 Fe(II), −¼ O~2~, +1 Fe(III)~aq~ | (*k*~SS~ [OH⁻]² + *k*~0~) [Fe(II)] *p*O~2~, on dissolved and exchangeable Fe(II) | *k*~SS~ = 8 × 10¹³ M⁻² min⁻¹ atm⁻¹; *k*~0~ = 10⁻⁷ min⁻¹ atm⁻¹ (Stumm and Lee, 1961; Singer and Stumm, 1970) |
| `fe2gr` green-rust formation and dissolution | Fe²⁺ + 2 Fe(OH)~3~ + 2 H~2~O → Fe~3~(OH)~8~ + 2 H⁺ | −1 Fe(II), −2 amfe3, +1 gr | k *f*~sat~ ln Ω; Ω = 10^−9.98^ [Fe²⁺]/[H⁺]²; × M(amfe3, 1) when forming, × M(gr, 1) when dissolving | k = 10⁴ mol m⁻³ yr⁻¹; log K −9.98 (Bourrié et al., 1999) |
| `groxy` green-rust oxidation | Fe~3~(OH)~8~ + ¼ O~2~ + ½ H~2~O → 3 Fe(OH)~3~ | −1 gr, −¼ O~2~, +3 amfe3 | k gr *K*~H,O2~ *p*O~2~ | k = 10⁷ L mol⁻¹ yr⁻¹ |
| `fe2fs` FeS precipitation and dissolution | Fe²⁺ + HS⁻ → FeS + H⁺ | −1 Fe(II), −1 HS, +1 fes | k ln Ω; × M(fes, 1) when dissolving | k = 10³ mol m⁻³ yr⁻¹; log K 3.915 |
| `fesox` FeS oxidation | FeS + 2 O~2~ → Fe²⁺ + SO~4~²⁻ | −1 fes, −2 O~2~, +1 Fe(II), +1 SO~4~ | k fes [O~2~] | k = 10⁶ L mol⁻¹ yr⁻¹ |
| `sidox` siderite oxidation | FeCO~3~ + ¼ O~2~ + 3/2 H~2~O → Fe(OH)~3~ + CO~2~ | −1 sid, −¼ O~2~, +1 amfe3, +1 CO~2~ | k sid [O~2~] | k = 10⁵ L mol⁻¹ yr⁻¹ |

All reference reactions in Tables A1 and A2 balance in every element and in charge. The units of the Fe(II) oxygenation constants follow Stumm and Lee (1961). In the code they are converted to yr⁻¹ (× 60 × 24 × 365), and the rate in mol m⁻³ yr⁻¹ is the product with the Fe(II) concentration expressed per bulk volume. Green rust stands in for the pH buffering of flooded soils near pH 6.5–7 (Ponnamperuma, 1972). Goethite and hematite are not allowed to precipitate, because the soil ferrihydrite would otherwise ripen during spin-up. Magnetite is also excluded, because it would replace green rust and lock up reducible Fe(III). Calcite nucleates from a seed of 0.001 mol m⁻³ (`--nucl=cc:0.001`). Siderite is allowed to form at equilibrium.

# A3 Nitrogen reactions

**Table A2.** Nitrogen reactions. *g*~pH~ = exp[−0.5 (pH − 7)²] (Maggi et al., 2008). NH~3~ denotes total ammonia (NH~3~ + NH~4~⁺).

| Reaction | Reference reaction (balanced) | Species advanced by the model (per mol extent) | Rate law (mol m⁻³ yr⁻¹) | Parameters |
|---|---|---|---|---|
| urea hydrolysis | CO(NH~2~)~2~ + H~2~O → 2 NH~3~ + CO~2~ | −1 urea, +2 NH~3~, +1 CO~2~ | first order, a few days | SCEPTER default |
| `amo2o` nitrification | NH~4~⁺ + 2 O~2~ → NO~3~⁻ + 2 H⁺ + H~2~O | −1 NH~3~, −2 O~2~, +1 NO~3~ | v M([NH~4~⁺], 1.4 × 10⁻⁴ M) M([O~2~], 2.41 × 10⁻⁵ M) *g*~pH~ | v = 30 yr⁻¹ |
| `g2n21` denitrification to N~2~O | CH~2~O + NO~3~⁻ + H⁺ → CO~2~ + ½ N~2~O + 3/2 H~2~O | −1 g2, −1 NO~3~, +½ N~2~O, +1 CO~2~ | *r* v M(g2) M([NO~3~⁻], 1.13 × 10⁻⁴ M) *f*~O2~ *g*~pH~ | v = 300 yr⁻¹ |
| `g2n0` denitrification to N~2~ | CH~2~O + 4/5 NO~3~⁻ + 4/5 H⁺ → CO~2~ + 2/5 N~2~ + 7/5 H~2~O | −1 g2, −4/5 NO~3~, +1 CO~2~ (N~2~ not tracked; it leaves the system) | 1.25 (1 − *r*) × the `g2n21` rate without *r* | |
| N~2~O yield *r* | | | $r = 0.1 + 0.9/\left[1 + 10^{\,\mathrm{pH}-6.2}\right]$ | Šimek and Cooper (2002); Liu et al. (2010); Russenes et al. (2016) |
| `g2n2p` N~2~O reduction | CH~2~O + 2 N~2~O → CO~2~ + 2 N~2~ + H~2~O | −1 g2, −2 N~2~O, +1 CO~2~ (N~2~ not tracked) | v M(g2) M([N~2~O], 5 × 10⁻⁶ M) I([NO~3~⁻], 10⁻³ M) *f*~O2~ / [1 + ([H⁺]/10^−5.5^)²] | v = 300 yr⁻¹; pH~50~ 5.5 |
| `nh4up` rice N uptake | NH~4~⁺ removed | −1 NH~3~ | *F* M([NH~4~⁺], 5 × 10⁻⁵ M) *f*~sat~ × root profile | *F* = 3.5 mol N m⁻² yr⁻¹ |

Urea is applied at 120 kg N ha⁻¹ per season, spread evenly over the 113-day season and placed in the plough layer. Mineralisation releases NH~3~ at N:C = 0.03 mol mol⁻¹ of OM decomposed (`--n2c=0.03`). NH~3~ volatilisation is not represented.

# A4 Temperature and pH dependence

Biological rates scale as

$$k(T)=k_{25}\,Q_{10}^{(T-25)/10},$$

with Q~10~ = 3 for `g2ch4` and Q~10~ = 2 for `g2fe3`, `g2gr`, `g2gt`, `g2so4`, `ch4o2`, `g2o2`, `amo2o`, `g2n21`, `g2n0`, `g2n2p` and `rtco2`. These are literature values (Segers, 1998), not fitted. Abiotic reactions (`fe2o2`, `fe2gr`, `groxy`, `fe2fs`, `fesox`, `sidox`), gas transport, `rtoxy`, `nh4up` and `siup` have no temperature term. Mineral dissolution follows SCEPTER's Arrhenius terms, and equilibrium and Henry's constants follow SCEPTER's thermodynamic temperature dependence. Soil temperature is constant within a run: 25 °C at the reference site, and the growing-season mean for each archetype.

pH enters the rate laws only through the explicit factors in Table A3. A bell-shaped methanogen pH response (`--ch4ph`) exists in the code but is off in all runs reported here (Sect. 5).

**Table A3.** Explicit pH factors.

| Process | pH factor |
|---|---|
| `fe2o2` | [OH⁻]² |
| `fe2gr`, `fe2fs` | through Ω ([H⁺]² and [H⁺]) |
| `amo2o`, `g2n21`, `g2n0` | *g*~pH~ = exp[−0.5 (pH − 7)²] |
| N~2~O yield *r* | logistic, pH~50~ 6.2 |
| `g2n2p` | 1/[1 + ([H⁺]/10^−5.5^)²] |
| Rhizosphere CH~4~ oxidation *P*~ox~ | logistic, pH~50~ 6 (Table A5) |

# A5 Plant and root terms

Each plant flux *F* (mol m⁻² yr⁻¹) is distributed with depth as *F* exp(−*z*/*z*~r~)/*z*~r~, with *z*~r~ = 0.1 m, and multiplied by *f*~sat~ and by a plant factor (1 in the season, 0 in the fallow).

**Table A4.** Plant and root terms.

| Term | Effect | Value |
|---|---|---|
| `rtco2` root respiration | + DIC | 60 mol C m⁻² yr⁻¹ (code default 15) |
| `rtoxy` radial O~2~ loss | + O~2~, × *f*~Si~ | 3.65 mol O~2~ m⁻² yr⁻¹ (10 mmol m⁻² d⁻¹) |
| Si feedback | *f*~Si~ = 1 − *w* + *w* *h*([Si])/*h*([Si]~ref~), *h*(Si) = Si/(Si + *K*~Si~) | *K*~Si~ = 2 × 10⁻³ M, [Si]~ref~ = 2.7 × 10⁻⁴ M, *w* = 0.2 (`--rtsi=2e-3:2.7e-4:0.2`) |
| `siup` rice Si uptake | − H~4~SiO~4~ | 3.7 mol Si m⁻² yr⁻¹ × M([Si], 3 × 10⁻⁴ M) |
| `nh4up` rice N uptake | − NH~4~⁺ | Table A2 |

The Si feedback is the only empirical term in the plant module. With *w* = 0 it is off, and root O~2~ loss does not depend on Si.

# A6 Gas transport and the floodwater boundary

**Table A5.** Gas transport. *k*(*z*) = *k*~pl~ exp(−*z*/0.1 m).

| Process | Rate (mol m⁻³ yr⁻¹) | Parameters |
|---|---|---|
| `ch4pl` plant-mediated CH~4~ transport | *k*(*z*) φ *S*~w~ 1000 *K*~H~ (*p*CH~4~ − 1.9 × 10⁻⁶) | *k*~pl~ = 1100 yr⁻¹ |
| `ch4rx` rhizosphere CH~4~ oxidation | a fraction *P*~ox~ of the `ch4pl` flux is oxidised to CO~2~ in the cell and (1 − *P*~ox~) is emitted; *P*~ox~ = *p*~min~ + (*p*~max~ − *p*~min~)/[1 + ([H⁺]/10^−pH50^)^*n*^] | *p*~min~ 0.3, *p*~max~ 0.9, pH~50~ 6, *n* 1 (`--pox=0.3:0.9:6:1`) |
| `n2opl` plant-mediated N~2~O transport | as `ch4pl`, rate constant × 0.207, atmospheric N~2~O 330 ppb | 0.207 |
| `ch4eb` ebullition | *k* φ *S*~w~ 1000 *K*~H~ max(*p*CH~4~ − 0.4 atm, 0), vented directly | *k* = 1000 yr⁻¹ |
| Soil diffusion | SCEPTER gas and aqueous diffusion with Millington-type tortuosity | |

While the surface is flooded, dissolved gases (O~2~, CO~2~, CH~4~, N~2~O, NH~3~) exchange between the top cell and the atmosphere through the standing water:

$$J = k_\mathrm{fw}\,w_\mathrm{fw}\,1000\,\left([X]_\mathrm{top} - K_\mathrm{H}\,p_\mathrm{atm}\right),\qquad w_\mathrm{fw}=\min\!\left(1,\max\!\left(0,\frac{S_\mathrm{w,top}-0.9}{0.1}\right)\right),$$

with *J* in mol m⁻² yr⁻¹ and *k*~fw~ = 36.5 m yr⁻¹ (0.1 m d⁻¹). When the surface drains (*S*~w~ < 0.9), gas diffusion through the air-filled pores takes over. CH~4~ emission is the sum of the surface flux, ebullition and (1 − *P*~ox~) times the plant flux. The plant terms are zero in the fallow.

# A7 Column, water regime and schedules

**Table A6.** Column, hydrology and schedules.

| Item | Setting |
|---|---|
| Column | 0.5 m, 25 cells (`--nz=25 --ztot=0.5`), porosity 0.5 |
| Plough pan | 0.20–0.24 m; aqueous diffusivity and mechanical dispersion × 0.1, gas diffusivity × 0.1; dispersivity scale fixed at 0.3 m (`--pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3`) |
| Subsoil | saturation capped at 0.8 below the pan (perched water above it); base of the column open to soil air for O~2~ (*p*O~2~ 0.21 atm); CO~2~ and other gases closed at the base |
| Percolation *q* | 0.5 m yr⁻¹ (1.4 mm d⁻¹), constant through the year, free outflow at the base |
| Saturation profile | *S*~w~(*z*) = min[1, *S*~top~ + (1 − *S*~top~) *z*/*z*~wt~] |
| Continuous flooding | days 0–99: *S*~top~ = 1 |
| Pre-harvest drain (`--phd=14`) | days 99–113: *S*~top~ = 0.6, *z*~wt~ = 0.15 m |
| AWD schedule (`--awd`) | managed AWD; also applied to rainfed archetypes as a prescribed intermittent-flooding regime (below). Flooded days 0–29, then cycles of 7.3 d drained (*S*~top~ 0.6, *z*~wt~ 0.15 m) and 14.6 d reflooded until the pre-harvest drain; 1.1 d ramps |
| Fallow | days 113–365 (0.69 yr): *S*~top~ = 0.5, *z*~wt~ = 0.5 m, plants off |
| Tillage | the top 0.2 m is mixed before each season (`TILL=0.2`) |
| Irrigation and infiltrating water | Ca 0.5, Mg 0.2, Na 0.3, K 0.05, Si 0.2, SO~4~ 0.2, Cl 1.15 mM, NO~3~ 10⁻³ mM; alkalinity 0.2 meq L⁻¹, pH ≈ 7.6 |

Irrigated archetypes and the reference site use continuous flooding with the pre-harvest drain. Rainfed archetypes are not managed AWD: they use the same prescribed drain and reflood schedule (`--awd`) as a simple representation of intermittent flooding by rainfall. The schedule is not driven by site rainfall, so it is a stylised water regime rather than a simulation of rainfed hydrology. Where the main text compares AWD with continuous flooding, it refers to this prescribed schedule.

# A8 Soil, organic matter, rock and the simulation protocol

**Table A7.** Reference soil and inputs. Archetype values replace the soil entries (Sect. 4).

| Input | Setting |
|---|---|
| OM input | 450 g C m⁻² yr⁻¹; 70 % added during the season, 30 % in the fallow |
| OM placement (`--omalloc=0.2:0.6:0.1`) | 60 % as incorporated residue, uniform over 0–0.2 m; 40 % as root-derived C, exp(−*z*/0.1 m), normalised to the column |
| Reducible Fe(III) | ferrihydrite 0.012 wt fraction (`--fe3=0.012`); goethite 0.02 (`--gt=0.02`) |
| Fe(III) supply | 0.3 mol Fe m⁻² yr⁻¹ as ferrihydrite with the OM input, plough layer only (`--fe3in=0.3`) |
| Clay and silica | kaolinite 0.05 (`--kaol=0.05`); 1 wt % phytolith (amorphous) silica |
| Cation exchange | CEC 15 cmol~c~ kg⁻¹; SCEPTER log K: Na 5.9, K 4.8, Ca 10.47, Mg 10.786, Al 16.47; Fe²⁺ as Mg + 0.158 |
| Calcite | none in the reference soil (seeded in calcareous archetypes) |
| Basalt | applied over the first 0.01 yr of each season, mixed into 0–0.15 m; particle size distribution from Renforth (2012) scaled to P80 = 100 µm |
| Rock rate scaling (`--kscale`) | mafic minerals × 0.45, feldspar × 0.25, amorphous silica × 30 (calibrated against Uchibayashi et al., 2025) |
| Protocol | 3-yr drained spin-up without rock, then 7 yr of season + fallow without rock (settled state), then 10 yr of control and basalt chains (113-d season + 252-d fallow), rock applied at the start of every season |

# A9 Calibration and code versions

Table A8 lists the constants set by calibration and the target for each. All other constants are literature values or SCEPTER defaults. The constants differ in kind. Most are rate constants of mechanistic rate laws, tuned to bulk observations (emission factors, gas partitioning, pore-water chemistry). Three are empirical parameterisations with no independent mechanistic basis in the model: the Si root-O~2~ feedback, the rock rate scaling and the Fe(III) supply.

The Si feedback in particular is an empirical sensitivity parameterisation, not an independently validated physiological relationship. Its form (a saturating response of root O~2~ loss to pore-water Si) is motivated by observations of Si-enhanced root oxidising capacity (Fleck et al., 2011), but its strength *w* was fitted to a single field CH~4~ response (Gong et al., 2026). Because it controls much of the simulated CH~4~ suppression, results are reported with *w* = 0 (feedback off) alongside the central value (Sect. 4).

**Table A8.** Calibrated constants (file `paddy/krxn_calibrated_v22.in`).

| Constant | Value | Target |
|---|---|---|
| `g2ch4` v~max~ | 1860 yr⁻¹ | IPCC (2019) flooded-rice emission factor, 1.19 kg CH~4~ ha⁻¹ d⁻¹, on the settled reference cycle |
| `ch4pl` *k*~pl~ | 1100 yr⁻¹ | plant-mediated share of emission ~80–90 % |
| `ch4eb` *k* | 1000 yr⁻¹ | no post-harvest venting pulse; fallow CH~4~ ~10 % of the season |
| `g2n2p` v~max~, pH~50~ | 300 yr⁻¹, 5.5 | season N~2~O ~0.3–0.4 kg N~2~O-N ha⁻¹ with 120 kg N (Akiyama et al., 2005) |
| O~2~ inhibition *K*~i~ | 2.5 × 10⁻⁷ M | fallow N~2~O ~1 kg N ha⁻¹ yr⁻¹ |
| *P*~ox~ parameters | 0.3, 0.9, 6, 1 | rhizosphere oxidation 0.4–0.9 (literature range) |
| `rtco2` | 60 mol C m⁻² yr⁻¹ | pore-water *p*CO~2~ 0.1–0.3 atm, HCO~3~⁻ ~10–15 mM |
| Si feedback *K*~Si~, *w* (empirical) | 2 mM, 0.2 | fitted to the Gong et al. (2026) CH~4~ response; sensitivity *w* = 0–0.4 |
| Rock rate scaling (empirical) | Table A7 | Uchibayashi et al. (2025) Mg and Na fluxes |
| `fe3in` (empirical) | 0.3 mol Fe m⁻² yr⁻¹ | limit control-plot Fe depletion by leaching |

Code versions: v22 (commit 162913a) produced Figs. 4–8. v23 (commit 267a856) adds nine lines that return to CO~2~ the 4 % of decomposed OM carbon that upstream SCEPTER routes to oxalate and acetate, which are not tracked in the paddy runs. This closes the carbon budget (Fig. 3) and changes CH~4~, N~2~O and alkalinity export by less than 0.3 % and CO~2~ degassing by up to 1 % (irr061, year 1). The archived release contains both exact versions (source at commits 162913a and 267a856, with build instructions), the calibration file `krxn_calibrated_v22.in`, the option file `v22_options.env` used for every run, and the run and post-processing scripts, so each figure can be regenerated with the version that produced it.

# A10 Model input files and run switches

The Python driver (`paddy/run_flooded_column.py`) writes one SCEPTER input file per process. If a file is absent the process is off, so the upland SCEPTER configuration is unchanged.

**Table A9.** Input files written by the driver.

| File | Content |
|---|---|
| `frame.in` | column depth, grid, run time, percolation, particle radius |
| `switches.in` | solver and process switches |
| `slds.in`, `solutes.in`, `gases.in` | tracked solid, aqueous and gas species |
| `extrxns.in` | list of extra (non-mineral) reactions (Tables A1, A2, A4, A5) |
| `krxn_ext.in` | rate constants overriding code defaults (copy of `krxn_calibrated_v22.in`) |
| `2ndslds.in` | secondary minerals allowed to precipitate (`data/2ndslds_paddy.in`) |
| `precnucl.in` | nucleating phases and seeds (calcite 0.001 mol m⁻³) |
| `dust.in`, `psdrain.in` | rock mineralogy and particle size distribution |
| `OM_rain.in` | OM, urea and Fe(III) inputs |
| `fert_temp.in`, `plant_temp.in` | timing of fertiliser input and of the plant factor |
| `Wet_temp.in`, `T_temp.in`, `q_temp.in` | surface saturation, temperature and percolation time series |
| `floodwater.in` | floodwater gas-exchange velocity |
| `cec.in` | CEC and exchange constants |
| `kinscale.in` | mineral rate scaling |
| `pan.in` | plough pan and subsoil settings |
| `omalloc.in` | OM depth allocation |
| `pox.in`, `rtsi.in`, `n2oy.in`, `o2inh.in`, `n2c.in` | *P*~ox~, Si feedback, N~2~O yield, O~2~ inhibition and N:C parameters |

**Table A10.** Driver switches used in this paper and the files they set.

| Switch | Meaning | Files |
|---|---|---|
| `--ch4` | Fe, S and CH~4~ species and reactions | `slds/solutes/gases.in`, `extrxns.in`, `2ndslds.in` |
| `--n` | N species and reactions; with `--nfert`, urea | `solutes/gases.in`, `extrxns.in`, `OM_rain.in`, `fert_temp.in` |
| `--season`, `--fallow` | season or fallow phase (plants on or off) | `Wet_temp.in`, `plant_temp.in` |
| `--awd`, `--phd=14` | AWD cycles; pre-harvest drain 14 d | `Wet_temp.in` |
| `--basalt=<t ha⁻¹>`, `--rock=<name>`, `--psd=<file>` | rock dose, mineralogy and size distribution | `dust.in`, `psdrain.in` |
| `--refsoil`, `--fe3`, `--gt`, `--kaol`, `--cec`, `--soilcc` | reference soil and its Fe, clay, CEC and calcite | `slds.in`, `cec.in`, `solutes.in` |
| `--om`, `--omalloc`, `--fe3in`, `--n2c` | OM input, depth allocation, Fe(III) supply, N:C | `OM_rain.in`, `omalloc.in`, `n2c.in` |
| `--q`, `--nz`, `--ztot`, `--pan` | percolation, grid, column depth, plough pan | `frame.in`, `q_temp.in`, `pan.in` |
| `--temp` | soil temperature | `T_temp.in` |
| `--kscale` | mineral rate scaling | `kinscale.in` |
| `--k` | calibrated rate constants | `krxn_ext.in` |
| `--nucl` | nucleation seeds | `precnucl.in` |
| `--pox`, `--rtsi`, `--n2oy`, `--o2inh` | *P*~ox~, Si feedback, N~2~O yield, O~2~ inhibition | `pox.in`, `rtsi.in`, `n2oy.in`, `o2inh.in` |
| `--rstrt=<run>` | start from the end state of another run | (restart files) |

The full option strings for the spin-up and production runs are in `stanage_handoff/v22_options.env` in the code release.
