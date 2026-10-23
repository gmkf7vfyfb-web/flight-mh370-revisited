def trace(st, P, thr=140, jump=30):
    sub=im.copy(); a,b,c,d=P["legend"]; sub[a:b,c:d]=255; sub[P["y0"]:P["y0"]+24, 52:115]=255
    pts=[]; prev=None; gaps=0
    for x in range(54, 337):
        col=sub[P["y0"]+2:P["y1"]-1, x]
        ys=np.where(col<thr)[0]+P["y0"]+2
        if len(ys)==0: continue
        cl=[]
        for s,e in clusters(ys):
            seg=sub[s:e+1,x]; cl.append(((s+e)/2, seg.min()))
        if prev is None: y=cl[0][0]
        else:
            near=[t for t in cl if abs(t[0]-prev)<=jump]
            if not near: gaps+=1; continue
            # prefer darkest among near, tie-broken by continuity
            y=min(near, key=lambda t:(t[1]//25, abs(t[0]-prev)))[0]
        prev=y; pts.append((x, F(x), 150-(y-P["ytop"])/3.6))
    return pd.DataFrame(pts, columns=["x_px","f_hz","tl_db"]), gaps
for st,P in panels.items():
    traces[st],g=trace(st,P); t=traces[st]
    print(st, len(t), "gaps", g, "f", t.f_hz.min().round(1), t.f_hz.max().round(1), "TL", t.tl_db.min().round(1), t.tl_db.max().round(1))
fig,ax=plt.subplots(figsize=(7,9)); ax.imshow(rgb, interpolation="nearest")
for st,P in panels.items():
    t=traces[st]; ax.plot(t.x_px, P["ytop"]+(150-t.tl_db)*3.6, "r.", ms=2)
ax.set_xlim(40,345); ax.set_ylim(420,140); ax.set_axis_off()
fig.savefig("hydro/fig23_trace_check.png", dpi=150, bbox_inches="tight")