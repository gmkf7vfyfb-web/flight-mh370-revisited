"""End-of-flight smoke contract: the six acceptance items, the children-per-parent pilot (item 7),
the measured cost (item 8), and the impact-displacement report requested for Pleiades section 11.

    python3 analyse.py <terminal-out-dir> <hand-off run dir> <out.json>

Reads impacts.npy, terminal.json and run.json from a `mh370 terminal` output, and handoff.toml from
the hand-off it was run on. Writes one JSON with every number the coordination entry quotes, so no
figure is re-typed by hand. SMOKE-SCALE: everything this produces is plumbing, not evidence.
"""
import json, math, sys, tomllib
from pathlib import Path
import numpy as np

T0019B = 1394237977.443          # 00:19:37.443 UTC, the R1200 log-on acknowledge
GLIDE_BOUND_NM = 103.4           # still-air energy-height glide from 35,000 ft, brief section 11
NM = 1852.0
R_EARTH_M = 6_371_008.8

# Latents that are NaN by declaration, never a defect.
DECLARED_NAN = {
    # sinks_not_floats retired 2026-10-09; nothing declared NaN by design remains but these:
    "impact_energy_transferred_j", "energy_transfer_t05_s", "energy_transfer_t95_s",
    "energy_transfer_tau90_s", "energy_transfer_peak_rate_w", "energy_transfer_n_pulses",
}
# NaN by construction in a stated case, checked case by case below.
CONDITIONAL_NAN = {"last_burst_latitude_deg", "last_burst_longitude_deg", "onset_support_truncated_fraction",
                   "realised_flameout_unix_s", "flameout_minus_predicted_s"}


