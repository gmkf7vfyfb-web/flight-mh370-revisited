"""Finish this running batch, then plot, report and archive its completed outputs.

This is a foreground computation pipeline, not a recurring scheduled task.
"""
from pathlib import Path
import argparse,json,subprocess,sys,time,os
ROOT=Path(__file__).resolve().parent
EXPECTED=[f'mh370_era5_{n}_{seed}_{kind}' for n,seed in [(100000,101),(100000,202),(300000,303)] for kind in ['bto','bto_bfo']]

def report():
    out=ROOT/'assessment'
    data=json.loads((out/'posterior_summary.json').read_text())
    rows=[r for r in data['runs'] if r['epoch']=='00:19']
    lines=['# Reconstructed v12 / ERA5 results','',
           'These are actual weighted outputs of newly reconstructed code, not recovered historical v12 outputs. **A stable reproduction of Davey Fig. 10.3 has not been established.** The scientific target should not be marked complete merely because the batch finished.','',
           '| Run | Smoothed mode latitude | Southern probability | Largest initial ancestor weight | Effective initial ancestors |',
           '|---|---:|---:|---:|---:|']
    for r in rows:
        lines.append(f"| {r['run']} | {r['mode_latitude_smoothed']:.3f}° | {r['south_probability']:.4f} | {r['largest_root_weight']:.4f} | {r['effective_roots']:.2f} |")
    lines+=['','Latitude is signed (negative = south). The mode uses a fixed 0.35° Gaussian display bandwidth. The probabilities and ancestor weights use the raw weighted particles. Initial ancestors are a useful depletion diagnostic, not a complete definition of independent trajectories: descendants continue to draw different later manoeuvres.','',
            '## Between-run differences at 00:19','',
            '| Treatment | Runs | Wasserstein distance (degrees) | Smoothed total variation |',
            '|---|---|---:|---:|']
    for c in data['between_run_comparisons']:
        if c['epoch']=='00:19':
            a=c['a'].split('_');b=c['b'].split('_')
            lines.append(f"| {c['kind']} | N={a[2]}, seed {a[3]} / N={b[2]}, seed {b[3]} | {c['wasserstein_deg']:.3f} | {c['smoothed_total_variation']:.3f} |")
    lines+=['',
      'At 100,000 particles the two BTO-only runs place approximately 22% and 98% of their mass in the south. The two BTO+BFO runs both select the south but differ in shape (about 0.48 smoothed total variation); their largest initial ancestors carry approximately 78% and 86% of the weight. Similar mean latitudes therefore do not establish agreement. The larger-run results above must be assessed against both replicates, not selected because they resemble the published figure.', '',
      'No stable northern shoulder is established by the present checks. Any small shoulder in an individual curve may reflect retained early trajectories. The refined comparator contains northern Gaussian components by construction and cannot independently confirm the feature.', '',
      'The executable reconstruction, tests and dense MH371 checks are substantial progress, but the fixed-population accident sampler remains a numerical limitation. Broader, correctly weighted trajectory proposals or source-style branching, followed by new convergence tests, are needed if larger counts continue to show depletion. Arbitrary state jitter or pooling the curves would conceal rather than resolve the issue.', '',
      '## Files','',
      '* `mh370_fig10_3_analogue.png`: BTO-only and BTO+BFO at 00:19, full latitude range plus southern detail; separate runs.',
      '* `mh370_refined_comparison_0011.png`: same-epoch comparison with the recovered no-drift summary-based refined output.',
      '* `latitude_pdfs.csv` and `posterior_summary.json`: plotted densities and numerical diagnostics.',
      '* `../README.md`: assumptions, departures from Davey, inputs and rerun instructions.',
      '* `../BFO_AND_CHECKPOINT_NOTES.md`: exact recovered BFO choices and the missing checkpoint limitation.',
      '* `../../mh370_v12_reconstruction_era5.zip`: portable source/input/evidence/finished-checkpoint bundle, with SHA256 inventory.', '',
      'The original full source was not recovered. ERA5, public TLE geometry and the reconstructed radar mean are disclosed substitutions; this is not an exact original-source or operator-data reproduction.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('--wait',action='store_true');args=p.parse_args()
    last=None;deadline=time.monotonic()+14400
    while True:
        states={}
        for name in EXPECTED:
            path=ROOT/'runs'/name/'manifest.json'
            try:
                m=json.loads(path.read_text());states[name]=m['status']
            except (FileNotFoundError,json.JSONDecodeError):states[name]='pending'
        if states!=last:print(json.dumps(states),flush=True);last=states
        if all(v=='completed' for v in states.values()):break
        if not args.wait:raise RuntimeError('Batch incomplete; use --wait to finish the active computation')
        if time.monotonic()>deadline:raise TimeoutError('Batch has not completed within four hours; inspect run sessions')
        time.sleep(10)
    env=os.environ.copy();env.setdefault('MPLCONFIGDIR',str(ROOT/'assessment/mpl-cache'))
    with (ROOT/'assessment/plot_log.json').open('w') as f:
        subprocess.run([sys.executable,str(ROOT/'plot_posteriors.py')],check=True,stdout=f,env=env)
    report()
    subprocess.run([sys.executable,str(ROOT/'make_archive.py')],check=True,env=env)
    (ROOT/'assessment/BATCH_COMPLETED.json').write_text(json.dumps({'completed_unix_time':time.time(),'runs':EXPECTED,'scientific_convergence_established':False},indent=2))
    print('Batch finished. Plots, report and portable archive saved; convergence is not claimed.',flush=True)

if __name__=='__main__':main()
