
def rd(f):
    txt=open(f'hycom/{f}.ascii').read().split('\n',2)[-1] if False else open(f'hycom/{f}.ascii').read()
    body=txt.split('---------------------------------------------')[-1]
    nums=body.split('\n',2)[2] if body.strip().startswith('') else body
    vals=[float(x) for x in nums.replace('\n',',').split(',') if x.strip()!='']
    return np.array(vals)
H={k:rd(k) for k in ['depth','lat','lon','time']}
print({k:(len(v),v[:3],v[-2:]) for k,v in H.items()})
