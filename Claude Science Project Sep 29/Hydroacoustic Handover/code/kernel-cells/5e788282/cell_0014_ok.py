import pandas as pd, datetime as dt
COLS={'1':(0.10194552689790726,0.26274511218070984,0.45488670468330383),'2':(0.6274357438087463,0.8274357318878174,0.9293965101242065),'3':(0.35684749484062195,0.5921568870544434,0.807827889919281)}
def polylines(pno):
    res=[]
    for d in fd[pno].get_drawings():
        c=d.get('color')
        if c is None or len(d['items'])<50: continue
        pts=[]
        for it in d['items']:
            if it[0]=='l':
                if not pts: pts.append((it[1].x,it[1].y))
                pts.append((it[2].x,it[2].y))
            elif it[0]=='c':
                if not pts: pts.append((it[1].x,it[1].y))
                pts.append((it[4].x,it[4].y))
        res.append((c,np.array(pts),[it[0] for it in d['items']]))
    return res
pl5=polylines(4)
panels={'C':dict(sta='H11N',x0=71.0,x1=241.98,t0=dt.datetime(2019,4,9,11,2,55)),'D':dict(sta='H11S',x0=284.91,x1=455.9,t0=dt.datetime(2019,4,9,11,3,55))}
ytop,ybot=135.65,189.22
traces={}
for c,pts,kinds in pl5:
    el=[k for k,v in COLS.items() if all(abs(a-b)<1e-3 for a,b in zip(c,v))][0]
    pn='C' if pts[:,0].mean()<260 else 'D'; p=panels[pn]
    t=(pts[:,0]-p['x0'])/(p['x1']-p['x0'])*30.0
    L=80+(ybot-pts[:,1])/(ybot-ytop)*40
    key=f"{p['sta']}{el}"
    traces[key]=pd.DataFrame({'t_rel_s':t,'utc':[ (p['t0']+dt.timedelta(seconds=float(x))).strftime('%H:%M:%S.%f')[:-3] for x in t],'rms_db_re_1uPa':L,'pdf_x_pt':pts[:,0],'pdf_y_pt':pts[:,1]})
    print(key,len(pts),collections.Counter(kinds).most_common(), round(t.min(),2),round(t.max(),2), "dt med",round(np.median(np.diff(t)),4),"peak",round(L.max(),2),"at",traces[key].utc[np.argmax(L)], "noise med",round(np.median(L),2))