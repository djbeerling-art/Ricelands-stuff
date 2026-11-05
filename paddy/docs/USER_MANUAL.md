---
title: "Riceland SCEPTER v1.0: user manual"
subtitle: "Reactive-transport model of flooded rice soils for enhanced weathering, methane and nitrous oxide"
date: "31 October 2026 (model versions v22 and v23)"
---

# 1 Overview, scope and limitations

## 1.1 What the model does

Riceland SCEPTER extends SCEPTER v1.0 (Kanzaki et al., 2022, 2024), a one-dimensional soil reactive-transport model written in Fortran 90 with Python drivers, to flooded rice paddies. It simulates a vertical soil column through repeated rice seasons and fallows. In each time step it solves, with an implicit Newton method:

- transport of solids, solutes and gases (advection, diffusion and dispersion);
- mineral dissolution and precipitation, including crushed basalt;
- cation exchange and pH from charge balance;
- the paddy extensions added in this version:
  - kinetic microbial redox reactions: aerobic respiration, denitrification, Fe(III) reduction, sulfate reduction, methanogenesis and CH₄ oxidation;
  - Fe phases: ferrihydrite, goethite, green rust, siderite and FeS;
  - an N cycle with urea, nitrification, pH-dependent N₂O yield and N₂O reduction;
  - CH₄ and N₂O exits by plant transport (with rhizosphere oxidation), ebullition and floodwater exchange;
  - rice root respiration, radial O₂ loss, N and Si uptake;
  - a plough pan and a partly saturated subsoil;
  - prescribed flooding, drainage and fallow schedules.

Its main outputs are season and fallow fluxes of CH₄, N₂O and CO₂, alkalinity leached from the column base, soil carbonate, cations released by rock weathering, and depth profiles of every species. Post-processing scripts turn these into greenhouse-gas and carbon-removal budgets of a basalt treatment against a year-matched control.

Rate laws, stoichiometry and parameter values are in Appendix A of the GMD paper (`manuscript_gmd/appendixA_2026-10-31.md`) and in `paddy/docs/riceland_process_spec.md`.

## 1.2 Intended use

- Site-scale experiments on how basalt application changes CH₄, N₂O and inorganic carbon in paddy soils.
- Comparison of continuous flooding with a prescribed intermittent-flooding (AWD-type) schedule.
- Multi-year control–treatment chains of 10 years or more.
- Building blocks for regional runs over soil–climate archetypes.

## 1.3 Limitations

Read these before interpreting results:

- **One dimension, prescribed hydrology.** Water saturation, the water table and percolation are imposed, not solved. Rainfall, runoff, lateral flow and irrigation decisions are not simulated.
- **The Si root-O₂ feedback is empirical.** Its strength `w` was fitted to one field result (Gong et al., 2026). It controls much of the simulated CH₄ suppression. Always report results with `w = 0` (feedback off) alongside the central value.
- **Plants are not simulated dynamically.** Root respiration, O₂ loss and N and Si uptake follow a fixed root profile and are on in the season and off in the fallow. There is no crop growth or yield.
- **No methanogen pH response** in the production configuration. The optional `--ch4ph` response gave CH₄ rises with basalt that contradict field trials.
- **Control-plot drift.** Reducible Fe(III) is slowly lost from the plough layer, so control CH₄ rises by about 5 % per year at the reference site. Always compare treatment and control year by year.
- **Known misfits:**
  - Mg release from olivine is about twice the Uchibayashi et al. (2025) observation.
  - Topsoil carbonate gain is underpredicted 2.5–4× against Wang et al. (2024).
  - The field Fe(III) gain under steel slag is not reproduced.
- **Carbon accounting.** Exported alkalinity and soil calcite are model accounting terms, not verified durable carbon removal. Retained cations are a potential that depends on later transport and reaction pathways.
- Mn cycling, microbial community change, multiple cropping and NH₃ volatilisation are not represented.

