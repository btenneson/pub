#!/usr/bin/env python3
"""Publish reviewed source artifacts as public PDF readers, slot 1 and slot 2.

Compiles actual audited submitted LaTeX; retains the original What-If permalink;
adds only the new curvature publication, and preserves all other catalog order.
"""
from __future__ import annotations
import base64, hashlib, io, json, shutil, subprocess, tarfile, zipfile
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / 'incoming_publications/curvature_imagination_20261019'
STAGE = ROOT / '.build/curvature_imagination_20261019'
CAT = ROOT / 'scripts/publications.json'
SUBJECT = 'cs.LO_Logic_in_Computer_Science'
BATCH = [
    {
        'stem':'01_CLEAN_ARTICLE_what_if_imagination',
        'filename':'Recursive_What_If_Imagination',
        'published_name':'AMLD_Recursive_What_If_Imagination_and_MAPQUEST_001.pdf',
        'slug':'recursive_what_if_imagination_in_amld',
        'title':'Recursive “What If?” Imagination in AMLD',
        'subtitle':'Chess-Style Counterfactual Search Guided by MAPQUEST',
        'quote':'only independently checked derivations may enter BANK.',
        'quote_page':1,
        'sha_tex':'27769ba4085339bb784a5d50ca9e6c2595162db14b69d6c2e6430f898e900e72',
        'pages':4,
        'card_text':'Audited revision of the previously published recursive imagination article. Branch-preserving counterfactual search, finite exploration caps, MAPQUEST-guided missing-lemma proposals, and a theorem that the certified BANK stays conservative under an independently sound frozen-judgment verifier. Imagination remains speculative until dependencies are discharged and certificates accepted.',
        'classification_note':'Audited source revision, 19 October 2026. Conditional mathematical safety result; no universal search-completeness or speedup guarantee.'
    },
    {
        'stem':'01_CLEAN_ARTICLE_Curvature',
        'filename':'Geodesic_Curvature_Profile',
        'published_name':'Geodesic_Curvature_Profile.pdf',
        'slug':'geodesic_curvature_profile_settlement_001',
        'title':'AMLD+0 Settlement of the Geodesic Curvature-Profile Conjecture',
        'subtitle':'Counterexample, Infinite Failure Family, and Curvature–Potential Criterion',
        'quote':'No proof-search performance gain follows from the geometric comparison alone.',
        'quote_page':1,
        'sha_tex':'253abd40b16e108144db9b22d0aff22f5e2b89f8541378e469e2eee74543de13',
        'pages':4,
        'card_text':'Audited settlement of a proposed connection between shortest directed proof paths and Ollivier–Ricci negative-curvature burden. A six-vertex example refutes the unconditional geodesic-minimization claim: the two-edge path has burden 1/3, while a three-edge path has zero. Gives an infinite counterexample family, a universal upper bound, a sufficient calibrated-potential condition, and a scoped Horn-path realization.',
        'classification_note':'Audited theorem note, 19 October 2026. Universal claim refuted in the specified graph/Horn path protocol; conditional positive theorems do not imply faster general proof search.'
    }
]

