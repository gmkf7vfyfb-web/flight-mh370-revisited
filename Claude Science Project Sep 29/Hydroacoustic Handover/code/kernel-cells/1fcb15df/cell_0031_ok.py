
import panel_search as PS
PSER = np.load(f"{SR}/panels/panel_series.npz")
PANELS={}
for p in "abcde":
    tg, x, tstart, nraw = PS.load_panel(p)
    PANELS[p] = dict(t0=tstart, t=tg, x=x, st="H01W" if p in "abc" else "H08S",
                     m1b_t=PSER[f"{p}_M1b_t"], m1b=PSER[f"{p}_M1b_s"],
                     res_t=PSER[f"{p}_M1b_res_t"] if f"{p}_M1b_res_t" in PSER else None, res=PSER[f"{p}_M1b_res_s"] if f"{p}_M1b_res_s" in PSER else None)
print({p:(hms(v["t0"]), v["m1b_t"][:2], v["m1b_t"][-1], v["m1b"].max().round(3)) for p,v in PANELS.items()})
print([k for k in PSER.files if k.startswith("e_")])
# check panel c M1b max near 00:52:04
pc_ = PANELS["c"]; j = np.argmax(np.where(np.abs(pc_["t0"]+pc_["m1b_t"]-hms2u("00:52:04"))<5, pc_["m1b"], -1)); print(hms(pc_["t0"]+pc_["m1b_t"][j]), pc_["m1b"][j])
# Royer
RD_ = os.path.join(MOD,"results-data/digitised/royer-2016")
import glob
ROY=[]
for f in sorted(glob.glob(RD_+"/spectrograms/*.npz")):
    d = np.load(f); b = pd.read_csv(f.replace(".npz","_band.csv"))
    ROY.append(dict(file=os.path.basename(f), station=str(d["station"]), t=d["t_utc_s"]+T0, f=d["f_hz"], psd=d["psd_db"].astype(float), band=b))
print(sorted({r["station"] for r in ROY}))
print([(r["file"], hms(r["t"][0],0), hms(r["t"][-1],0), r["f"].max()) for r in ROY][:6])
rarr = pd.read_csv(RD_+"/royer_arrivals.csv"); rarr = rarr[rarr.arrival_utc.notna()]; print(rarr.station.value_counts().to_dict(), len(rarr))
