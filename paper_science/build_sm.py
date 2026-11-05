import docx, copy, sys
from docx.shared import Pt
SRC = sys.argv[1]; OUT = sys.argv[2]
d = docx.Document(SRC)
P = d.paragraphs
TITLE = "Enhanced weathering in rice agriculture couples rapid methane cuts with delayed carbon removal"

def settext(p, t):
    for r in p.runs[1:]: r._element.getparent().remove(r._element)
    if p.runs: p.runs[0].text = t
    else: p.add_run(t)

settext(P[25], TITLE)
settext(P[27], "[Author list to be added]")
settext(P[29], "Corresponding author: d.j.beerling@sheffield.ac.uk")

REFS = {
'rsc': "Riceland SCEPTER model description paper (Geosci. Model Dev., in preparation).",
'kan22': "Y. Kanzaki, S. Zhang, N. J. Planavsky, C. T. Reinhard, Soil Cycles of Elements simulator for Predicting TERrestrial regulation of greenhouse gases: SCEPTER v0.9. Geosci. Model Dev. 15, 4959-4990 (2022). doi:10.5194/gmd-15-4959-2022",
'kan24': "Y. Kanzaki, I. Chiaravalloti, S. Zhang, N. J. Planavsky, C. T. Reinhard, In silico calculation of soil pH by SCEPTER v1.0. Geosci. Model Dev. 17, 4515-4532 (2024). doi:10.5194/gmd-17-4515-2024",
'gong26': "X. Gong et al., Investigating the effects of co-applied basalt and biochar on carbon removal efficiency and grain yield in rice paddy. J. Environ. Manage. 405, 129708 (2026). doi:10.1016/j.jenvman.2026.129708",
'wang14': "W. Wang et al., Steel slag amendment reduces methane emission and increases rice productivity in subtropical paddy fields in China. Wetl. Ecol. Manag. 22, 683-691 (2014). doi:10.1007/s11273-014-9364-4",
'yu20': "Q. Yu et al., A cultivated planet in 2010 - Part 2: The global gridded agricultural-production maps. Earth Syst. Sci. Data 12, 3545-3572 (2020). doi:10.5194/essd-12-3545-2020",
'poggio': "L. Poggio et al., SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. SOIL 7, 217-240 (2021). doi:10.5194/soil-7-217-2021",
'glim': "J. Hartmann, N. Moosdorf, The new global lithological map database GLiM: A representation of rock properties at the Earth surface. Geochem. Geophys. Geosyst. 13, Q12004 (2012). doi:10.1029/2012GC004370",
'georoc': "K. Lehnert, Y. Su, C. H. Langmuir, B. Sarbas, U. Nohl, A global geochemical database structure for rocks. Geochem. Geophys. Geosyst. 1, 1999GC000026 (2000). doi:10.1029/1999GC000026",
'renforth': "P. Renforth, The potential of enhanced weathering in the UK. Int. J. Greenh. Gas Control 10, 229-243 (2012). doi:10.1016/j.ijggc.2012.06.011",
'ggcmi': "J. Jagermeyr et al., Climate impacts on global agriculture emerge earlier in new generation of climate and crop models. Nat. Food 2, 873-885 (2021). doi:10.1038/s43016-021-00400-y",
'mueller': "N. D. Mueller et al., Closing yield gaps through nutrient and water management. Nature 490, 254-257 (2012). doi:10.1038/nature11420",
'bouman': "B. A. M. Bouman, R. M. Lampayan, T. P. Tuong, Water Management in Irrigated Rice: Coping with Water Scarcity (International Rice Research Institute, 2007).",
'qi20': "D. Qi, Q. Wu, J. Zhu, Nitrogen and phosphorus losses from paddy fields and the yield of rice with different water and nitrogen management practices. Sci. Rep. 10, 9734 (2020). doi:10.1038/s41598-020-66757-5",
'sujono': "J. Sujono, Flood reduction function of paddy rice fields under different water saving irrigation techniques. J. Water Resour. Prot. 2, 555-559 (2010). doi:10.4236/jwarp.2010.26063",
'peng12': "S. Peng et al., Integrated irrigation and drainage practices to enhance water productivity and reduce pollution in a rice production system. Irrig. Drain. 61, 285-293 (2012). doi:10.1002/ird.684",
'era5land': "J. Munoz-Sabater et al., ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth Syst. Sci. Data 13, 4349-4383 (2021). doi:10.5194/essd-13-4349-2021",
'cmip6': "V. Eyring et al., Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6) experimental design and organization. Geosci. Model Dev. 9, 1937-1958 (2016). doi:10.5194/gmd-9-1937-2016",
'scenmip': "B. C. O'Neill et al., The Scenario Model Intercomparison Project (ScenarioMIP) for CMIP6. Geosci. Model Dev. 9, 3461-3482 (2016). doi:10.5194/gmd-9-3461-2016",
'lefebvre': "D. Lefebvre et al., Assessing the potential of soil carbonation and enhanced weathering through Life Cycle Assessment: a case study for Sao Paulo State, Brazil. J. Clean. Prod. 233, 468-481 (2019). doi:10.1016/j.jclepro.2019.06.099",
'ar6ch7': "P. Forster et al., in Climate Change 2021: The Physical Science Basis, V. Masson-Delmotte et al., Eds. (Cambridge Univ. Press, 2021), pp. 923-1054. doi:10.1017/9781009157896.009",
'faostat': "FAO, FAOSTAT Emissions from crops (Food and Agriculture Organization of the United Nations); www.fao.org/faostat [accessed 4 November 2026].",
'ipcc19': "IPCC, 2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories, Vol. 4, E. Calvo Buendia et al., Eds. (IPCC, 2019).",
'leach21': "N. J. Leach et al., FaIRv2.0.0: a generalized impulse response model for climate uncertainty and future scenario exploration. Geosci. Model Dev. 14, 3007-3036 (2021). doi:10.5194/gmd-14-3007-2021",
'smith24': "C. Smith et al., fair-calibrate v1.4.1: calibration, constraining, and validation of the FaIR simple climate model for reliable future climate projections. Geosci. Model Dev. 17, 8569-8592 (2024). doi:10.5194/gmd-17-8569-2024",
'prather12': "M. J. Prather, C. D. Holmes, J. Hsu, Reactive greenhouse gas scenarios: Systematic exploration of uncertainties and the role of atmospheric chemistry. Geophys. Res. Lett. 39, L09803 (2012). doi:10.1029/2012GL051440",
'noaa': "X. Lan, K. W. Thoning, E. J. Dlugokencky, Trends in globally-averaged CH4, N2O, and SF6 determined from NOAA Global Monitoring Laboratory measurements (NOAA GML). doi:10.15138/P8XG-AA10",
'veefkind': "J. P. Veefkind et al., TROPOMI on the ESA Sentinel-5 Precursor: A GMES mission for global observations of the atmospheric composition for climate, air quality and ozone layer applications. Remote Sens. Environ. 120, 70-83 (2012). doi:10.1016/j.rse.2011.09.027",
'balasus': "N. Balasus et al., A blended TROPOMI+GOSAT satellite data product for atmospheric methane using machine learning to correct retrieval biases. Atmos. Meas. Tech. 16, 3787-3807 (2023). doi:10.5194/amt-16-3787-2023",
'era5': "H. Hersbach et al., The ERA5 global reanalysis. Q. J. R. Meteorol. Soc. 146, 1999-2049 (2020). doi:10.1002/qj.3803",
'gc1471': "The International GEOS-Chem User Community, GEOS-Chem 14.7.1 (Zenodo) [DOI to be added].",
'bey01': "I. Bey et al., Global modeling of tropospheric chemistry with assimilated meteorology: Model description and evaluation. J. Geophys. Res. 106, 23073-23095 (2001). doi:10.1029/2001JD000807",
'keller14': "C. A. Keller et al., HEMCO v1.0: a versatile, ESMF-compliant component for calculating emissions in atmospheric models. Geosci. Model Dev. 7, 1409-1417 (2014). doi:10.5194/gmd-7-1409-2014",
'lin21': "H. Lin et al., Harmonized Emissions Component (HEMCO) 3.0 as a versatile emissions component for atmospheric models. Geosci. Model Dev. 14, 5487-5506 (2021). doi:10.5194/gmd-14-5487-2021",
'varon22': "D. J. Varon et al., Integrated Methane Inversion (IMI 1.0): a user-friendly, cloud-based facility for inferring high-resolution methane emissions from TROPOMI satellite observations. Geosci. Model Dev. 15, 5787-5805 (2022). doi:10.5194/gmd-15-5787-2022",
'estrada25': "L. A. Estrada et al., Integrated Methane Inversion (IMI) 2.0. Geosci. Model Dev. 18, 3311-3330 (2025). doi:10.5194/gmd-18-3311-2025",
'geosfp': "R. Lucchesi, File Specification for GEOS FP (GMAO Office Note No. 4, NASA Global Modeling and Assimilation Office, 2018).",
}

