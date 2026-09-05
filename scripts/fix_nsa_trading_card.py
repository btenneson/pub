#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / 'docs' / 'search-index.json'
OLD_HREF = 'papers/nsa_and_trading_speedup/'
NEW_HREF = 'cs.LO_Logic_in_Computer_Science/nsa_and_trading_speedup/'
QUOTE = ('A hyperfinite witness or advantageous traded presentation is semantic compression; '
         'a speed-up theorem requires a standard extractor, a complete cost model, and a '
         'certificate-preserving return translation.')

payload = json.loads(INDEX.read_text(encoding='utf-8'))
items = payload['items']
lead = next((
    x for x in items
    if x.get('href') in {OLD_HREF, NEW_HREF}
    or x.get('archive_path') == 'cs.LO_Logic_in_Computer_Science/nsa_and_trading_speedup.pdf'
), None)
if lead is None:
    raise SystemExit('NSA/trading card missing from search index')
lead['href'] = NEW_HREF
lead['quote'] = QUOTE
lead['quote_attribution'] = 'Brian Tenneson'
lead['pdf'] = ''  # Reader is the canonical public surface; avoid a dead raw-PDF link.
lead['source'] = ''
lead['archive_path'] = 'cs.LO_Logic_in_Computer_Science/nsa_and_trading_speedup/'
lead['search'] = ' '.join([str(lead.get('search') or ''), QUOTE, NEW_HREF, 'Brian Tenneson']).strip()
payload['count'] = len(items)
INDEX.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('NSA/trading card fixed: reader path moved out of papers, quote present, dead PDF link removed')
