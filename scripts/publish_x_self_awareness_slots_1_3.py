#!/usr/bin/env python3
"""Publish X0, X1, X2 as *separate* articles in the first three library slots.

The authorized, reviewed LaTeX inputs are staged in incoming_publications.
Build and verify all three PDFs *before* changing any catalog entries.  Preserve
all pre-existing cards and their relative order; no combined volume is created.
"""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
SUBJECT='cs.LO_Logic_in_Computer_Science'
STAGE=ROOT/'incoming_publications/x_self_awareness_20261031'
BUILD=ROOT/'.build/x_self_awareness_20261031'
CATALOG=ROOT/'scripts/publications.json'
DOCS=ROOT/'docs'
NAMES=('X0','X1','X2')
SLUGS={
 'X0':'formal_self_awareness_semi_ideal_computers_x0',
 'X1':'evidence_geometry_formal_self_awareness_x1',
 'X2':'horizon_certified_memory_x2',
}
TITLES={
 'X0':'Formal Self-Awareness in Semi-Ideal Computers',
 'X1':'The Evidence Geometry of Formal Self-Awareness',
 'X2':'The Horizon of Certified Memory',
}
QUOTES={
 'X0':('A name, a stream of outputs, and a self-theory are different mathematical objects.',9),
 'X1':('A self-ascription, an accepted derivation, and a recoverable receipt are different data.',3),
 'X2':('The disappearing obligations, not a magical compression routine, justify the memory shedding.',7),
}
PAGES={'X0':24,'X1':20,'X2':19}
DESCRIPTIONS={
 'X0': 'Part I of a three-article research sequence. Defines tagged self-theories for semi-ideal computers, distinguishes assertion from checked proof and semantic truth, develops reflection levels including a conditional unbounded construction, and proves self-awareness transfer under declared tag, quotation, and certificate hypotheses. Retrospective prior-art citations and an explicit originality ledger are included.',
 'X1': 'Part II. Builds a typed, witness-complete hierarchy of linked proof receipts and an exact residual-equivalence model for deterministic certified-history monitors. Develops conditional preservation of reflective observations and charged hitting costs, with finite stabilization, a sixteen-state delayed-distinction witness, and certificate-preserving transfers.',
 'X2': 'Part III. Studies bounded future verification duties through observational horizon partitions, a class-index bit bound under a free shared decoder, online countdown forgetting, task-portfolio metadata increments, and safety conditions for coupling external proof checkers. Clearly distinguishes idealized identifiers from authentic proof-certificate storage.',
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def command(cmd,cwd):
    subprocess.run(cmd,cwd=cwd,check=True,stdout=subprocess.DEVNULL)

def compile_tex(name):
    src=BUILD/name
    for _ in range(5):
        command(['pdflatex','-interaction=nonstopmode','-halt-on-error',name],BUILD)
    pdf=src.with_suffix('.pdf')
    assert pdf.is_file() and pdf.read_bytes().startswith(b'%PDF-'),name
    return pdf

def main():
    import fitz
    assert CATALOG.is_file() and STAGE.is_dir(), 'Publication source/catalog missing'
    BUILD.mkdir(parents=True,exist_ok=True)
    for p in STAGE.glob('*.tex'):
        shutil.copy2(p,BUILD/p.name)
    for f in ('W0_Original_Source.tex','W0_Editorial_Figures_Repaired.tex','X0_Publication_Repaired.tex','X1_Publication_Repaired.tex','X2_Publication_Repaired.tex'):
        assert (BUILD/f).is_file(),f
    # The unmodified W0 source is retained as provenance, while editorial
    # figure geometry is compiled into the X0 source-page facsimile.
    assert sha(BUILD/'W0_Original_Source.tex') != sha(BUILD/'W0_Editorial_Figures_Repaired.tex')
    srcpdf=compile_tex('W0_Editorial_Figures_Repaired.tex')
    assert len(fitz.open(srcpdf))==19, 'W0 source facsimile should have 19 pages'
    pdfs={}
    for name in NAMES:
        text=(BUILD/(name+'_Publication_Repaired.tex')).read_text(encoding='utf-8')
        assert r'\end{document}' in text and 'See the AI disclaimer that follows this essay.' in text,name
        assert '<Brian Tenneson>' in text or r'\AuthorExact' in text,name
        pdf=compile_tex(name+'_Publication_Repaired.tex')
        doc=fitz.open(pdf)
        assert len(doc)==PAGES[name],(name,len(doc),PAGES[name])
        assert all(p.get_text().strip() for p in doc), 'Unreadable PDF page: '+name
        assert 'Disclaimer on Mathematical Accuracy' in doc[-1].get_text(), name
        assert 'See the AI disclaimer that follows this essay.' in doc[0].get_text(),name
        quote,page=QUOTES[name]
        normalized=' '.join(doc[page-1].get_text().split())
        assert quote in normalized,(name,page,quote)
        assert '<Brian Tenneson>' in doc[0].get_text(),name
        assert doc[1].get_text().count('Contents')>=1 if name in ('X1','X2') else True, 'TOC page missing'
        assert len(doc.get_toc())>=1, 'PDF bookmarks missing: '+name
        doc.close()
        pdfs[name]=pdf
    # Build all three cards only AFTER every PDF and source passes.
    catalog=json.loads(CATALOG.read_text(encoding='utf-8'))
    old=list(catalog['items'])
    ids=[x['id'] for x in old]
    newids=[SUBJECT+'/'+SLUGS[n] for n in NAMES]
    assert len(ids)==len(set(ids)) and not (set(ids)&set(newids)), 'Duplicate/existing article card'
    min_order=min(x['order'] for x in old if isinstance(x.get('order'),(int,float)))
    records=[]
    for i,name in enumerate(NAMES):
        slug=SUBJECT+'/'+SLUGS[name]
        dest=DOCS/slug
        dest.mkdir(parents=True,exist_ok=True)
        pdfname=name+'_Publication_Repaired.pdf'
        shutil.copyfile(pdfs[name],dest/pdfname)
        shutil.copyfile(BUILD/(name+'_Publication_Repaired.tex'),dest/'source.tex')
        if name=='X0':
            shutil.copyfile(BUILD/'W0_Original_Source.tex',dest/'W0_Original_Source.tex')
            shutil.copyfile(BUILD/'W0_Editorial_Figures_Repaired.tex',dest/'W0_Editorial_Figures_Repaired.tex')
            shutil.copyfile(srcpdf,dest/'W0_Editorial_Figures_Repaired.pdf')
        quote,page=QUOTES[name]
        record={
          'id':slug,'href':slug+'/','title':TITLES[name],
          'kind':'Research paper','subject':SUBJECT,'authors':'<Brian Tenneson>',
          'pdf':slug+'/'+pdfname,'archive_path':'docs/'+slug+'/'+pdfname,
          'source':slug+'/source.html','source_file':slug+'/source.tex',
          'card_text':DESCRIPTIONS[name],
          'quote':quote,'quote_page':page,'quote_attribution':TITLES[name]+', p. '+str(page),
          'quote_also_on_card':True,
          'publication_date':'31 October 2026',
          'classification_note':('Authorized separate publication, 31 October 2026. Part '+str(i+1)+' of 3. '+
             'Earlier mathematical works and non-original prior results are attributed in the article. '+
             ('X0 source pages are regenerated from the preserved original W0 LaTeX with editorial diagram repairs. ' if name=='X0' else '')+
             'Pre-publication disclaimers in the source describe an earlier preparation stage.'),
          'status':('ATLAS manuscript review and re-audit completed with conditional, paper-level findings. '+
             'Not an independently machine-checked proof or external peer review.'),
          'pages':PAGES[name],'sha256':sha(dest/pdfname),
          'order':min_order-30+i*10,
        }
        records.append(record)
    catalog['items']=records+old
    CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Force fresh main and subject catalog page generation without touching
    # existing old publication reader pages or altering their identifiers.
    for path in (DOCS/'index.html',DOCS/SUBJECT/'index.html'):
        if path.exists():path.unlink()
    command([sys.executable,'scripts/build_publications_106.py'],ROOT)
    for path in (DOCS/'index.html',DOCS/SUBJECT/'index.html'):
        page=path.read_text(encoding='utf-8')
        matches=re.findall(r'<article class="card"[^>]*><h2><a href="([^"]+)"',page)
        expected=['/pub/'+id+'/' for id in newids]
        assert matches[:3]==expected,('Wrong top slots',path,matches[:4])
        assert matches[3]=='/pub/'+old[0]['id']+'/',('Original slot one must now be four',path)
    check=json.loads(CATALOG.read_text())['items']
    assert [x['id'] for x in check[3:]]==ids,'Old catalog order modified'
    for name in NAMES:
        d=DOCS/SUBJECT/SLUGS[name]
        assert (d/'index.html').exists() and (d/'source.html').exists()
    command([sys.executable,'scripts/audit_subject_catalog_106.py'],ROOT)
    print('PASS: Published X0, X1, X2 in slots 1, 2, 3; original slot 1 is slot 4; all other entries retain their original order.')
    print('PDF SHA256:',{n:sha(pdfs[n]) for n in NAMES})

if __name__=='__main__':main()