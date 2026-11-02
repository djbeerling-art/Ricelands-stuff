# Tracked edits on David's Nov2_v3: Patrick and Jugsujinda (1992) citation order and reference entry.
import sys; sys.path.insert(0, '.')
from tcedit import Doc
d = Doc('Riceland_SCEPTER_GMD_Nov2_v3.docx', '2026-11-02T12:05:00Z')
d.rep('Jugsujinda and Patrick, 1992', 'Patrick and Jugsujinda, 1992')
d.newpara_before('Peng, S., Luo, Y.', 'Patrick, W. H. and Jugsujinda, A.: Sequential reduction and oxidation of inorganic nitrogen, manganese, and iron in flooded soil, Soil Sci. Soc. Am. J., 56, 1071–1073, https://doi.org/10.2136/sssaj1992.03615995005600040011x, 1992.', like='Akiyama, H., Yagi, K., and Yan, X.')
d.save('Riceland_SCEPTER_GMD_Nov2_v3_tc.docx'); print('ok')
