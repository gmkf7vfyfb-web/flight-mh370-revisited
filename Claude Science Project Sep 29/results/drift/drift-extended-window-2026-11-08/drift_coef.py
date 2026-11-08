"""Offline scorer for the debris-drift recovery coefficients (coefficients.jsonl + coefficients-meta.json).

Reproduces lib.rs node_ln_likelihood_zeros exactly:
  ln L = ln mean_{env e, level draw d} sum_c sum_{finds j of class c} [ ln(a_cj(e) . nu_d) - ln(A_c(e) . nu_d) ],
  nu_d = exp(mu + sigma z_d) per block (segment x period), z the module's own standard-normal draws.
Any level prior mu (e.g. an Australian detection ratio) and any subset of finds is a re-scoring; no transport.
"""
import json, numpy as np

class Meta:
    def __init__(self, path):
        m = json.load(open(path))
        self.m = m; self.seg = m['segments']; self.np = m['n_periods']; self.nb = len(self.seg) * self.np
        self.z = np.array(m['levels']['z']); self.sigma = m['levels']['sigma']
        self.mu_primary = np.array(m['levels']['mu_primary'])
        self.alts = {a['name']: np.array(a['mu']) for a in m['levels']['alternatives']}
        self.finds = m['finds']; self.ncls = len(m['classes'])
        self.by_class = [[j for j, f in enumerate(self.finds) if f['class'] == c] for c in range(self.ncls)]
        self.base = np.array(m['levels']['ln_mean_by_period'])
    def mu(self, overrides=None):
        """Block means: ln_mean_by_period for every segment, then {segment: [per-period ln means]} overrides."""
        mu = np.tile(self.base, len(self.seg))
        for s, v in (overrides or {}).items():
            i = self.seg.index(s); mu[i * self.np:(i + 1) * self.np] = v
        return mu

def ln_l(coefset, meta, mu, finds=None, return_zero_fraction=False):
    """coefset: node['sets'][k]['full' | 'half_a' | 'half_b']; finds: indices into meta.finds (None = all)."""
    nu = np.exp(mu[None, :] + meta.sigma * meta.z)            # draws x blocks
    keep = set(range(len(meta.finds))) if finds is None else set(finds)
    terms = []; zero_env = 0
    for env in coefset:
        s = np.zeros(nu.shape[0]); dead = False
        for c, k in enumerate(env):
            js = [(jj, j) for jj, j in enumerate(meta.by_class[c]) if j in keep]
            if k is None or not js:
                continue
            qtot = nu @ np.asarray(k['A'])
            for jj, j in js:
                sg = meta.finds[j]['segment']
                q = nu[:, sg * meta.np:(sg + 1) * meta.np] @ np.asarray(k['a'][jj])
                if not (np.all(q > 0) and np.all(qtot > 0)):
                    dead = True; break
                s += np.log(q) - np.log(qtot)
            if dead:
                break
        zero_env += dead
        terms.append(np.full(nu.shape[0], -np.inf) if dead else s)
    t = np.concatenate(terms); mx = t.max()
    v = np.nan if not np.isfinite(mx) else mx + np.log(np.mean(np.exp(t - mx)))
    return (v, zero_env / max(len(coefset), 1)) if return_zero_fraction else v

def read_nodes(path):
    return [json.loads(l) for l in open(path)]

# ---- shadow finds (alternative dates, later finds): written only to the coefficient file -------------
def find_table(meta):
    """id -> (source, class, segment, index): source 'p' = scored find, 's' = shadow find."""
    t = {f['id']: ('p', f['class'], f['segment'], jj) for c in range(meta.ncls) for jj, j in enumerate(meta.by_class[c]) for f in [meta.finds[j]]}
    sh = meta.m.get('shadow_finds', [])
    for c in range(meta.ncls):
        for jj, f in enumerate([f for f in sh if f['class'] == c]):
            t[f['id']] = ('s', f['class'], f['segment'], jj)
    return t

def ln_l_sel(setd, part, meta, mu, sel, return_zero_fraction=False):
    """setd: node['sets'][k]; part: 'full' | 'half_a' | 'half_b'; sel: list of find ids, scored ('<object_id>')
    or shadow ('shadow:<name>'), in any mix. Same estimator as ln_l; A (class total) from the scored set."""
    tab = find_table(meta); P = setd[part]; S = setd.get('shadow_' + part)
    nu = np.exp(mu[None, :] + meta.sigma * meta.z)
    terms = []; zero_env = 0
    for e, env in enumerate(P):
        s = np.zeros(nu.shape[0]); dead = False
        for fid in sel:
            src, c, sg, jj = tab[fid]
            k = env[c]; ks = k if src == 'p' else S[e][c]
            q = nu[:, sg * meta.np:(sg + 1) * meta.np] @ np.asarray(ks['a'][jj]); qtot = nu @ np.asarray(k['A'])
            if not (np.all(q > 0) and np.all(qtot > 0)):
                dead = True; break
            s += np.log(q) - np.log(qtot)
        zero_env += dead
        terms.append(np.full(nu.shape[0], -np.inf) if dead else s)
    t = np.concatenate(terms); mx = t.max()
    v = np.nan if not np.isfinite(mx) else mx + np.log(np.mean(np.exp(t - mx)))
    return (v, zero_env / max(len(P), 1)) if return_zero_fraction else v
