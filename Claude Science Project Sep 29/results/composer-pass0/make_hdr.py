"""Composer pass 0: write the plain-text header the Rust driver reads (seed-<k>.hdr) from prep_inputs.py's JSON,
adding core (b)'s final per-mode evidence from core's run.json (used only for refusal case R1).
Usage: python make_hdr.py <stratum> <input dir>"""
import json, pathlib, sys
st, d = sys.argv[1], pathlib.Path(sys.argv[2])
core = json.loads((pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/next-run") / st / "run.json").read_text())
fmt = lambda x: "-inf" if x is None else repr(float(x))
for k in (1, 2, 3, 4):
    h = json.loads((d / f"seed-{k}.json").read_text())
    rep = [r for r in core["replicates"] if r["seed"] == k][0]
    lines = [f"{k}\t{h['rows']}", "\t".join(h["columns"])]
    lines += ["\t".join(fmt(m[x]) for x in ("prior_weight", "log_evidence", "posterior_probability")) for m in h["modes"]]
    lines += ["\t".join(fmt(m[x]) for x in ("prior_weight", "log_evidence", "posterior_probability")) for m in rep["modes"]]
    (d / f"seed-{k}.hdr").write_text("\n".join(lines) + "\n")
print("ok", st)
