
st=12
EL=np.asarray(el[::st, ::st]).astype(np.float32)
GLATS=gj['lat0']+np.arange(EL.shape[0])*st*gj['step_deg']; GLONS=gj['lon0']+np.arange(EL.shape[1])*st*gj['step_deg']
print(EL.shape, GLATS[[0,-1]], GLONS[[0,-1]])
np.savez_compressed('work/gebco_coarse.npz', EL=EL, lat=GLATS, lon=GLONS)
