#!/usr/bin/env python3
"""Publish only approved headliners 1, 2, 4, preserving all existing card order."""
import sys,json,shutil,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=R/'docs'
S=R/'incoming_publications/headliners_20261021/source_parts'
WORK=R/'.build/headliners_20261021'
SPECS=[
('cs.CR_Cryptography_and_Security/amld_security_3_1_atlas_repaired_v0_3','AMLD_Security_3_1_ATLAS_Repaired_v0_3.tex','AMLD Security 3.1: Certified Security Settlement with Five FORGE-6 Federations and Player-0 B*','Research manuscript','cs.CR_Cryptography_and_Security','ATLAS-repaired sequel to AMLD Security 3. Five FORGE-6 role federations coordinated by Player-0 with verifier-gated certification; no executed federation or experimental speedup claim.','Search proposes. Verification certifies.','AMLD Security 3.1, title page','ATLAS-REPAIRED v0.3 · PROVISIONAL MATHEMATICAL MANUSCRIPT; independent machine verification not claimed.',15),
('cs.LO_Logic_in_Computer_Science/basin_escape_atlas_repaired_v0_2','Basin_Escape_ATLAS_Repaired_v0_2.tex','Basin Escape, Player-0 Activation, and Settlement Preorders — ATLAS-Repaired v0.2','Working research note','cs.LO_Logic_in_Computer_Science','Repaired nine-page note separating actual from possible settlement, enforcing BANK assumption discharge and proving conditional simulation-order and antichain results.','An automated prover may stall because of its search policy rather than because its fixed theorem is unprovable.','Basin Escape v0.2, abstract','WORKING RESEARCH NOTE · ATLAS-repaired v0.2; no executed experiment.',7),
('cs.LO_Logic_in_Computer_Science/atlas_basin_escape_audit_v0_1','ATLAS_Basin_Escape_Audit_v0_1.md','ATLAS Independent Logical Audit — Basin Escape v0.1','Audit report','cs.LO_Logic_in_Computer_Science','Historical first-pass audit identifying settlement-region and BANK assumption-handling defects; later repairs are documented in the separate second audit, not published in this selection.','Verdict: CONDITIONAL PASS as a working research note','ATLAS first audit v0.1, decision','HISTORICAL FIRST AUDIT; identified defects were subsequently addressed in v0.2.',4),
]
def source_bytes(name,n):
 p=sorted(S.glob(name+'.part*'))
 if len(p)!=n:raise RuntimeError(f'{name}: expected {n} parts, found {len(p)}')
 content=b''.join(x.read_bytes() for x in p)
 if not content or (name.endswith('.tex') and b'\\end{document}' not in content):raise RuntimeError('Source incomplete: '+name)
 return content
def prepare():
 WORK.mkdir(parents=True,exist_ok=True)
 for id,name,*last in SPECS:
  n=last[-1]
  (WORK/name).write_bytes(source_bytes(name,n))
 print('Verified all three selected source files')
def finalize():
 data=json.loads((R/'scripts/publications.json').read_text())
 before=[x['id'] for x in data['items']]
 new=[]
 for id,name,title,kind,subject,desc,quote,attrib,status,n in SPECS:
  pdf=name.rsplit('.',1)[0]+'.pdf'
  artifact=WORK/pdf
  if not artifact.is_file() or artifact.stat().st_size<10000 or artifact.read_bytes()[:5]!=b'%PDF-':raise RuntimeError('Missing or invalid PDF: '+pdf)
  f=D/id;f.mkdir(parents=True,exist_ok=True)
  shutil.copy2(artifact,f/pdf)
  shutil.copy2(WORK/name,f/name)
  new.append(dict(id=id,href=id+'/',title=title,kind=kind,subject=subject,authors='Research direction: Brian Tenneson; ATLAS-style drafting/audit assistance: ChatGPT',pdf=id+'/'+pdf,source=id+'/source.html',source_file=id+'/'+name,archive_path='docs/'+id+'/'+pdf,card_text=desc,quote=quote,quote_attribution=attrib,quote_also_on_card=True,status=status,classification_note=status,sha256=hashlib.sha256(artifact.read_bytes()).hexdigest()))
 if any(x['id'] in before for x in new):raise RuntimeError('Publication already exists; refusing duplicate cards')
 data['items']=new+data['items']
 assert [x['id'] for x in data['items'][3:]]==before
 (R/'scripts/publications.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('Prepared '+str(len(new))+' cards at slots 1,2,3; existing card order unchanged')
if __name__=='__main__':
 {'prepare':prepare,'finalize':finalize}[sys.argv[1]]()
