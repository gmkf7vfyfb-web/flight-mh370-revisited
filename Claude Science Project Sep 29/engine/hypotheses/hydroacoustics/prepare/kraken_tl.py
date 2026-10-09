"""Range-dependent transmission loss by adiabatic normal modes: KRAKEN modes per range profile, summed
by FIELD (Acoustics Toolbox, M. B. Porter; build artifact acoustics-toolbox-build-arm64.tar.gz).

TL is -20 log10 |p| with FIELD's normalisation (pressure re the free-field pressure at 1 m), for a
point source in cylindrical coordinates ('R'), adiabatic ('A'), omnidirectional ('O'), with
INCOHERENT mode addition ('I'). Incoherent addition is the band- and shot-averaged quantity, which is
what Blackman Fig. 23 plots (a median over shots, band-limited spectra), so a coherent single-tone
TL would be the wrong comparison.

Volume attenuation: Francois-Garrison, inside KRAKEN (top option letter 4 = 'F').
Earth curvature: spherical spreading correction 10 log10(r / (R sin(r/R))) added after FIELD
(0.05 dB at 1,663 km, 0.22 dB at 3,549 km); refraction effects of the earth-flattening transform
are neglected and stated.

Functions:
  write_env(path, title, freq, profiles, sd, rd, bottom, fg)   multi-profile KRAKEN .env
  write_flp(path, rprof_km, rr_km, sd, rd)                     FIELD .flp
  read_shd(path) -> dict(freq, sz, rz, rr_m, p[ntheta, nsz, nrz, nrr])
  tl_path(workdir, root, freq, profiles, rprof_km, rr_km, sd, rd, bottom, fg, at_bin) -> (rr_km, TL[nrz, nrr], n_modes_first)
"""

import os
import pathlib
import subprocess
import time

import numpy as np


def write_env(path, title, freq, profiles, sd, rd, bottom, fg=None, pts_per_lambda=15):
    """profiles: list of (depth_m, z[], c[]); z must start at 0 and end at depth_m.
    bottom: dict(cp, cs, rho, ap) acoustic half-space, attenuation in dB/wavelength."""
    opt = "NVWF" if fg else "NVW "
    lines = []
    for depth, z, c in profiles:
        lines.append(f"'{title}'")
        lines.append(f"{freq:.4f}")
        lines.append("1")
        lines.append(f"'{opt}'")
        if fg:
            lines.append(f"{fg['T']:.2f} {fg['S']:.2f} {fg['pH']:.2f} {fg['z_bar']:.1f}")
        nmesh = max(500, int(pts_per_lambda * depth * freq / min(c)) + 1)   # explicit mesh: the auto mesh was 0.1 dB off in the analytic test
        lines.append(f"{nmesh} 0.0 {depth:.2f}")
        lines.append(f"    {z[0]:.2f} {c[0]:.4f} 0.0 1.0 0.0 0.0")
        for zz, cc in zip(z[1:], c[1:]):
            lines.append(f"    {zz:.2f} {cc:.4f} /")
        if bottom.get("bc") == "R":                      # rigid bottom (analytic tests only)
            lines.append("'R' 0.0")
            lines.append(f"1400.0 {bottom['c_high']:.2f}")
        else:
            lines.append("'A' 0.0")
            lines.append(f"    {depth:.2f} {bottom['cp']:.2f} {bottom.get('cs', 0.0):.2f} {bottom['rho']:.3f} {bottom['ap']:.3f} 0.0 /")
            lines.append(f"1400.0 {bottom['cp']:.2f}")
        lines.append("0.0")
        lines.append(f"{len(sd)}")
        lines.append(" ".join(f"{v:.2f}" for v in sd) + " /")
        lines.append(f"{len(rd)}")
        lines.append(" ".join(f"{v:.2f}" for v in rd) + " /")
    pathlib.Path(path).write_text("\n".join(lines) + "\n")


