p="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/air9_tl_validation.py"
t=open(p).read()
old="""                for js, zs in enumerate(SRC_DEPTHS):
                    # tl has shape (nrz, nrr) for the FIRST source depth only in tl_path; recompute per sz
                    pass
"""
assert t.count(old)==1; open(p,"w").write(t.replace(old,""))
out="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/blackman/fig23_air9_digitised.csv"
df=pd.concat([traces[s].assign(station=s) for s in ["H01W","H08S"]])[["station","f_hz","tl_db","x_px"]]
with open(out,"w") as f:
    f.write("# DIGITISED from Blackman et al. (2004) UCRL-TR-207323 Fig. 23 (observed TL, median over shots, shown only where SNR > 3 dB),\n"
            "# page image artifact p23_img0.png (99b55187-e5c8-4c37-abff-0482499b5a7f). air9 curve only; H01W = 'CL' panel, H08S = 'DGS' panel.\n"
            "# Method: darkest thin curve per pixel column with continuity (threshold 140/255, max jump 30 px), legend and panel labels masked;\n"
            "# calibration from tick-label centres: 3.6 px/dB, 2.875 px/Hz, 0 Hz at x=51.5 px. Chart reading +/-2 dB. Not a measurement.\n"
            "# Script: prepare/air9_tl_validation.py docstring. DGS: air8 dotted curve may capture the trace where they cross.\n")
    df.to_csv(f,index=False,float_format="%.3f")
print(len(df))