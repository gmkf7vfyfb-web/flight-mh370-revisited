wsrc=inspect.getsource(windows_fig)
wsrc=wsrc.replace('predicted 9-10 minutes earlier (median)','predicted {lo_:.0f}-{hi_:.0f} minutes earlier (median)')
wsrc=wsrc.replace('    bins=np.array(p["bins_s"])/60;','    dd=[(p["windows"][s]["reweighted"]["q_flight"][1]-p["windows"][s]["reweighted"]["q_H"][1])/60 for s,_ in STN]; lo_,hi_=np.floor(min(dd)),np.ceil(max(dd))\n    bins=np.array(p["bins_s"])/60;')
exec(wsrc)
for o,nm in (("r600-bto-only","00:19 R600 BTO Only"),("held-out","00:19 Held Out"),("r600-bto-raw-bfo","00:19 R600 BTO + Raw BFO")):
    f=windows_fig(PW[o],o,nm); print(o, f._suptitle.get_text()[:95])
plt.close("all")
for o in PW: print(o, {s:round(PW[o]["windows"][s]["reweighted"]["ovl"],2) for s in PW[o]["windows"]})