from PIL import ImageDraw, ImageFont
ck["interpretation"]=[ "consistent" if c else ("whole-hour reference offset (different data segment)" if abs((p)/3600-round(p/3600))<0.001 and round(p/3600)!=0 else ("~60 s origin-time offset in Appendix B prediction; observed differences match Table 5" if a=="A7sus2" else "unexplained reference offset; unresolved")) 
  for c,p,a in zip(ck.consistent_within_2s,ck.predicted_minus_table_s,ck.later_event)]
ck.to_csv("out/appendixB_timing_consistency.csv",index=False)
p26=Image.open("pages/p26.png").convert("RGB")
y0=int(0.56*3301)
tab5=p26.crop((250,y0,2250,y0+1000)).copy()
tab5.save("crops/tab5_test.png")