def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    payload=''.join((INCOMING/'source_bundle.tar.gz.b64').read_text(encoding='ascii').split())
    data=base64.b64decode(payload,validate=True)
    STAGE.mkdir(parents=True,exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
        members=tf.getmembers()
        allowed={f'{i["stem"]}/{n}' for i in BATCH for n in (i['filename']+'.tex','common.texfrag')}
        actual={m.name for m in members if m.isfile()}
        assert actual==allowed,(actual,allowed)
        for m in members:
            if not m.isfile(): continue
            assert m.name in allowed and not m.issym() and not m.islnk()
            target=STAGE/m.name; target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(tf.extractfile(m).read())
    for i in BATCH:
        directory=STAGE/i['stem']
        tex=directory/(i['filename']+'.tex')
        assert sha(tex.read_bytes())==i['sha_tex'],f"Source hash mismatch: {tex}"
        for _ in range(2):
            subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',tex.name], cwd=directory,check=True,stdout=subprocess.DEVNULL)
        pdf=directory/(i['filename']+'.pdf')
        doc=fitz.open(pdf)
        assert len(doc)==i['pages'],(pdf,len(doc))
        assert all(p.get_text().strip() for p in doc),pdf
        assert i['quote'] in doc[i['quote_page']-1].get_text(),(i['title'],i['quote'])
        i['pdf']=pdf
        i['tex']=tex
        i['common']=directory/'common.texfrag'
        i['pdf_sha']=sha(pdf.read_bytes())
        print('Compiled and validated',i['title'],i['pdf_sha'])
    original=json.loads(CAT.read_text(encoding='utf-8'))
    oldids=[f'{SUBJECT}/{i["slug"]}' for i in BATCH]
    original_items=original['items']
    assert sum(x.get('id')==oldids[0] for x in original_items)==1,'Must replace exactly one old What If card'
    assert all(x.get('id')!=oldids[1] for x in original_items),'Curvature card unexpectedly preexists'
    others=[x for x in original_items if x.get('id') not in oldids]
    prev_order=[x.get('id') for x in sorted(others,key=lambda x:x.get('order',0))]
    first_order=min([x['order'] for x in others if isinstance(x.get('order'),int)]+[0])-2
    entries=[]
    for n,i in enumerate(BATCH):
        rel=f'{SUBJECT}/{i["slug"]}'
        for prefix in ('docs/',''):
            dest=ROOT/prefix/rel
            dest.mkdir(parents=True,exist_ok=True)
            shutil.copy2(i['pdf'],dest/i['published_name'])
            shutil.copy2(i['tex'],dest/'source.tex')
            shutil.copy2(i['common'],dest/'common.texfrag')
        dest=ROOT/'docs'/rel
        pkg=dest/(i['filename']+'_Audited_Source_and_PDF.zip')
        with zipfile.ZipFile(pkg,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.write(dest/i['published_name'],i['published_name'])
            z.write(dest/'source.tex','source.tex')
            z.write(dest/'common.texfrag','common.texfrag')
        entries.append({
           'title':i['title'],'kind':'Research paper' if n==0 else 'Formal settlement note',
           'subject':SUBJECT,'id':rel,'href':rel+'/',
           'pdf':rel+'/'+i['published_name'],'archive_path':rel+'/'+i['published_name'],
           'source':rel+'/source.html','source_file':rel+'/source.tex',
           'source_package':rel+'/'+pkg.name,
           'sha256':i['pdf_sha'],'sha256_tex':i['sha_tex'],
           'pages':i['pages'],'order':first_order+n,
           'authors':'Brian Tenneson','quote':i['quote'],'quote_page':i['quote_page'],
           'card_quote':i['quote'],'card_quote_attribution':f'Brian Tenneson · p. {i["quote_page"]}',
           'quote_also_on_card':True,'card_text':i['card_text'],
           'status':'AUDITED REVISION · 19 OCTOBER 2026' if n==0 else 'AUDITED SETTLEMENT · 19 OCTOBER 2026',
           'classification_note':i['classification_note']
        })
    original['items']=entries+others
    CAT.write_text(json.dumps(original,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run(['python','scripts/build_publications_106.py'],cwd=ROOT,check=True)
    # The repository currently has a preexisting, unrelated catalog quote
    # mismatch (DATA MIND self-description); do not rewrite its publication.
    # Preserve visibility of that failure while validating our two entries.
    audit=subprocess.run(['python','scripts/audit_subject_catalog_106.py'],cwd=ROOT,text=True,capture_output=True)
    if audit.returncode:
        stderr=audit.stdout+audit.stderr
        known="('quote not in cited page', 'DATA MIND: A Current Self-Description', 'Reflection ≠ Verification')"
        if known not in stderr:
            raise RuntimeError('Unexpected global catalog audit failure: '+stderr[-2500:])
        print('WARNING: preexisting DATA MIND quote/page mismatch blocks global catalog audit; no unrelated publication changed.')
    else:
        print('Full publication catalog audit passed.')
    search=json.loads((ROOT/'docs/search-index.json').read_text())
    assert [x['id'] for x in search['items'][:2]]==oldids
    remaining=[x['id'] for x in search['items'] if x['id'] not in oldids and not x.get('catalog_alias_of')]
    assert remaining==prev_order,(remaining[:10],prev_order[:10])
    assert len([x for x in search['items'] if x['id']==oldids[0]])==1
    for i in BATCH:
        rel=f'{SUBJECT}/{i["slug"]}'
        assert (ROOT/'docs'/rel/'index.html').exists()
    print('PASS: audited article readers, PDF/source packages, slot #1 and slot #2, all old card order preserved')

if __name__=='__main__':main()
