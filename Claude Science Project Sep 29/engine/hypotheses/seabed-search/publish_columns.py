"""Publish this module's per-impact columns for one release on the exchange.

The composer and the other consumers should never transcribe this module's likelihood: a
transcription is a second implementation that can drift from lib.rs silently. Where `mh370 evaluate`
cannot read a release directly (end of flight's compact run C layout), this module runs evaluate
itself and posts the columns, row-aligned with the release's own impact table.

  python hypotheses/seabed-search/publish_columns.py <adapted runs dir>... --out <exchange dir>

Columns per seed, row-aligned with `impacts32.npy` (or `impacts.npy`):
  seabed-lnL.npy                 float64  ln P(no find | impact), run.toml as committed
  seabed-coverage-phase2.npy     float32  raw raster coverage of the ATSB Phase 2 union
  seabed-coverage-bluefin.npy    float32  raw raster coverage of Bluefin-21/Artemis 2014
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BINARY = ROOT / "target" / "release" / "mh370"
sys.path.insert(0, str(ROOT / "hypotheses" / "pleiades" / "prepare"))
import compact_eval as ce  # noqa: E402

WANT = [("seabed-lnL.npy", "seabed-search:loglik", np.float64),
        ("seabed-coverage-phase2.npy", "seabed-search:covered_fraction_phase2-2014-2017", np.float32),
        ("seabed-coverage-bluefin.npy", "seabed-search:covered_fraction_bluefin-2014", np.float32)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()
    scratch = ROOT / "runs" / "seabed-search-analysis" / "scratch-publish"
    scratch.mkdir(parents=True, exist_ok=True)
    sums, nrows = [], 0
    for d in a.runs:
        name = d.name
        for sd in sorted((d / "bto-bfo").glob("seed-*")):
            dest = a.out / name / sd.name
            dest.mkdir(parents=True, exist_ok=True)
            tmp = None
            try:
                src = sd / "impacts.npy"
                if ce.is_compact(sd):
                    tmp = scratch / f"c-{name}-{sd.name}"
                    src = ce.eval_input(sd, tmp)
                out = scratch / f"e-{name}-{sd.name}"
                subprocess.run([str(BINARY), "evaluate", str(HERE / "run.toml"), str(src), str(out)],
                               check=True, capture_output=True, cwd=ROOT)
            finally:
                if tmp is not None:
                    shutil.rmtree(tmp, ignore_errors=True)
            cols = json.loads((out / "evaluate.json").read_text())["columns"]
            V = np.load(out / "evaluate.npy")
            for fn, col, dt in WANT:
                np.save(dest / fn, V[:, cols.index(col)].astype(dt))
                h = hashlib.sha256((dest / fn).read_bytes()).hexdigest()
                sums.append(f"{h}  {name}/{sd.name}/{fn}")
            nrows += V.shape[0]
            shutil.rmtree(out, ignore_errors=True)
            print(f"  {name}/{sd.name} {V.shape[0]:,} rows", flush=True)
    (a.out / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    return nrows


if __name__ == "__main__":
    print(f"{main():,} rows published")
