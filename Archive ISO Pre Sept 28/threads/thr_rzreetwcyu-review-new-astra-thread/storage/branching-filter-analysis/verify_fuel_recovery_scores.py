"""Independent scalar recovery-score checks, without reporting-module imports."""
from pathlib import Path
import csv, json, math, hashlib, itertools, argparse
B=Path(__file__).parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--methods',nargs='+',default=['larger-fuel','command-path-larger'],choices=['larger-fuel','command-path-larger','rate-partition','high-effort-fuel'])
args=parser.parse_args()
results=[]
for stem in args.methods:
    state=json.loads((B/f'synthetic-cruise-{stem}-status.json').read_text())
    summary_path=B/f'synthetic-cruise-{stem}-comparison/summary.json'
    summary=json.loads(summary_path.read_text())
    outputs={r['inference_seed']:Path(r['output']) for r in state['runs'] if r['status']=='completed'}
    design=json.loads(Path(state['design']).read_text())
    fixtures={f['truth_seed']:f for f in design['fixtures']}
    for entry in summary['data_sets']:
        if 'independent_maximum_coordinate_cdf_difference' not in entry:continue
        clouds=[]; z=[]; efforts=[]
        for rep,run in enumerate(fixtures[entry['truth_seed']]['runs']):
            out=outputs[run['inference_seed']]
            rows=list(csv.DictReader((out/'posterior.csv').open()))
            weight_sum=math.fsum(float(r['weight']) for r in rows)
            assert abs(weight_sum-1)<1e-8
            cloud=[(float(r['latitude_deg']),float(r['longitude_deg']),float(r['weight'])/weight_sum) for r in rows]
            expected=entry['replicates'][rep]
            ranks=[math.fsum(row[2] for row in cloud if row[k]<=entry['truth_coordinates_deg'][k]) for k in [0,1]]
            assert max(abs(a-b) for a,b in zip(ranks,expected['cdf_at_truth']))<2e-12
            effective=1/math.fsum(row[2]*row[2] for row in cloud)
            assert abs(effective-expected['weighted_row_effective_count'])<1e-9*max(1,effective)
            roots={}
            for row,point in zip(rows,cloud):roots.setdefault(row['root'],[]).append(point[2])
            largest=max(math.fsum(weights) for weights in roots.values())
            assert abs(largest-expected['largest_ancestor_mass'])<2e-12
            record=json.loads((out/'summary.json').read_text());z.append(record['log_evidence']);efforts.append(record['initial_particles']);clouds.append(cloud)
        gaps=[]
        for k in [0,1]:
            # At each distinct coordinate, sum signed probability jumps from the two populations.
            jumps=sorted([(row[k],row[2]) for row in clouds[0]]+[(row[k],-row[2]) for row in clouds[1]])
            running=0.;largest=0.
            for coordinate,group in itertools.groupby(jumps,key=lambda point:point[0]):
                running=math.fsum([running,math.fsum(v for _,v in group)])
                largest=max(largest,abs(running))
            gaps.append(largest)
        assert max(abs(a-b) for a,b in zip(gaps,entry['independent_maximum_coordinate_cdf_difference']))<2e-11
        alpha=[n*math.exp(v-max(z)) for n,v in zip(efforts,z)];total=math.fsum(alpha);alpha=[a/total for a in alpha]
        pooled=[math.fsum(a*row[2] for a,cloud in zip(alpha,clouds) for row in cloud if row[k]<=entry['truth_coordinates_deg'][k]) for k in [0,1]]
        assert max(abs(a-b) for a,b in zip(pooled,entry['pooled_cdf_at_truth']))<2e-12
        results.append({'method':stem,'truth_seed':entry['truth_seed'],'maximum_cdf_differences':gaps,'pooled_truth_cdf':pooled,'summary_sha256':hashlib.sha256(summary_path.read_bytes()).hexdigest()})
path=B/'fuel-recovery-independent-verification.json'
previous=json.loads(path.read_text())['checked_pairs'] if path.exists() else []
results=[r for r in previous if r['method'] not in args.methods]+results
path.write_text(json.dumps({'checked_pairs':results,'scope':'Direct raw-CSV scalar normalization, truth CDF, exact support-wise CDF difference, row effective count, ancestor sums and evidence/effort pooling; no claim of model or sampling calibration.'},indent=2)+'\n')
print('Verified',len(results),'completed pairs')
