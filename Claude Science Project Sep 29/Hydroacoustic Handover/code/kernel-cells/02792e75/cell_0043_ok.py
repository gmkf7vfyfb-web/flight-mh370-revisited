r=requests.get(CMR+"/collections.json",params={"provider":"CSDA","page_size":200},timeout=60)
csda=[(c["short_name"],c["id"]) for c in r.json()["feed"]["entry"]]
print(len(csda),[s for s,_ in csda][:80])
sel=[(s,i) for s,i in csda if re.search(r"^(WV0[1-3]|GE01|QB02|IK|IKONOS).*(L1B)",s)]
print(sel)
cs={}
for s,i in sel:
    n,e=gran(i,temporal="2014-03-08T00:00:00Z,2014-05-31T23:59:59Z"); cs[s]=e; 
    nc,_=gran_b(i,"115,-33,117,-31","2014-03-08T00:00:00Z,2014-05-31T23:59:59Z")
    print(s,"locality",n,"| Perth control",nc, [x.get("time_start") for x in (e if isinstance(e,list) else [])][:4])