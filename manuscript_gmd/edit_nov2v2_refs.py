# Tracked edits on David's Nov2_v2: section cross-references, figure callouts, heading styles and citations.
import re, sys
sys.path.insert(0, '.')
from tcedit import Doc
D = '2026-11-02T12:00:00Z'
d = Doc('Riceland_SCEPTER_GMD_Nov2_v2.docx', D)

def restyle(ctx, style):
    pm, _ = d.find(ctx); p = pm.group()
    m = re.search(r'<w:pPr>(.*?)</w:pPr>', p, re.S)
    inner = m.group(1); old = re.sub(r'<w:rPr>.*?</w:rPr>', '', inner, flags=re.S)
    old = re.sub(r'<w:pPrChange.*?</w:pPrChange>', '', old, flags=re.S)
    new = re.sub(r'<w:pStyle w:val="[^"]*"/>', '', inner)
    if style: new = '<w:pStyle w:val="%s"/>' % style + new
    chg = '<w:pPrChange w:id="%d" w:author="Claude" w:date="%s"><w:pPr>%s</w:pPr></w:pPrChange>' % (d.wid(), D, old)
    rp = re.search(r'<w:rPr>.*?</w:rPr>', new, re.S)
    new = new[:rp.start()] + chg + new[rp.start():] if rp else new + chg
    p2 = p[:m.start()] + '<w:pPr>%s</w:pPr>' % new + p[m.end():]
    d.d = d.d[:pm.start()] + p2 + d.d[pm.end():]

def delpara(ctx):
    pm, _ = d.find(ctx); t = d.ptext(pm.group())
    d.rep(t, '', pre='')
    pm, _ = d.find(t) if False else (None, None)
    # mark the paragraph mark deleted
    for pm in d.PARA.finditer(d.d):
        if '<w:delText' in pm.group() and ctx[:30] in re.sub(r'<[^>]+>', '', pm.group()):
            p = pm.group(); mark = '<w:del w:id="%d" w:author="Claude" w:date="%s"/>' % (d.wid(), D)
            if '<w:pPr>' in p:
                pp = re.search(r'<w:pPr>.*?</w:pPr>', p, re.S).group()
                pp2 = re.sub(r'<w:rPr>', '<w:rPr>' + mark, pp, 1) if '<w:rPr>' in pp else pp.replace('</w:pPr>', '<w:rPr>%s</w:rPr></w:pPr>' % mark)
                p = p.replace(pp, pp2, 1)
            else:
                p = re.sub(r'(<w:p(?: [^>]*)?>)', r'\1<w:pPr><w:rPr>%s</w:rPr></w:pPr>' % mark, p, 1)
            d.d = d.d[:pm.start()] + p + d.d[pm.end():]; break

# --- headings: styles and wording
for ctx, st in [('1 Introduction', 'Heading1'), ('2.7 The implementation architecture', 'Heading2'),
                ('2.9 CDR accounting in Riceland SCEPTER', 'Heading2'), ('4 Model behaviour', 'Heading1'),
                ('4.3 Long-term evolution of alkalinity', 'Heading2'), ('4.4 Contrasting rice-soil archetypes', 'Heading2'),
                ('4.5 Uncertainty in the Si–root response', 'Heading2'), ('4.6 Morris screening of methane', 'Heading2'),
                ('5.2 Soil retention and delayed', 'Heading2'), ('5.3 EW-related CH4 mitigation', 'Heading2'),
                ('5.4 Implications for deployment', 'Heading2'), ('5.5 Model limitations and priorities', 'Heading2')]:
    restyle(ctx, st)
for ctx in ('This appendix documents the processes added', 'DJB conceptualized, designed', 'D.J.B. has a minority equity stake'):
    restyle(ctx, None)
d.rep('The implementation architecture', 'Implementation architecture', pre='2.7 ')
d.rep('spin-up/treatment protocols.', 'spin-up and treatment protocols')
d.rep('flooded rice soils.', 'flooded rice soils', pre='5.1 Advances in modelling EW in ')

# --- section cross-references
d.rep('(Sect. 2.7)', '(Sect. 2.8)', pre='element mass balances ')
d.rep('(Sect. 2.8)', '(Sect. 2.9)', pre='is recorded as signed lateral export ')
d.rep('(Sect. 2.8)', '(Sect. 2.9)', pre='used to calculate the GHG and CDR budgets ')
d.rep('Sect. 4.2 tests', 'Sect. 4.5 tests')
d.rep('(Sect. 2.7)', '(Sect. 2.8)', pre='alkalinity export by less than 0.3 % ')
d.rep('central value (Sect. 4)', 'central value (Sect. 4.5)')

