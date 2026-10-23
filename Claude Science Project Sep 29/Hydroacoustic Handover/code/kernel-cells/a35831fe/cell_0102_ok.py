_orig_text=plt.Axes.text
files1={}
for k in CANDS:
    files1[k]=chart1(k)
N1=pd.concat([pd.DataFrame(v) for v in chart1_notes.values()])
print(N1.pivot(index='cand',columns='rx',values='data').to_string())
print(N1[N1.land_points>0][['cand','rx','land_points']])
for k in CANDS: print(k, CANDS[k]['lat'], CANDS[k]['lon'], fmt(CANDS[k]['t0']))