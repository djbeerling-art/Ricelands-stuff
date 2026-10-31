import sys
src=open('../ms/edit.py').read().split('# ---------------- edits')[0]
sys.argv=['x','ms.docx','ms_tracked.docx']
exec(src)
# in-text
sub(8,'; Beerling et al., 2020)','; Beerling et al., 2018, 2020)')
sub(8,'(this study; Hartmann and ','(this study, combining the MapSPAM rice areas of Yu et al., 2020, with the GLiM lithology of Hartmann and ')
sub(9,'where soil Si supply is inadequate.','where soil Si supply is inadequate (Ma and Yamaji, 2006).')
sub(41,'other microbial pathways.','other microbial pathways (Segers, 1998).')
sub(43,'Fe₃(OH)₈-type phase,','Fe₃(OH)₈-type phase (Ponnamperuma, 1972),')
sub(44,'times more slowly)','times more slowly; Roden and Zachara, 1996)')
sub(75,'AWD applies weekly drains to a 0.15 m water-table depth after the first month.',
 'Managed alternate wetting and drying (AWD) is imposed as a prescribed schedule: after day 29, drains of 7.3 d to a 0.15 m water-table depth alternate with 14.6 d of reflooding. Rainfed archetypes use the same numerical schedule as a prescribed intermittent-flooding regime; it is not driven by simulated rainfall, so it stands in for rain-fed wetting and drying without representing rainfall or irrigation decisions mechanistically.')
sub(105,'GEOROC basalt analyses;','GEOROC basalt analyses (Lehnert et al., 2000);')
sub(105,'Rainfed archetypes are run with alternate wetting and drying, irrigated ones continuously flooded with a 14-day pre-harvest drain.',
 'Rainfed archetypes are run with a prescribed intermittent-flooding schedule (the AWD drain–reflood schedule of Sect. 2.6.2, not driven by simulated rainfall) and irrigated ones are continuously flooded; both end with a 14-day pre-harvest drain.')
sub(105,'SoilGrids','SoilGrids; Poggio et al., 2021')
sub(113,'Fig. ?','Fig. 6b3; inorganic-carbon terms in Fig. 7')

sub(5,'refine model predictions','refine model predictions.')
sub(12,'(Huang et al., 2004), ','(Huang et al., 2004), simulate ')
sub(16,'in rice soils under','rice soils under')
sub(33,' (vanCappellen',''); sub(33,'1996;Hunter1998;Maggi',''); sub(33,'2008)','')
sub(50,'given ','given')
sub(87,'most rate constants keep literature values (Appendix A).','most rate constants keep literature values (Table 1; Appendix A).')
sub(102,'six rice-soil archetypes,','six rice-soil archetypes (Table 2),')
sub(189,'Scepter','SCEPTER')
sub(191,'Riceland Scepter','Riceland SCEPTER')

T0=d.tables[0]
sub(-1,'1860 yr⁻¹','1860 mol m⁻³ yr⁻¹',p=T0.rows[1].cells[1].paragraphs[0])
sub(-1,'300 yr⁻¹, 5.5','300 mol m⁻³ yr⁻¹, pH₅₀ 5.5',p=T0.rows[6].cells[1].paragraphs[0])
T1=d.tables[1]
for r in (1,4,6): sub(-1,'Rainfed, AWD','Rainfed, intermittent',p=T1.rows[r].cells[3].paragraphs[0])
# references
R={
'hart13':'Hartmann, J., West, A. J., Renforth, P., Köhler, P., De La Rocha, C. L., Wolf-Gladrow, D. A., Dürr, H. H., and Scheffran, J.: Enhanced chemical weathering as a geoengineering strategy to reduce atmospheric carbon dioxide, supply nutrients, and mitigate ocean acidification, Rev. Geophys., 51, 113–149, https://doi.org/10.1002/rog.20004, 2013.',
'huang18':'Huang, L.-M., Jia, X.-X., Zhang, G.-L., Thompson, A., Huang, F., Shao, M.-A., and Chen, L.-M.: Variations and controls of iron oxides and isotope compositions during paddy soil evolution over a millennial time scale, Chem. Geol., 476, 340–351, [DOI to add], 2018.',
'hunter':'Hunter, K. S., Wang, Y., and Van Cappellen, P.: Kinetic modeling of microbially-driven redox chemistry of subsurface environments: coupling transport, microbial metabolism and geochemistry, J. Hydrol., 209, 53–80, https://doi.org/10.1016/S0022-1694(98)00157-7, 1998.',
'lehnert':'Lehnert, K., Su, Y., Langmuir, C. H., Sarbas, B., and Nohl, U.: A global geochemical database structure for rocks, Geochem. Geophy. Geosy., 1, 1012, https://doi.org/10.1029/1999GC000026, 2000.',
'ma':'Ma, J. F. and Yamaji, N.: Silicon uptake and accumulation in higher plants, Trends Plant Sci., 11, 392–397, https://doi.org/10.1016/j.tplants.2006.06.007, 2006.',
'plan':'Planavsky, N. J., Woollen, B. J., Milliken, E., Kanzaki, Y., Fakhraee, M., Beerling, D. J., and Reinhard, C. T.: Bridging carbon removal time lags in agricultural enhanced weathering via methane emission reduction, Environ. Res. Lett., 21, 121002, https://doi.org/10.1088/1748-9326/ae74e7, 2026.',
'poggio':'Poggio, L., de Sousa, L. M., Batjes, N. H., Heuvelink, G. B. M., Kempen, B., Ribeiro, E., and Rossiter, D.: SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty, SOIL, 7, 217–240, https://doi.org/10.5194/soil-7-217-2021, 2021.',
'roden':'Roden, E. E. and Zachara, J. M.: Microbial reduction of crystalline iron(III) oxides: influence of oxide surface area and potential for cell growth, Environ. Sci. Technol., 30, 1618–1628, https://doi.org/10.1021/es9506216, 1996.',
'segers':'Segers, R.: Methane production and methane consumption: a review of processes underlying wetland methane fluxes, Biogeochemistry, 41, 23–51, https://doi.org/10.1023/A:1005929032764, 1998.',
'vcw':'Van Cappellen, P. and Wang, Y.: Cycling of iron and manganese in surface sediments: a general theory for the coupled transport and reaction of carbon, oxygen, nitrogen, sulfur, iron, and manganese, Am. J. Sci., 296, 197–243, https://doi.org/10.2475/ajs.296.3.197, 1996.',
}
insert_after(163,R['huang18']); insert_after(163,R['hart13'])
insert_after(164,R['hunter'])
insert_after(170,R['ma']); insert_after(170,R['lehnert'])
delete_par(171)
insert_after(174,R['poggio']); insert_after(174,R['plan'])
insert_after(175,R['roden'])
insert_after(176,R['segers'])
insert_after(179,R['vcw'])
delete_par(185)
d.save(OUT); print('\n'.join(log))
