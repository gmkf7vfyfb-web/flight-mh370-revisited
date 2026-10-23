cal={"DGN":(44.5,140,80.0,130),"DGS":(184.5,140,220.5,130),"CL":(324.5,140,360.5,130)}
def y2db(y,name):
    ya,da,yb,db=cal[name]; return da+(y-ya)*(db-da)/(yb-ya)
def x2hz(x): return (x-51)/2.88
masks={"DGS":[(200,339,190,232)],"CL":[(200,339,330,356)],"DGN":[(200,339,55,122)]}
res={}
for name,(y0,y1) in zip(["DGN","DGS","CL"],[(9,134),(149,274),(289,414)]):
    pts=[]
    for x in range(54,337):
        ys=[y for y in range(y0+3,y1-2) if f[y,x]<90 and not any(a<=x<=b and c<=y<=d for a,b,c,d in masks[name])]
        if name=="DGN" or True:
            # exclude panel label text region top-left
            ys=[y for y in ys if not (x<120 and y<y0+25)]
        if ys: pts.append((x2hz(x),y2db(min(ys),name),y2db(max(ys),name),y2db(np.median(ys),name)))
    res[name]=np.array(pts)
for name in ["CL","DGS"]:
    a=res[name]
    for lo,hi in [(5,60),(10,60),(30,60),(5,100)]:
        s=a[(a[:,0]>=lo)&(a[:,0]<=hi)]
        if len(s): print(name,lo,hi,"freq span %.1f-%.1f"%(s[:,0].min(),s[:,0].max()),"dB min %.1f max %.1f median-trace %.1f-%.1f"%(s[:,2].min() if False else s[:,1:3].min(), s[:,1:3].max(), s[:,3].min(), s[:,3].max()))