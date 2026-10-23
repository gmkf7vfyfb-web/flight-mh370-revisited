cd leg; python -c "
import pandas as pd; R=pd.read_csv('out/window_statistics.csv'); x=R[R.station=='PerthCanyon_3376']; print(x[['source_set','option','statistic','observed','p_panel','snr_db','spl_max_db','peak_utc','covered_s']].to_string(index=False))
y=R[(R.station=='H08S')]; print(y.groupby(['source_set','option']).p_panel.min())"