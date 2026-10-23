rs=d2.sum(1); print([(y,int(rs[y])) for y in range(150,330) if rs[y]>60])
cs=d2[200:300].sum(0); print([(x,int(cs[x])) for x in range(600) if cs[x]>35])