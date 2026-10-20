"""Fixed every-k-th-row subset of a 00:11 hand-off (overnight order A, 19 Oct 2026; core supplement README section 5, rule B).

    python handoff_stride.py HANDOFF_DIR OUT_DIR K [OFFSET]

Keeps rows OFFSET, OFFSET + K, ... of handoff.toml (the state the terminal stage reads) and the same rows of handoff.npy
(row-aligned), and writes stride.json with the original row index of each kept row. The [stop] and [lookahead] headers are
copied unchanged, so the terminal stage reads the subset with handoff::read_corrected exactly as a full hand-off. The weights
are not changed: a consumer multiplies the subset's weights by K (rule B: u2 x k).
"""
import gzip, json, pathlib, sys, hashlib
import numpy as np

SEP = "\n[[row]]\n"


def main(src, out, k, off=0):
    src, out = pathlib.Path(src), pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    gz = src / "handoff.toml.gz"
    text = gzip.open(gz, "rt").read() if gz.exists() else (src / "handoff.toml").read_text()
    head, *rows = text.split(SEP)
    h = np.load(src / "handoff.npy")
    assert len(rows) == len(h), (len(rows), len(h))
    keep = np.arange(off, len(rows), k)
    body = head + "".join(SEP + rows[i] for i in keep)
    if not body.endswith("\n"):
        body += "\n"
    (out / "handoff.toml").write_text(body)
    np.save(out / "handoff.npy", h[keep])
    json.dump({"source": str(src), "k": k, "offset": off, "rows_in": len(rows), "rows_kept": int(len(keep)),
               "kept_original_rows": keep.tolist(),
               "sha256_handoff_toml_subset": hashlib.sha256(body.encode()).hexdigest()}, open(out / "stride.json", "w"))
    print(f"{src}: kept {len(keep)} of {len(rows)} rows (k = {k}, offset {off})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 0)