S = []   # (kind, text): 'h' subhead, 't' text
def h(t): S.append(('h', t))
def t(x): S.append(('t', x))

h("Overview")
t("We simulated basalt amendment of the world's ricelands that lie within 150 km of basaltic rock with Riceland SCEPTER, a one-dimensional reactive-transport model of flooded rice soils {rsc,kan22,kan24}. The rice area was grouped into 602 soil-climate-management archetypes. Each archetype was spun up, settled to a steady control state and run for 25 consecutive years (2026-2050) with and without basalt. Treatment minus the year-matched control gives the change in CH4, N2O and inorganic carbon removal. Archetype results were mapped back to their 5-arcmin cells, summed by country and globally, converted to climate forcing and temperature with the FaIR simple climate model, and used to test whether the CH4 reduction could be verified from satellite observations.")

h("Riceland SCEPTER model")
t("Riceland SCEPTER extends SCEPTER v1.0 {kan22,kan24} with kinetic microbial redox reactions (O2, NO3-, Mn, Fe(III) and SO4 reduction and methanogenesis), Fe and S cycling, CH4 and N2O production and transport by diffusion, ebullition and plant aerenchyma, rice root exudation and O2 release, a plough pan, and prescribed flooding, drainage and fallow schedules. Basalt minerals dissolve kinetically from a particle size distribution, and secondary calcite precipitates where saturated. The rate laws, parameters and calibration are given in Appendix A of the model description paper {rsc}. We used model version v25b (source commit a8159b4) with calibration file krxn_calibrated_v25b.in (commit b0ba34a), the version behind all figures of the model description paper. The model column is 0.5 m deep (25 layers) with a plough pan at 0.20-0.24 m.")
t("Basalt lowers CH4 in the model through two mechanisms: (i) Fe(III) supplied by the rock and by enhanced Fe cycling diverts electrons from methanogenesis to Fe reduction, and (ii) silicon released by weathering strengthens rice root O2 loss and CH4 oxidation in the rhizosphere (the Si-root feedback). The Si feedback is empirical. Its strength w = 0.15 (half-saturation 2 mM, reference Si 0.27 mM) was fitted jointly to field data for basalt and steel slag amendment of rice paddies {gong26,wang14}. A full set of runs with the feedback switched off (w = 0) gives the structural sensitivity [results pending].")

