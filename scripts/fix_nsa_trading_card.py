#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / 'docs' / 'search-index.json'
HOME = ROOT / 'docs' / 'index.html'
HREF = 'papers/nsa_and_trading_speedup/'
QUOTE = ('A hyperfinite witness or advantageous traded presentation is semantic compression; '
         'a speed-up theorem requires a standard extractor, a complete cost model, and a '
         'certificate-preserving return translation.')

payload = json.loads(INDEX.read_text(encoding='utf-8'))
items = payload['items']
lead = next((x for x in items if x.get('href') == HREF), None)
if lead is None:
    raise SystemExit('NSA/trading card missing from search index')
lead['quote'] = QUOTE
lead['quote_attribution'] = 'Brian Tenneson'
lead['pdf'] = ''  # Avoid a dead raw-PDF link; the reader is the canonical public surface for now.
lead['search'] = ' '.join([str(lead.get('search') or ''), QUOTE, 'Brian Tenneson']).strip()
items.remove(lead)
items.insert(0, lead)
payload['count'] = len(items)
INDEX.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

page = HOME.read_text(encoding='utf-8')
data = json.dumps(items, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
page, n = re.subn(r'const DATA=.*?;\nconst q=', lambda _m: 'const DATA=' + data + ';\nconst q=', page, count=1, flags=re.S)
if n != 1:
    raise SystemExit('Could not patch homepage DATA payload')
HOME.write_text(page, encoding='utf-8')
print('NSA/trading card fixed: quote present, reader first, dead PDF link removed')
