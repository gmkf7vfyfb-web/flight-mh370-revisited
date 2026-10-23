def strokes(pno, col=(0.141,0.125,0.118)):
    out=[]
    for d in fd[pno].get_drawings():
        c=d.get('color')
        if c and all(abs(a-b)<3e-3 for a,b in zip(c,col)):
            for it in d['items']:
                if it[0]=='l': out.append((round(it[1].x,2),round(it[1].y,2),round(it[2].x,2),round(it[2].y,2)))
                elif it[0]=='re': r=it[1]; out.append(('re',round(r.x0,2),round(r.y0,2),round(r.x1,2),round(r.y1,2)))
    return out
s5=strokes(4)
rects=[s for s in s5 if s[0]=='re']; print(rects)
lines=[s for s in s5 if s[0]!='re']
# long lines (frames)
L=[l for l in lines if abs(l[0]-l[2])>50 or abs(l[1]-l[3])>30]; print(L)
short=[l for l in lines if l not in L]; print(len(short)); print(sorted(short)[:80])