# 2 System requirements and installation

| Component | Tested version | Notes |
|---|---|---|
| Operating system | Ubuntu 24.04 (cloud container); Rocky Linux (Sheffield Stanage HPC) | any Linux or macOS with gfortran should work |
| Fortran compiler | GNU Fortran 13.3 | Intel `ifort` is supported by the makefiles but untested for the paddy build |
| BLAS/LAPACK | OpenBLAS 0.3 | linked as `-lopenblas` |
| Python | 3.11–3.13 | |
| Python packages | numpy, scipy, pandas, matplotlib | run, budgets and figures |
| Optional | phreeqpython | verification against PHREEQC |
| Optional | scikit-learn, SALib | archetype clustering and the Morris screen |

Installation on Ubuntu:

```bash
sudo apt-get install gfortran libopenblas-dev git python3-pip
git clone https://github.com/djbeerling-art/Ricelands-stuff.git
cd SCEPTER
git checkout claude/project-thread-pip6bj-pan     # or the archived release tag
python3 -m pip install --user numpy scipy pandas matplotlib phreeqpython
```

On an HPC system, load the compiler and OpenBLAS modules instead. For example, on Stanage: `module load GCC/12.3.0 OpenBLAS/0.3.23-GCC-12.3.0`. `stanage_handoff/slurm/build.sh` is a working example.

Disk: an unpruned season run is about 50 MB and a pruned year about 30 MB. A 10-year chain at three doses needs about 1 GB.

# 3 Compilation

All commands are run from the repository root.

```bash
# frozen production build used in the GMD paper (v22: commit 162913a; v23: commit 267a856)
make --file=makefile_paddy PROGRAM=scepter_paddy_v23 OBJS=scepter_paddy_v23.o
```

- `makefile_paddy` sets the paddy preprocessor flags: banded Jacobian solve, speciation cache and basalt composition.
- `makefile_paddy_fast` is the same without run-time bounds checks (`-fcheck=all`) and with `-march=native`. It is faster, but use `makefile_paddy` when debugging.
- The executable name is passed to the driver with `--exe=<name>`. It must be in the repository root.

To build an exact older version:

```bash
git show 162913a:scepter.f90 > scepter.f90.v22
cp scepter.f90 scepter.f90.head && cp scepter.f90.v22 scepter.f90
make --file=makefile_paddy PROGRAM=scepter_paddy_v22 OBJS=scepter_paddy_v22.o
mv scepter.f90.head scepter.f90
```

**Confirming the build.** The build has succeeded when:

1. `make` ends without errors and an executable `scepter_paddy_v23` (about 3–4 MB) appears in the root;
2. the smoke test in Sect. 5.2 runs to completion and writes `run_complete.txt` in its run directory;
3. the PHREEQC example 11 benchmark (Sect. 9.1) reproduces PHREEQC within 0.02 mM.

Do not use the plain `makefile`. It builds the upland configuration, which has a constant-diffusivity flag that the paddy runs must not use.

# 4 Directory structure, inputs, units and switches

## 4.1 Repository layout (paddy-relevant parts)

| Path | Content |
|---|---|
| `scepter.f90` | model source (single file; paddy code is in the extra-reaction routines and the `*_f()` input readers) |
| `makefile_paddy`, `makefile_paddy_fast` | builds |
| `spinup.py` | upstream SCEPTER helper that writes input files and launches a run |
| `paddy/run_flooded_column.py` | **paddy driver**: one run (one season, one fallow or a spin-up) |
| `paddy/multiyear/run_chain.sh` | multi-year chains of season + fallow restarts |
| `paddy/multiyear/till.py` | puddling/tillage: mixes the plough layer between years |
| `paddy/krxn_calibrated_v22.in` | calibrated rate constants (used by v22 and v23) |
| `paddy/ghg_budget.py` | greenhouse-gas and carbon budget of runs against a control |
| `paddy/v22/annual22.py` | year-by-year diagnostics of a chain against its control |
| `paddy/prune_run.sh` | shrinks finished runs to what budgets or restarts need |
| `paddy/verification/` | PHREEQC re-speciation, mass balance and Fig. 3 scripts |
| `paddy/compare_ex11_phreeqc.py` | PHREEQC example 11 comparison |
| `paddy/screen/` | Morris sensitivity screen |
| `paddy/global/` | archetype construction (regional runs; not used in the GMD paper) |
| `data/` | rock recipes (`dust_*.in`), particle-size distributions (`psdrain_*.in`), secondary-mineral lists (`2ndslds_paddy.in`), thermodynamic data |
| `stanage_handoff/v22_options.env` | exact option strings used for every production run |
| `paddy/docs/` | this manual and the process specification |

