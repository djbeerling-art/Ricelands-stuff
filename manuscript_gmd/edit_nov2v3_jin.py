# Tracked edits on David's Nov2_v3_tc (N:C sentence): Jin et al. (2020) reference entry; ratio notation.
import sys; sys.path.insert(0, '.')
from tcedit import Doc
d = Doc('Riceland_SCEPTER_GMD_Nov2_v3_tc_DB.docx', '2026-11-02T12:10:00Z')
d.rep('molar N ratio of 0.03 (C = 33:1)', 'molar N:C ratio of 0.03 (C:N ≈ 33)')
d.newpara_before('Jones, A. M., Collins', 'Jin, Z., Shah, T., Zhang, L., Liu, H., Peng, S., and Nie, L.: Effect of straw returning on soil organic carbon in rice–wheat rotation system: a review, Food Energy Secur., 9, e200, https://doi.org/10.1002/fes3.200, 2020.', like='Akiyama, H., Yagi, K., and Yan, X.')
d.save('Riceland_SCEPTER_GMD_Nov2_v3_tc2.docx'); print('ok')
d2 = Doc('Riceland_SCEPTER_GMD_Nov2_v3_tc2.docx', '2026-11-02T12:15:00Z')
d2.rep('(Sect. 2.7)', '(Sect. A7)', pre='retained in the v25b simulations reported here ')
d2.save('Riceland_SCEPTER_GMD_Nov2_v3_tc2.docx'); print('ok2')
