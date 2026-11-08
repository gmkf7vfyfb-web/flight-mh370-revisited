"""Build the row-aligned energy-transfer sidecars (impact_tau_method = 1) for both final end-of-flight hand-offs.

Usage: python build_sidecars.py HANDOFF_DIR OUT_DIR
Checks the hand-off SHA-256 against HANDOFF_DIR/SHA256SUMS and the presence of READY before reading.
Writes OUT_DIR/settling-energy-transfer-m1-{df,wp}.npz (np.savez_compressed) and a .json description each.
"""
import sys, os, json, hashlib
import numpy as np
import settling_energy_transfer_m1 as m1

HANDOFF_N = {"df": 501102, "wp": 500198}
ROUTE_NAME = {"df": "Davey model + fuel", "wp": "waypoints"}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main(hdir, odir):
    assert os.path.exists(f"{hdir}/READY"), "hand-off READY missing"
    sums = dict(reversed(l.split()) for l in open(f"{hdir}/SHA256SUMS") if l.strip())
    os.makedirs(odir, exist_ok=True)
    for route in ("df", "wp"):
        fn = f"eof-final-handoff-{route}.npz"
        got = sha256(f"{hdir}/{fn}")
        assert got == sums[fn], f"{fn} SHA-256 mismatch"
        z = np.load(f"{hdir}/{fn}")
        h = {k: z[k] for k in z.files}
        n = len(h["mass_kg"]); assert n == HANDOFF_N[route]
        s = m1.build_sidecar(h, route)
        out = f"{odir}/settling-energy-transfer-m1-{route}.npz"
        np.savez_compressed(out, **s)
        desc = {
            "description": "Row-aligned sidecar to the final end-of-flight hand-off: mechanical energy-transfer duration at water entry, impact_tau_method = 1.",
            "owner": "ocean settling (Pete's ruling 8 Nov 2026)",
            "route_model": ROUTE_NAME[route], "route_code": m1.ROUTE_CODE[route],
            "rows": n, "row_order": "identical to the hand-off file; row_index = 0-based hand-off row",
            "handoff_file": f"EX:end-of-flight/final-2026-11-07/results/{fn}", "handoff_sha256": got,
            "method_note": "results/settling/energy-transfer-m1-2026-11-08/settling-energy-transfer-method.md (supersedes as owner's note results/eof-impact-tau-method-oct11.md, which is unchanged)",
            "columns": {k: str(v.dtype) for k, v in s.items()},
            "parameters": {"a_bar_g": m1.A_BAR_G, "l_eff_fraction_of_63.7_m": m1.L_EFF_FRAC,
                           "blend_band_deg": m1.BAND_DEG, "sensitivity_band_deg": m1.BAND_SENS_DEG,
                           "rng": "splitmix64 counter hash of (salt 0x5E771E0000000001, route_code, seed, row_index, k)"},
            "conventions": [
                "energy_transfer_tau90_s = t95 - t05 (contract of 8 Oct). energy_transfer_tau90_logblend_s is the note's literal log-linear blend of tau90; it differs from t95 - t05 only for 10 < theta < 30 deg.",
                "impact_energy_transferred_j = contact kinetic energy (declared upper bound).",
                "energy_transfer_n_pulses = 1 (declared single-pulse model); stored as float so that NaN can mark a row not computed.",
                "NaN means not computed. No value is filled.",
                "bank_assigned = 1: family_code 2 or 3 with bank_deg == 0.0 (placeholder bank). Method 1 does not use bank.",
                "Columns with suffix _band5_45: band-edge sensitivity, same draws, blend band 5-45 deg.",
                "Contact speed v = sqrt(2 KE / m): ground-relative, wind included, ocean current not subtracted; surface is ISA sea level."],
            "weights": "Not carried. Use log_weight_<treatment> from the hand-off row of the same index.",
            "status": "UNCHECKED",
        }
        json.dump(desc, open(out.replace(".npz", ".json"), "w"), indent=1)
        t = s["energy_transfer_tau90_s"]
        print(route, n, "nan", int(np.isnan(t).sum()), "tau90 min/med/max %.4f %.4f %.4f" % (np.nanmin(t), np.nanmedian(t), np.nanmax(t)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