## 4.2 Output location

Runs are written to `$SCEPTER_OUT/paddy/flood_<tag>/` (default `./scepter_output/`). Each run directory holds:

- the input files the driver wrote (Sect. 4.4);
- `flx/`: time series of fluxes by process for every species (`flx_gas-pch4.txt`, `flx_aq-ca.txt` …), in mol m⁻² yr⁻¹, plus integrated forms `int_flx_*`;
- `prof/`: depth profiles at the output times (`prof_sld-NNN.txt`, `prof_aq-NNN.txt` …), which also form the restart state;
- `run_complete.txt`, written at a normal finish.

In the `flx` files the first column is time (yr) and the remaining columns are named processes. For gases, `adv` is leaching through the base and `dif` is the surface exchange. Rows are interval averages, so integrate them as a sum of rate × Δt.

## 4.3 Units

| Quantity | Unit |
|---|---|
| Time | yr (season 0.31 yr = 113 d; fallow 0.69 yr = 252 d) |
| Depth | m |
| Solids | mol m⁻³ bulk soil |
| Solutes | mol L⁻¹ pore water |
| Gases | atm |
| Reaction rates | mol m⁻³ yr⁻¹ |
| Plant fluxes, OM input | mol m⁻² yr⁻¹; OM in g C m⁻² yr⁻¹ |
| Rock dose | t ha⁻¹ (per application) |
| Budgets | CH₄ kg ha⁻¹, N₂O kg N ha⁻¹, carbon terms t CO₂ ha⁻¹, net t CO₂e ha⁻¹ (GWP100: CH₄ 27, N₂O 273) |

## 4.4 How switches work

The driver turns each option into one small input file in the run directory. The Fortran code reads the file if it exists and leaves the process off if it does not, so the upland SCEPTER configuration is unchanged when no paddy file is present. The reactions themselves are switched on by listing them in the second positional argument (written to `extrxns.in`).

**Positional arguments:** `python3 paddy/run_flooded_column.py <tag> <reaction list | none> [run length, yr] [options]`

Reaction lists used in production (set inside `run_chain.sh`):

- **Season:** `fe2o2,g2fe3,g2gr,g2so4,g2ch4,ch4o2,fe2gr,ch4pl,ch4eb,fe2fs,fesox,amo2o,g2n21,g2n2p,n2opl,g2gt,rtco2,g2o2,nh4up,rtoxy,groxy,siup,sidox`
- **Fallow:** the same without the plant terms `ch4pl`, `n2opl`, `rtco2`, `nh4up`, `rtoxy`, `siup`.
- **Spin-up:** `fe2o2,amo2o`.

The driver adds `g2n0` automatically with `--n2oy` and `ch4rx` with `--pox`.

**Table 1.** Main driver options. The full list with defaults is in the header of `paddy/run_flooded_column.py`.

