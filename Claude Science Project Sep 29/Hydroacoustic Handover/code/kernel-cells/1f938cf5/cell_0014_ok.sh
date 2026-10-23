cd ~/Downloads/mh370-exchange/end-of-flight/run-j/; python3 -c "
import json;d=json.load(open('summary/table-0019-mixture.json'));
def walk(x,p='',depth=0):
  if depth>2: return
  if isinstance(x,dict):
    for k,v in list(x.items())[:25]:
      print('  '*depth+str(k), (json.dumps(v)[:160] if not isinstance(v,(dict,list)) or depth==2 else type(v).__name__+str(len(v))))
      walk(v,p+'/'+k,depth+1)
  elif isinstance(x,list) and x and depth<2:
    print('  '*depth+'[0]', json.dumps(x[0])[:300])
walk(d)
"; head -50 summary/table-0019-mixture.txt