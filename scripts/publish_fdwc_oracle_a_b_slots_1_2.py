#!/usr/bin/env python3
"""Publish both ATLAS repaired FDWC alternatives into the first two library slots."""
from pathlib import Path
import hashlib, json, shutil, subprocess, re
import fitz

ROOT=Path(__file__).resolve().parents[1]
SUB='cs.LO_Logic_in_Computer_Science'
CATALOG=ROOT/'scripts/publications.json'
STAGING=ROOT/'incoming_publications/oracle_attested_fdwc_1_1'
FDWC_TEXT="""For the following two documents, I used a technique I wrote I call the discrete completion which is loosely based on the Cauchy completion except for writing. Here is ChatGPT's description of my private prompt to initiate the writing completion protocol I wrote for OpenAI:

### What Finite Discrete Writing Completion (FDWC) Does

Finite Discrete Writing Completion (FDWC) is a systematic method for developing an existing mathematical manuscript into more complete, rigorous, and intellectually productive forms while preserving its mathematical identity.

The process treats the original manuscript as a fixed point of reference rather than something to be replaced. It examines the mathematical content for incomplete arguments, missing definitions, unstated assumptions, logical weaknesses, unexplored consequences, and opportunities for further development.

Rather than merely correcting errors or improving prose, FDWC attempts to increase the mathematical substance of the work. This may involve completing proofs, deriving additional propositions, identifying relationships among existing results, constructing examples and counterexamples, strengthening definitions, and developing new mathematical insights that arise naturally from the original theory.

A distinctive feature is that completion need not have a unique outcome. Different mathematically legitimate developments may emphasize different strengths, reveal different consequences, or pursue different directions. FDWC therefore explores alternative completed manuscripts and evaluates their relative mathematical and expository merits without assuming that one must dominate all others.

Throughout the process, established results are distinguished from conjectures, proposed extensions, and claims requiring further verification. Corrections and substantive changes remain traceable to the original work.

The term completion is analogous in spirit to mathematical completion constructions, but it does not assert metric convergence, uniqueness, or the existence of a universally maximal manuscript. Instead, it describes a controlled process of discrete intellectual enlargement, in which a mathematical work acquires additional rigor, structure, explanatory power, and deductive consequences.

**The objective is not simply to make a paper longer. It is to discover and develop mathematical content that the original paper supports but has not yet fully expressed.**"""

PAPERS=[
 {
  'key':'A',
  'slug':'oracle_attested_mathematical_knowledge_fdwc_a_typed_evidence_calculus_1_1',
  'title':'Oracle-Attested Mathematical Knowledge — Completion A: A Typed Evidence Calculus for Blind Relays, Source Deactivation, and Noncomputable Finality',
  'filename':'Oracle_Attested_Knowledge_FDWC_A_1_1_ATLAS_Repaired',
  'abstract':"An ideal mathematical truth source answers a halting query, transmits a finite authenticated receipt to a blind relay, and is then deactivated. Can a receiving Pioneer maintain an exact account of what has been proved, attested, delivered, and merely trusted? We give a finite-ledger, typed evidence calculus in which the answer is yes, conditional on explicit reliability, authentication, locally closed storage, and checker hypotheses. We prove termination of the evidence-classification procedure, separation of the proof and testimony gates, persistence of already recorded evidence after source deactivation, and trust-relative soundness. A self-contained halting diagonal argument shows why no uniform all-input truth service can be realized entirely by computable components. We further construct a one-drop proof-horizon sequence and show that its stabilization predicate has exactly halting-oracle Turing degree. The mathematical results are conditional paper-level arguments; neither operational AMLD+0 execution nor independent certificate verification is claimed.",
  'quote':'Source identity is a provenance fact, not a semantic proof.',
  'quote_page':9
 },
 {
  'key':'B',
  'slug':'oracle_attested_mathematical_knowledge_fdwc_b_epistemic_boundary_theorem_1_1',
  'title':'Oracle-Attested Mathematical Knowledge — Completion B: An Epistemic Boundary Theorem for Deactivated Sources and Blind Transmission',
  'filename':'Oracle_Attested_Knowledge_FDWC_B_1_1_ATLAS_Repaired',
  'abstract':"We study what a Pioneer is warranted in saying after a truthful but noncomputable source has transmitted one authenticated answer to a blind relay and disappeared. Rather than deriving knowledge from message delivery, we construct a finite, auditable evidence view recording proof certificates, source-origin attestations, two-hop relay histories, and explicit trust flags. We prove receiver-view determinacy for locally closed ledgers and preservation after source loss, while establishing by countermodels that authentication, mere receipt, and finite observed prefixes do not independently certify mathematical truth or eventual stabilization. A self-contained halting argument demonstrates that a uniformly correct all-query decision service cannot emerge from computable relaying. For an effective one-drop sequence we also prove that stabilization finality has halting-oracle degree. The results specify sufficient operational assumptions and examine what fails when they are withdrawn. This is an alternative complete conditional settlement, not an AMLD+0 execution or a formal proof certificate.",
  'quote':'Source deactivation alone neither causes nor repairs these failures.',
  'quote_page':4
 }
]

