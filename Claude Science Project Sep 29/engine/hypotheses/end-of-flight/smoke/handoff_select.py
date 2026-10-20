"""Parent groups of a K-strided hand-off for an extra-descents pass (overnight order A step 4, 19 Oct 2026).

    python handoff_select.py HANDOFF_DIR OUT_DIR K LAT_MIN GROUP NGROUPS

Takes the K-strided subset (original rows 0, K, 2K, ...; as handoff_stride.py), keeps the subset rows whose 00:11 latitude
(handoff.npy column 1) is >= LAT_MIN, and of those keeps every NGROUPS-th starting at GROUP. Writes handoff.toml and handoff.npy
for those rows (same headers, weights unchanged) and select.json with, for each kept row, its index in the K-strided subset
("subset_index"), so the extra descents can be pooled with the first pass parent by parent. The selection depends only on the
00:11 state, never on any descent, so pooling the passes with fixed per-parent weights is exact.
"""
import gzip, json, pathlib, sys
import numpy as np

SEP = "\n[[row]]\n"


def main(src, out, k, lat_min, grp, ng):
    src, out = pathlib.Path(src), pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    head, *rows = gzip.open(src / "handoff.toml.gz", "rt").read().split(SEP)
    h = np.load(src / "handoff.npy"); assert len(rows) == len(h)
    orig = np.arange(0, len(rows), k); sel = np.nonzero(h[orig, 1] >= lat_min)[0][grp::ng]
    keep = orig[sel]
    body = head + "".join(SEP + rows[i] for i in keep)
    (out / "handoff.toml").write_text(body if body.endswith("\n") else body + "\n")
    np.save(out / "handoff.npy", h[keep])
    json.dump({"source": str(src), "k": k, "lat_min": lat_min, "group": grp, "ngroups": ng, "rows_kept": int(len(keep)),
               "subset_rows": int(len(orig)), "subset_rows_selected": int((h[orig, 1] >= lat_min).sum()),
               "subset_index": sel.tolist(), "original_rows": keep.tolist()}, open(out / "select.json", "w"))
    print(f"{src}: group {grp}/{ng}: {len(keep)} parents (subset {len(orig)}, lat >= {lat_min}: {(h[orig, 1] >= lat_min).sum()})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]))
