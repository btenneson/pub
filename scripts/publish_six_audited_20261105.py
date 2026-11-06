#!/usr/bin/env python3
"""Publish exactly six audited PDFs at library slots 1-6 without disturbing existing cards."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys
R=Path(__file__).resolve().parents[1]
STAGE=R/'incoming_publications/six_final_audited_20261105'
D=R/'docs'
CAT=R/'scripts/publications.json'
SUBJECT='cs.LO_Logic_in_Computer_Science'
SPECS=json.loads(r'''[["the_trading_theorem_for_sic_formal_systems_v2_0","Trading_Theorem_SIC_Source_v0_1v2.0(2).pdf","5620626c2f018b9be6f033115251b1ab162aef98a78fd487b74df928049141b9",8,"The Trading Theorem for SIC Formal Systems","Audited study of hypothesis-to-rule trading, context-safe two-sided proof simulation, deductive isomorphisms, SIC-state transport, and boundaries of induction handoff.","Moving an assumed formula into a zero-premise rule is unconditional.",1,"Audited mathematical research edition v2.0. No independent machine checking or search-cost advantage is claimed."],["hilbert_filled_inference_spaces_gbgplus_player0_v2_0","HFIS_GBGplus_Player0_Research_Edition_1_0(2)v2.0(2).pdf","e11f8ffc74afeabe8e83fcd42c22480b8d41a18c61deffe6a51f3147372b1d4a",17,"Hilbert-Filled Inference Spaces for Automated Theorem Proving","Hilbert-directed proof-search scheduling, generalized board games, Player-0 control, fair proof discovery, and limits of finite-budget search.","Traversal is a permutation of a finite action list; it does not create inference legality",3,"Integrated research edition v2.0, mathematical repair. Historical prototype claims are not independently reproduced."],["certified_multiarticle_intertwining_six_low_fan_in_shells","Certified_Multiarticle_Intertwining_Six_Low_Fan_In_Shells(2).pdf","fdcb270d2a7e19fbab67136e2a87e0581d566ddbf607a187a11115040f375aab",11,"Certified Multiarticle Intertwining: Six Proof-Carrying Low-Fan-In Shells","Four-island proof-bearing Multiarticle integration across GBG, MUSIC, SYMPHONY, and TISO. Includes six conditional bridge layers and a counterexample separating possibilities from certified performances.","A name shared by two articles is not a proof of such compatibility.",2,"Research exposition with conditional paper-level proofs; no running federation or J4 settlement claimed."],["trading_intuition_and_return_v2_0","Trading_Intuition_and_Return_0_1_REGENERATED(5)v2.0(4).pdf","1a2faf5931099b483d84dcd18f5bf90e5d8ab1d9440de7a406fd78ddf2b610cb",9,"Trading, Intuition, and Return","Context-preserving proof translation between first-order Hilbert systems and an MP-only presentation, followed by theoremgraph-guided certified return and finite obligation antichains.","A candidate dependency graph is not a proof by itself.",2,"ATLAS-audited research edition v2.0, with repaired certification diagram; no independent formal proof certificate."],["four_island_multiarticle_tiso_gbg_attained_labels_j4","Four_Island_Multiarticle_TISO_GBG_Attained_Labels_J4(3).pdf","315ad5a859c58cd2173f2693d100fc39fd70737b1c6e8a4112fe460819fd9ca3",11,"A Four-Island Multiarticle: TISO, Certified GBG Self-Embeddings, Undecidable Attainment, and J4","Typed synthesis of resource allocation, generalized board game self-embeddings, undecidable attained labels, and the J4 interface. Separates navigation improvements from physical theoremhood.","An optimized search policy is not itself a proof of a physical statement.",3,"Research draft 0.1, with paper-level arguments; the J4 physical problem is not claimed solved."],["amld000_multiarticle_trading_quotient_basin_escape_v1_0","AMLD000_Multiarticle_Trading_Quotient_Basin_Escape_Expository_v1_0(1).pdf","0b98e98cc1743c1ab6fc5b6e2f6743b8b8649fd382b229ca8574d27a74eb0758",13,"A Limited Multiarticle Example of AMLD Settlement","Worked finite-checked synthetic example of MP trading, quotient hunting, proof-carrying return, chess-style reachability, and informal basin escape, separating the restricted model from general speedup claims.","A representation may change proof length, search branching, or the cost of producing a certificate without changing the underlying consequence relation.",2,"Limited research exposition v1.0; finite local checks, no live federation and no general basin-escape speedup theorem."]]''')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    data=json.loads(CAT.read_text(encoding='utf-8'))
    original=data['items']
    prior_ids=[x['id'] for x in original]
    assert len(prior_ids)==len(set(prior_ids)), 'Pre-existing publication IDs are not unique'
    ids=[SUBJECT+'/'+s[0] for s in SPECS]
    existing=[x for x in ids if x in prior_ids]
    if existing:
        if len(existing)!=6 or prior_ids[:6]!=ids:
            raise RuntimeError('Partial or out-of-order prior publication: '+repr(existing))
        for s in SPECS:
            p=D/SUBJECT/s[0]/s[1]
            assert p.is_file() and digest(p)==s[2], p
        print('PASS: already published with six consecutive cards and exact audited PDF hashes')
        return
    if not STAGE.is_dir():
        raise RuntimeError('Missing six-PDF staged directory')
    for s in SPECS:
        pdf=STAGE/s[1]
        assert pdf.is_file() and pdf.stat().st_size>50000 and pdf.read_bytes()[:5]==b'%PDF-', pdf
        assert digest(pdf)==s[2], ('AUDITED PDF HASH MISMATCH',pdf)
        assert not (D/SUBJECT/s[0]).exists(), ('Refusing to overwrite existing reader',s[0])
    old_order=min((float(x['order']) for x in original if isinstance(x.get('order'),(int,float))),default=0)
    new=[]
    for i,s in enumerate(SPECS):
        slug,filename,sha,pages,title,description,quote,quote_page,status=s
        ident=SUBJECT+'/'+slug
        rel=ident+'/'+filename
        dst=D/rel
        dst.parent.mkdir(parents=True,exist_ok=False)
        shutil.copyfile(STAGE/filename,dst)
        assert digest(dst)==sha
        new.append(dict(
            id=ident,href=ident+'/',subject=SUBJECT,title=title,kind='Research paper',
            authors='<Brian Tenneson>',pdf=rel,archive_path='docs/'+rel,
            card_text=description,quote=quote,quote_page=quote_page,
            quote_attribution=title+' · p. '+str(quote_page),quote_also_on_card=True,
            classification_note=('Published 5 November 2026 from its exact final-audited PDF. '
                'AI-assisted drafting/auditing and verification boundaries are disclosed within the paper. '
                'Independent formal proof certification is not implied.'),
            publication_date='5 November 2026',status=status,pages=pages,sha256=sha,
            order=old_order-6+i))
    data['items']=new+original
    CAT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    subprocess.run([sys.executable,'scripts/build_publications_106.py'],cwd=R,check=True)
    subprocess.run([sys.executable,'scripts/audit_subject_catalog_106.py'],cwd=R,check=True)
    after=json.loads(CAT.read_text(encoding='utf-8'))['items']
    assert [x['id'] for x in after[:6]]==ids
    assert [x['id'] for x in after[6:]]==prior_ids
    for page in (D/'index.html',D/SUBJECT/'index.html'):
        content=page.read_text(encoding='utf-8')
        positions=[content.find('/pub/'+id+'/') for id in ids]
        assert all(x>=0 for x in positions) and positions==sorted(positions),('Card order failed',page)
        first_existing=content.find('/pub/'+prior_ids[0]+'/')
        assert positions[-1]<first_existing,('Pre-existing cards were not shifted',page)
    for s in SPECS:
        p=D/SUBJECT/s[0]
        assert (p/'index.html').is_file()
        assert digest(p/s[1])==s[2]
    shutil.rmtree(STAGE)
    print('PASS: six distinct publication cards at slots 1..6, no gaps; old order preserved; source PDFs verified')
if __name__=='__main__':
    main()
