
recs = pd.read_csv(RUN.MODULE / "data" / "imos" / "recordings.csv"); r = recs[recs.logger == 3315].copy()
t = pd.to_datetime(r.start_logger, utc=True).astype("int64") / 1e9
print(t.iloc[:3].values, r.dur_s.iloc[:3].values, ((t+r.dur_s) >= 1394238240.0).sum(), (t <= 1394242860.0).sum())
keep = (t + r.dur_s < 1394238240.0) | (t > 1394242860.0); print(keep.sum(), (~keep).sum())