# --- figure callouts (new order: 6 ref 10 yr, 7 ref 40 yr, 8 archetypes, 9 Si feedback, 10 Morris)
d.rep('Fig. 7 alone uses', 'Figs. 9d–g alone use')
d.rep('produced Figs. 4–9, including the Morris screen (Fig. 6a) and the alternative Si–root structures (Fig. 7)',
      'produced Figs. 4–10, including the alternative Si–root structures (Fig. 9d–g) and the Morris screen (Fig. 10)')
d.rep('used only for Fig. 7;', 'used only for Fig. 9d–g;')
d.rep('--ch4si used in Fig. 7', '--ch4si used in Fig. 9d–g')
d.rep('(Fig. 8b). Methane', '(Fig. 8a). Methane')
d.flag('remain similar among these structures (Fig. 9', 'Fig. 9 does not plot PDA or calcite for the structures: say "not shown" or add a panel/table')
# typos that change meaning (w = 0 case)
d.rep('strength from w to 0.15', 'strength from w = 0 to 0.15')
d.rep('At w, first-year', 'At w = 0, first-year')
d.rep('as Si increases wc = 0.5)', 'as Si increases (wc = 0.5)')

# --- citations in text
d.ins_after('in 2024 (FAO', ', 2025')
d.rep('Song2023GBC', 'Song et al., 2023')
d.rep('the MapSPAM rice areas of Yu et al., 2020, with the GLiM lithology of Hartmann and Moosdorf, 2012)',
      'the MapSPAM rice areas of Yu et al. (2020) with the GLiM lithology of Hartmann and Moosdorf (2012)')
d.rep('(IPCC AR6)', '(Forster et al., 2021)')
d.rep('Jugsujinda and Patrick, 1996', 'Patrick and Jugsujinda, 1992')
d.rep('(Shiratori2010)', '(Shiratori et al., 2007)')
d.flag('(Shiratori et al., 2007)', 'Shiratori 2010 not found; reference added for Shiratori et al. 2007 (subsurface drainage, oxidised soil, lower CH4) - check this is the paper you meant')
d.rep('; doi.org/10.1002/agg2.20119', '')
d.ins_after('accompanied by increased soil redox potential and altered Fe cycling', ' (Yuan et al., 2023)')
d.rep('(Yuan2023, https://link.springer.com/article/10.1007/s44246-023-00049-1)', '(Yuan et al., 2023)')
d.rep('Anderson2026', 'Andersen et al., 2026')

