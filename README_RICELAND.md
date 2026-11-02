# Riceland SCEPTER v1.0

Riceland SCEPTER is a one-dimensional reactive-transport model of flooded rice soils for studying enhanced weathering. It extends SCEPTER v1.0 (Kanzaki et al., 2022, 2024) with:

- kinetic microbial redox reactions;
- Fe and S cycling;
- CH₄ and N₂O production and transport;
- rice root terms;
- a plough pan;
- flooding, drainage and fallow schedules.

It simulates how basalt application changes CH₄, N₂O and inorganic carbon over multi-year season and fallow chains.

The full user manual is `paddy/docs/USER_MANUAL.md`. Rate laws and parameters are in Appendix A of the GMD paper.

## Quick start

```bash
sudo apt-get install gfortran libopenblas-dev
python3 -m pip install --user numpy scipy pandas matplotlib
make --file=makefile_paddy PROGRAM=scepter_paddy_v23 OBJS=scepter_paddy_v23.o

export SCEPTER_OUT=$PWD/scepter_output/
source stanage_handoff/v22_options.env
export EXE=scepter_paddy_v23; export SOIL=${SOIL//scepter_paddy_v22/$EXE}; export PROD=${PROD//scepter_paddy_v22/$EXE}

python3 paddy/run_flooded_column.py gs_ref fe2o2,amo2o 3 --fallow --basalt=0 $SOIL $P21       # spin-up, ~3 min
paddy/multiyear/run_chain.sh st_ref 7 0 gs_ref status.txt $PROD $P21                          # settle, ~35 min
cp -a $SCEPTER_OUT/paddy/flood_st_ref_y7f $SCEPTER_OUT/paddy/flood_s0
cp -a $SCEPTER_OUT/paddy/flood_st_ref_y7f $SCEPTER_OUT/paddy/flood_s20
paddy/multiyear/run_chain.sh ref_0 1 0 s0 status.txt $PROD $P21 &                              # control
paddy/multiyear/run_chain.sh ref_20 1 20 s20 status.txt $PROD $P21 & wait                      # 20 t/ha basalt
python3 paddy/ghg_budget.py $SCEPTER_OUT/paddy/flood_ref_0_y1s $SCEPTER_OUT/paddy/flood_ref_20_y1s
```

Expected year-1 season result (v23, checked by running these commands as written): CH₄ about 131 kg ha⁻¹ (control) and 73 kg ha⁻¹ (20 t ha⁻¹), with a net change of about −2.1 t CO₂e ha⁻¹.

## Versions

- **v22** (commit 162913a) was used for the GMD results.
- **v23** (commit 267a856) is v22 plus a carbon-closure fix. It changes year-1 CH₄, N₂O and alkalinity by less than 0.3 %.
- The calibration file `paddy/krxn_calibrated_v22.in` and the options in `stanage_handoff/v22_options.env` are the same for both.

## Important caveats

- The Si root-O₂ feedback (`--rtsi`, w = 0.2) is empirical. Always also run w = 0.
- Hydrology is prescribed. The `--awd` schedule is not driven by rainfall.
- Compare treatments only with year-matched controls started from the same settled state.

## Licence and citation

GPL-3.0. Cite the Riceland SCEPTER GMD paper (in preparation), the code release (Zenodo DOI to be added), and Kanzaki et al. (2022, 2024).