h("Model domain and input data")
t("Rice area is MapSPAM 2010 v2.0 harvested area at 5 arcmin, split into irrigated and rainfed {yu20}. Soil pH, cation exchange capacity, soil organic carbon and clay (0-15 cm) are from SoilGrids 2.0 {poggio} at 5 km. Gaps in deltas and near water bodies are filled from the nearest valid pixel. The distance from each rice cell to the nearest basic volcanic outcrop (class vb) was computed from the full-resolution vector Global Lithological Map (GLiM) {glim}, rasterised at 5 arcmin so that small outcrops are kept. The main domain is all rice within 150 km of basalt: 95.8 Mha of harvested rice in 148,807 cells. Rice on the Pacific coast of Colombia and Ecuador was excluded because its extreme rainfall lies outside the model's calibration range. Extending the domain to 250 km adds 29.4 Mha. These cells were assigned to the nearest archetype of the same water regime in standardised soil and temperature space; applied to the 150 km cells, this rule reproduces the archetype totals to within 1-4%. The 250 km results are reported as an upper bound.")
t("Soil reducible Fe(III) (ferrihydrite) is set from clay content (0.012 mol per unit volume at 30% clay, scaled linearly and clipped to 0.004-0.03). Soil organic matter input is set from SOC. Soil pH is matched through the irrigation water alkalinity and, for calcareous soils (pH >= 6.8), a small initial soil calcite fraction.")

