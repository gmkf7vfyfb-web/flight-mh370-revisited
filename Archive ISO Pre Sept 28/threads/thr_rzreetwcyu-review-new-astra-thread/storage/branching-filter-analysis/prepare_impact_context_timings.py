"""Freeze point-specific acoustic timing labels; no flight or acoustic likelihood."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math

B = Path(__file__).resolve().parent
R = Path('/jackbox/home/MH370')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
context_path = B / 'impact-context-inputs.json'
config_path = B / 'impact-acoustic-million.json'
x = json.loads(context_path.read_text())
config = json.loads(config_path.read_text())
geometry_path = Path(config['provenance']['stations_source'])
assert sha(geometry_path) == config['provenance']['stations_source_sha256']
geometry = json.loads(geometry_path.read_text())
LOW, HIGH = config['celerity_km_s']['minimum'], config['celerity_km_s']['maximum']
RADIUS = geometry['earth_radius_km']
stations = {s['name']: s['position'] for s in config['stations']}
arrivals = {
    'A': [('H01W', '00:49:58', 'Table 1 entry; matching peak not recovered')],
    'B': [('H01W', '00:53:31', 'Table 1 entry; matching peak not recovered')],
    'C': [('H01W', '00:52:00', 'Reported cluster; local peak at 00:52:04.350')],
    'D': [('H01W', '00:54:30', 'Kadri preferred reported candidate')],
    'E': [('H01W', '00:52:04.350', 'Exploratory publication-trace feature'),
          ('H08S', '01:10:00.500', 'Exploratory periodic/panel-boundary feature')],
    'F': [('H01W', '00:54:26.950', 'Exploratory publication-trace feature'),
          ('H08S', '01:12:49.300', 'Exploratory periodic feature')],
}
# Arrival strings must be present in the frozen shortlist; no inferred second
# station is introduced for A/B/D. C has no point-specific propagation distance.
for t in x['targets']:
    for station, arrival, _ in arrivals[t['id']]:
        field = t['cl_arrival'] if station == 'H01W' else t['dg_arrival']
        assert arrival in field


def unix(utc):
    return dt.datetime.fromisoformat('2014-03-08T' + utc + '+00:00').timestamp()


def clock(seconds, fractional=False):
    value = dt.datetime.fromtimestamp(seconds if fractional else math.floor(seconds + .5), dt.timezone.utc)
    return value.strftime('%H:%M:%S.%f')[:-3] if fractional else value.strftime('%H:%M:%S')


def distance(point, station):
    lat, lon = map(math.radians, point)
    la, lo = map(math.radians, [station['latitude'], station['longitude']])
    hav = math.sin((lat - la) / 2)**2 + math.cos(lat) * math.cos(la) * math.sin((lon - lo) / 2)**2
    return 2 * RADIUS * math.asin(math.sqrt(min(1., max(0., hav))))


def impact_window(arrival, path_distance):
    return [arrival - path_distance / LOW, arrival - path_distance / HIGH]


result = dict(created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
    context_sha256=sha(context_path), config_sha256=sha(config_path), geometry_sha256=sha(geometry_path),
    script_sha256=sha(__file__), source_paths=[str(context_path),str(config_path),str(geometry_path)],
    earth_radius_km=RADIUS, celerity_km_s=[LOW,HIGH], stations=stations,
    method='Impact time = arrival time minus great-circle distance / effective celerity at the exact plotted point. For E/F, intersect the two station intervals, allowing each path its own celerity within the declared range. No station time correction is fitted.',
    interpretation='Scenario bounds at fixed coordinates, not a confidence interval, acoustic association or precision claim. Location, bearing and propagation-model errors are not integrated. Nominal 1.50 km/s estimates are diagnostics only.',
    superseded_timing='The old shortlist impact columns A–D used quantiles over a different broad source distribution. Old E/F seconds-wide values conditioned on central-celerity alignment choices. Neither is a point-specific uncertainty interval for these maps.',
    targets={})
for t in x['targets']:
    records=[]
    for name, arrival, kind in arrivals[t['id']]:
        entry=dict(station=name,arrival_utc=arrival,arrival_unix_s=unix(arrival),kind=kind,
                   map_arrival_utc=clock(unix(arrival)))
        if t['position'] is not None:
            d=distance(t['position'],stations[name]);bounds=impact_window(unix(arrival),d)
            entry.update(distance_km=d,impact_time_unix_s=bounds,
                nominal_impact_unix_s=unix(arrival)-d/1.5,
                nominal_impact_utc=clock(unix(arrival)-d/1.5))
            for time,c in zip(bounds,[LOW,HIGH]):
                assert abs(time+d/c-unix(arrival))<1e-6
        records.append(entry)
    bounds = None
    if t['position'] is not None:
        bounds=[max(r['impact_time_unix_s'][0] for r in records),min(r['impact_time_unix_s'][1] for r in records)]
        assert bounds[0] <= bounds[1]
    timing=dict(arrivals=records,implied_impact_unix_s=bounds,
        implied_impact_utc=[clock(v) for v in bounds] if bounds else None,
        display_impact='–'.join(clock(v) for v in bounds) if bounds else 'Unresolved: no mapped source position',
        counterpart_note='No identified H08S counterpart' if t['id'] in ['A','B','D'] else '',
        source_time_is_conditional=True)
    result['targets'][t['id']]=timing
out=B/'impact-context-timings.json'
assert not out.exists(), 'Inspect existing timing payload before replacing'
out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:v['display_impact'] for k,v in result['targets'].items()}))
