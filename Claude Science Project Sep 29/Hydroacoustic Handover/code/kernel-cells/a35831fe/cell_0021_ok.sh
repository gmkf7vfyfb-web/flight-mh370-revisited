cd "hyd/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"; python - <<'E'
import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',40); pd.set_option('display.max_colwidth',40)
s=pd.read_csv('/Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked/ranked_singles.csv')
print(s.rx.value_counts()); print(s.source.value_counts())
print(s[['rank_lnLR','lnLR','rx','time_utc','det','p','label_searches','kadri_label','in_window','eta_needed','eta_x_F35A','implied_source','implied_impact_utc','src_E_med','baz_H01W','bearing_consistency','status']].head(25).to_string())
E
head -3 searches_run_j/named/table1_verdicts.csv; wc -l searches_run_j/named/table1_verdicts.csv; head -8 searches_run_j/named/poster_boxes.csv