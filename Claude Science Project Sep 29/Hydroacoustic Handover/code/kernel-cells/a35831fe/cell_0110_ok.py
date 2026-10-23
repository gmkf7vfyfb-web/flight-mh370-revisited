RT=[]
base_='/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo/'
seeds=sorted(glob.glob(base_+'seed-*'))
for sd in seeds:
    r=np.load(sd+'/routes.npy'); RT.append(r)
RT=np.concatenate(RT); print(RT.shape, len(seeds))
end=RT[:,-1,:]; 
# distance of route end to arc line
dA=np.array([np.min(G.inv(np.full_like(flo,lo_),np.full_like(fla,la_),flo,fla)[2]) for la_,lo_ in end[:2000:50]])/1000
print('end-to-impact-line km (sample):', np.percentile(dA,[5,50,95]))
rj=json.load(open('/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/run.json'))
def find(o,key,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if key in k.lower(): print(p+k, str(v)[:200])
            find(v,key,p+k+'.')
find(rj,'route_start'); find(rj,'start_utc'); find(rj,'end_utc'); find(rj,'final_utc')