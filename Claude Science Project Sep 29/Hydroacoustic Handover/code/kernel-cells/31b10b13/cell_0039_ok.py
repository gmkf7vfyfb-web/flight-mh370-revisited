
src=open("energy_chart.py").read().replace("(a fighter aircraft that hit the sea in 2022)","(a military jet that hit the sea)")
open("energy_chart.py","w").write(src)
import matplotlib.pyplot as plt
exec(src)
r=fig.canvas.get_renderer(); import matplotlib as mpl
texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
ov=[(a.get_text()[:30],b.get_text()[:30]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
print(ov[:20]); fb=fig.bbox; print([t.get_text()[:30] for t,b in texts if b.x0<fb.x0-1 or b.x1>fb.x1+1 or b.y0<fb.y0-1 or b.y1>fb.y1+1])