def gc(lat1, lon1, lat2, lon2):
    """Great-circle distance (NM) and initial bearing (deg) from point 1 to point 2."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(lon2 - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    d = 2 * R_EARTH_M * np.arcsin(np.sqrt(np.clip(a, 0, 1))) / NM
    b = np.degrees(np.arctan2(np.sin(dl) * np.cos(p2), np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)))
    return d, np.mod(b, 360.0)


def advance(lat, lon, ve, vn, dt):
    """Flat-earth step, adequate over the minutes involved. dt may be negative."""
    dlat = np.degrees(vn * dt / R_EARTH_M)
    dlon = np.degrees(ve * dt / (R_EARTH_M * np.cos(np.radians(lat))))
    return lat + dlat, lon + dlon


def wq(x, w, qs):
    o = np.argsort(x); x, w = x[o], w[o]
    c = np.cumsum(w); c /= c[-1]
    return [float(np.interp(q, c, x)) for q in qs]


def main(out_dir, handoff_run, out_json):
    out_dir, handoff_run = Path(out_dir), Path(handoff_run)
    run = json.loads((out_dir / "run.json").read_text())
    cols = run["impact_columns"]
    ci = {c: i for i, c in enumerate(cols)}
    families = run["terminal"].get("module_families") or []
    report = {"source": str(out_dir), "runtime_s": run.get("runtime_s"), "code_revision": run.get("code_revision"),
              "children": run["terminal"].get("children"), "replicates": []}

    for rep in run["replicates"]:
        case, seed = rep["case"], rep["seed"]
        d = out_dir / case / f"seed-{seed}"
        X = np.load(d / "impacts.npy")
        diag = json.loads((d / "terminal.json").read_text())
        ho = tomllib.loads((handoff_run / case / f"seed-{seed}" / "handoff.toml").read_text())
        rows = ho["row"]
        parents = len(rows)
        fuel = np.array([r["aircraft"]["fuel_kg"] for r in rows])
        dry_rows = np.flatnonzero(~(fuel > 0))
        lat = lambda n: X[:, ci[f"latent:{n}"]]
        w = X[:, ci["weight"]]
        parent = X[:, ci["parent"]].astype(int)
        fam = X[:, ci["family"]].astype(int)
        r = {"case": case, "seed": seed, "parents": parents, "descents": int(len(X)),
             "terminal_json": diag}

        # Item 2: every parent has at least one impact (the stage errors on any empty descend).
        per_parent = np.bincount(parent, minlength=parents)
        r["item2_parents_without_impact"] = int((per_parent == 0).sum())

        # Item 3: rows dry at the hand-off take the no-thrust branch; the rest derive flame-out in-stage.
        is_dry_child = np.isin(parent, dry_rows)
        thrust = lat("engines_thrusting_at_onset")
        flown_dry = lat("powered_after_core_exhaustion_s")
        r["item3"] = {
            "hand_off_fuel_kg_median": float(np.median(fuel)),
            "rows_dry_at_hand_off": int(len(dry_rows)),
            "dry_parent_descents": int(is_dry_child.sum()),
            "dry_parent_descents_labelled_thrusting": int((is_dry_child & (thrust > 0)).sum()),
            "wet_parent_descents": int((~is_dry_child).sum()),
            "fuel_fallback_fired": int((lat("fuel_kg_assumed") != 0).sum()),
            "mass_fallback_fired": int((lat("mass_kg_assumed") != 0).sum()),
            # The burn-gap cost: children the core flew powered after its own tanks were dry.
            "share_flown_powered_after_core_exhaustion": float(w[flown_dry > 0].sum() / w.sum()),
            "flown_powered_after_core_exhaustion_s_quantiles_5_50_95_of_those": (
                wq(flown_dry[flown_dry > 0], w[flown_dry > 0], [0.05, 0.5, 0.95]) if (flown_dry > 0).any() else None),
        }

        # Item 4: full ImpactView present; latents present and finite except declared NaN.
        latent_names = [c.split(":", 1)[1] for c in cols if c.startswith("latent:")]
        bad = {}
        for n in latent_names:
            nan = int(np.isnan(lat(n)).sum())
            if nan and n not in DECLARED_NAN and n not in CONDITIONAL_NAN:
                bad[n] = nan
        r["item4"] = {"latent_columns": len(latent_names),
                      "unexpected_nan_by_latent": bad,
                      "declared_nan_all_nan": all(np.isnan(lat(n)).all() for n in DECLARED_NAN if n in latent_names),
                      "impact_fields_finite": bool(np.isfinite(X[:, [ci[c] for c in cols[:20] if c != "weight"]]).all())}

        # Item 5: impact spread per family, weighted under the held-out option ("none").
        arc = X[:, ci["arc_distance_nm"]]
        il, io = X[:, ci["latitude_deg"]], X[:, ci["longitude_deg"]]
        spread = []
        for f in np.unique(fam):
            m = fam == f
            wf = w[m]
            if wf.sum() <= 0:
                continue
            clat, clon = wq(il[m], wf, [0.5])[0], wq(io[m], wf, [0.5])[0]
            dist, _ = gc(clat, clon, il[m], io[m])
            q50, q90 = wq(dist, wf, [0.5, 0.9])
            beyond = float(wf[np.abs(arc[m]) > GLIDE_BOUND_NM].sum() / wf.sum())
            spread.append({"family": int(f), "label": families[f] if f < len(families) else None,
                           "descents": int(m.sum()), "weight_share": float(wf.sum() / w.sum()),
                           "radius_50_nm": q50, "radius_90_nm": q90,
                           "arc_distance_nm_5_50_95": wq(arc[m], wf, [0.05, 0.5, 0.95]),
                           "share_beyond_glide_bound_of_arc": beyond,
                           "flag": "collapsed" if q90 < 0.5 else ("beyond glide bound" if beyond > 0.05 else None)})
        r["item5_spread_by_family"] = spread

        # Core requests 2 and 3: provenance of the mechanism and pricing of the burn.
        mech = lat("onset_mechanism")
        r["requests_2_3"] = {
            "mechanism_from_draw_share": float(w[lat("mechanism_from_draw") == 1].sum() / w.sum()),
            "mechanism_relabelled_dry_share": float(w[lat("mechanism_relabelled_dry") == 1].sum() / w.sum()),
            "mechanism_share_anticipatory_fuelcue_flameout": [float(w[mech == k].sum() / w.sum()) for k in (0, 1, 2)],
            "family_prior_zero_share": float(w[lat("family_prior") == 0].sum() / w.sum()),
            "fuel_unpriced_s_share_nonzero": float(w[lat("fuel_unpriced_s") > 0].sum() / w.sum()),
            "fuel_below_tables_s_share_nonzero": float(w[lat("fuel_below_tables_s") > 0].sum() / w.sum()),
            "fuel_extrapolated_s_share_nonzero": float(w[lat("fuel_extrapolated_s") > 0].sum() / w.sum()),
            "fuel_extrapolated_s_mean": float((w * lat("fuel_extrapolated_s")).sum() / w.sum()),
            "fuel_below_tables_s_mean": float((w * lat("fuel_below_tables_s")).sum() / w.sum()),
        }

        # Breakup family (settling's candidate rule, provisional): drawn share and mean probabilities.
        dc = lat("debris_class")
        r["breakup"] = {
            "refused_share": float(w[~np.isfinite(dc)].sum() / w.sum()),
            "drawn_share_intact_broken_fragmented": [float(w[dc == k].sum() / w.sum()) for k in (0, 1, 2)],
            "mean_probability_intact_broken_fragmented": [float(np.nansum(w * lat(n)) / w.sum()) for n in
                                                          ("breakup_p_intact", "breakup_p_broken", "breakup_p_fragmented")],
        }

        # Pleiades section 11: displacement from the 00:19:37 position.
        to = X[:, ci["takeover_unix_s"]]
        tlat, tlon = X[:, ci["takeover_latitude_deg"]], X[:, ci["takeover_longitude_deg"]]
        blat, blon = lat("last_burst_latitude_deg"), lat("last_burst_longitude_deg")
        ve, vn = lat("takeover_ground_velocity_east_mps"), lat("takeover_ground_velocity_north_mps")
        p_lat = np.full(len(X), np.nan); p_lon = np.full(len(X), np.nan)
        cls = np.full(len(X), "", dtype=object)
        flew = np.isfinite(blat)                                   # module flew through 00:19:37
        p_lat[flew], p_lon[flew] = blat[flew], blon[flew]; cls[flew] = "flown"
        after = (~flew) & (to >= T0019B)                           # takeover after the burst
        p_lat[after], p_lon[after] = advance(tlat[after], tlon[after], ve[after], vn[after], T0019B - to[after])
        cls[after] = "back-extrapolated"
        down = (~flew) & (to < T0019B)                             # already down by 00:19:37
        p_lat[down], p_lon[down] = il[down], io[down]; cls[down] = "down before 00:19:37"
        disp, bear = gc(p_lat, p_lon, il, io)
        nw = (bear >= 270.0) & (bear < 360.0)

        def pleiades(mask, weights):
            ws = weights[mask].sum()
            if ws <= 0:
                return None
            g = lambda sel: float(weights[mask & sel].sum() / ws)
            return {"weight_share": float(ws / weights.sum()),
                    "displacement_nm_50_90_99": wq(disp[mask], weights[mask], [0.5, 0.9, 0.99]),
                    "nw_ge_30nm": g(nw & (disp >= 30)), "nw_ge_50nm": g(nw & (disp >= 50)),
                    "any_dir_ge_30nm": g(disp >= 30), "any_dir_ge_50nm": g(disp >= 50),
                    "inside_arc_ge_30nm": g(arc <= -30), "inside_arc_ge_50nm": g(arc <= -50)}

        def weights_for(column):
            if column is None:
                return w
            ll = X[:, ci[column]]
            lw = np.where(np.isfinite(ll), ll, -np.inf)
            m = lw.max()
            return w * np.exp(lw - m) if np.isfinite(m) else np.zeros_like(w)

        pl = {}
        for label, column in [("none", None), ("both/no-offset", "loglik:both/no-offset"),
                              ("both/startup-offset", "loglik:both/startup-offset")]:
            if column is not None and column not in ci:
                continue
            ww = weights_for(column)
            pl[label] = {"all": pleiades(np.ones(len(X), bool), ww),
                         "by_family": {int(f): pleiades(fam == f, ww) for f in np.unique(fam)},
                         "position_class_share": {k: float(ww[cls == k].sum() / ww.sum()) for k in
                                                  ["flown", "back-extrapolated", "down before 00:19:37"]}}
        r["pleiades_s11"] = pl
        report["replicates"].append(r)

    report["families"] = families
    Path(out_json).write_text(json.dumps(report, indent=1, default=float))
    print("wrote", out_json)


if __name__ == "__main__":
    main(*sys.argv[1:4])
