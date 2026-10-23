d3=cr<215
rs=d3.sum(1); print("rows", [(y,int(rs[y])) for y in range(150,330) if rs[y]>250])
cs=d3[200:300].sum(0); print("cols", [(x,int(cs[x])) for x in range(600) if cs[x]>60])