import json, glob, numpy as np
F=[json.load(open(f)) for f in sorted(glob.glob('eofmeas/*.json'))]
B=["45-40","40-35","35-30","30-25","25-20","20-15"]
def tot(d, sel, sub=None):
    A=np.zeros((4,6))
    for r in F:
        x = r[d][sel] if sub is None else r[d][sel][str(sub)]
        A += np.array(x)
    return A
out={}
for d in ("D0","D2","D3","D4"):
    T=sum(r[d]["total"] for r in F)
    full=tot(d,"full"); M,M2,P2,NP=full
    out[d]={"mass":(M/T).tolist(),"ess_rows":(M**2/M2).tolist(),"ess_par":(M**2/P2).tolist(),"n_par_pos":NP.tolist()}
    print(d, " | ".join(f"{B[i]}: {M[i]/T:.4f} {M[i]**2/M2[i]:.0f}/{M[i]**2/P2[i]:.0f}" for i in range(2,5)))
    for kr in ("8","16","32"):
        M,M2,P2,NP=tot(d,"krows",kr); print("   rows/parent",kr, " | ".join(f"{B[i]}: {M[i]**2/M2[i]:.0f}/{M[i]**2/P2[i]:.0f}" for i in range(2,5)))
        out[d][f"krows{kr}"]={"ess_rows":(M**2/M2).tolist(),"ess_par":(M**2/P2).tolist()}
    print("   rows/parent 64", " | ".join(f"{B[i]}: {full[0][i]**2/full[1][i]:.0f}/{full[0][i]**2/full[2][i]:.0f}" for i in range(2,5)))
    for j in ("1","2","4"):
        M,M2,P2,NP=tot(d,"jpar",j); print("   parents",j,"/8", " | ".join(f"{B[i]}: {M[i]**2/M2[i]:.0f}/{M[i]**2/P2[i]:.0f}" for i in range(2,5)))
        out[d][f"jpar{j}"]={"ess_rows":(M**2/M2).tolist(),"ess_par":(M**2/P2).tolist()}
    # by mode
    for md,name in enumerate(["TH","MH","TT","MT","LN"]):
        M,M2,P2,NP=tot(d,"by_mode",md)
        print(f"   mode {name}", " | ".join(f"{B[i]}: m {M[i]/T:.4f} essP {M[i]**2/P2[i] if P2[i]>0 else 0:.0f}" for i in range(2,5)))
    M,M2,P2,NP=tot(d,"by_handoff_band"); print("   by 00:11 band", " | ".join(f"{B[i]}: {M[i]/T:.4f} {M[i]**2/M2[i]:.0f}/{M[i]**2/P2[i]:.0f}" for i in range(1,5)))
json.dump(out,open('eof_scaling.json','w'),indent=1)