def main():
 data=json.loads(CATALOG.read_text())
 existing={x['id'] for x in data['items']}
 added=[]
 min_order=min((x.get('order',0) for x in data['items'] if isinstance(x.get('order'),int)),default=0)
 for i,p in enumerate(PAPERS):
  pid=SUB+'/'+p['slug']
  if pid in existing:
   print('Already published:',pid);continue
  tex=STAGING/(p['key']+'.tex')
  assert tex.exists() and tex.stat().st_size>20000,tex
  text=tex.read_text()
  assert '\\end{document}' in text
  build=ROOT/'.build'/'fdwc_oracle_publish'/p['key']
  build.mkdir(parents=True,exist_ok=True)
  build_tex=build/(p['filename']+'.tex')
  shutil.copyfile(tex,build_tex)
  for _ in range(2):
   subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',build_tex.name],cwd=build,check=True,stdout=subprocess.DEVNULL)
  build_pdf=build/(p['filename']+'.pdf')
  doc=fitz.open(build_pdf)
  assert len(doc)==9,(p['key'],len(doc))
  all_text=' '.join(' '.join(page.get_text().split()) for page in doc)
  assert 'Completion '+p['key'] in all_text and 'ATLAS-repaired' in all_text
  q_text=' '.join(doc[p['quote_page']-1].get_text().split())
  assert p['quote'] in q_text,(p['key'],p['quote'])
  out=ROOT/'docs'/pid
  out.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(build_pdf,out/(p['filename']+'.pdf'))
  shutil.copyfile(tex,out/(p['filename']+'.tex'))
  sha=hashlib.sha256((out/(p['filename']+'.pdf')).read_bytes()).hexdigest()
  print('Validated',p['key'],'9 pages, PDF SHA256:',sha)
  item={
   'id':pid,'href':pid+'/', 'title':p['title'],
   'kind':'Research paper','subject':SUB,'authors':'<Brian Tenneson>',
   'pdf':pid+'/'+p['filename']+'.pdf',
   'archive_path':'docs/'+pid+'/'+p['filename']+'.pdf',
   'source':pid+'/source.html',
   'source_file':pid+'/'+p['filename']+'.tex',
   'card_text':'Abstract — '+p['abstract'],
   'fdwc_explanation':FDWC_TEXT,
   'quote':p['quote'],'quote_attribution':'FDWC Completion '+p['key']+', v1.1, p. '+str(p['quote_page']),
   'quote_page':p['quote_page'],'quote_also_on_card':True,
   'status':'ATLAS-repaired and re-audited v1.1: conditional paper-level PASS. No independent formal proof checking, external peer review, AMLD+0 engine execution, or physical truth-oracle implementation.',
   'classification_note':'FDWC Level-1 alternative '+p['key']+', 9 pages, 30 October 2026. This source and PDF correspond to the ATLAS-repaired v1.1 manuscript. Original W0 remains immutable; the companion Level-1 alternative is independently published. The full FDWC method description is on this publication card.',
   'publication_date':'30 October 2026','pages':9,'sha256':sha,
   'order':min_order-2+i
  }
  added.append(item)
 if not added:
  print('No new publication entries');return
 data['items']=added+data['items']
 CATALOG.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 # These two curated listings must be explicitly re-rendered to insert slots 1 and 2.
 for index in [ROOT/'docs/index.html',ROOT/'docs'/SUB/'index.html']:
  if index.exists():index.unlink()
 subprocess.run(['python','scripts/build_publications_106.py'],cwd=ROOT,check=True)
 # Explicitly test positions, card description, and all new reader/download links.
 home=(ROOT/'docs/index.html').read_text()
 first=home.index('href="/pub/'+added[0]['href']+'"')
 second=home.index('href="/pub/'+added[1]['href']+'"')
 assert first<second
 assert home.find('fdwc-note')>0
 assert home.count('The objective is not simply to make a paper longer.')>=2
 for item in added:
  assert (ROOT/'docs'/item['href']/'index.html').is_file()
  assert (ROOT/'docs'/item['source']).is_file()
  assert (ROOT/'docs'/item['pdf']).is_file()
  assert item['id'] in home
 print('New headliners:',[x['id'] for x in added])

if __name__=='__main__':main()
