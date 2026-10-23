from shapely.geometry import Polygon
def direct(az,s): p=GG.Direct(-34.8903,114.1426,az,s*1e3); return (p['lon2'],p['lat2'])
R7=1591.3
ring=[direct(305.18,s) for s in np.linspace(R7-60,R7+250,40)]+[direct(307.18,s) for s in np.linspace(R7+250,R7-60,40)]
strip_poly=Polygon(ring)
def disc(lat,lon,r): return Polygon([ (GG.Direct(lat,lon,a,r*1e3)['lon2'],GG.Direct(lat,lon,a,r*1e3)['lat2']) for a in np.linspace(0,360,73)])
X200=disc(-25.732,101.369,200); X50=disc(-25.732,101.369,50)
# static coverage of L by day: fraction of strip area within the day's union of boxes
day_rows=[]
zd=np.load('ocean/drift_dense_0.012.npz'); cells_d=zd['cells']
hs=H[('D0','strip')][:-1]; hT=H[('D0','Tcore')][:-1]; hC=H[('D0','Ccore')][:-1]
wS=hs[cells_d]/hs[cells_d].sum(); wT=hT[cells_d]/hT[cells_d].sum(); wC=hC[cells_d]/hC[cells_d].sum()
POOR={13,17,20,25,26,45,46,47,48,49,50,52}
for dn in sorted(byday):
    u_=unary_union([g for _,g in byday[dn]])
    fs=strip_poly.intersection(u_).area/strip_poly.area; f200=X200.intersection(u_).area/X200.area
    ins=zd[f'inbox|{dn}']
    day_rows.append({'day':(dt.date(2014,3,7)+dt.timedelta(days=dn)).strftime('%d %b'),'D':dn,'n_boxes':len(byday[dn]),'weather':'poor' if dn in POOR else 'fair/good',
                     'strip_area_in_boxes':round(fs,3),'X200_area_in_boxes':round(f200,3),
                     'drifted_debris_in_boxes_strip':round(float(wS@ins),3),'drifted_T':round(float(wT@ins),3),'drifted_C':round(float(wC@ins),3)})
dfd=pd.DataFrame(day_rows); print(dfd[(dfd.strip_area_in_boxes>0)|(dfd.X200_area_in_boxes>0)|(dfd.drifted_debris_in_boxes_strip>0.005)].to_string(index=False))