def write_flp(path, rprof_km, rr_km, sd, rd, opt="RAOI"):
    L = ["/,", f"'{opt}'", "9999", f"{len(rprof_km)}", " ".join(f"{v:.4f}" for v in rprof_km) + " /",
         f"{len(rr_km)}", " ".join(f"{v:.4f}" for v in rr_km) + " /",
         f"{len(sd)}", " ".join(f"{v:.2f}" for v in sd) + " /",
         f"{len(rd)}", " ".join(f"{v:.2f}" for v in rd) + " /",
         f"{len(rd)}", " ".join("0.0" for _ in rd) + " /"]
    pathlib.Path(path).write_text("\n".join(L) + "\n")


def read_shd(path):
    b = pathlib.Path(path).read_bytes()
    lrecl = int(np.frombuffer(b[:4], "<i4")[0])
    rec = 4 * lrecl

    def r(i):
        return b[i * rec:(i + 1) * rec]

    plot_type = r(1)[:10].decode(errors="replace")
    hdr = r(2)
    nfreq, ntheta, nsx, nsy, nsz, nrz, nrr = np.frombuffer(hdr[:28], "<i4")
    freq0, atten = np.frombuffer(hdr[28:44], "<f8")
    freqs = np.frombuffer(r(3)[:8 * nfreq], "<f8")
    sz = np.frombuffer(r(7)[:4 * nsz], "<f4")
    rz = np.frombuffer(r(8)[:4 * nrz], "<f4")
    rr = np.frombuffer(r(9)[:8 * nrr], "<f8")
    p = np.zeros((ntheta, nsz, nrz, nrr), complex)
    irec = 10
    for it in range(ntheta):
        for js in range(nsz):
            for jz in range(nrz):
                x = np.frombuffer(r(irec)[:8 * nrr], "<f4")
                p[it, js, jz] = x[0::2] + 1j * x[1::2]
                irec += 1
    return dict(plot_type=plot_type, freq0=freq0, freqs=freqs, sz=sz, rz=rz, rr_m=rr, p=p)


def tl_path(workdir, root, freq, profiles, rprof_km, rr_km, sd, rd, bottom, at_bin, fg=None, sphere=True, pts_per_lambda=15):
    wd = pathlib.Path(workdir); wd.mkdir(parents=True, exist_ok=True)
    write_env(wd / f"{root}.env", root, freq, profiles, sd, rd, bottom, fg, pts_per_lambda)
    write_flp(wd / f"{root}.flp", rprof_km, rr_km, sd, rd)
    env = dict(os.environ)
    t0 = time.time()
    k = subprocess.run([f"{at_bin}/Kraken/kraken.exe", root], cwd=wd, capture_output=True, text=True, env=env)
    t1 = time.time()
    f = subprocess.run([f"{at_bin}/KrakenField/field.exe", root], cwd=wd, capture_output=True, text=True, env=env)
    t2 = time.time()
    prt = (wd / f"{root}.prt").read_text(errors="replace") if (wd / f"{root}.prt").exists() else ""
    if k.returncode or f.returncode or "Fatal" in prt or not (wd / f"{root}.shd").exists():
        raise RuntimeError(f"{root}: kraken rc={k.returncode} field rc={f.returncode}\n{k.stdout[-500:]}\n{prt[-1500:]}")
    import re
    nm = [int(x) for x in re.findall(r"Number of modes\s*=\s*(\d+)", prt)]
    s = read_shd(wd / f"{root}.shd")
    p = np.abs(s["p"][0, 0])
    with np.errstate(divide="ignore"):
        tl = -20 * np.log10(p)
    if sphere:
        R = 6371.0
        x = np.asarray(rr_km) / R
        tl = tl + 10 * np.log10(np.where(x > 0, x / np.sin(np.where(x > 0, x, 1)), 1.0))
    return np.asarray(rr_km), tl, nm, (t1 - t0, t2 - t1)
