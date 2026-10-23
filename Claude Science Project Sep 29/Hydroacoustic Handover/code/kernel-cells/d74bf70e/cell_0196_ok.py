lab=cr<150
ylab=[y for y in range(195,300) if lab[y,90:132].sum()>0]; print("ylabel rows", clusters(np.array(ylab)))
xlab=[x for x in range(120,560) if lab[290:306,x].sum()>0]; print("xlabel cols", [(a,b,(a+b)/2) for a,b in clusters(np.array(xlab))])
# minor/major ticks along bottom spine inside box
tk=[x for x in range(136,537) if d3[280:286,x].sum()>=4]; print("bottom ticks", [(a+b)/2 for a,b in clusters(np.array(tk))] if tk else [])