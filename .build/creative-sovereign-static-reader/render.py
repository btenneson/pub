from pathlib import Path
import hashlib, re, subprocess, sys, struct
reader=Path(sys.argv[1])
pdf=Path(sys.argv[2])
pages=reader.parent / sys.argv[3]
assert hashlib.sha1(b"blob "+str(pdf.stat().st_size).encode()+b"\0"+pdf.read_bytes()).hexdigest()=="f9917c01deff175701325a8bb38ad423f61c4517", "Unexpected PDF revision"
pages.mkdir(parents=True,exist_ok=True)
subprocess.run(["pdftoppm","-r","150","-png",str(pdf),str(pages/"page")],check=True)
files=sorted(pages.glob("page-*.png"))
assert len(files)==16, len(files)
s=reader.read_text()
if 'data-static-typeset="true"' in s:
    print("Reader already converted; regenerated verified images")
    sys.exit(0)
s=s.replace("Complete manuscript — text reader","Complete manuscript — original typeset pages")
s=s.replace("Read full text below","Read original typeset pages")
s=s.replace("This static transcript does not require a PDF viewer or JavaScript. Mathematical typography and diagrams are authoritative in the original PDF.","All 16 original typeset pages are displayed below, including equations and diagrams. Click a page to enlarge it. No embedded PDF viewer or JavaScript is required. Optional text transcripts appear below each page.")
s=s.replace("Return to text index","Return to page index")
s=s.replace("</style>",".typeset-page{display:block;width:100%;height:auto;max-width:900px;margin:0 auto;background:white;border:1px solid #aaa}.paper-page details{margin:.6rem 0} </style>",1)
def replacement(m):
    n=int(m.group(1))
    f=pages/f"page-{n:02d}.png"
    b=f.read_bytes()
    assert b[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack(">II",b[16:24])
    assert w>1000 and h>1400
    src=f"{sys.argv[3]}/page-{n:02d}.png"
    return m.group(0).replace("<pre>",f'<a href="{src}" target="_blank" rel="noopener"><img class="typeset-page" data-static-typeset="true" src="{src}" width="{w}" height="{h}" decoding="async" alt="Original typeset manuscript page {n} of 16"></a><details><summary>Optional text transcript</summary><pre>',1).replace("</pre>","</pre></details>",1)
s,count=re.subn(r'<section class="paper-page" id="page-(\d+)">.*?</section>',replacement,s,flags=re.S)
assert count==16 and s.count('data-static-typeset="true"')==16 and s.count('Optional text transcript')==16
reader.write_text(s)
print("Verified 16 rendered pages, original PDF unchanged, optional transcript preserved")
