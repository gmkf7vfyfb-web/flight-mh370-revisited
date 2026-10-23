import pandas as pd, numpy as np, json, os
pd.set_option('display.width',250); pd.set_option('display.max_columns',50); pd.set_option('display.max_colwidth',60)
H='hyd/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/'
RK='/Users/pete/Downloads/mh370-exchange/hydroacoustics/graphics-2026-10-22/ranked/'
ev=pd.read_csv(H+'digitised/royer-2016/royer_events.csv')
arr=pd.read_csv(H+'digitised/royer-2016/royer_arrivals.csv')
pw=pd.read_csv(H+'searches_run_j/panels/panel_windows.csv')
iw=pd.read_csv(H+'searches_run_j/imos/imos_windows.csv')
print(pw.head(3).to_string()); print(pw.shape)
print(iw.head(3).to_string()); print(iw.shape)
print(arr[arr.arrival_utc.notna()].station.value_counts())