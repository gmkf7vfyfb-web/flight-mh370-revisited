P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
cd "$P" && PYTHONPATH=. python - <<'EOF'
import sys; sys.argv=["x"]
import imos_ram_grid as G
P,rx=G.plan(1.0,[-30,0,30],"/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables")
print(P.run.sum(), P.groupby(["priority"]).run.sum().to_dict()); print(P[P.run].groupby("logger").size().to_dict()); print(rx)
print(P.head(8).to_string())
EOF