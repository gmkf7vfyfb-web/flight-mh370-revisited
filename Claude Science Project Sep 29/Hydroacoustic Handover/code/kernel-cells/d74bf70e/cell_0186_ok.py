import pandas as pd, numpy as np
A="hydro/air9/"
m=pd.read_csv(A+"air9_tl_model.csv")
for st in ["H01W","H08S"]:
    o=pd.read_csv(A+f"observed_bands_{st}.csv").set_index("fc_hz")
    h=m[(m.station==st)&(m.src_depth_m==10)&(m.bottom=="hard")].set_index("fc_hz")
    s=m[(m.station==st)&(m.src_depth_m==10)&(m.bottom=="soft")].set_index("fc_hz")
    t=pd.DataFrame({"obs":o.obs_tl_db,"n_px":o.n_obs_px,"hard":h.tl_db,"hard-obs":h.tl_db-o.obs_tl_db,"soft":s.tl_db,"modes_min_hard":h.n_modes_min,"modes_first":h.n_modes_first})
    print(st); print(t.round(1).to_string())