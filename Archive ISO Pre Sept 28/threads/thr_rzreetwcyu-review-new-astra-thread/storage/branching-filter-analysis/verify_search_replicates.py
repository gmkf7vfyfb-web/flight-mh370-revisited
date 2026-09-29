"""Independently sum retained second-run weights inside first-run search cells."""
import csv
import hashlib
import json
import math
from pathlib import Path

B = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report_path = B / 'search-million-comparison/summary.json'
repeat_path = B / 'joint-terminal-replicate-seed-37092012-conditioned/summary.json'
report = json.loads(report_path.read_text())
repeat = json.loads(repeat_path.read_text())
index = {(c['terminal_family'], c['contact_case']): c for c in report['cases']
         if c['evidence_model'] == 'flight-fuel-final-contacts'}
flattening = 1 / 298.257223563
eccentricity = math.sqrt(flattening * (2 - flattening))
parallel = math.radians(35)
scale = math.cos(parallel) / math.sqrt(1 - (eccentricity * math.sin(parallel))**2)


def authalic(latitude):
    sine = math.sin(math.radians(latitude))
    u = eccentricity * sine
    return (1-eccentricity**2) * (sine/(1-u*u) - math.log((1-u)/(1+u))/(2*eccentricity))


results = []
for family in repeat['families']:
    for case in family['cases']:
        path = repeat_path.parent / case['weights_file']
        assert sha(path) == case['weights_sha256']
        points = []
        for row in csv.DictReader(path.open()):
            if not row['impact_latitude_deg'] or float(row['conditional_weight']) <= 0:
                continue
            x = 6378.137 * scale * math.radians(float(row['impact_longitude_deg']) - 90)
            y = 6378.137 * (authalic(float(row['impact_latitude_deg'])) - authalic(-35)) / (2*scale)
            points.append((x, y, float(row['conditional_weight'])))
        denominator = math.fsum(w for x, y, w in points)
        for plan in index[(family['name'], case['name'])]['plans']:
            chosen = {(x, y) for x, y, w in plan['tiles']}
            size = plan['cell_size_km']
            value = math.fsum(w for x, y, w in points if (math.floor(x/size), math.floor(y/size)) in chosen) / denominator
            expected = plan['captured_in_independent_numerical_run']
            assert abs(value - expected) < 2e-12, (family['name'], case['name'], size)
            results.append(dict(family=family['name'], contact_case=case['name'], cell_size_km=size,
                                independent_probability=value, reported_probability=expected,
                                second_run_weights_sha256=sha(path)))
output = dict(status='passed', comparisons=len(results), cases=results,
              report_sha256=sha(report_path), repeat_summary_sha256=sha(repeat_path),
              verification_script_sha256=sha(Path(__file__)),
              scope='Independent scalar equal-area expression, raw CSV membership and probability sum; no calibrated sonar model')
(B / 'search-replication-independent-verification.json').write_text(json.dumps(output, indent=2)+'\n')
print(json.dumps(dict(status='passed', comparisons=len(results))))
