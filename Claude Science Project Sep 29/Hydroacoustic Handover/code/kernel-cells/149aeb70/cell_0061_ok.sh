cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/149aeb70-e4ae-4829-a477-5c291fc000a5" && python3 - <<'PY'
p="make_hydro_figs.py"; s=open(p).read()
old_start = s.index('"Technical: run I, 00:19 held out, weighted draw of 20,000 impacts, tau90')
old_end = s.index('fig3.savefig')
new = ('"Technical: run I, 00:19 held out, weighted draw of 20,000 impacts, tau90 and energy from the end-of-flight sidecar "\n'
       '     "tau90_v1.npz (method 1, results/eof-impact-tau-method-oct11.md). Loud decile n=1,972; median tau90 in that decile "\n'
       '     "0.124 s against 4.03 s overall. F-35A figures (900 +/- 200 MJ impact kinetic energy, about 0.7 Pa at 3,300 km at "\n'
       '     "H11, coupling into the sound channel about 1e-4) are taken from this project\'s own literature record and are to be "\n'
       '     "re-verified against the source by the module. Kadri (2024), Scientific Reports, doi:10.1038/s41598-024-60529-1, "\n'
       '     "reviews aircraft-crash signatures; durations published there are RECEIVED durations after dispersion, not source "\n'
       '     "durations. Coupling efficiency is a declared alternative with a prior, not a constant.")\n')
s = s[:old_start] + new + s[old_end:]
open(p,"w").write(s); print(s[old_start-200:old_start+len(new)+40])
PY