W_=pd.read_csv(SR/"panels/panel_windows.csv")
W_["ws"]=W_.window_start_utc.map(unix)
def winp(rxn,t):
    tt=unix(t); m=W_[(W_.receiver==rxn)&(W_.ws<=tt)&(W_.ws+55>tt)]
    return {r.detector+" "+str(r.band_hz):(round(r.p_A,3), r.label, round(r.eta_needed,4), r.window_start_utc) for r in m.itertuples()}
for t in ["00:49:58","00:53:31","00:52:50","00:52:04","00:54:27","00:54:30"]: print(t, winp("H01W",t))
for t in ["01:10:00.5","01:12:49.3"]: print(t, winp("H08S",t))
t1=pd.read_csv(SR/"named/table1_verdicts.csv"); print(t1[t1.time_utc.isin(["00:49:58","00:53:31","00:54:30","00:52:03","00:52:50"])][["event_id","time_utc","bearing_deg","arc_crossing_lat","arc_crossing_lon","range_km","implied_impact_utc","implied_time_band_D0","log10_BF_demonstrated_t3_3p3","bearing_verdict","panel_min_p","panel_best"]].to_string())
bf=pd.read_csv(RD/"composition_run_j/v2/bayes_factors_conditionals.csv"); print(bf.columns.tolist()[:30]); print(bf.iloc[:, :3].to_string())