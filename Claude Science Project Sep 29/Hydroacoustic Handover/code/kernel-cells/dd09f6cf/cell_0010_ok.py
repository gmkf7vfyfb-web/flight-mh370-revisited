import struct, numpy as np, glob, os
D="repo/Claude Science Project Sep 29/engine/hypotheses/seabed-search/coverage/"
def readcov(p):
    b=open(p,'rb').read(); assert b[:8]==b"MH370COV"
    v,s,w,st,R,C,n=struct.unpack("<IdddIII",b[8:8+40])
    rec=np.frombuffer(b[48:48+3*n],dtype=np.dtype([('v','u1'),('n','<u2')]))
    a=np.repeat(rec['v'],rec['n']).astype(float)/255; assert a.size==R*C
    return dict(s=s,w=w,st=st,R=R,C=C,a=a.reshape(R,C))
cov={os.path.basename(p)[:-4]:readcov(p) for p in sorted(glob.glob(D+"*.cov"))}
for k,c in cov.items():
    rr,cc=np.nonzero(c['a']>0)
    print(k, c['s'],c['w'],c['st'],c['R'],c['C'], 'covered lat %.2f..%.2f lon %.2f..%.2f'%(c['s']+rr.min()*c['st'],c['s']+(rr.max()+1)*c['st'],c['w']+cc.min()*c['st'],c['w']+(cc.max()+1)*c['st']))