| Option | Meaning | File written |
|---|---|---|
| `--ch4`, `--n` | Fe–S–CH₄ and N species and secondary phases | `slds/solutes/gases.in`, `2ndslds.in` |
| `--season`, `--fallow` | flooded season (plants on) or drained fallow (S_top 0.5, water table 0.5 m) | `Wet_temp.in`, `plant_temp.in` |
| `--awd`, `--zdry`, `--sdry` | intermittent-flooding schedule; drain depth (0.15 m) and surface saturation (0.6) | `Wet_temp.in` |
| `--phd=<d>` | pre-harvest drain of `d` days | `Wet_temp.in` |
| `--nfert=<kg N/ha>` | urea through the season | `OM_rain.in`, `fert_temp.in` |
| `--basalt=<t/ha>` | rock dose over the first 0.01 yr, mixed into `--zmix` (0.15 m) | `dust.in` |
| `--rock=<name>` | rock recipe `data/dust_<name>.in` (default basalt) | `dust.in` |
| `--psd=<file>` | rock particle-size distribution | `psdrain.in` |
| `--basfe3`, `--basmgn` | Fe(III) oxide or magnetite in the rock (wt fraction) | `dust.in` |
| `--kscale=maf:x,fsp:y,amsi:z` | rate multipliers: mafic minerals, feldspars, amorphous silica | `kinscale.in` |
| `--refsoil` | reference soil: CEC 15, 1 % phytolith silica, river-type irrigation water | several |
| `--fe3`, `--gt`, `--kaol`, `--cec`, `--soilcc` | soil ferrihydrite, goethite, kaolinite (wt fraction), CEC (cmol kg⁻¹), calcite | `slds.in`, `cec.in` |
| `--irralk` | alkalinity of the irrigation water (factor on 0.2 meq L⁻¹) | `solutes.in` |
| `--om`, `--omalloc=zres:fres:zroot` | OM input and its depth allocation | `OM_rain.in`, `omalloc.in` |
| `--fe3in=<mol/m²/yr>` | Fe(III) supply with the OM input | `OM_rain.in` |
| `--n2c`, `--n2oy`, `--o2inh` | N:C of OM, N₂O yield, O₂ inhibition constant | `n2c.in`, `n2oy.in`, `o2inh.in` |
| `--pox=pmin:pmax:pH50:n` | rhizosphere CH₄ oxidation | `pox.in` |
| `--rtsi=K_Si:Si_ref:w` | Si root-O₂ feedback (`w = 0` off) | `rtsi.in` |
| `--k=<file>` | rate-constant overrides (`name krxn1 krxn2`, −999 keeps default) | `krxn_ext.in` |
| `--nucl=<solid>:<seed>` | nucleation seed (production: `cc:0.001`) | `precnucl.in` |
| `--q`, `--nz`, `--ztot`, `--pan` | percolation (m yr⁻¹), cells, column depth, plough pan | `frame.in`, `q_temp.in`, `pan.in` |
| `--temp` | soil temperature (°C) | `T_temp.in` |
| `--rstrt=<tag>` | start from the end of run `flood_<tag>` | — |
| `--exe=<name>` | executable | — |
| `--nstep` | number of output records per run | `frame.in` |

## 4.5 Production option set

All GMD runs used the strings in `stanage_handoff/v22_options.env`. Source the file from the repository root:

```bash
source stanage_handoff/v22_options.env      # sets TILL, EXE, SOIL, PROD, P21
export EXE=scepter_paddy_v23                  # to use v23
export SOIL=${SOIL//scepter_paddy_v22/$EXE}; export PROD=${PROD//scepter_paddy_v22/$EXE}
```

- `SOIL`: soil options for the drained spin-up.
- `PROD`: season and fallow options, including `--k=paddy/krxn_calibrated_v22.in`, `--phd=14`, `--pox=0.3:0.9:6:1` and `--rtsi=2e-3:2.7e-4:0.2`.
- `P21`: the 0.5 m, 25-cell column with plough pan, `--nz=25 --ztot=0.5 --pan=0.2:0.24:0.1:0.8:1:0.1:0.21:-1:0.3`.
- `TILL=0.2`: tillage depth (m).

