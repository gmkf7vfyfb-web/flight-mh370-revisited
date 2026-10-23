
z=np.load(S+'/geometry/sample.npz'); slat,slon,sw=z['lat'],z['lon'],z['w_D0']; st_t=z['t_unix']
sw=sw/sw.sum(); print(len(slat), 'ESS', 1/np.sum(sw**2))
def wq(x,w,q):
    o=np.argsort(x); c=np.cumsum(w[o]); return np.interp(q, c/c[-1], x[o])
print('lat q', wq(slat,sw,[0.005,0.01,0.05,0.5,0.95,0.99,0.995]))
# mass within 150 km of G, ±1 deg
def hav(lat, lon, la, lo):
    p1, p2 = np.radians(lat), np.radians(la); dl = np.radians(lo - lon)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))
dG=hav(slat,slon,G['lat'],G['lon']); print('mass<150km', sw[dG<150].sum(), 'mass ±1deg', sw[np.abs(slat-G['lat'])<1].sum())
print('impact time q', [pd.Timestamp(v,unit='s').strftime('%H:%M:%S') for v in wq(st_t,sw,[0.05,0.25,0.5,0.75,0.95])])
im=pd.read_csv(X+'/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv')
q=im[(im.quantile=='arc033.5S_+0')&(im.src_depth_m==10)]
print(q[['logger','fc_hz','status','tl_db','ram_grid_covered']].to_string())
