z=np.load(SR/"panels/panel_series.npz")
for k in ["a_M1b_t","a_M1b_s","c_D1_t","c_BE_2-5_t"]: print(k, z[k][:3], z[k][-1], np.nanmax(z[k]))
pb=pd.read_csv(SR/"named/poster_boxes.csv"); print(pb[["box","start","end","H01W_arrival_mass_D0","minutes_before_earliest","verdict_timing","min_p_M1b","min_p_D1","min_p_BE_2-5","min_p_BE_5-9"]].to_string())
bm=pd.read_csv(SR/"panels/box_minima.csv"); print(bm[bm.detector=="M1b"].to_string())
TR="hydro/Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data/kadri-figure-extraction/figure9-vector-traces/"
t=pd.read_csv(TR+"kadri-2024-figure9-panel-a-H01W.csv"); print(len(t), t.plotted_time_s.max(), t.pressure_pa.abs().max())
w=pd.read_csv(SR/"panels/panel_windows.csv"); print(w[(w.receiver=="H01W")&(w.detector=="M1b")].groupby("panel").p_A.min())