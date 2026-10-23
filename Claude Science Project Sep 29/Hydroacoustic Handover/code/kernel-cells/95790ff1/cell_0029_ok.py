for (y0,y1) in [(9,134),(149,274),(289,414)]:
    t=[y for y in range(y0+1,y1) if dark[y,52:56].sum()>=3]
    tr=[y for y in range(y0+1,y1) if dark[y,334:339].sum()>=3]
    print(y0,y1,t,tr)
# x ticks on bottom of CL panel
print([x for x in range(51,340) if dark[410:414,x].sum()>=3])