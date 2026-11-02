# Sect. 2.6.1 (Si–plant feedback): evidence pack and citations

Working note for David, 31 Oct 2026. Facts and citations only, organised in the order of the current 2.6.1 text, so the
rationale can be rewritten with sources. Sentences marked **[fact]** are statements of what a paper measured or reports;
sentences marked **[framing]** are suggestions for the point to make, to be worded by the author. Items marked *check*
have not been verified against the original (network blocks here).

## 1. What the term does (unchanged)

Eq. (11): F_O2,root = F0 [1 − w + w h(Si)/h(Si_ref)], h = Si/(Si + K_Si); Si_ref = 0.27 mmol L⁻¹, K_Si = 2 mmol L⁻¹,
F0 = 3.65 mol O₂ m⁻² yr⁻¹, w = 0.2.

Useful check **[fact]**: Das et al. (2022) measured porewater Si of 0.05–0.26 mmol L⁻¹ in unamended pots and ~1.1 mmol L⁻¹
with 2 Mg ha⁻¹ slag silicate fertiliser. Si_ref sits at the top of their control range. At 1.1 mmol L⁻¹, Eq. (11) with
w = 0.2 gives F_O2,root = 1.40 F0 (+40 %).

## 2. Why a plant term at all: field evidence that silicate amendments lower CH₄

- **[fact]** Slag-based silicate fertiliser lowered seasonal CH₄ by 16–20 % at 4 Mg ha⁻¹ in a two-year field trial
  (Ali, Oh and Kim, 2008) and by 12–33 % at 2–20 Mg ha⁻¹ in pots (Ali, Lee and Kim, 2008); Ali et al. (2009) report
  reductions under no-till. A meta-analysis gives −15 % CH₄ and +18 % yield for slag silicate fertiliser (Lim et al.,
  2022; *check*, cited via Das et al., 2022).
- **[fact]** Pure Si sources give inconsistent CH₄ responses: SiO₂ lowered CH₄ (Lou et al., 2019), CaSiO₃ raised it with
  larger plant biomass (Ku et al., 2020), and CaSiO₃ + H₄SiO₄ had no significant effect (Limmer et al., 2018). All three
  as summarised by Das et al. (2022); *check* originals.
- **[framing]** Slag supplies Fe(III) as well as Si, so the field signal cannot by itself separate a plant-Si effect from
  the Fe electron-acceptor effect already represented in the model's geochemistry.

## 3. Direct evidence on the mechanism the term encodes (Si → root O₂ release)

For:
- **[fact]** Das et al. (2022): 2 Mg ha⁻¹ slag silicate fertiliser, two cultivars, pots. CH₄ −21 and −26 %; root oxidase
  activity (α-naphthylamine method) rose significantly at 43 and 71 days; soil CH₄-oxidation potential +23–33 %; pmoA
  transcripts +12–18 %, mcrA −8–11 %; Geobacter gltA +17–20 %. Their structural equation model (R² 0.94) puts the main
  path through Fe-reducer/methanogen competition (gltA/mcrA) and a second path through methanotrophs (pmoA/mcrA); dissolved
  Si acts on the second path indirectly via root oxidase activity. Dissolved Fe also increases root oxidase activity.
- **[fact]** Tong et al. (2024): hydroponic rice with and without Si under stagnant deoxygenated conditions (flooded-soil
  analogue). Si delayed and weakened the barrier to radial O₂ loss (measured as O₂ resistance of the outer root with
  microsensors), lowered lignin and suberin in the outer root, and reduced inducible cortical aerenchyma. No effect under
  aerated conditions. From the abstract and highlights; full text not seen.
- **[fact]** Older root-physiology work reports higher root oxidising power in Si-fed rice (Okuda and Takahashi, 1965;
  Ma and Takahashi, 2002). *check* pages; the 1965 source is not on Crossref.

