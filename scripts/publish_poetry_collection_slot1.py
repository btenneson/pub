#!/usr/bin/env python3
"""Publish the provisional recovered poetry manuscript, preserving catalog order."""
from pathlib import Path
from html import escape
import hashlib, json, re, subprocess, sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
import fitz

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'incoming_publications/brian_tenneson_poetry_2006_2012_provisional/manuscript.md'
SUBJECT='cs.CY_Computers_and_Society'
NAME='brian_tenneson_collected_poetry_2006_2012_provisional'
SLUG=f'{SUBJECT}/{NAME}'
PDF='Brian_Tenneson_Collected_Poetry_2006-2012_Provisional.pdf'
TITLE='Collected Poetry: Recovered Forum Poems, 2006–2012'
QUOTE='words fill pages without saying anything'
raw=SOURCE.read_bytes()
md=raw.decode('utf-8')
assert len(re.findall(r'^## BT-\d{3} — ',md,re.M))==65,'65 poems required'
assert QUOTE in md,'Card quote missing from original manuscript'
assert 'PROVISIONAL TRANSCRIPTION' in md

fonts=Path('/usr/share/fonts/truetype/dejavu')
regular=fonts/'DejaVuSerif.ttf'; bold=fonts/'DejaVuSerif-Bold.ttf'
if regular.exists() and bold.exists():
    pdfmetrics.registerFont(TTFont('Poetry',str(regular)))
    pdfmetrics.registerFont(TTFont('PoetryBold',str(bold)))
    pdfmetrics.registerFontFamily('Poetry',normal='Poetry',bold='PoetryBold',italic='Poetry',boldItalic='PoetryBold')
    font='Poetry'; boldfont='PoetryBold'
else:
    font='Times-Roman'; boldfont='Times-Bold'
normal=ParagraphStyle('body',fontName=font,fontSize=9.5,leading=14.6,spaceAfter=8,textColor=colors.HexColor('#202020'))
poem=ParagraphStyle('poem',parent=normal,spaceAfter=9)
small=ParagraphStyle('note',parent=normal,fontSize=8.0,leading=11.5,textColor=colors.HexColor('#555555'))
heading=ParagraphStyle('heading',parent=normal,fontName=boldfont,fontSize=15,leading=20,spaceAfter=12)
heading2=ParagraphStyle('section',parent=heading,fontSize=13,leading=18)
title_style=ParagraphStyle('title',parent=heading,fontSize=21,leading=29,alignment=TA_CENTER,spaceAfter=18)
subtitle=ParagraphStyle('subtitle',parent=normal,fontSize=11,leading=16,alignment=TA_CENTER)

out=ROOT/'docs'/SLUG
archive=ROOT/SLUG
out.mkdir(parents=True,exist_ok=True)
archive.mkdir(parents=True,exist_ok=True)

def ptext(s):
    return escape(s).replace('**','').replace('`','').replace('*','')

story=[]
lines=md.splitlines()
block=[]
started=False

def flush():
    global block
    if not block:return
    s=' '.join(block) if not started else '<br/>'.join(ptext(x) for x in block)
    story.append(Paragraph(s if started else ptext(s), poem if started else normal))
    block=[]

for line in lines:
    if line.startswith('## BT-'):
        flush()
        if started:story.append(PageBreak())
        else:story.append(PageBreak())
        started=True
        story.append(Paragraph(ptext(line[3:]),heading))
        continue
    if line.startswith('# '):
        flush();story.append(Paragraph(ptext(line[2:]),title_style));continue
    if line.startswith('## '):
        flush();story.append(Spacer(1,9));story.append(Paragraph(ptext(line[3:]),heading2));continue
    if line.strip()=='---':
        flush();story.append(Spacer(1,9));continue
    if not line.strip():
        flush();story.append(Spacer(1,3 if started else 2));continue
    if line.startswith('*Source:') or line.startswith('*Editorial note:'):
        flush();story.append(Paragraph(ptext(line),small));continue
    if line.startswith('**Brian Tenneson**'):
        flush();story.append(Paragraph(ptext(line),small));continue
    if line.startswith('- BT-'):
        flush();story.append(Paragraph(ptext(line),small));continue
    block.append(line)
flush()

def footer(canvas,doc):
    canvas.saveState()
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawCentredString(letter[0]/2,31,f'Brian Tenneson · Provisional collection · {doc.page}')
    canvas.restoreState()

pdf_path=out/PDF
SimpleDocTemplate(str(pdf_path),pagesize=letter,leftMargin=54,rightMargin=54,topMargin=52,bottomMargin=56,
                  title=TITLE,author='Brian Tenneson').build(story,onFirstPage=footer,onLaterPages=footer)
with fitz.open(pdf_path) as doc:
    page_count=len(doc)
    allpages=[p.get_text() for p in doc]
    assert page_count>=65, f'Unexpectedly short collection: {page_count}'
    assert any(QUOTE in t for t in allpages),'Quote absent in PDF'
    quote_page=next(i+1 for i,t in enumerate(allpages) if QUOTE in t)
    assert sum('BT-' in t for t in allpages)>=50

for folder in (out,archive):
    if folder!=out:(folder/PDF).write_bytes(pdf_path.read_bytes())
    (folder/'manuscript.md').write_bytes(raw)

catalog=ROOT/'scripts/publications.json'
data=json.loads(catalog.read_text(encoding='utf-8'))
old=[x for x in data['items'] if x.get('id')!=SLUG]
prior=[x['id'] for x in old]
order=min([x.get('order',0) for x in old if isinstance(x.get('order'),int)]+[0])-1
card={
    'id':SLUG,'href':SLUG+'/','title':TITLE,'kind':'Poetry collection','subject':SUBJECT,
    'pdf':SLUG+'/'+PDF,'archive_path':SLUG+'/'+PDF,'source':SLUG+'/source.html',
    'source_file':SLUG+'/manuscript.md','sha256':hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    'sha256_md':hashlib.sha256(raw).hexdigest(),'pages':page_count,'order':order,
    'authors':'Brian Tenneson','quote':QUOTE,'quote_page':quote_page,
    'card_quote':QUOTE,'card_quote_attribution':f'Brian Tenneson, poem BT-001, p. {quote_page}',
    'quote_also_on_card':True,
    'card_text':'A provisional collection of 65 recovered poem entries from 2006–2012, preserved from forum postings under the author’s modus_tollens account. Original handles and textual provenance are retained. The remaining scanned material and transcription fidelity require further checking.',
    'status':'PRELIMINARY RELEASE — PROVISIONAL TRANSCRIPTION. Source scans have not received complete line-by-line verification.',
    'classification_note':'Creative writing collection hosted in the existing Computers and Society library wing for catalog compatibility; the subject label does not imply arXiv submission. The author also confirms the handle modus_ponens as his, but this edition identifies no poems from that handle.'
}
data['items']=[card]+old
assert [x['id'] for x in data['items'][1:]]==prior
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
subprocess.run([sys.executable,'scripts/build_publications_106.py'],cwd=ROOT,check=True)
search=json.loads((ROOT/'docs/search-index.json').read_text())
assert search['items'][0]['id']==SLUG,'Slot #1 failed'
index=(ROOT/'docs/index.html').read_text()
first=index.split('<article class="card"',1)[1].split('</article>',1)[0]
assert 'Collected Poetry' in first and 'PROVISIONAL' in first
assert (out/'index.html').is_file() and (out/'source.html').is_file()
assert (out/PDF).read_bytes()==(archive/PDF).read_bytes()
print(f'PASS: {page_count}-page poetry collection published slot 1; {len(prior)} prior cards unchanged in relative order')
