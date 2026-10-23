for name,(y0,y1) in {"DGN":(9,134),"DGS":(149,274),"CL":(289,414)}.items():
    for xs in [(46,51),(52,56)]:
        seg=(im[y0:y1+1, xs[0]:xs[1]]<140).sum(1); print(name, xs, np.where(seg>=3)[0]+y0)
    for ys in [(y1+1,y1+5),(y1-4,y1)]:
        xt=(im[ys[0]:ys[1], 52:338]<140).sum(0); print("  x", ys, np.where(xt>=3)[0]+52)