h("Basalt composition")
t("Whole-rock basalt analyses were taken from GEOROC {georoc} (fresh basalts only: 45-52 wt% SiO2, Na2O + K2O <= 5 wt%, loss on ignition <= 3 wt%, oxide totals 97-101.5 wt%, altered samples removed). Each rice cell takes its nearest analysis. The analyses were grouped by area-weighted k-means on standardised oxides into 12 regional recipes. Each recipe is the area-weighted median composition of its group, converted to model minerals (plagioclase, K-feldspar, diopside, enstatite/ferrosilite or forsterite/fayalite, ilmenite, apatite and quartz) by a simplified CIPW norm. Fe3+/Fe-total is taken as 0.15 where only total Fe is reported. Basalt is applied at the start of each rice season at 20 t ha-1 yr-1 and mixed into the top 0.15 m, with 0.2 m tillage before each season. Its particle size distribution is that of Renforth {renforth} scaled so that the volume-weighted P80 is 100 um, represented as 14 log-normal components. A 5 t ha-1 yr-1 case tests dose realism [results pending].")

h("Crop calendar, fertiliser and water management")
t("Planting date and growing season length are from the GGCMI phase 3 crop calendar for the main rice season {ggcmi}, separately for irrigated and rainfed rice. Every archetype has a 113-day flooded season, the length used in the model calibration, timed to end at GGCMI maturity. One rice season per year is simulated, followed by a 252-day drained fallow. Multiple cropping is therefore not counted. N fertiliser (urea) is the EarthStat rice N application rate {mueller}, capped at 300 kg N ha-1 per season. Cells without data take the nearest valid pixel within 150 km, then their country's area-weighted median.")
t("Irrigated rice is continuously flooded with a final drain 14 days before harvest. Rainfed rice follows an alternate wetting and drying (AWD) schedule: flooded for the first month, then three drains of about 7 days (to a water table 0.15 m below the surface and surface saturation 0.6) separated by about 15 days of reflooding, flooded again from about day 80, and the same 14-day final drain from day 99. The rate at which floodwater solutes drain from the field is 0.74 m yr-1 for continuous flooding and 0.96 m yr-1 for AWD, from an adopted surface discharge of 200 mm per season divided by the flooded time {bouman,qi20,sujono,peng12}. In the fallow, surface saturation follows ERA5-Land soil wetness capped at 0.6 of saturation, and percolation follows max(P - ET, 0.05 m yr-1). ERA5-Land does not represent paddy drainage, and the uncapped values gave unrealistically wet fallows.")

h("Climate forcing")
t("Each archetype is forced by monthly soil temperature (0-7 cm), surface soil wetness, precipitation and evapotranspiration. These are area-weighted means of its cells from ERA5-Land monthly means for 1995-2014 {era5land}, sampled at the nearest land point. Soil temperature varies through both season and fallow. Future climate uses CMIP6 {cmip6,scenmip} SSP2-4.5 and SSP5-8.5 projections from five models (BCC-CSM2-MR, GFDL-ESM4, IPSL-CM6A-LR, MIROC6, UKESM1-0-LL). Changes in soil temperature (tsl, 0.1 m) are applied as additive deltas. Changes in precipitation, evapotranspiration and surface soil moisture are applied as ratios of 2041-2060 to 1995-2014 in the same model (clipped to 0.25-4, and 0.5-2 for soil moisture). In the transient future runs, each year's monthly climate is interpolated linearly from the baseline (centred on 2005) towards the 2041-2060 climatology (centred on 2050). The present-climate results hold the 1995-2014 climatology fixed for all 25 years. A further run adds recycled ERA5-Land 1995-2014 year-to-year anomalies to one model's trend to estimate interannual variability in control CH4 [pending].")

h("Archetypes and upscaling")
t("Cells were grouped into 602 archetypes by area-weighted k-means within each combination of water regime (irrigated or rainfed) and basalt recipe. The clustering variables (standardised) were soil pH, CEC, SOC, reducible Fe(III), N rate, season start day (as sine and cosine), mean soil temperature in the season and over the year, and fallow wetness and P - ET. Archetype inputs are area-weighted means of their member cells, with planting day as a circular mean. Each cell takes the per-hectare result of its archetype, multiplied by its harvested area. To test the upscaling, 100 cell-regime units drawn at random with probability proportional to rice area were run individually through the full protocol, and each was compared with its archetype [validation results pending].")

