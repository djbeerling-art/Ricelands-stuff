# Tracked edits on David's Riceland_SCEPTER_GMD_Nov2.docx (2 Nov 2026): remaining v22/v24 items -> v25b
# (Morris screen, Fig. 7 structures, Fig. 2/4/5/6/7 captions, Fe redistribution, provenance) and a factual
# description of how the archetype basalt mineral compositions were derived (Appendix A8).
# Facts only; cyan = drafted interpretive text for David to reword (GMD AI policy); yellow = flag.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from tcedit import Doc
D=Doc(sys.argv[1],'2026-11-02T08:00:00Z'); r=D.rep
# ---- 2.3 methanogenesis formulation (Fe_pool unchanged in v25: goethite does not enter the inhibition term)
r('in the v22 calibration','in the v22 and v25b calibrations')
r('(v22 and v23)','(v22 to v25b)')
# ---- 4.2 Morris v25b
r('The v22 Morris screen (96 successful evaluations, 11 factors) identified ferrihydrite as the leading control on baseline CH₄, followed by temperature and organic matter input (Fig. 6a).',
  'The v25b Morris screen (104 evaluations, 12 factors: the v22 factors plus floodwater discharge, 100–400 mm per season) identified ferrihydrite (μ* 325 kg CH₄ ha⁻¹) and organic matter input (μ* 308 kg CH₄ ha⁻¹) as the leading controls on baseline CH₄, followed by temperature (μ* 67 kg CH₄ ha⁻¹) (Fig. 6a).')
r('One-year net GHG change is most sensitive to ferrihydrite availability,','One-year net GHG change is most sensitive to ferrihydrite availability (μ* 2.38 t CO₂e ha⁻¹), then organic matter input (2.22) and w (1.81),')
r('All 96 screened simulations reduced CH₄ (median −43%) and net GHG (median −0.93 t CO₂e ha⁻¹), but the sampled feedback strength was restricted to w = 0.1–0.4.',
  'CH₄ fell in 95 of 104 screened simulations (median −35%; range −89 to +31%) and one-year net GHG change was negative in 97 of 104 (median −0.80 t CO₂e ha⁻¹; range −5.9 to +1.6), with w sampled between 0 and 0.4. Floodwater discharge has μ* close to zero for all outputs; lateral export in this one-year screen is about 0.01 t CO₂ ha⁻¹.')
r(' The Morris screen was run with v22 and has not been repeated with v25b.','')
# ---- 4.2 alternative Si-root structures (Fig. 7 v25b; each structure against a control run with the same structure)
r('first-year CH₄ emission increased by 60 % relative to the matched control (216 vs 135 kg ha⁻¹), and by 73 % in year 3.',
  'first-year CH₄ emission increased by 59 % relative to the matched control (170 vs 107 kg ha⁻¹), and by 57 % in year 3 (172 vs 110 kg ha⁻¹).')
r('Plant-mediated emission fell from 120 to 67 kg ha⁻¹, but ebullition rose from 11 to 137 kg ha⁻¹ and floodwater diffusion from 4.5 to 12 kg ha⁻¹, so that about 2.5 kg CH₄',
  'Plant-mediated emission fell from 104 to 65 kg ha⁻¹, but ebullition rose from 2.8 to 104 kg ha⁻¹ and floodwater diffusion from 0.1 to 1.1 kg ha⁻¹, so that about 2.6 kg CH₄')
r('In year 10, ebullition was 207 kg ha⁻¹, against 33 kg ha⁻¹ in the control.',
  'In year 10, ebullition was 79 kg ha⁻¹, against 4 kg ha⁻¹ in the control, and total CH₄ emission was 6.7 % below the control (115 vs 124 kg ha⁻¹).')
D.flag('this structure did not reproduce the observed first-year decrease.','v25b: this structure falls below its control by year 10; check wording of the previous sentence')
r('Ten-year net realised GHG change was −3.2 t CO₂e ha⁻¹, compared with −50.0 t CO₂e ha⁻¹ for the O₂ structure (w = 0.2).',
  'Ten-year net realised GHG change was −14.5 t CO₂e ha⁻¹, compared with −40.1 t CO₂e ha⁻¹ for the O₂ structure (w = 0.15).')
r('(wr = 0.5) gave +30.0 t CO₂e ha⁻¹','(wr = 0.5) gave +1.1 t CO₂e ha⁻¹ (first-year CH₄ +162 %)',pre='as well ')
r('(wc = −0.2, w = 0.2), the direction reported by Tong et al. (2024), gave −52.3 t CO₂e ha⁻¹ with ebullition close to zero.',
  '(wc = −0.2, w = 0.15), the direction reported by Tong et al. (2024), gave −40.5 t CO₂e ha⁻¹ (first-year CH₄ −28 %, against −29 % for the O₂ structure).')
