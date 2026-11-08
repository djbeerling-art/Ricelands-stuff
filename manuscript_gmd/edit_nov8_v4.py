# Tracked edits on Riceland_SCEPTER_GMD_Nov2_v4.docx (8 Nov 2026, David's requests):
# 2.6.1 slag electron budget (Ali et al., 2008) + Becker et al. (2020); 5.5 methanogen pH response + Lee et al. (2012);
# 5.5 Ni and Cr mass balance. Interpretive wording highlighted cyan for David to reword; placeholder yellow.
import sys; sys.path.insert(0, '.')
from tcedit import Doc
d = Doc('Riceland_SCEPTER_GMD_Nov2_v4.docx', '2026-11-08T13:30:00Z')

# --- 2.6.1: electron budget for the Ali et al. (2008) pot experiment
d.ins_after('Riceland SCEPTER therefore represents this pathway explicitly (Sect. 2.4).',
    ' In the pot experiment of Ali et al. (2008), the 33 % reduction in seasonal CH₄ at 20 Mg ha⁻¹ corresponds to about '
    '3.9 × 10⁵ mol electrons ha⁻¹ (8 electrons per CH₄), whereas the oxalate-extractable Fe supplied by the slag '
    '(about 62 kg ha⁻¹) could accept about 0.3 % of this if each Fe(III) were reduced once. Oxalate-extractable Fe in '
    'the soil after harvest increased by about 1 g kg⁻¹ (about 2.9 t Fe ha⁻¹), considerably more than the slag supplied.')
d.ins_after('considerably more than the slag supplied.',
    ' This suggests that the soil’s own Fe became more reactive or was recycled faster, consistent with the inhibition '
    'of ferrihydrite ageing by dissolved Si (Sect. 2.4), although this mechanism was not tested in that study.', 'cyan')

# --- 2.6.1: Becker et al. (2020)
d.ins_after('(Fleck et al., 2011; Hinrichs et al., 2017), which would reduce O₂ loss per unit root surface.',
    ' Si-enhanced exodermal Casparian band formation has also been linked to reduced Fe uptake by rice roots '
    '(Becker et al., 2020).')

# --- 5.5: methanogen pH response and Lee et al. (2012)
d.ins_after('require further constraints on the turnover and replenishment of reactive Fe pools.',
    ' Methanogenesis has no direct pH dependence in the model; a bell-shaped methanogen pH response is implemented but '
    'switched off in all runs reported here (Sect. A4).')
d.ins_after('switched off in all runs reported here (Sect. A4).',
    ' With this response switched on, the basalt-induced rise in soil pH increases simulated CH₄ emissions, opposite in '
    'sign to the reductions reported in the slag and basalt experiments used for evaluation (Ali et al., 2008; '
    'Wang et al., 2014; Gong et al., 2026)', 'cyan')
d.ins_after('slag and basalt experiments used for evaluation (Ali et al., 2008; Wang et al., 2014; Gong et al., 2026)',
    ' [effect size from the new pH case to be added]', 'yellow')
d.ins_after('[effect size from the new pH case to be added]', '.', 'cyan')
d.ins_after('[effect size from the new pH case to be added].',
    ' Lee et al. (2012) found that 2.3 Mg ha⁻¹ of slag silicate fertiliser reduced seasonal CH₄ by about 14.5 % without '
    'green manure but increased it where Chinese milk vetch was incorporated at 10–40 Mg ha⁻¹ (fresh weight), which '
    'the authors attributed to faster decomposition of the added organic matter under the liming effect of the slag.')
d.ins_after('under the liming effect of the slag.',
    ' A pH response may therefore matter most where fresh organic matter is abundant, a case not evaluated here.', 'cyan')

# --- 5.5: Ni and Cr alongside arsenic
d.rep('such as arsenic.', 'such as arsenic, nickel and chromium.')
d.ins_after('such as arsenic, nickel and chromium.',
    ' A total-element mass balance for the 0–0.20 m layer (2600 t soil ha⁻¹; no leaching, crop removal or erosion), '
    'using GEOROC basalt compositions (Lehnert et al., 2000; mean Ni 90 and Cr 159 mg kg⁻¹), gives topsoil Ni of about '
    '40 mg kg⁻¹ and Cr of about 84 mg kg⁻¹ after 25 yr at 20 t ha⁻¹ yr⁻¹, from assumed backgrounds of 30 and '
    '70 mg kg⁻¹; for 90th-percentile basalt compositions the values are about 56 and 124 mg kg⁻¹. Chinese risk-screening '
    'values for paddy soils are 60–190 mg kg⁻¹ for Ni and 250–350 mg kg⁻¹ for Cr, increasing with soil pH (MEE, 2018).')
d.ins_after('increasing with soil pH (MEE, 2018).',
    ' Ni-rich basalts applied to acidic soils could therefore approach these values within a few decades (cf. Dupla '
    'et al., 2023), whereas redox-driven release of Ni from Fe oxides and Cr(VI) formation would require explicit '
    'representation in the model.', 'cyan')

# --- references
L = 'Akiyama, H., Yagi, K., and Yan, X.'
d.newpara_before('Beerling, D. J., Kantzas, E. P., Lomas, M. R., Taylor, L. L.',
    'Becker, M., Ngo, N. S., and Schenk, M. K. A.: Silicon reduces the iron uptake in rice and induces iron homeostasis '
    'related genes, Sci. Rep., 10, 5079, https://doi.org/10.1038/s41598-020-61718-4, 2020.', like=L)
d.newpara_before('ESG Post: Alt Carbon',
    'Dupla, X., Möller, B., Baveye, P. C., and Grand, S.: Potential accumulation of toxic trace elements in soils during '
    'enhanced rock weathering, Eur. J. Soil Sci., 74, e13343, https://doi.org/10.1111/ejss.13343, 2023.', like=L)
d.newpara_before('Lefebvre, D., Goglio, P.',
    'Lee, C. H., Kim, S. Y., Villamil, M. B., Pramanik, P., Hong, C. O., and Kim, P. J.: Different response of silicate '
    'fertilizer having electron acceptors on methane emission in rice paddy soil under green manuring, Biol. Fertil. '
    'Soils, 48, 435–442, https://doi.org/10.1007/s00374-011-0637-2, 2012.', like=L)
d.newpara_before('Okuda, A. and',
    'MEE (Ministry of Ecology and Environment of the People’s Republic of China): Soil environmental quality – Risk '
    'control standard for soil contamination of agricultural land, GB 15618-2018, China Environmental Science Press, '
    'Beijing, 2018.', like=L)
d.save('Riceland_SCEPTER_GMD_Nov8_v4_tc.docx'); print('ok')
