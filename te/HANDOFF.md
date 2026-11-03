# SCEPTER-TE handoff (3 Nov 2026)

Goal (David): short paper on trace-element (Ni, Cr, Cu, Zn, Cd, Pb) build-up under basalt
enhanced weathering in AERATED upland soils, as a mechanistic answer to Dupla et al. 2023
(EJSS 74:e13343). 3 temperate + 3 tropical soils, several basalts, 10-40 t/ha/yr, 10-40 yr.

Plan doc: https://claude.ai/artifact/4V212c94Do8WZqrCrWxDZ9

Design: one-way coupled TE module inside upstream (cropland) SCEPTER, called after each
converged time step (metals too dilute to feed back on pH/majors). Processes: host-mineral
release, aqueous speciation, exchange, DLM surface complexation on Fe oxides, humic binding,
solubility caps, Cr redox (Mn oxides), plant uptake. Prototype chemistry in Python vs PHREEQC first.

Status:
- Build: apt-get install gfortran libopenblas-dev; make --file=makefile_gmd24 -> scepter_gmd24.
  pip install scipy pandas matplotlib phreeqpython.
- te/upland.py: spin-up (inert + g2 OM + CEC, Ca rain sets pH; 10 kyr, w=1e-3, ~25 s) and
  amend() (restart, Hillhouse la/agt/fo/anl as dust, tilling mix, 2 yr ~40 s).
  Porewater pH vs Ca rain (10 C, q 0.25 m/yr, CEC 12, no N): 5e-6 -> 5.5, 1e-4 -> 6.4, 5e-4 -> 7.4.
  N fertiliser (NH4NO3) without base drives pH to 2.4: needs liming or skip N.
- Gotchas: rstrt must be an absolute path; every aq species needs a nonzero rain conc
  (1e-20; Fe3+ 1e-21) or the run goes NaN; cec.in needs 5 logK values + beta.
