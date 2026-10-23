cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j" && python - <<'EOF'
import re
s=open("common.py").read()
s=s.replace("        self.log10eta = np.log10(R.ETA_GRID)\n",
"        # evaluation set: the 41-point prior grid (marginal) followed by the three fixed eta values (exact)\n        self.eta_eval = np.concatenate([R.ETA_GRID, np.array(list(R.ETA_FIXED.values()))])\n        self.n_grid = len(R.ETA_GRID)\n        self.log10eta = np.log10(self.eta_eval)\n")
s=s.replace("        n = len(t); K = len(R.ETA_GRID)\n","        n = len(t); K = len(self.eta_eval)\n")
s=s.replace('''    @staticmethod
    def marg(lnL):
        """ln sum_k omega_k exp(lnL_k) with equal omega (log-uniform prior on the grid)."""
        m = lnL.max(1, keepdims=True)
        return (m + np.log(np.mean(np.exp(lnL - m), axis=1, keepdims=True)))[:, 0]

    @staticmethod
    def at_eta(lnL, eta):
        k = int(np.argmin(np.abs(np.log10(R.ETA_GRID) - np.log10(eta))))
        assert abs(np.log10(R.ETA_GRID[k]) - np.log10(eta)) < 0.051, eta
        return lnL[:, k], k
''','''    def marg(self, lnL):
        """ln sum_k omega_k exp(lnL_k) over the 41 prior grid points with equal omega (log-uniform prior)."""
        g = lnL[:, :self.n_grid]; m = g.max(1, keepdims=True)
        return (m + np.log(np.mean(np.exp(g - m), axis=1, keepdims=True)))[:, 0]

    def fixed(self, lnL, name):
        """Column of the exact fixed eta value `name` (prereg ETA_FIXED key)."""
        return lnL[:, self.n_grid + list(R.ETA_FIXED).index(name)]
''')
open("common.py","w").write(s); print("ok")
EOF