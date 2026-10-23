def trace(name,y0,y1,thr):
    pts=[]
    for x in range(54,337):
        ys=[y for y in range(y0+3,y1-2) if f[y,x]<thr and not any(a<=x<=b and c<=y<=d for a,b,c,d in masks[name]) and not (x<120 and y<y0+25)]
        if ys: pts.append((x2hz(x),y2db(np.median(ys),name),y2db(min(ys),name),y2db(max(ys),name)))
    return np.array(pts)
out={}
for thr in (90,120):
    for name,(y0,y1) in [("DGS",(149,274)),("CL",(289,414))]:
        a=trace(name,y0,y1,thr); out[(name,thr)]=a
        for lo,hi in [(5,60),(10,60)]:
            s=a[(a[:,0]>=lo)&(a[:,0]<=hi)]
            print(thr,name,lo,hi,"cols",len(s),"of",int((hi-lo)*2.88),"Hz %.1f-%.1f"%(s[:,0].min(),s[:,0].max()),"median-trace %.1f..%.1f"%(s[:,1].min(),s[:,1].max()),"envelope %.1f..%.1f"%(s[:,2].min(),s[:,3].max()))