Later options override earlier ones, so a site option such as `--temp=28` or `--rtsi=2e-3:2.7e-4:0` can be appended after `$PROD $P21`.

# 5 Worked example: the reference paddy

## 5.1 Protocol

The model starts with no organic matter and needs several years before its OM, Fe and carbonate pools settle. The standard protocol is:

1. a 3-yr drained spin-up without rock;
2. a 7-yr settle of season + fallow years without rock;
3. control and treatment chains from the same settled state, compared year by year.

```bash
cd SCEPTER
export SCEPTER_OUT=$PWD/scepter_output/
source stanage_handoff/v22_options.env
ST=status_ref.txt

# 1. drained spin-up, 3 yr (~3 min)
python3 paddy/run_flooded_column.py gs_ref fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $P21
echo "gs_ref rc $?" >> $ST

# 2. settle: 7 years of season + fallow without rock (~35 min)
paddy/multiyear/run_chain.sh st_ref 7 0 gs_ref $ST $PROD $P21

# 3. control and 20 t/ha/yr treatment, 10 years each, from the settled state
for d in 0 20; do
  cp -a $SCEPTER_OUT/paddy/flood_st_ref_y7f $SCEPTER_OUT/paddy/flood_start_ref_$d
  paddy/multiyear/run_chain.sh ref_$d 10 $d start_ref_$d $ST $PROD $P21 &
done; wait
```

The chain copies the settled state for each dose so that tillage between years acts on separate copies. Each chain line in `$ST` reads `<tag> rc 0` when a phase finished. Rerunning the same command resumes after the last finished phase.

Run time on one core: about 1.5 h for a 10-yr control and about 3.5 h at 20 t ha⁻¹ yr⁻¹, because basalt years slow down after year 5.

## 5.2 Smoke test (about 10 min)

For a quick installation check, run steps 1 and 2 with one settle year:

```bash
paddy/multiyear/run_chain.sh st_ref 1 0 gs_ref $ST $PROD $P21
ls $SCEPTER_OUT/paddy/flood_st_ref_y1s/run_complete.txt
```

## 5.3 Budgets and expected output

```bash
python3 paddy/ghg_budget.py $SCEPTER_OUT/paddy/flood_ref_0_y1s $SCEPTER_OUT/paddy/flood_ref_20_y1s
python3 paddy/v22/annual22.py $SCEPTER_OUT/paddy ref_0 ref_20 st_ref_y7f
```

`ghg_budget.py` gives season totals. `annual22.py` gives yearly CH₄ production, oxidation and emission, Fe(III) reduction, plough-layer Fe(III) and cation fluxes for a chain against its control.

Expected year-1 season values for the reference site (v23, from running the quick start in Sect. 3 verbatim on 31 Oct 2026; v22 differs by < 2 %; 25 °C, continuous flooding with a 14-day pre-harvest drain, 120 kg urea-N ha⁻¹):

| Quantity | Control | 20 t ha⁻¹ basalt |
|---|---|---|
| CH₄ emission (kg ha⁻¹) | 131 | 73 |
| N₂O emission (kg N ha⁻¹) | 0.32 | 0.29 |
| Carbonate alkalinity export (t CO₂ ha⁻¹) | 0.31 | 0.30 |
| Calcite (t CO₂ ha⁻¹) | −0.01 | 0.57 |
| Cation release (t CO₂ ha⁻¹, potential) | 0 | 4.1 |
| Net change, season only (t CO₂e ha⁻¹) | — | −2.12 (realised), −5.65 (potential) |

Your numbers should agree to within about 1 % with v22. v23 differs from v22 by less than 0.3 % for CH₄ and N₂O and up to 1 % for CO₂ degassing. Over 10 years (season + fallow) the reference-site net change is about −50 t CO₂e ha⁻¹ at 20 t ha⁻¹ yr⁻¹, and control CH₄ rises from 130 to about 214 kg ha⁻¹.