h("Simulation protocol")
t("Each archetype was (i) spun up for 3 years under drained conditions to equilibrate soil organic matter and mineralogy, (ii) settled without basalt under its rice-fallow cycle until both season CH4 (by less than 2% per year) and the plough-layer Fe(III) stock (by less than 1% per year) were stable over two consecutive years (minimum 7, maximum 60 years; median 20 years; 601 of 602 archetypes converged), and (iii) run for 25 years from the settled state at 0 and 20 t ha-1 yr-1. Effects are always treatment minus the control of the same year, run from the same settled state. Where SCEPTER's initial exchange-equilibrium solve failed (20 archetypes), the irrigation alkalinity was scaled by 0.8-1.2 and the scaled value kept for all runs of that archetype; all 602 archetypes completed. The future cases start from the present-climate settled state, re-settle for 3 years under the first year's climate, then run 2026-2050 under transient climate.")
t("Dynamic Fe return. Without a source of Fe from below the plough pan, the settled controls slowly ran down their plough-layer Fe and their CH4 drifted upward over decades. In real paddies, Fe lost from the plough layer is partly returned by capillary rise, ploughing of the Fe-enriched layer above the pan and deposition with irrigation water. In each year we therefore return to the plough layer (z <= 0.2 m), as ferrihydrite with the organic matter input, the net dissolved Fe that left it the year before, capped at 5 mol m-2 yr-1. The same rule applies to control and treated runs, and model physics and calibration are unchanged. With it, the control CH4 of all archetypes is stable (median change +0.07% per year over 25 years). For the model's reference archetype, the percentage CH4 cut from basalt is the same as with the fixed Fe input of the model description paper (15/33/47% vs 14/29/48% at years 1/5/10). Thirty-six archetypes (6.7% of area) whose control CH4 still trends by 1% per year or more, or that did not converge, are flagged. Excluding them changes the global net benefit by -4.4%.")

h("Greenhouse gas and carbon removal accounting")
t("For each year, CH4 and N2O emissions from the season and the fallow are summed and converted to CO2-equivalents with GWP100 (CH4 27, N2O 273) {ar6ch7}. Inorganic carbon removal has two parts. (i) Alkalinity export: the potentially durable alkalinity leaving the column, computed as alkalinity minus twice the dissolved Fe2+ and NH4+, which can re-acidify on oxidation. (ii) Pedogenic calcite: counted as removal only up to half of the basalt cation charge not already exported as alkalinity, as a cumulative cap. Emissions from mining and grinding are not included. Road transport emissions are computed per cell from its own distance to basalt, following Lefebvre et al. {lefebvre}: (0.218 x road distance + 5.9) kg CO2e per tonne of rock, with road distance 1.3 times the straight-line distance, applied to the rock added each year. Results are reported both gross and net of transport.")

h("Comparison with emission inventories")
t("Simulated control CH4 was compared with FAOSTAT {faostat} Tier 1 {ipcc19} rice CH4 emissions (2015-2020 mean) for the countries in the domain. Area-weighted control emissions are 0.72 of the FAOSTAT value (107 vs 148 kg CH4 ha-1 yr-1), with ratios of 0.34-2.4 among the 25 countries with at least 0.2 Mha in the domain (Table S[n]). We did not re-tune the model to the inventory. Because the CH4 response is close to proportional to the control flux, the absolute CH4 reduction scaled to FAOSTAT emissions is given as an alternative estimate.")

h("Climate response")
t("Annual global changes in CH4 and N2O emissions and in CO2 removal (net of transport emissions) were run through FaIR v2.2.5 {leach21} with the 841-member constrained calibration v1.4.1 {smith24}, against an SSP2-4.5 background {scenmip}. Each perturbation, alone and combined, is differenced from the background run with the same calibration member. Two deployment cases are shown: application from 2026 to 2050 and then stopped, and year-25 rates held to 2100. The second case extrapolates beyond the simulated period. Ensemble medians and 5-95% ranges are reported. Repeating the calculation against SSP1-2.6 and SSP5-8.5 backgrounds changes the 2050 temperature response by +10% and -11% (-7.9 and -6.4 mK vs -7.2 mK), mainly through the background dependence of CH4 forcing and lifetime.")

