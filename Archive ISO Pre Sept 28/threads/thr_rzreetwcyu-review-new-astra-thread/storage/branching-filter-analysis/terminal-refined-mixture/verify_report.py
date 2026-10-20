"""Check generated links, embedded figures and PDF completeness on the thread server.
This is not an authenticated remote-phone browser test.
"""
import base64,datetime as dt,hashlib,json,urllib.parse,urllib.request
from html.parser import HTMLParser
from pathlib import Path
import fitz
D=Path(__file__).resolve().parent
B=D.parent;R=Path('/jackbox/home/MH370');W=B.parent/'overnight-analysis/web'
report=D/'mixed/model-mixture/report'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='img':self.images.append(a['src'])
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text())
state=read(D/'progress.json');assert state['status']=='completed'
text=(R/'mh370-impact-model-mixture.html').read_bytes()
assert text==(W/'mh370-impact-model-mixture.html').read_bytes()==(report/'index.html').read_bytes()
assert len(text)<5*1024**2
page=Links();page.feed(text.decode());links=[]
for url in sorted(set(page.links)):
 parsed=urllib.parse.urlparse(url);assert parsed.netloc=='internal--8771.iso.abiome.org'
 assert parsed.path.startswith('/overnight/terminal-refined-mixture/')
 path=D/parsed.path.split('/overnight/terminal-refined-mixture/',1)[1]
 data=urllib.request.urlopen('http://127.0.0.1:8771'+parsed.path,timeout=15).read()
 assert data==path.read_bytes(),url
 links.append(dict(url=url,sha256=sha(data)))
images={sha(p.read_bytes()) for p in report.glob('*.png')}
for url in page.images:
 assert url.startswith('data:image/png;base64,')
 assert sha(base64.b64decode(url.split(',',1)[1],validate=True)) in images
pdf=report/'impact-and-residual-results.pdf'
with fitz.open(pdf) as doc:
 pages=doc.page_count
 for p in doc:
  assert p.get_text().strip(),p.number
  rect=p.rect
  for block in p.get_text('dict')['blocks']:
   if block['type']==0:
    bbox=fitz.Rect(block['bbox'])
    assert bbox.x0>=-1 and bbox.y0>=-1 and bbox.x1<=rect.width+1 and bbox.y1<=rect.height+1,(p.number,bbox,rect)
 for i,label in [(0,'methods'),(1,'impact'),(3,'case-weights'),(pages-1,'source-contributions')]:
  doc[i].get_pixmap(matrix=fitz.Matrix(1.15,1.15)).save('/tmp/mh370-refined-'+label+'.png')
summary=read(report/'summary.json');assert summary['methodology_words']<500
result=dict(status='passed',checked_utc=dt.datetime.now(dt.timezone.utc).isoformat(),linked_files=len(links),embedded_images=len(page.images),pdf_pages=pages,methodology_words=summary['methodology_words'],html_bytes=len(text),html_sha256=sha(text),pdf_sha256=sha(pdf.read_bytes()),links=links,scope=__doc__)
(report/'http-verification.json').write_text(json.dumps(result,indent=2)+'\n')
state['report_link_verification']=dict(path=str(report/'http-verification.json'),sha256=sha((report/'http-verification.json').read_bytes()))
state.update(report_sha256=result['pdf_sha256'],report_verified_utc=result['checked_utc'])
(D/'progress.json').write_text(json.dumps(state,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='links'}))