# 6 Continuous flooding versus prescribed intermittent flooding

The water regime is a prescribed surface saturation S_top(t) and water-table depth z_wt(t). In each cell, S_w(z) = min[1, S_top + (1 − S_top) z/z_wt].

| Regime | Options | Schedule |
|---|---|---|
| Continuous flooding | `--season --phd=14` (the `PROD` default) | flooded days 0–99, then a 14-day drain to S_top 0.6, z_wt 0.15 m |
| Intermittent flooding (AWD-type) | add `--awd` | flooded days 0–29; then 7.3-d drains (S_top 0.6, z_wt 0.15 m) alternating with 14.6-d reflooding until the pre-harvest drain; 1.1-d ramps |
| Deeper drains | add `--zdry=0.3 --sdry=0.5` | as above, with drain depth and surface saturation changed |
| Fallow | set by `run_chain.sh` (`--fallow`) | S_top 0.5, z_wt 0.5 m, plants off |

Append `--awd` to the chain options:

```bash
paddy/multiyear/run_chain.sh awd_0 10 0 start_awd_0 $ST $PROD $P21 --awd
```

`run_chain.sh` removes `--awd` and `--phd` from the fallow automatically.

The same `--awd` schedule is managed AWD for irrigated paddies and a stylised proxy for rain-driven wetting and drying in rainfed paddies. It is not driven by rainfall. Compare regimes against controls that run the same regime.

# 7 Basalt, mineral composition, Fe supply and the Si feedback

## 7.1 Rock dose and timing

`run_chain.sh <name> <years> <dose>` applies `<dose>` t ha⁻¹ at the start of every season. Inside the chain the rock gets `--psd=data/psdrain_renforth_p80-100um.in`, the Renforth (2012) size distribution scaled to P80 = 100 µm. For one season use `--basalt=<t/ha>`, with `--zmix` setting the mixing depth (0.15 m). Controls must use `--basalt=0`, not omit it. This keeps the same Si and Al species tracked, which the restarts need.

## 7.2 Mineral composition

- `--rock=<name>` reads `data/dust_<name>.in`. Examples: `Hillhouse`, `Oregon`, `Tichum` and `GongXuyi` (basalts), `WangSlag` (steel slag), `WangWls` (wollastonite) and `glb00`–`glb11` (global basalt groups).
- Each recipe lists mineral codes and weight fractions. An `inrt` entry keeps an unreactive fraction (glass, clays) in the dose.
- To build a recipe from whole-rock oxides, use `paddy/global/basalt_norm.py`.
- Rock Fe(III) can be added as ferrihydrite with `--basfe3=<wt fraction>`.
- `--kscale=maf:0.45,fsp:0.25,amsi:30` scales the dissolution rates of mafic minerals, feldspars and soil amorphous silica. These are the calibrated values against Uchibayashi et al. (2025).

## 7.3 Fe(III) supply

`--fe3in=0.3` adds 0.3 mol Fe m⁻² yr⁻¹ of ferrihydrite to the plough layer with the OM input, standing in for irrigation sediment and soil-mineral weathering. With `--fe3in=0` the control plough layer loses Fe(III) faster and control CH₄ rises about 2 % per year more. The soil's initial Fe is set with `--fe3` (ferrihydrite, wt fraction) and `--gt` (goethite).

## 7.4 Si root-O₂ feedback

`--rtsi=K_Si:Si_ref:w` scales root O₂ loss by f_Si = 1 − w + w h(Si)/h(Si_ref), with h(Si) = Si/(Si + K_Si). The production value is `--rtsi=2e-3:2.7e-4:0.2`. This term is empirical, so run every analysis at least with `w = 0` as well:

```bash
paddy/multiyear/run_chain.sh ref_w0_20 10 20 start_w0_20 $ST $PROD $P21 --rtsi=2e-3:2.7e-4:0
```

