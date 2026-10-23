cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
python - <<'EOF'
p='run.py'; s=open(p).read()
s=s.replace('t = pd.to_datetime(r.start_logger, utc=True).astype("int64") / 1e9', 't = (pd.to_datetime(r.start_logger, utc=True) - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds()')
open(p,'w').write(s)
EOF
python -c "
import sys; sys.path[:0]=['.','..','../weak_signal']; import run as RUN
for lg in ('3315','3275'):
    f,info=RUN.own_8mar_outside_files(lg); print(lg, len(f), info)"
tail -2 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/templates.log