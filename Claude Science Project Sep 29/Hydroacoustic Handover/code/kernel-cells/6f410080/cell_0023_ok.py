res=json.load(open('handoff/cdx_misc.json'))
os.makedirs('mot',exist_ok=True); os.makedirs('jacc',exist_ok=True); os.makedirs('gistda',exist_ok=True)
want=[]
for x in res['www.mot.gov.my/*']:
    s=x[0]
    if '/my/Newsroom/Press%20Release/Tahun%202014/' in s and re.search(r'(2[0-9]|3[01])%20Mac|(1[6-9]|2[0-9]|3[01])%20March|April|MRSA',s): want.append(('mot',x))
for x in res['www.jacc.gov.au/*']:
    if re.search(r'/media/releases/2014/(april|march|may)/mr\d+\.aspx|interviews/2014/.*/tr\d+\.aspx|releases/2014/march/index',x[0],re.I): want.append(('jacc',x))
for x in res['gistda.or.th/*']:
    if x[3]=='text/html': want.append(('gistda',x))
print(len(want))
import concurrent.futures as cf
def get(item):
    d,x=item; orig,ts=x[0],x[1]
    fn=d+'/'+re.sub(r'[^A-Za-z0-9._-]','_',orig.split('/',3)[-1])[-150:]
    if os.path.exists(fn) and os.path.getsize(fn)>0: return fn,'cached'
    try:
        r=requests.get(f'http://web.archive.org/web/{ts}id_/{orig}',timeout=90)
        open(fn,'wb').write(r.content); return fn,(r.status_code,len(r.content))
    except Exception as e: return fn,str(e)[:60]
with cf.ThreadPoolExecutor(6) as ex:
    out=list(ex.map(get,want))
bad=[o for o in out if not (isinstance(o[1],tuple) and o[1][0]==200) and o[1]!='cached']
print(len(out),'bad',len(bad)); print(bad[:20])