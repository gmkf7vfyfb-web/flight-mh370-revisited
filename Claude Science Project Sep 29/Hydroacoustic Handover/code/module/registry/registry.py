"""Loader for the hydroacoustic data registry (REGISTRY.json). Hydro clean-up run, 23 Oct 2026.

Rule for all new module code: read data ONLY through this loader.
    from registry import Registry
    R = Registry()                         # finds REGISTRY.json next to this file
    p = R.path("ex.run_j_gated_v2")        # refuses unknown ids; warns on status
    f = R.file("ex.run_j_gated_v2", "README.txt", verify=True)   # sha256 checked against the manifest
    eta = R.const("eta_F35A_metz")         # value + status + source quote
Statuses WITHDRAWN and KNOWN_DEFECT raise unless allow_defect=True is passed, and the caller must then state the defect ids
beside every number it reports.
"""
from __future__ import annotations
import gzip, hashlib, json, os, warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLOCK = {"WITHDRAWN", "KNOWN_DEFECT"}
WARN = {"SUPERSEDED", "UNCHECKED", "PENDING_RULING", "CURRENT_WITH_CAVEATS"}


class RegistryError(Exception):
    pass


class Registry:
    def __init__(self, path=HERE / "REGISTRY.json", roots: dict | None = None):
        self.reg = json.load(open(path))
        self.roots = {**self.reg["roots"], **(roots or {})}
        for k in list(self.roots):
            env = os.environ.get(f"HYDRO_ROOT_{k}")
            if env:
                self.roots[k] = env
        self.e = {x["id"]: x for x in self.reg["entries"]}
        self.c = {x["id"]: x for x in self.reg["constants"]}
        self.d = {x["id"]: x for x in self.reg["defects"]}

    def entry(self, id_, allow_defect=False):
        if id_ not in self.e:
            raise RegistryError(f"{id_!r} is not in the registry. Add it to entries.yaml and rebuild; do not read unregistered data.")
        e = self.e[id_]
        if e["status"] in BLOCK and not allow_defect:
            raise RegistryError(f"{id_} has status {e['status']} (defects {e.get('defects')}). Pass allow_defect=True and report the defects.")
        if e["status"] in WARN:
            warnings.warn(f"{id_}: status {e['status']}; defects {e.get('defects')}; {e.get('note', '')}", stacklevel=2)
        return e

    def path(self, id_, allow_defect=False) -> Path:
        e = self.entry(id_, allow_defect)
        root, _, rel = e["path"].partition(":")
        if root not in self.roots:
            raise RegistryError(f"root {root} not configured (set HYDRO_ROOT_{root})")
        return Path(self.roots[root]) / rel

    def manifest(self, id_):
        e = self.e[id_]
        if not e.get("manifest"):
            return {}
        rows = gzip.open(HERE / e["manifest"], "rt").read().splitlines()[1:]
        return {r.split("\t")[0]: (int(r.split("\t")[1]), r.split("\t")[2]) for r in rows}

    def file(self, id_, rel, verify=False, allow_defect=False) -> Path:
        base = self.path(id_, allow_defect)
        p = base if base.is_file() else base / rel
        m = self.manifest(id_)
        key = base.name if base.is_file() else rel
        if m and key not in m:
            raise RegistryError(f"{rel} is not in the manifest of {id_} (file added after the registry build?)")
        if m:
            size, sha = m[key]
            if p.stat().st_size != size:
                raise RegistryError(f"{p}: size {p.stat().st_size} differs from manifest {size}")
            if verify:
                h = hashlib.sha256()
                with open(p, "rb") as f:
                    for b in iter(lambda: f.read(1 << 22), b""):
                        h.update(b)
                if h.hexdigest() != sha:
                    raise RegistryError(f"{p}: sha256 differs from manifest")
        return p

    def const(self, id_):
        if id_ not in self.c:
            raise RegistryError(f"constant {id_!r} is not in the registry")
        c = self.c[id_]
        if c["status"] not in ("CURRENT", "EXTERNAL_STANDARD"):
            warnings.warn(f"constant {id_}: status {c['status']}; {c.get('note', '')}", stacklevel=2)
        return c

    def defects_of(self, id_):
        return [self.d[x] for x in self.e[id_].get("defects", [])]
