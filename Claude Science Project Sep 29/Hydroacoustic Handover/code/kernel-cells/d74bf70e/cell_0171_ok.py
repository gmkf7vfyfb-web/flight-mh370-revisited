import pandas as pd
F=lambda x:(x-51.5)/2.875
panels={"H08S":dict(y0=149,y1=274,ytop=148.5,legend=(222,268,215,338)),"H01W":dict(y0=289,y1=414,ytop=288.5,legend=(368,410,215,338))}
traces={}
for st,P in panels.items():
    sub=im.copy(); a,b,c,d=P["legend"]; sub[a:b,c:d]=255
    pts=[]; prev=None
    for x in range(54, 337):
        ys=np.where(sub[P["y0"]+2:P["y1"]-1, x]<95)[0]+P["y0"]+2
        if len(ys)==0: continue
        cl=[( (s+e)/2, e-s+1) for s,e in clusters(ys)]
        if prev is None: y=min(cl, key=lambda t:-t[0])[0] if False else cl[0][0]
        else:
            y=min(cl, key=lambda t:abs(t[0]-prev))[0]
            if abs(y-prev)>14: continue
        prev=y; pts.append((F(x), 150-(y-P["ytop"])/3.6))
    traces[st]=pd.DataFrame(pts, columns=["f_hz","tl_db"])
    t=traces[st]; print(st, len(t), "f", t.f_hz.min().round(1), t.f_hz.max().round(1), "TL", t.tl_db.min().round(1), t.tl_db.max().round(1))