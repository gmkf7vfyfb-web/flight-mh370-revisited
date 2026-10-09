#!/usr/bin/env python3
"""Build the internal fuel model file for core (fuel session, 10 Oct 2026; core request 16 C).

Usage (from engine/):  python fuel-model/build_internal.py
Writes data/external/fuel-model/internal-v1.json (git-ignored via /data/external; LOCAL USE ONLY:
derived from FPPM-confidential cells; never commit, never upload to a third-party service).

Contents:
  "tables"        the 16 extract.py grids, unchanged (so FuelTables::from_json still parses it);
  "model"         calibration and correction parameters (from calibrate.py);
  "grid"          dense standard-day flow, both engines, kg/h, BEFORE kappa and temperature but
                  WITH the lookup fixes (F3, F4) and the drag-rise term: flow[i_fl][i_w][i_m] on
                  fl_nodes x weight_t x mach, with a flag bitmask per cell (internal.FLAG_BITS).
                  Trilinear interpolation reproduces internal.Internal.ff_shape to < 0.05 %.
  "grid_inop"     the same for one engine inoperative (flow of the live engine), FL015-300;
  "ceiling_fl"    highest FL the tables price at each weight (F5 bound), 1-FL resolution;
  "test_vectors"  off-node points with the full model value, for core's unit test.
Core applies:  FF = kappa_traj * tau(dISA, M) * trilinear(grid),  kappa_traj ~ N(kappa, sd),
               tau = 1 + 0.003 * dISA * (1 + 0.2 M^2).
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import calibrate  # noqa: E402
import internal  # noqa: E402

ENGINE = HERE.parent
TABLES = ENGINE / "data/fuel-tables.json"
OUT = ENGINE / "data/external/fuel-model/internal-v1.json"

FL_NODES = [15.0, 30.0, 50.0] + [float(x) for x in range(60, 431, 10)]
W_NODES = [float(x) for x in range(150, 251)]
M_NODES = [round(0.40 + 0.005 * k, 3) for k in range(101)]  # 0.40 .. 0.90
FL_INOP = [15.0, 30.0, 50.0] + [float(x) for x in range(60, 301, 10)]
M_INOP = [round(0.35 + 0.005 * k, 3) for k in range(81)]  # 0.35 .. 0.75


def dense(model, fls, ws, ms):
    flow = np.full((len(fls), len(ws), len(ms)), np.nan)
    flag = np.zeros(flow.shape, dtype=np.int64)
    for a, fl in enumerate(fls):
        for b, w in enumerate(ws):
            for c, m in enumerate(ms):
                f, fg = model.ff_shape(fl, w, m)
                if f is not None:
                    flow[a, b, c] = f
                flag[a, b, c] = internal.flag_mask(fg)
    return flow, flag


def trilinear(grid, fls, ws, ms, fl, w, m):
    def idx(nodes, x):
        k = int(np.clip(np.searchsorted(nodes, x, side="right") - 1, 0, len(nodes) - 2))
        return k, (x - nodes[k]) / (nodes[k + 1] - nodes[k])
    (i, x), (j, y), (k, z) = idx(fls, fl), idx(ws, w), idx(ms, m)
    acc = 0.0
    for di, wx in ((0, 1 - x), (1, x)):
        for dj, wy in ((0, 1 - y), (1, y)):
            for dk, wz in ((0, 1 - z), (1, z)):
                acc += wx * wy * wz * grid[i + di, j + dj, k + dk]
    return acc


def main():
    _, cal_tab, model = calibrate.run(temp="fppm")  # table model: fixes c_hi, q_hi
    flow, flag = dense(model, FL_NODES, W_NODES, M_NODES)
    flow = np.round(flow, 2)  # the stored values ARE the model: calibrate and test on them
    grid_doc = dict(fl_nodes=FL_NODES, weight_t=W_NODES, mach=M_NODES, flow_kg_h=flow.tolist(), flags=flag.tolist())
    gm = lambda temp: internal.GridModel(grid_doc, temp=internal.tau_fppm if temp == "fppm" else internal.tau_none)
    items, cal = calibrate.calibrate_model(gm("fppm"), cal_tab)  # the model of record is the grid
    items_none, cal_none = calibrate.calibrate_model(gm("none"), cal_tab)
    OUTR = ENGINE.parent / "results/fuel-model"
    items.assign(temperature_rule="fppm").to_csv(OUTR / "internal-calibration-items-fppm.csv", index=False, float_format="%.6g")
    items_none.assign(temperature_rule="none").to_csv(OUTR / "internal-calibration-items-none.csv", index=False, float_format="%.6g")
    (OUTR / "internal-calibration.json").write_text(json.dumps(dict(fppm=cal, none=cal_none, table_model_fppm=cal_tab), indent=1, default=float))
    resid_sd = cal["groups"]["Boeing-T4"]["resid_sd"]
    j = cal["joint"]
    prior_sd = math.sqrt(j["se"] ** 2 + j["tau_between"] ** 2 + resid_sd**2)
    inop = internal.Internal(TABLES, kappa=1.0, c_hi=0.0, inop=True)
    flow_i, flag_i = dense(inop, FL_INOP, W_NODES, M_INOP)
    flow_i = np.round(flow_i, 2)
    ceiling = [model.tb.ceiling_fl(w) for w in W_NODES]
    # test vectors: off-node, inside the posterior envelope and around it
    rng = np.random.default_rng(20261010)
    tv = []
    while len(tv) < 300:
        fl = float(rng.uniform(250, 430)); w = float(rng.uniform(174, 222)); m = float(rng.uniform(0.70, 0.86))
        d = float(rng.uniform(-5, 15))
        f, fg = model.ff_shape(fl, w, m)
        if f is None or fg.get("above_ceiling"):
            continue
        g = gm("fppm").ff_shape(fl, w, m)[0]
        if g is None:
            continue
        tv.append(dict(fl=fl, weight_t=w, mach=m, delta_isa_k=d, flow_isa_kg_h=f, flow_grid_kg_h=g,
                       tau=internal.tau_fppm(d, m), kappa=j["kappa"],
                       flow_full_kg_h=j["kappa"] * internal.tau_fppm(d, m) * f, flags=internal.flag_mask(fg)))
    err = float(np.median([abs(t["flow_grid_kg_h"] / t["flow_isa_kg_h"] - 1) for t in tv]))
    for t in tv:  # the model of record is the grid; flow_isa_kg_h (table lookup) is for reference only
        t["flow_full_kg_h"] = j["kappa"] * t["tau"] * t["flow_grid_kg_h"]
    doc = dict(
        source=dict(tables=json.loads(TABLES.read_text())["source"],
                    note="LOCAL USE ONLY. Derived from FPPM-confidential cells; never commit or upload."),
        tables=json.loads(TABLES.read_text())["tables"],
        model=dict(
            version="internal-v1", formula="FF = kappa_traj * tau(dISA, M) * grid(FL, W, M)",
            kappa=dict(mean=j["kappa"], sd=prior_sd, sd_components=dict(se_mean=j["se"], tau_between_groups=j["tau_between"],
                       state_residual=resid_sd), convention="multiplier on flow; > 1 burns more than the tables"),
            kappa_alternatives=dict(
                boeing_only=dict(mean=cal["boeing"]["kappa"], sd=math.sqrt(cal["boeing"]["se"] ** 2 + cal["boeing"]["resid_sd"] ** 2)),
                mh371_only=dict(mean=cal["groups"]["MH371"]["kappa"], sd=math.sqrt(cal["groups"]["MH371"]["se"] ** 2 + resid_sd**2)),
                joint_without_temperature=dict(mean=cal_none["joint"]["kappa"], sd=math.sqrt(cal_none["joint"]["se"] ** 2 + cal_none["joint"]["tau_between"] ** 2 + resid_sd**2))),
            temperature=dict(rule="fppm_tat", formula="tau = 1 + 0.003 * dISA_K * (1 + 0.2 * M^2)", standard_day_tau=1.0),
            drag_rise=dict(m_dd=internal.M_DD, c=cal["c_hi"], q=cal["q_hi"], cl_ref=internal.CL_REF, s_ref_m2=internal.S_REF,
                           resid_sd=cal["c_hi_resid_sd"], baked_into_grid=True),
            lookup=dict(zero_weight_corner_fix=True, low_mach_rule="physical U-fit when a,b>0 else clamp at slowest schedule",
                        merge_tol_mach=0.005, below_fl060="FL060 Mach curve x holding(FL)/holding(FL060)"),
            extrapolated_sd=dict(above_m084=cal["c_hi_resid_sd"], other=0.0),
            calibration=cal, calibration_without_temperature=cal_none, calibration_table_model=cal_tab),
        grid=dict(fl_nodes=FL_NODES, weight_t=W_NODES, mach=M_NODES, flow_kg_h=np.round(flow, 2).tolist(), flags=flag.tolist(),
                  flag_bits=internal.FLAG_BITS, median_grid_vs_table_lookup=err),
        grid_inop=dict(fl_nodes=FL_INOP, weight_t=W_NODES, mach=M_INOP, flow_kg_h=np.round(flow_i, 2).tolist(), flags=flag_i.tolist(),
                       note="one engine inoperative: flow of the live engine, kg/h; holding_inop / 1.05 and LRC INOP; no calibration applied"),
        ceiling_fl=dict(weight_t=W_NODES, fl=ceiling),
        test_vectors=tv)
    text = json.dumps(doc, allow_nan=True).replace("NaN", "null")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"wrote {OUT} ({len(text) / 1e6:.1f} MB) sha256 {hashlib.sha256(text.encode()).hexdigest()[:16]}; "
          f"kappa {j['kappa']:.4f} sd {prior_sd:.4f}; median |grid/table - 1| {err:.2e}")


if __name__ == "__main__":
    main()
