cd /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/5e788282-a899-406d-be81-a794b69469f6
H="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - "$H/prepare/digitise_metz_2023.py" <<'E'
import sys
p=sys.argv[1]; s=open(p).read()
old='''            elif it[0] == "c":
                if not pts: pts.append((it[1].x, it[1].y))
                pts.append((it[4].x, it[4].y))
        out.append((c, np.array(pts)))'''
new='''            elif it[0] == "c":                         # cubic Bezier: sampled at 8 points (chords would cut corners)
                p0, p1, p2, p3 = it[1], it[2], it[3], it[4]
                if not pts: pts.append((p0.x, p0.y))
                for u in np.linspace(0.125, 1.0, 8):
                    w = ((1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3)
                    pts.append((w[0] * p0.x + w[1] * p1.x + w[2] * p2.x + w[3] * p3.x, w[0] * p0.y + w[1] * p1.y + w[2] * p2.y + w[3] * p3.y))
        out.append((c, np.array(pts)))'''
assert old in s; s=s.replace(old,new); open(p,'w').write(s)
E
python "$H/prepare/digitise_metz_2023.py" --pdf "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/8713f33b-92dd-4026-b29d-18c6ec42e04a/v1dc5cd5c_art3A10.10072Fs00024-022-03117-6.pdf" > digit.log 2>&1; python -c "
import json;m=json.load(open('$H/results-data/digitised/metz2023/METHOD.json'));c=m['checks']
print(c['fig3CD']); print(c['fig3_tick_residuals']); print(c['fig4']); print({k:(v['peak_db'],v['peak_utc'],v['pre_event_median_db']) for k,v in c['fig2EH'].items()})"