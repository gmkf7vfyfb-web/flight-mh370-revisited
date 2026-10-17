"""Make refinement configs from drift's production configs: deskstar forcing, node subset, independent seeds."""
import re, sys, json
H = '/home/pete/.claude-science-scratch/ocean'; nodes = json.load(open(sys.argv[1]))
src = {'glorys12': 'production-glorys12.toml', 'globcurrent': 'production-globcurrent-relwind.toml'}
cur = {'glorys12': f'{H}/glorys12/glorys12v1_uo_vo_surface_15-160E.series.json', 'globcurrent': f'{H}/globcurrent/grid/globcurrent_my_p1d_uo_vo_0m_15-160E.series.json'}
D = sys.argv[2]
for m, fn in src.items():
    s = open(f'{D}/{fn}').read()
    s = re.sub(r'(?m)^current_manifest = .*$', f'current_manifest = "{cur[m]}"', s)
    s = re.sub(r'(?m)^wind10_manifest = .*$', f'wind10_manifest = "{H}/era5/era5_u10_v10_3h_15-160E.series.json"', s)
    s = re.sub(r'(?m)^gshhg_path = .*$', f'gshhg_path = "{H}/gshhg/gshhs_f.b"', s)
    s = re.sub(r'(?m)^threads = .*$', 'threads = 88', s, count=1)
    s = re.sub(r'(?m)^seed = 1$', 'seed = 2', s, count=1)
    s = re.sub(r'(?m)^env_seeds = .*$', 'env_seeds = [5, 6, 7, 8]', s)
    s = re.sub(r'(?m)^node_(stride|offset) = .*\n', '', s)
    s = re.sub(r'(?m)^output_dir = .*$', f'output_dir = "/home/pete/mh370/drift/runs/refine-core94-{m}"\nnode_subset = {nodes}', s, count=1)
    assert '/Users/' not in s.split('[[hypotheses.debris-drift.classes]]')[0], m
    s = '# REFINEMENT (architecture stand-in, 17 Oct 2026): run A production config, 94 nodes carrying 95 % of run J core D0 mass,\n# independent seeds (seed 2, env seeds 5-8), deskstar 15-160 E forcing files (15-120 E domain unchanged).\n' + s
    open(f'refine-core94-{m}.toml', 'w').write(s); print(m, 'ok', s.count('node_subset'))