r('Alkalinity export (7.3 t CO₂ ha⁻¹) and carbonate accumulation (15 t CO₂ ha⁻¹) were identical across the four structures (Fig. 7).',
  'Cumulative PDA export (9.2–9.6 t CO₂ ha⁻¹) and calcite (14.2–14.4 t CO₂ ha⁻¹) were almost identical across the four structures (Fig. 7).')
r(' These four simulations are historical structural sensitivity tests run with v24 (v22 calibration, w = 0.2) and have not been rerun with v25b, so their absolute values are not comparable with the v25b results in Sects. 4.2–4.3.','')
r('(−52.3 vs −50.0 t CO₂e ha⁻¹)','(−40.5 vs −40.1 t CO₂e ha⁻¹)')
# ---- 5.2 Fe redistribution (v25b reference control, years 0-10, paddy/v25/results/fe_inventory.csv)
r('approximately 1.1 mol m⁻² yr⁻¹ [v22 values in this paragraph; v25b ref control plough layer: ferrihydrite −0.54 and goethite −0.91 mol m⁻² yr⁻¹]',
  'approximately 1.45 mol m⁻² yr⁻¹ (ferrihydrite 0.54, goethite 0.91 mol m⁻² yr⁻¹; the subsoil gains 1.45 mol m⁻² yr⁻¹)')
r('approximately 3.3% yr⁻¹','approximately 1.7% yr⁻¹')
# ---- Table 2 caption -> derivation of the basalt groups
D.ins_after('each archetype uses the group of its nearest basalt outcrops.',' The derivation of the group mineral compositions is described in Appendix A8.')
# ---- Appendix intro, A9 code versions, code availability
r(', v24 (commit f2d2aa8) for the alternative Si–root structures in Fig. 7, and v22 (commit 162913a) for the Morris screen in Fig. 6a.','.')
r('produced Figs. 4, 5, 6b, 8 and 9; v22 (commit 162913a) produced the Morris screen in Fig. 6a.','produced Figs. 4–9, including the Morris screen (Fig. 6a) and the alternative Si–root structures (Fig. 7).')
r('which is used only for Fig. 7 and is off in all other runs.','which is carried into v25 and used only for Fig. 7; it is off in all other runs.')
r(' The Morris screen (Fig. 6a) used the v22 executable, commit 162913a.','')
r('Fig. 7 used scepter_paddy_v24 (commit f2d2aa8), which adds the alternative Si–root-barrier option --ch4si to v23; the option is off in all other runs.',
  'The alternative Si–root-barrier option --ch4si used in Fig. 7 was added in v24 (commit f2d2aa8) and is carried into scepter_paddy_v25; it is off in all other runs.')
