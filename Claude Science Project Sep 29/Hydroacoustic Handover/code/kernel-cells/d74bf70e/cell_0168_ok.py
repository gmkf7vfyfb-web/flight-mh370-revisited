for name,(y0,y1) in {"DGN":(9,134),"DGS":(149,274),"CL":(289,414)}.items():
    seg=dark[y0+1:y1, 52:57].sum(1); ticks=np.where(seg>=4)[0]+y0+1
    xt=dark[y1-5:y1, 52:338].sum(0); xticks=np.where(xt>=4)[0]+52
    print(name, "yticks", ticks, "xticks", xticks)