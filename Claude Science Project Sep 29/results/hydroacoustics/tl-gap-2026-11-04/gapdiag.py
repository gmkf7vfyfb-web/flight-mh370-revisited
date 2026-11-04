"""Diagnostics for the Cape Leeuwin vs Wake loss gap (back-to-basics step 1, 4 Nov 2026).

Uses the frozen chain tl-chain-2026-10-27 UNCHANGED (imported read-only). Adds one thing only: a forward march that
records, every REC metres, the depth-integrated water-column energy F(r) = sum_{z < seafloor} |f3 u|^2 dz
(= r * integral of |p|^2 dz, i.e. cylindrical spreading removed) and the seafloor depth. Physics, grid (G2), seabed
models, self-starter, absorbing layer and the end window are exactly those of tlchain.ram.RamLayered.march.

Job kinds (run with `python gapdiag.py run <jobs.json> <out.jsonl> <nproc>`):
  'rev'  frozen tlchain.run.do() (reciprocal run from the hydrophone, rec_every_m -> TL vs source position at the
         first output depth); nothing added.
  'fwd'  forward march from the impact end, source depth zsrc, end-window intensity at the hydrophone depth and F(r).
  'krk'  frozen chain.kraken_freq (adiabatic coherent modes, RAOC) from the impact end; reference only.
"""
from __future__ import annotations

import json
import os
import pickle
import sys
import time
import traceback
from multiprocessing import get_context

import numpy as np

FROZEN = os.environ.get("TLCHAIN_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "..",
                                                     "tlchain", "tl-chain-2026-10-27"))
sys.path.insert(0, FROZEN)
os.environ.setdefault("TLCHAIN_GLOBSED", "/Users/pete/Downloads/mh370-ocean-data/globsed/GlobSed-v3.nc")
from tlchain import chain as C            # noqa: E402
from tlchain import run as TR             # noqa: E402
from tlchain.bottom import Bottom         # noqa: E402
from tlchain.ram import RamLayered        # noqa: E402
from pyram.solve import solve             # noqa: E402


class RamFlux(RamLayered):
    """RamLayered.march plus a record of F(r) and the seafloor depth. Nothing else differs."""

    def march(self):
        rmax0 = self._rmax
        self.setup()
        self._rmax = rmax0
        nr = int(np.round(self._rmax / self._dr)) - 1
        zi = self._outz / self._dz
        iz = np.floor(zi).astype(int); fz = zi - iz
        acc = np.zeros(len(self._outz)); nacc = 0
        step_rec = max(1, int(round(self._rec_every / self._dr)))
        r_win = self._rmax - self._window
        rec_r, rec_F, rec_zb, rec_Fup = [], [], [], []
        for rn in range(nr):
            self.updat()
            solve(self.u, self.v, self.s1, self.s2, self.s3, self.r1, self.r2, self.r3, self.iz, self.nz, self._np)
            self.r = (rn + 2) * self._dr
            if self.r >= r_win:
                p = (1 - fz) * self.f3[iz] * self.u[iz] + fz * self.f3[iz + 1] * self.u[iz + 1]
                acc += np.abs(p) ** 2 / self.r; nacc += 1
            if rn % step_rec == 0:
                k = int(self.iz)
                pz = self.f3[: k + 1] * self.u[: k + 1]
                e = np.abs(pz) ** 2 * self._dz
                rec_r.append(self.r); rec_F.append(float(e.sum())); rec_zb.append(float(self._zb_now))
                rec_Fup.append(float(e[: min(k + 1, int(1500.0 / self._dz))].sum()))   # energy above 1,500 m
        return dict(I=acc / max(nacc, 1), n_window=nacc, rec_r=np.array(rec_r), rec_F=np.array(rec_F),
                    rec_zb=np.array(rec_zb), rec_Fup=np.array(rec_Fup), nz=self.nz, nr=nr)


def fwd_freq(sec, f, zsrc, rd, bottom, rec_every_m=1000.0, mode="native"):
    r, zb, h, zs2, rp, Cr = C.ram_env(sec, bottom, mode, rd)
    lam = 1500.0 / f
    L = sec["L_km"] * 1e3
    od = np.minimum(np.asarray([rd], float), zb[-1] - 1.0)
    dr = min(5.0 * lam, 250.0)
    m = RamFlux(f, zsrc, od, zs2, rp, Cr, r, zb, h, bottom, rmax=L, dr=dr, dz=0.05 * lam, np_pade=8,
                window_m=1000.0, rec_every_m=rec_every_m)
    o = m.march()
    o["out_depths_used"] = od
    return o


def do(job):
    t0 = time.time()
    try:
        if job["kind"] == "rev":
            row = TR.do(job)
            row["kind"] = "rev"
            return row
        sec = pickle.load(open(job["sec"], "rb"))
        bot = Bottom(**job["bottom"])
        if job["kind"] == "fwd":
            o = fwd_freq(sec, job["f"], job["zsrc"], job["rd"], bot, job.get("rec_every_m", 1000.0), job.get("mode", "native"))
            row = dict(I=o["I"].tolist(), rec_r=o["rec_r"][::1].tolist(), rec_F=o["rec_F"].tolist(), rec_zb=o["rec_zb"].tolist(),
                       rec_Fup=o["rec_Fup"].tolist(), out_depths_used=o["out_depths_used"].tolist())
        elif job["kind"] == "krk":
            wd = job["work"]
            tag = f"k{os.getpid()}_{abs(hash(job['id'])) % 10**8}"
            o = C.kraken_freq(sec, job["f"], job["src_depths"], job["rd"], wd, tag, bottom=bot, mode=job.get("mode", "native"), opt="RAOC")
            row = dict(ok=o["ok"], nm_min=o["nm_min"], rd_used=o["rd_used"], err=o["err"][-300:], I=(o["I"].tolist() if o["ok"] else None))
        row.update(id=job["id"], kind=job["kind"], status="ok", wall_s=time.time() - t0, L_km=sec["L_km"])
    except Exception as e:  # noqa: BLE001
        row = dict(id=job["id"], kind=job.get("kind"), status="error", err=f"{type(e).__name__}: {e}"[:500],
                   tb=traceback.format_exc()[-800:], wall_s=time.time() - t0)
    return row


def run(jobs_path, out_path, nproc):
    jobs = json.load(open(jobs_path))
    done = set()
    if os.path.exists(out_path):
        for ln in open(out_path):
            try:
                r = json.loads(ln)
                if r.get("status") == "ok":
                    done.add(r["id"])
            except json.JSONDecodeError:
                pass
    todo = sorted([j for j in jobs if j["id"] not in done], key=lambda j: -j.get("cost", 0))
    print(f"{len(jobs)} jobs, {len(done)} done, {len(todo)} to run, {nproc} processes", flush=True)
    t0 = time.time(); n = 0
    with get_context("spawn").Pool(int(nproc), maxtasksperchild=20) as p, open(out_path, "a") as fo:
        for row in p.imap_unordered(do, todo):
            fo.write(json.dumps(row) + "\n"); fo.flush(); n += 1
            if n % 20 == 0 or row["status"] != "ok":
                print(f"{n}/{len(todo)} {time.time() - t0:.0f}s {row['id']} {row['status']} {row.get('err', '')[:150]}", flush=True)
    print("done", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4])
