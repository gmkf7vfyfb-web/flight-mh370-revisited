import time
def ok(fn): return os.path.exists(fn) and os.path.getsize(fn)>0
pending=[w for w in want if not ok(w[0]+'/'+re.sub(r'[^A-Za-z0-9._-]','_',w[1][0].split('/',3)[-1])[-150:])]
# prioritise
pending.sort(key=lambda w:(0 if (w[0]=='mot') else 1 if 'releases' in w[1][0] else 2))
print(len(pending))
for attempt in range(3):
    still=[]
    for w in pending:
        fn,st=get(w)
        if not ok(fn): still.append(w)
        time.sleep(1.5)
    pending=still
    print('attempt',attempt,'remaining',len(pending))
    if not pending: break
    time.sleep(10)
print([p[1][0][-80:] for p in pending])