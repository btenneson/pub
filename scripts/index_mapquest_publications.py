"""Keep the uploaded MAPQUEST series and RANSOM in the publication index."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
items = json.loads((root / 'scripts/mapquest_publications.json').read_text())
path = root / 'docs/search-index.json'
data = json.loads(path.read_text())
hrefs = {x['href'] for x in items}
data['items'] = items + [x for x in data['items'] if x['href'] not in hrefs]
data['count'] = len(data['items'])
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
home = root / 'docs/index.html'
html = home.read_text()
link = '<a href="MAPQUEST_Trilogy/">MAPQUEST trilogy · I, II, III</a>'
if link not in html:
    html = html.replace('<nav class="toplinks">', '<nav class="toplinks">' + link, 1)
home.write_text(html)
print('Indexed MAPQUEST I–III and RANSOM; total:', data['count'])
