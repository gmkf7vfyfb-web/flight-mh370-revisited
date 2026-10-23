for o,fn in zip(O,["r600-bto-only","held-out","r600-bto-raw-bfo"]):
    for sc,k in (("A","reweighted|A"),("A-IMOS","reweighted|A-IMOS")):
        ob=O[o][k]["lnR"]; S=PW[fn]["synthetic"][sc]
        print(o, sc, round(ob,3), "P(lnR<=obs|H)=%.2f  |noH=%.2f"%(np.mean(np.array(S["H"]["reweighted"]["values"])<=ob), np.mean(np.array(S["noH"]["reweighted"]["values"])<=ob)))