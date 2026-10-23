hs=pd.read_csv(H+'searches_run_j/panels/h08s_suppression.csv'); print(hs.shape); print(hs.head(5).to_string()); print(hs.columns.tolist())
import glob
print(glob.glob(H+'h08s_template/*') if os.path.exists(H+'h08s_template') else 'no h08s_template checkout')
pc=pd.read_csv(H+'searches_run_j/panels/panel_candidates.csv'); print(pc.columns.tolist()); print(pc[pc.receiver=='H08S'][['panel','time_utc','detector','band_hz','p','label']].head(30).to_string())