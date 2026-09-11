"""Keep MAPQUEST/RANSOM indexed and make Universal Theorem Geometry I card #1."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
search_path = root / 'docs/search-index.json'
home_path = root / 'docs/index.html'

UTG_TITLE = 'Universal Theorem Geometry I'
UTG_HREF = 'papers/universal_theorem_geometry_i_001/Universal_Theorem_Geometry_I_Corrected.pdf'
UTG_ARCHIVE = 'cs.LO_Logic_in_Computer_Science/Universal_Theorem_Geometry_I.pdf'
UTG = {
    'title': UTG_TITLE,
    'kind': 'Core paper',
    'category': 'Logic & Automated Reasoning',
    'tags': ['theorem space', 'proof geometry', 'automated theorem proving'],
    'href': UTG_HREF,
    'pdf': '',
    'source': '',
    'archive_path': UTG_ARCHIVE,
    'search': (
        'Universal Theorem Geometry I theorem space proof geometry automated theorem proving '
        'fibered tagged variable-dimensional directed hypergraph Hilbert-addressable inference geometry '
        + UTG_ARCHIVE
    ),
    'pin_label': 'Pinned card #1',
    'pinned': True,
}

# Preserve the explicitly curated MAPQUEST trilogy and RANSOM records.
mapquest_items = json.loads((root / 'scripts/mapquest_publications.json').read_text(encoding='utf-8'))
data = json.loads(search_path.read_text(encoding='utf-8'))

# Remove any automatically generated duplicate of Universal Theorem Geometry I,
# then put the canonical UTG record first in the search index as well.
def is_utg(item):
    return (
        item.get('title') == UTG_TITLE
        or item.get('archive_path') == UTG_ARCHIVE
        or item.get('href') == UTG_HREF
    )

rest = [x for x in data['items'] if not is_utg(x)]
mapquest_hrefs = {x['href'] for x in mapquest_items}
rest = [x for x in rest if x.get('href') not in mapquest_hrefs]
data['items'] = [dict(UTG)] + mapquest_items + rest
data['count'] = len(data['items'])
search_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# The live homepage prepends a separate FEATURED object before search-index data.
# Replace that object so the actual visible card #1 is Universal Theorem Geometry I.
html = home_path.read_text(encoding='utf-8')
featured_json = json.dumps(UTG, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html, n = re.subn(
    r'const FEATURED=\{.*?\};\nconst COMPANION=',
    lambda _m: 'const FEATURED=' + featured_json + ';\nconst COMPANION=',
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError('Could not replace homepage FEATURED card')

link = '<a href="MAPQUEST_Trilogy/">MAPQUEST trilogy · I, II, III</a>'
if link not in html:
    html = html.replace('<nav class="toplinks">', '<nav class="toplinks">' + link, 1)
home_path.write_text(html, encoding='utf-8')

print('Card #1:', UTG_TITLE)
print('Indexed MAPQUEST I–III and RANSOM; total:', data['count'])