The control for a `w` test must use the same `w`. At the reference site the 10-yr net change at 20 t ha⁻¹ yr⁻¹ is −38 (w = 0), −50 (w = 0.2) and −59 (w = 0.4) t CO₂e ha⁻¹.

# 8 Seasonal restarts and ten-year chains

**Year structure.** Each model year in `run_chain.sh` has three steps:

1. **Tillage.** `till.py` mixes the soil solids over the top `TILL` metres of the previous fallow's restart state.
2. **Season.** A 0.31-yr run with the season reaction list, urea (`--nfert=120`), rock if the dose is above 0, and the OM input share `OMF` (default 0.7) converted to a seasonal rate.
3. **Fallow.** A 0.69-yr drained run without plant terms, carrying the remaining OM.

The tags are `<name>_y<n>s` and `<name>_y<n>f`. Each phase restarts from the previous one with `--rstrt`.

**Checks.** After each phase the chain checks that `flx_gas-pch4.txt` reaches the full phase length. A run that stops early (for example on a full disk) is marked `rc 98`, and the chain stops.

**Pruning.** The chain prunes as it goes. It keeps the budget files of every season and the profiles of the latest fallow, which is the next restart state. Set `KEEPALK=1` to keep porewater and solid profiles for alkalinity diagnostics.

**Control–treatment design.**

- Start the control and every treatment from copies of the same settled state.
- Run them for the same number of years, with identical options apart from the dose (and `w` if testing it).
- Compute treatment − control for each year, for the season and the fallow.
- Sum over years for cumulative budgets.

The fixed-year-1 diagnostic in the paper holds the year-1 CH₄ difference constant. It shows how much of the cumulative result depends on the control's drift.

**Environment variables.**

| Variable | Default | Meaning |
|---|---|---|
| `SCEPTER_OUT` | `./scepter_output/` | output root |
| `TILL` | 0.16 | tillage depth in m (0.2 in production) |
| `OMF` | 0.7 | share of annual OM added in the season |
| `FOPT` | (empty) | extra options for the fallow only, e.g. `"--temp=18"` |
| `KEEPALK` | (empty) | keep profiles for alkalinity diagnostics |

**Parallel runs.** Chains are independent, one core each, so run them in parallel (`&` with `wait`, `xargs -P`, or a Slurm array as in `stanage_handoff/slurm/arch_array.sbatch`). Do not use `nohup` in cloud containers that pause when idle, because the job is killed; use the scheduler or a tracked background job instead.

# 9 Verification tests, tolerances and troubleshooting

## 9.1 Verification tests

| Test | How | Expected (v23) |
|---|---|---|
| Cation exchange vs PHREEQC example 11 | `make --file=makefile_ex11`; run `test_phreeqc_ex11_init.py` then `test_phreeqc_ex11.py` (set `outdir_src` in both to your output path); `SCEPTER_OUT=<path> python3 paddy/compare_ex11_phreeqc.py` | outlet Na, K, Ca, Cl RMSE ≤ 0.02 mM |
| pH and saturation vs PHREEQC | `python3 paddy/verification/phreeqc_respeciate.py out.json <run>/prof:<index>:<tag> ...` on unpruned runs | pH within 0.04 for 175 porewaters; SI offsets in the ideal-solution model (calcite +0.14) explained by activity coefficients |
| Element budgets | `python3 paddy/verification/mass_balance.py out.json <run dir> ...` | C, Fe, N, Ca, Mg: reaction terms cancel to ≤ 5 × 10⁻¹¹ and storage matches inventories to ≤ 2 × 10⁻⁷ of the gross flux (v22: C residual 0.35 %) |
| Figure | `python3 paddy/verification/fig3_verification.py` | GMD Fig. 3 |
| Reference values | Sect. 5.3 | within ~1 % of the table |

Runs for the pH and mass-balance tests must keep their `prof/` and `flx/` files. Run one year with `run_chain.sh` and then copy the directories before the chain prunes them, or call `run_flooded_column.py` directly.