# ---- Table A7 rows
r('then 7 yr of season + fallow without rock (settled state)','then 7–12 yr of season + fallow without rock until control season CH₄ changes by less than 2 % yr⁻¹ (settled state; reference site 9 yr; Morris points 7 yr)')
D.ins_after('scaled to P80 = 100 µm','; reference-site basalt: forsterite 0.141, fayalite 0.059, albite 0.203, anorthite 0.304, diopside 0.223, K-feldspar 0.071 (wt fractions; SCEPTER default basalt without hornblende, renormalised); archetype basalts as described below')
# ---- New A8 paragraph: archetype basalt mineralogy (inserted before the A9 heading)
D.newpara_before('A9 Calibration and code versions',
 'Archetype basalt compositions. The basalt applied at each archetype is derived from whole-rock analyses in GEOROC (Lehnert et al., 2000), downloaded in 10° tiles (258,692 analyses; script paddy/global/rock_recipes.py). '
 'Analyses were retained if they were whole-rock and not flagged as altered, had SiO₂ of 45–52 wt % and Na₂O + K₂O ≤ 5 wt % on a volatile-free basis (the TAS basalt field), LOI ≤ 3 wt % where reported, an oxide total including LOI of 97–101.5 wt % and valid coordinates (13,207 analyses). '
 'Of these, the 1,380 analyses that are the nearest analysis within 250 km of at least one rice cell were used, each weighted by the rice area for which it is the nearest analysis. '
 'They were grouped by area-weighted k-means clustering on standardised SiO₂, TiO₂, Al₂O₃, FeOT, MgO, CaO, Na₂O and K₂O into 12 groups (glb00–glb11). '
 'Each group composition is the area-weighted median of its oxides. Total Fe is split into FeO and Fe₂O₃ using the area-weighted median Fe³⁺/Fe_tot of the analyses that report both, where more than half of the group does, and otherwise with Fe³⁺/Fe_tot = 0.15. '
 'The composition is converted to a mineral assemblage (data/dust_glbNN.in) by a simplified CIPW norm (paddy/global/basalt_norm.py), allocated in the order apatite (P₂O₅, removing CaO only), ilmenite (TiO₂ with FeO), Fe₂O₃ as reducible ferrihydrite (amfe3), K-feldspar, albite, anorthite, Fe-free diopside and hypersthene (enstatite and ferrosilite), with olivine (forsterite and fayalite) replacing hypersthene where silica is insufficient and quartz taking any silica excess; MnO is added to FeO and excess Al₂O₃ is inert. '
 'Each rice cell takes the group of its nearest retained analysis, and archetypes are formed within each combination of water regime and basalt group, so that each archetype has a single basalt. '
 'The six archetypes in Table 2 use three groups (wt fractions): glb09 (176 analyses; rf189, rf184 and irr092), anorthite 0.300, diopside 0.196, albite 0.181, ferrosilite 0.179, enstatite 0.063, ilmenite 0.038, ferrihydrite 0.022, K-feldspar 0.014 and quartz 0.008; '
 'glb04 (59 analyses; irr061), albite 0.347, anorthite 0.231, fayalite 0.110, diopside 0.105, ferrosilite 0.053, ilmenite 0.053, forsterite 0.038, ferrihydrite 0.025, enstatite 0.021 and K-feldspar 0.017; '
 'glb03 (185 analyses; irr043 and rf151), anorthite 0.316, albite 0.278, diopside 0.104, ferrosilite 0.090, enstatite 0.056, K-feldspar 0.046, fayalite 0.042, ilmenite 0.027, forsterite 0.024 and ferrihydrite 0.018. '
 'All basalts use the same particle size distribution, mixing depth and rock rate scaling (Table A7).',
 like='Table A8 lists the constants set by calibration')
# ---- Captions
r('3-yr drained spin-up, 7-yr settle without rock,','3-yr drained spin-up, 7–12-yr settle without rock until control season CH₄ changes by less than 2 % yr⁻¹ (reference site 9 yr; rf151 stopped at 12 yr without meeting the criterion),')
r('the water-management response (first-year','the water-management response (v22; first-year')
r('and Fe(III) (Wang et al. 2014).','and Fe(III) (Wang et al. 2014; v22).')
r('after the 7-yr settle.','after the 9-yr settle.')
r('in the control after a further 10 years (run r10_ref_0, identical physics)','at the end of control year 10, nine years after the plotted year (run v25bb_ref_0, same chain)')
r('Morris elementary-effects screen, v22 (11 factors, r = 8, 96 points;','Morris elementary-effects screen, v25b (12 factors: the v22 factors plus floodwater discharge, 100–400 mm per season; r = 8, 104 points;')
r('it spans 6–1390 kg ha⁻¹ across the points and is controlled mainly by soil ferrihydrite (lowers CH₄), temperature and OM input (raise it).',
  'it spans 16–716 kg ha⁻¹ (median 87) across the points and is controlled mainly by soil ferrihydrite (lowers CH₄) and OM input (raises it), then temperature.')
r('then by w, temperature and OM input.','then by OM input and w.')
r('CH₄ fell in all 96 runs (median −43%) and the one-year net change was negative in all (median −0.93 t CO₂e ha⁻¹), but w was sampled only between 0.1 and 0.4:',
  'CH₄ fell in 95 of 104 runs (median −35%) and the one-year net change was negative in 97 of 104 (median −0.80 t CO₂e ha⁻¹), with w sampled between 0 and 0.4; floodwater discharge has μ* ≈ 0 for all outputs.')
r(' These are historical structural sensitivity tests run with v24 (v22 calibration, w = 0.2), not rerun with v25b.',' v25b runs (scepter_paddy_v25 with option --ch4si); each structure is compared with a control run with the same structure.')
r('(w = 0.2, as in the v22 runs)','(w = 0.15, as in the v25b runs)')
r('(w_c = −0.2, w = 0.2)','(w_c = −0.2, w = 0.15)')
r('Panels show cumulative net realised GHG change and its CH₄, N₂O, alkalinity and carbonate components relative to matched controls, and annual CH₄ emission by pathway (plant-mediated, ebullition, diffusion).',
  '(a) Cumulative net realised GHG change relative to the matched controls. (b) Season CH₄ change against the matched control. (c, d) CH₄ emission by pathway (plant-mediated, ebullition, surface diffusion) in years 1 and 10.')
D.save(sys.argv[2]); print('ok')
