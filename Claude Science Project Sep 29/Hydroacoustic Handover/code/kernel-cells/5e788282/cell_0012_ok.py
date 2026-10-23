for pno in [3,4,1,6]:
    pg=fd[pno]; drw=pg.get_drawings()
    cc=collections.Counter()
    for d in drw:
        col=tuple(round(x,3) for x in d['color']) if d.get('color') else None
        fill=tuple(round(x,3) for x in d['fill']) if d.get('fill') else None
        cc[(col,fill,len(d['items'])>20)]+=1
    print("page",pno+1,len(drw))
    for k,v in cc.most_common(25): print("  ",k,v)
    for inf in pg.get_image_info(xrefs=True): print("  img", inf['xref'], inf['width'], inf['height'], [round(v,1) for v in inf['bbox']])
    big=[d for d in drw if len(d['items'])>20]
    for d in big: print("   big", d.get('color'), len(d['items']), [round(v,1) for v in d['rect']])