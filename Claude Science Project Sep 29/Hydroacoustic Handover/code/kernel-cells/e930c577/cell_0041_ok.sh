cd leg; python -c "
import pandas as pd; W=pd.read_csv('out/arrival_windows.csv'); 
print(W[W.station.isin(['PerthCanyon_3376','H08S','OHAS_SSEIR','OHAS_MAD','OHAS_NCRO','OHAS_SWAMS3','OHAS_WKER'])][['branch','source_set','station','window_start','window_end','width_s','dt_minus_h01w_s_min','dt_minus_h01w_s_max','eq4_dr_max_km']].to_string(index=False))"