## 9.2 Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Chain stops with `rc 98` | phase ended before its full length, usually a full disk: free space (`paddy/prune_run.sh`), delete the incomplete phase directory and its status line, rerun |
| Run exits 0 but budgets are short | as above: the flux file ends early; `ghg_budget.py` prints a WARNING with the end day |
| CH₄ about half the expected value in a control | control run without `--basalt=0` (Si and Al species not tracked) |
| Restart fails or gives odd profiles | restart taken from a run with a different `--nz`/`--ztot`, or its `prof/` was pruned; restarts need the full `prof/` of the previous phase |
| pH above 9 in flooded soil | green-rust reaction `fe2gr` missing from the reaction list, or `--ch4` not set |
| Late options ignored | options are read left to right and the last one wins: check you did not repeat `--om=` or `--rtsi=` |
| Very slow basalt years | expected after year 5 at high doses (~25 min per year); use `makefile_paddy_fast` |
| Solver stalls at a phase change | try a different `--nstep`; a stalled phase can usually be rerun with a slightly different nucleation seed (`--nucl=cc:0.0011`) |
| Need to change a rate constant | copy `paddy/krxn_calibrated_v22.in`, edit the line (`name krxn1 krxn2`; −999 keeps the default) and pass `--k=<file>`; no recompilation needed |

# 10 Version history, known limitations and citation

## 10.1 Versions

| Version | Commit | Change |
|---|---|---|
| SCEPTER v1.0 | upstream (cdr-laboratory/SCEPTER) | upland model with soil pH and cation exchange (Kanzaki et al., 2024) |
| paddy v1–v16 | branch `paddy/fe3-reduction` | development of the paddy modules and their calibration |
| v17–v21 | branch `claude/project-thread-pip6bj-pan` | plough pan and subsoil, OM allocation, Fe(III) supply, budget and solver fixes |
| **v22** | **162913a** | frozen production version: all GMD figures except Fig. 3 |
| **v23** | **267a856** | v22 plus a 9-line fix that returns the 4 % of decomposed OM carbon routed to untracked oxalate and acetate to CO₂, closing the carbon budget; same options and calibration file; year-1 CH₄, N₂O and alkalinity changes < 0.3 % |

The archived release (Zenodo DOI to be added) contains both versions, `paddy/krxn_calibrated_v22.in`, `stanage_handoff/v22_options.env` and all run and post-processing scripts.

## 10.2 Known limitations

See Sect. 1.3. The most important are:
- the empirical Si feedback;
- the control-plot Fe(III) drift;
- the prescribed hydrology;
- the Mg and carbonate misfits;
- the absence of dynamic plant growth.

## 10.3 How to cite

Cite the model description paper and the code release:

- Beerling, D. J., et al.: Riceland SCEPTER v1.0: a reactive-transport model of flooded rice paddies for enhanced weathering, methane and nitrous oxide, Geosci. Model Dev., in preparation, 2026.
- Riceland SCEPTER v1.0 code, Zenodo, https://doi.org/[to be added], 2026.

Also cite the SCEPTER papers it builds on:

- Kanzaki, Y., Zhang, S., Planavsky, N. J., and Reinhard, C. T.: Soil Cycles of Elements simulator for Predicting TERrestrial regulation of greenhouse gases: SCEPTER v0.9, Geosci. Model Dev., 15, 4959–4990, https://doi.org/10.5194/gmd-15-4959-2022, 2022.
- Kanzaki, Y., Chiaravalloti, I., Zhang, S., Planavsky, N. J., and Reinhard, C. T.: In silico calculation of soil pH by SCEPTER v1.0, Geosci. Model Dev., 17, 4515–4532, https://doi.org/10.5194/gmd-17-4515-2024, 2024.

The code is released under GPL-3.0, as is upstream SCEPTER.