Against / complicating:
- **[fact]** Fleck et al. (2011) found Si increased suberin and lignin in the exodermis of rice roots and reduced radial O₂
  loss; Hinrichs et al. (2017; *check*) likewise report Si-induced Casparian band formation. Tong et al. (2024) state
  that the Si effect on the barrier is debated (enhanced, unaffected or delayed in different studies).
- **[fact]** In flooded rice the barrier confines radial O₂ loss to root tips and laterals (ROL ~175 nmol m⁻² s⁻¹ near the
  tip, <1 nmol m⁻² s⁻¹ 60–80 mm behind it); the same barrier is thought to slow entry of soil gases including CH₄, and
  plants carry most paddy CH₄ to the atmosphere (Colmer, 2003). Barrier formation is induced by flooding and by
  short-chain organic acids.
- **[fact]** Ali, Lee and Kim (2008): CH₄ production also fell (−10 to −27 %) in root-free anoxic soil incubations from
  slag-amended pots, soil Eh showed no treatment effect, and the slag supplied only 6–62 kg ha⁻¹ active Fe against a
  soil pool of ~9 g kg⁻¹. Root porosity rose from 18.5 to 25 %. Root O₂ loss was not measured.
- **[fact]** Ma and Yamaji (2006) and Wu et al. (2016) do not address root O₂ loss or CH₄ (Si uptake via Lsi1; Si and Fe
  plaque/As). Ma and Yamaji is the citation for Si accumulation (up to 10 % of shoot dry weight) and active uptake.

## 4. Suggested shape of the revised rationale **[framing, for the author to word]**

1. Silicate amendments lower paddy CH₄ in field and pot trials (Ali et al., 2008a,b, 2009; Lim et al., 2022), but
   slag also adds Fe(III), and pure-Si trials disagree in sign (Lou 2019; Ku 2020; Limmer 2018).
2. The term follows two measured plant responses: higher root oxidase activity and methanotroph abundance under slag
   silicate fertiliser (Das et al., 2022) and a more O₂-permeable root barrier with Si under flooded conditions
   (Tong et al., 2024).
3. The sign is contested (Fleck et al., 2011; Hinrichs et al., 2017), the barrier also governs CH₄ entry (Colmer, 2003),
   Si and Fe co-vary in every amendment study, and the model does not represent aerenchyma, root architecture or
   root CH₄ conductance. Hence w is an empirical net plant response; w = 0 is reported throughout; an alternative
   structure in which Si acts on plant CH₄ conductance (v24, `--ch4si`) is tested in Sect. 4.x.

## 5. Parameter notes

- Model rice Si uptake is ~130 kg Si ha⁻¹ season⁻¹ (siup 3.7 mol m⁻² yr⁻¹, K_m 0.3 mM). Literature: 151–300 kg Si ha⁻¹
  (Meena et al., 2014, via Das et al., 2022); Lsi1 K_m ≈ 0.15 mM (Mitani and Ma, 2005, via Ma and Yamaji, 2006).
  Low uptake would leave porewater Si higher in basalt runs and so strengthen the Si signal.

## References (verified against Crossref unless marked)

- Ali, M. A., Lee, C. H., and Kim, P. J.: Effect of silicate fertilizer on reducing methane emission during rice
  cultivation, Biol. Fertil. Soils, 44, 597–604, https://doi.org/10.1007/s00374-007-0243-5, 2008a.
- Ali, M. A., Oh, J. H., and Kim, P. J.: Evaluation of silicate iron slag amendment on reducing methane emission from
  flood water rice farming, Agric. Ecosyst. Environ., 128, 21–26, https://doi.org/10.1016/j.agee.2008.04.014, 2008b.
- Ali, M. A., Lee, C. H., Lee, Y. B., and Kim, P. J.: Silicate fertilization in no-tillage rice farming for mitigation of
  methane emission and increasing rice productivity, Agric. Ecosyst. Environ., 132, 16–22,
  https://doi.org/10.1016/j.agee.2009.02.014, 2009.