h("Satellite detectability of the CH4 reduction")
t("Global record. A one-box CH4 model (2.75 Tg per ppb, lifetime 9.1 years) {prather12} converts the simulated emission reductions to changes in global mean CH4. Detection was tested against the year-to-year variability of the NOAA global CH4 growth rate {noaa} (1984-2025; detrended standard deviation about 3 ppb yr-1, lag-1 autocorrelation about 0.45), represented as AR(1) noise, using a generalised least-squares fingerprint with and without an unknown background trend.")
t("Regional inversion. We built an analytical-inversion observing system simulation experiment (OSSE) for TROPOMI {veefkind} XCH4 (blended with GOSAT {balasus}) over the main rice deltas and over Rio Grande do Sul, Brazil. Emissions are resolved at 0.25 degree as separate rice and other-source states, with prior uncertainties of 50%. Column enhancements follow a Gaussian-plume Jacobian driven by ERA5 {era5} 06 UTC wind speed and direction statistics for 2019-2023 for each region and month. The number of soundings per cell per season follows from the TROPOMI pixel area (38.5 km2), cloud-free fraction (1 minus ERA5 total cloud cover) and a quality-filter pass rate of 0.5. Each sounding has a retrieval error of 12 ppb plus 8 ppb model error, and spatially correlated retrieval bias is represented by 1-degree bias blocks with 2 ppb prior uncertainty. Detection compares two periods (before and after treatment). The treatment effect is a free parameter, while the persistent emission states are shared between periods. A uniform rice-emission anomaly between years (10%) and an other-source anomaly (15%) are also free parameters. Paired designs compare treated with neighbouring untreated rice (difference-in-differences), adding a 4% pairing error. The reduction is detectable when it exceeds twice its posterior standard deviation. We map detection as a function of treated fraction and years since first application, using the simulated per-region CH4 reduction for each year.")
t("Transport-model check. The plume Jacobian is being checked against GEOS-Chem 14.7.1 {gc1471,bey01} with HEMCO {keller14,lin21} forward and inversion runs through the Integrated Methane Inversion (IMI 2.3.1) {varon22,estrada25}, driven by GEOS-FP meteorology {geosfp}, for Bangladesh-West Bengal, the Mekong delta and Rio Grande do Sul [pending].")

h("Code and data availability")
t("Model code, archetype definitions, run scripts and analysis scripts are available at github.com/djbeerling-art/SCEPTER (branch to be archived on Zenodo with a DOI on acceptance).")


import re
order = []
def cite(m):
    ks = [k.strip() for k in m.group(1).split(',')]
    ns = []
    for k in ks:
        assert k in REFS, k
        if k not in order: order.append(k)
        ns.append(order.index(k)+1)
    ns = sorted(ns); out=[]; i=0
    while i < len(ns):
        j=i
        while j+1 < len(ns) and ns[j+1]==ns[j]+1: j+=1
        out.append(str(ns[i]) if j==i else (f"{ns[i]},{ns[j]}" if j==i+1 else f"{ns[i]}-{ns[j]}")); i=j+1
    return "(" + ",".join(out) + ")"
S = [(k, re.sub(r"\{([a-z0-9_, ]+)\}", cite, x)) for k, x in S]
S.append(('h', "References (for merging into the single main-text reference list; numbers will follow on from the main text)"))
for i, k in enumerate(order): S.append(('t', f"{i+1}. {REFS[k]}"))

# insert after the "Materials and Methods" heading (index 47), replacing the placeholder subhead/text (48, 49)
anchor = P[47]
sub_style = P[48].style; txt_style = P[49].style
for p in (P[48], P[49]): p._element.getparent().remove(p._element)
cur = anchor._element
for kind, text in S:
    np_ = copy.deepcopy(anchor._element)
    cur.addnext(np_); cur = np_
    para = docx.text.paragraph.Paragraph(np_, anchor._parent)
    for r in list(para.runs): r._element.getparent().remove(r._element)
    para.style = sub_style if kind == 'h' else txt_style
    para.add_run(text)
# drop the instructions page (paragraphs before the logo block)
for p in P[0:20]:
    p._element.getparent().remove(p._element)
d.save(OUT)
print('saved', OUT, sum(len(x.split()) for k, x in S if k == 't'), 'words')