# --- reference list: new entries (alphabetical) and DOIs
R = 'Akiyama, H., Yagi, K., and Yan, X.'
def add(before, text, hl=None): d.newpara_before(before, text, hl, like=R)
add('Beerling, D. J., Kantzas, E. P., Lomas, M. R., Taylor', 'Andersen, A. G., Song, Z., Guhr, T., Roy, K. S., Radanielson, A. M., Jiménez, J. de la C., and Pedersen, O.: Root barriers to radial O₂ loss restrict CH₄ entry and plant-mediated emissions, J. Exp. Bot., https://doi.org/10.1093/jxb/erag497, 2026.')
add('Jones, A. M., Collins', 'Jiménez, J. de la C., Song, Z., Pineda, M., Lozano, P., Rebolledo, M. C., Cardoso, J. A., Alvarez, M. F., Armstrong, W., and Pedersen, O.: Radial oxygen loss, rhizospheric methane oxidation and methane emissions from rice roots, New Phytol., 252, 1035–1049, https://doi.org/10.1111/nph.71549, 2026.')
d.ins_after('Environ. Exp. Bot., ', '226, ')
add('Fleck, A. T., Nye, T.', 'FAO: FAOSTAT: Crops and livestock products, Food and Agriculture Organization of the United Nations, Rome, https://www.fao.org/faostat/en/#data/QCL (last access: [date to add]), 2025.', 'yellow')
add('Fumoto, T., Kobayashi, K.', "Forster, P., Storelvmo, T., Armour, K., Collins, W., Dufresne, J.-L., Frame, D., Lunt, D. J., Mauritsen, T., Palmer, M. D., Watanabe, M., Wild, M., and Zhang, H.: The Earth's energy budget, climate feedbacks, and climate sensitivity, in: Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change, edited by: Masson-Delmotte, V., Zhai, P., Pirani, A., et al., Cambridge University Press, Cambridge, UK and New York, NY, USA, 923–1054, https://doi.org/10.1017/9781009157896.009, 2021.")
add('Lehnert, K., Su, Y.', 'Lefebvre, D., Goglio, P., Williams, A., Manning, D. A. C., de Azevedo, A. C., Bergmann, M., Meersmans, J., and Smith, P.: Assessing the potential of soil carbonation and enhanced weathering through Life Cycle Assessment: a case study for Sao Paulo State, Brazil, J. Clean. Prod., 233, 468–481, https://doi.org/10.1016/j.jclepro.2019.06.099, 2019.')
add('Peng, S., Luo, Y.', 'Patrick, W. H. and Jugsujinda, A.: Sequential reduction and oxidation of inorganic nitrogen, manganese, and iron in flooded soil, Soil Sci. Soc. Am. J., 56, 1071–1073, https://doi.org/10.2136/sssaj1992.03615995005600040011x, 1992.')
add('Renforth, P.: The potential', 'Reba, M. L., Fong, B. N., Rijal, I., Adviento-Borbe, M. A., Chiu, Y.-L., and Massey, J. H.: Methane flux measurements in rice by static flux chamber and eddy covariance, Agrosyst. Geosci. Environ., 3, e20119, https://doi.org/10.1002/agg2.20119, 2020.')
add('Šimek, M. and Cooper', 'Shiratori, Y., Watanabe, H., Furukawa, Y., Tsuruta, H., and Inubushi, K.: Effectiveness of a subsurface drainage system in poorly drained paddy fields on reduction of methane emissions, Soil Sci. Plant Nutr., 53, 387–400, https://doi.org/10.1111/j.1747-0765.2007.00171.x, 2007.')
add('Stumm, W. and Lee', 'Song, H., Zhu, Q., Blanchet, J.-P., Chen, Z., Zhang, K., Li, T., Zhou, F., and Peng, C.: Central role of nitrogen fertilizer relative to water management in determining direct nitrous oxide emissions from global rice-based ecosystems, Global Biogeochem. Cy., 37, e2023GB007744, https://doi.org/10.1029/2023GB007744, 2023.')
add('Stumm, W. and Lee', 'Strefler, J., Amann, T., Bauer, N., Kriegler, E., and Hartmann, J.: Potential and costs of carbon dioxide removal by enhanced weathering of rocks, Environ. Res. Lett., 13, 034010, https://doi.org/10.1088/1748-9326/aaa9c4, 2018.')
# Yuan after Yu (last entry): insert before the Figure captions heading would change style, so insert before Yu and move Yu? keep order: Yu < Yuan, so add after Yu
pm, _ = d.find('Yu, Q., You, L.')
yu = pm.group()
d.newpara_before('Figure captions', 'Yuan, Z.-F., Zhou, Y., Chen, Z., Tang, X., Wang, Y., Kappler, A., and Xu, J.: Reduce methane emission from rice paddies by man-made aerenchymatous tissues, Carbon Res., 2, 17, https://doi.org/10.1007/s44246-023-00049-1, 2023.', like=R)
d.rep('[DOI to add]', 'https://doi.org/10.1016/j.ijggc.2012.06.011', pre='Int. J. Greenh. Gas Control, 10, 229–243, ')
d.rep('[DOI to add]', 'https://doi.org/10.1111/j.1574-6941.2010.00856.x', pre='FEMS Microbiol. Ecol., 72, 407–417, ')
d.ins_after('Ind. Eng. Chem., 53, 143–146', ', https://doi.org/10.1021/ie50614a030')
d.rep('[article number to check]', '9734')
# uncited references (GMD: every listed reference must be cited) - tracked deletions, reject to keep
for ctx in ('Amann, T., Hartmann, J.', 'Cain, M., Lynch, J.', 'Conrad, R.: Microbial ecology', 'Huang, L.-M., Jia, X.-X.',
            'Jäckel, U. and Schnell', 'Kölbl, A., Schad, P.', 'Reershemius, T., Kelland'):
    delpara(ctx)
d.save('Riceland_SCEPTER_GMD_Nov2_v2_refs_tc.docx')
print('ok')