- Colmer, T. D.: Long-distance transport of gases in plants: a perspective on internal aeration and radial oxygen loss
  from roots, Plant Cell Environ., 26, 17–36, https://doi.org/10.1046/j.1365-3040.2003.00846.x, 2003.
- Das, S., Jena, S. N., Bhuiyan, M. S. I., Kim, G. W., and Kim, P. J.: Mechanism of slag-based silicate fertilizer
  suppressing methane emissions from paddies, J. Clean. Prod., 373, 133799,
  https://doi.org/10.1016/j.jclepro.2022.133799, 2022. (DOI from the PDF.)
- Fleck, A. T., Nye, T., Repenning, C., Stahl, F., Zahn, M., and Schenk, M. K.: Silicon enhances suberization and
  lignification in roots of rice (Oryza sativa), J. Exp. Bot., 62, 2001–2011, 2011. *check DOI*
- Hinrichs, M., Fleck, A. T., Biedermann, E., Ngo, N. S., Schreiber, L., and Schenk, M. K.: An ABC transporter is
  involved in the silicon-induced formation of Casparian bands in the exodermis of rice, Front. Plant Sci., 8, 671,
  2017. *check*
- Ku, H. H., Hayashi, K., Agbisit, R., and Villegas-Pangga, G.: Effects of calcium silicate on nutrient use of lowland
  rice and greenhouse gas emission from paddy soil in the Philippines under alternating wetting and drying,
  Pedosphere, 30, 535–543, 2020. *check*
- Lim, J. Y., Kang, Y. G., Sohn, K. M., Kim, P. J., and Galgo, S. J. C.: Creating new value of blast furnace slag as
  soil amendment to mitigate methane emission and improve rice cropping environments, Sci. Total Environ., 806,
  150961, 2022. *check*
- Limmer, M. A., Mann, J., Amaral, D. C., Vargas, R., and Seyfferth, A. L.: Silicon-rich amendments in rice paddies:
  effects on arsenic uptake and biogeochemistry, Sci. Total Environ., 624, 1360–1368, 2018. *check*
- Lou, Y., Ren, L., Zhao, S., Shi, Y., Zhang, Y., and Zhu, H.: Effects of silicate application on CH4 and N2O
  emissions and global warming potentials in paddy soil under enhanced UV-B radiation, Energy Sci. Eng., 7,
  1784–1794, 2019. *check*
- Ma, J. F. and Takahashi, E.: Soil, Fertilizer, and Plant Silicon Research in Japan, Elsevier, Amsterdam, 2002.
- Ma, J. F. and Yamaji, N.: Silicon uptake and accumulation in higher plants, Trends Plant Sci., 11, 392–397,
  https://doi.org/10.1016/j.tplants.2006.06.007, 2006.
- Meena, V. D., Dotaniya, M. L., Coumar, V., Rajendiran, S., Kundu, S., and Rao, A. S.: A case for silicon
  fertilization to improve crop yields in tropical soils, Proc. Natl. Acad. Sci. India B, 84, 505–518, 2014. *check*
- Okuda, A. and Takahashi, E.: The role of silicon, in: The Mineral Nutrition of the Rice Plant, Johns Hopkins Press,
  Baltimore, 123–146, 1965. *not verified*
- Tong, S., Ranathunge, K., Pellegrini, E., Liu, D., Herzog, M., Jiménez, J. de la C., Kotula, L., and Pedersen, O.:
  Silicon weakens the outer apoplastic barrier in roots of rice and delays its formation, resulting in increased Na+
  and Cl− fluxes to the shoot, Environ. Exp. Bot., 105941, https://doi.org/10.1016/j.envexpbot.2024.105941, 2024.
  *check volume*
- Wu, C., Zou, Q., Xue, S.-G., Pan, W.-S., Huang, L., Hartley, W., Mo, J.-Y., and Wong, M.-H.: The effect of silicon on
  iron plaque formation and arsenic accumulation in rice genotypes with different radial oxygen loss (ROL), Environ.
  Pollut., 212, 27–33, https://doi.org/10.1016/j.envpol.2016.01.004, 2016.
