import os, json, textwrap, numpy as np, pandas as pd, matplotlib as mpl, matplotlib.pyplot as plt
H='hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/'
WR=H+'results-data/digitised/waveform-rasters/'; S1B=H+'results-data/calibration_events/stage1b/'
OUT='figs'; os.makedirs(OUT,exist_ok=True)
def foot(fig, ste, tech, y0=0.008, width=190):
    t1="\n".join(textwrap.wrap("Simplified English: "+ste, width)); t2="\n".join(textwrap.wrap("Technical: "+tech, width))
    fig.text(0.01, y0, t1+"\n\n"+t2, fontsize=5.6, va='bottom', ha='left', color='0.25')
def utcsec(df, ref): return (pd.to_datetime(df.utc, format='ISO8601')-pd.Timestamp(ref)).dt.total_seconds().values
def check(fig):
    r=fig.canvas.get_renderer(); texts=[(t,t.get_window_extent(r)) for t in fig.findobj(mpl.text.Text) if t.get_text().strip() and t.get_visible()]
    fb=fig.bbox
    o=[(a.get_text()[:40],b.get_text()[:40]) for i,(a,ba) in enumerate(texts) for b,bb in texts[i+1:] if ba.overlaps(bb)]
    out=[t.get_text()[:40] for t,b in texts if b.x0<fb.x0-1 or b.x1>fb.x1+1 or b.y0<fb.y0-1 or b.y1>fb.y1+1]
    print('overlaps',o[:12]); print('outside',out[:6])
C_K='#1f4e9c'; C_V='#c8641e'; C_N='#4d8f3a'; C_M='#7a3d9c'
