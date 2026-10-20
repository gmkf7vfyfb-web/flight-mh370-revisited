"""Summarize runner-generated acoustic predictions under saved contact weights."""
from __future__ import annotations
import argparse, base64, csv, datetime as dt, gzip, html, json, shlex, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from arc_density_report import digest, scalar_quantiles, save_figure, draw_land
from cruise_impact_report import LABELS, DEFAULT_CASE

MIDNIGHT = 1394236800.0  # 2014-03-08 00:00:00 UTC


def cdf(values, weights, edges):
    order = np.argsort(values)
    indices = np.searchsorted(values[order], edges, side='right')
    cumulative = np.cumsum(weights[order])
    return np.where(indices > 0, cumulative[np.maximum(indices - 1, 0)], 0).tolist()


def load_predictions(source):
    summary = json.loads((source / 'summary.json').read_text())
    if summary['status'] != 'conditional_acoustic_predictions_only':
        raise ValueError('Incomplete acoustic source')
    if digest(source / 'predictions.jsonl') != summary['predictions_sha256']:
        raise ValueError('Acoustic predictions changed')
    families = {}
    for line in (source / 'predictions.jsonl').open():
        p = json.loads(line)
        if p['likelihood_evaluated'] or p['log_weight_increment'] != 0:
            raise ValueError('Predictions unexpectedly contain an acoustic likelihood')
        key = (p['source_index'], p['draw'])
        group = families.setdefault(p['family'], {})
        if key in group:
            raise ValueError('Duplicate continuation identity')
        group[key] = p
    return summary, families


def load_case(source, family, case, predictions):
    path = source / case['weights_file']
    if digest(path) != case['weights_sha256']:
        raise ValueError('Contact weights changed')
    rows = [r for r in csv.DictReader(path.open())
            if r['impact_latitude_deg'] and float(r['conditional_weight']) > 0]
    points = [predictions[(int(r['source_index']), int(r['draw']))] for r in rows]
    w = np.array([float(r['conditional_weight']) for r in rows])
    represented = float(w.sum())
    result = dict(terminal_family=family, contact_case=case['name'],
                  contact_label=LABELS[case['name']], impact_mass_within_scored_support=represented,
                  incoming_uncomputed_likelihood_mass=case['fraction_of_fuel_conditioned_prior_with_uncomputed_likelihood'],
                  input_weights_sha256=digest(path), stations=[], examples=[])
    if not points:
        return result
    w /= represented
    result['effective_weighted_impact_rows'] = float(1 / (w @ w))
    mask = np.array([p['event_geometrically_compatible'] for p in points], dtype=bool)
    result['event_geometry_compatible_impact_mass'] = float(w[mask].sum())
    result['event_geometry_compatible_rows'] = int(mask.sum())
    subset_weights = w[mask] / w[mask].sum() if mask.any() else np.array([])
    result['event_geometry_effective_rows'] = float(1 / (subset_weights @ subset_weights)) if mask.any() else 0.
    for p, weight in zip(points, w):
        if p['event_geometrically_compatible']:
            result['examples'].append({k: p[k] for k in ['source_index', 'draw', 'parent_slot', 'root_id',
                'latitude_deg', 'longitude_deg', 'impact_time_unix_s', 'impact_velocity_angle_deg',
                'ground_frame_kinetic_energy_j', 'vertical_kinetic_energy_j']} |
                dict(weight_within_computed_impacts=float(weight),
                     weight_within_geometry_subset=float(weight / w[mask].sum())))
    result['examples'].sort(key=lambda p: -p['weight_within_geometry_subset'])
    time_edges = np.arange(0, 181., .5)
    bearing_edges = np.arange(0, 360.1, 1.)
    for j, station in enumerate(points[0]['stations']):
        values = [p['stations'][j] for p in points]
        if any(v['station'] != station['station'] for v in values):
            raise ValueError('Station ordering changed')
        lower = np.array([(v['prediction']['arrival_time_s']['minimum'] - MIDNIGHT) / 60 for v in values])
        upper = np.array([(v['prediction']['arrival_time_s']['maximum'] - MIDNIGHT) / 60 for v in values])
        bearing = np.array([v['source_bearing_true_deg'] for v in values])
        result['stations'].append(dict(name=station['station'], time_edges_minutes_utc=time_edges.tolist(),
            earliest_arrival_cdf=cdf(lower, w, time_edges), latest_arrival_cdf=cdf(upper, w, time_edges),
            earliest_arrival_quantiles=scalar_quantiles(lower, w), latest_arrival_quantiles=scalar_quantiles(upper, w),
            bearing_edges_deg=bearing_edges.tolist(), bearing_cdf=cdf(bearing, w, bearing_edges)))
    energy_edges = np.arange(-2, 12.001, .05)
    energy = np.array([p['ground_frame_kinetic_energy_j'] for p in points])
    vertical = np.array([p['vertical_kinetic_energy_j'] for p in points])
    result.update(energy_log10_edges=energy_edges.tolist(),
                  total_energy_cdf=cdf(np.log10(energy), w, energy_edges),
                  vertical_energy_cdf=cdf(np.log10(np.maximum(vertical, 1e-300)), w, energy_edges),
                  total_energy_quantiles_j=scalar_quantiles(energy, w),
                  vertical_energy_quantiles_j=scalar_quantiles(vertical, w))
    return result


def figure(family, cases, output):
    selected = next(c for c in cases if c['contact_case'] == DEFAULT_CASE)
    if not selected['stations']:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.9))
    for station, color in zip(selected['stations'], ['#207aab', '#ba6121']):
        x = station['time_edges_minutes_utc']
        axes[0].fill_between(x, station['latest_arrival_cdf'], station['earliest_arrival_cdf'], color=color, alpha=.22)
        axes[0].plot(x, station['earliest_arrival_cdf'], color=color, label=station['name'])
        axes[0].plot(x, station['latest_arrival_cdf'], color=color, ls='--')
    axes[0].axvline(54.5, color='#333', lw=1, ls=':', label='Kadri H01W feature')
    axes[0].set(xlim=(15, 100), ylim=(0, 1), xlabel='Arrival: minutes after 00:00 UTC', ylabel='Cumulative probability', title='Travel-time sensitivity: 1.43–1.57 km/s')
    axes[0].legend(fontsize=8)
    for values, label in [(selected['total_energy_cdf'], 'Total ground-frame energy'),
                          (selected['vertical_energy_cdf'], 'Vertical energy')]:
        axes[1].plot(selected['energy_log10_edges'], values, label=label)
    axes[1].set(xlim=(3, 11), ylim=(0, 1), xlabel='log₁₀ incident kinetic energy (joules)', ylabel='Cumulative probability', title='Impact energy; acoustic fraction uncalibrated')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle(family.replace('-', ' ') + '\nR600 BTO + BFO, no startup offset', fontsize=11)
    fig.tight_layout(rect=(0, .12, 1, .93))
    fig.text(.5, .02, 'Conditional on computed impacts. Shading spans fixed celerity alternatives, not a confidence interval.\n'
             'A matching arrival time alone does not identify an event. Body attitude, source pressure and receiver likelihood remain uncomputed.\n'
             f"Kadri timing AND bearing subset: {100*selected['event_geometry_compatible_impact_mass']:.3g}% of computed-impact weight; "
             f"{selected['event_geometry_compatible_rows']} positive-weight rows.", ha='center', fontsize=7.5)
    save_figure(fig, output, family)



def serialization_equivalent(a, b):
    # The archived Rust JSON reader differs from Python by one final float bit
    # in some fields. Reject larger changes and every non-numeric mismatch.
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(serialization_equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(serialization_equivalent(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and isinstance(b, float):
        return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= max(math.ulp(a), math.ulp(b))
    return a == b


def trace_figures(source, history_status, output):
    """Render verified cruise, powered and terminal states; no new likelihood."""
    summary = json.loads((source / 'summary.json').read_text())
    if summary['status'] != 'selected_terminal_traces':
        raise ValueError('Trace source is not a selected-history illustration')
    if digest(source / 'continuations.jsonl') != summary['continuations_sha256']:
        raise ValueError('Terminal trace data changed')
    verification = json.loads((source / 'replay-verification.json').read_text())
    if verification['differences'] or verification['records'] != verification['exact_saved_transition_matches']:
        raise ValueError('Saved terminal paths did not replay exactly')
    state = json.loads(history_status.read_text())
    if state['status'] != 'completed':
        raise ValueError('Cruise history recovery incomplete')
    config = json.loads((source / 'resolved-config.json').read_text())
    histories = {}
    history_inputs = []
    for run in state['runs']:
        path = Path(run['output']) / 'trajectory-examples.json'
        if digest(path) != run['trajectory_sha256']:
            raise ValueError('Cruise history data changed')
        if config['source_runs'][run['source_index']] != run['source']:
            raise ValueError('Cruise and terminal history identities differ')
        values = json.loads(path.read_text())
        if not values['full_contact_state_and_likelihood_match']:
            raise ValueError('Cruise contact replay mismatch')
        for example in values['examples']:
            if example['terminal_slot'] in run['requested_slots']:
                histories[(run['source_index'], example['terminal_slot'])] = example
        history_inputs.append(dict(path=str(path), sha256=digest(path)))
    rows = [json.loads(line) for line in (source / 'continuations.jsonl').open()]
    families = {}
    for row in rows:
        history = histories[(row['source_index'], row['parent_slot'])]
        if not serialization_equivalent(history['terminal']['flight'], row['source_state_0011']):
            raise ValueError('Cruise/terminal handoff state differs')
        if row['terminal_trace'][-1] != row['transition']['terminal']:
            raise ValueError('Trace does not end at its retained impact')
        families.setdefault(row['family'], []).append((row, history))
    figures = []
    origin = config['source_runs'][0]
    origin = json.loads((Path(origin) / 'resolved-config.json').read_text())['inputs']['time_origin_unix_s']
    for family, examples in families.items():
        fig, axs = plt.subplots(2, 2, figsize=(10.5, 9.0))
        route, final, altitude, vertical = axs.flat
        all_terminal = []
        colours = plt.cm.viridis(np.linspace(.1, .9, len(examples)))
        for colour, (row, history) in zip(colours, examples):
            cruise = history['points']
            route.plot([p['longitude_deg'] for p in cruise], [p['latitude_deg'] for p in cruise], color=colour, lw=.9, alpha=.8)
            boundary = row['boundary']['aircraft']
            first = row['source_state_0011']['aircraft']
            powered = [dict(time_s=first['time'], latitude_deg=first['position']['latitude'], longitude_deg=first['position']['longitude'], altitude_ft=first['altitude'])] + row['powered_trace']
            powered.append(dict(time_s=boundary['time'], latitude_deg=boundary['position']['latitude'], longitude_deg=boundary['position']['longitude'], altitude_ft=boundary['altitude']))
            terminal = [p['kinematics']['point_mass'] for p in row['terminal_trace']]
            tx = [p['position']['longitude'] for p in terminal]
            ty = [p['position']['latitude'] for p in terminal]
            all_terminal.extend(zip(tx, ty))
            final.plot([p['longitude_deg'] for p in powered], [p['latitude_deg'] for p in powered], color=colour, ls='--', lw=1)
            final.plot(tx, ty, color=colour, lw=1)
            final.scatter([tx[-1]], [ty[-1]], c=[colour], marker='x', s=22)
            route.scatter([first['position']['longitude']], [first['position']['latitude']], c=[colour], s=13)
            final.scatter([first['position']['longitude']], [first['position']['latitude']], c=[colour], s=13)
            altitude.plot([(origin+p['time_s']-MIDNIGHT)/60 for p in powered], [p['altitude_ft']/1000 for p in powered], color=colour, ls='--', lw=1)
            altitude.plot([(origin+p['time']-MIDNIGHT)/60 for p in terminal], [p['altitude']/1000 for p in terminal], color=colour, lw=1)
            vertical.plot([(origin+p['kinematics']['point_mass']['time']-MIDNIGHT)/60 for p in row['terminal_trace']], [p['kinematics']['vertical_speed'] for p in row['terminal_trace']], color=colour, lw=1)
        route.set(xlim=(80,116), ylim=(-40,10), xlabel='Longitude (°E)', ylabel='Latitude (°)', title='Exact cruise histories to 00:11')
        draw_land(route)
        final.set(xlabel='Longitude (°E)', ylabel='Latitude (°)', title='00:11 to impact: recorded solver states')
        altitude.set(xlim=(10,45), xlabel='Minutes after 00:00 UTC', ylabel='Pressure-altitude approximation (kft)', title='Altitude: powered dash / unpowered solid')
        vertical.set(xlim=(10,45), xlabel='Minutes after 00:00 UTC', ylabel='Vertical velocity (m/s; upward positive)', title='Velocity direction, not body attitude')
        for ax in (altitude, vertical):
            ax.axvline(19+29.416/60, color='#933', lw=.7, ls=':')
            ax.axvline(19+37.443/60, color='#933', lw=.7, ls=':')
        for ax in axs.flat: ax.grid(alpha=.15)
        fig.suptitle(family.replace('-', ' ') + f' — {len(examples)} retained event-geometry examples', fontsize=11)
        fig.tight_layout(rect=(0,.10,1,.95))
        fig.text(.5,.015,'All shown paths meet the declared Kadri timing/bearing screen; they are selected witnesses, not a new event-conditioned PDF.\n'
                 'Found in the earlier 680,000-candidate cruise parent; the current terminal reconstruction matches every stored contact and impact exactly.\n'
                 'Markers: dot 00:11, cross impact. Vertical lines mark the two final SATCOM epochs; compatibility depends on the selected BFO model.\n'
                 'The colour separates examples and carries no probability. Body attitude and acoustic coupling remain uncomputed.',ha='center',fontsize=7.2)
        stem='kadri-routes-'+family
        save_figure(fig,output,stem)
        figures.append(dict(family=family,examples=len(examples),svg=stem+'.svg',pdf=stem+'.pdf'))
    return dict(source=str(source),summary_sha256=digest(source/'summary.json'),
                replay_verification_sha256=digest(source/'replay-verification.json'),
                history_inputs=history_inputs,examples=len(rows),figures=figures,
                handoff_serialization_allowance='At most one final float bit; audited full handoff states; every recorded terminal contact and impact replays exactly.')


def browser(result, output, inline):
    packed = base64.b64encode(gzip.compress(json.dumps(result['cases'], separators=(',', ':'), allow_nan=False).encode(), mtime=0)).decode()
    body = '''<h1>Impact acoustics: predictions and conditional event geometry</h1>
<p>These predictions use the saved flight, fuel and final-contact weights. No acoustic detection or event-identity likelihood has been added. Select a terminal model and final-contact case to see how arrival times and impact energy change.</p>
<label>Terminal model<select id="family"></select></label><label>Final contacts<select id="contact"></select></label><label>Hydrophone station<select id="station"><option>H01W</option><option>H08S</option></select></label>
<p id="status">Loading saved predictions…</p><div id="stats"></div>
<canvas id="arrival" width="1000" height="480"></canvas><p>Solid: faster 1.57 km/s effective celerity. Dashed: slower 1.43 km/s. These are sensitivity limits, not a statistical confidence band. The vertical marker is Kadri’s H01W feature at 00:54:30; bearing must also agree.</p>
<canvas id="bearing" width="1000" height="480"></canvas>
<label>Illustrative acoustic energy fraction<select id="efficiency"><option value="1">1 — energy-conservation ceiling</option><option value=".01">0.01</option><option value=".0001">0.0001</option><option value=".000001">0.000001</option><option value=".00000001">0.00000001</option><option value="0">0 — no coupled energy</option></select></label>
<canvas id="energy" width="1000" height="480"></canvas><p>Blue: fraction of total kinetic energy relative to stationary water. Orange: the same fraction of vertical kinetic energy as a separate reference. Fractions are unweighted illustrations. None is a calibrated coupling estimate or a prediction of received pressure.</p>
<details open><summary>Kadri preferred-event conditional samples</summary><p>The screen requires a predicted source bearing within ±0.5° of 306.18° at H01W and an arrival envelope containing 00:54:30. It imposes no probability density inside that envelope. The table shows actual sampled impacts satisfying both; their weights describe this finite conditional subset.</p><div class="scroll" id="examples"></div></details>
<details><summary>Assumptions, limitations and sources</summary>
<p>Kadri (2024), <a href="https://www.nature.com/articles/s41598-024-60529-1">PDF pages 13–14 and Table 1</a>, supplies the preferred feature, bearing tolerance and celerity sensitivity. Its approximate seventh-arc range of 1,586 km implies impact around 00:36–00:38 if this feature is identified with the aircraft. That is a conditional inference, not a measured impact time or location.</p>
<p>The station coordinates are H01W 34.892°S, 114.141°E and H08S 7.639°S, 72.484°E. Great-circle effective-celerity timing omits path-dependent sound speed, bathymetry, scattering, multipath and receiver response. A compatible timing/bearing construction does not establish that MH370 generated the recorded feature.</p>
<p>The point-mass model supplies velocity direction and commanded bank, not body pitch, water-entry attitude or breakup. Source coupling, pulse duration and attenuation need separate calibration before signal amplitude or non-detection can update the location estimate. Full raw hydrophone waveforms are not available in this source collection.</p>
<p>Each aerodynamic/control family is a separate conditional model. Uncomputed terminal outcomes are excluded from the predictive subset and reported above. Effective row counts measure weight concentration and do not count independent flight histories. Most cases using both final BFOs remain poorly sampled.</p></details>'''
    traces=result.get('trajectory_traces')
    if result.get('initial_cruise_candidates'):
        body = body.replace('</h1>', '</h1><p>The weighted comparisons below use the '+f"{result['initial_cruise_candidates']:,}"+'-candidate cruise pool and its recorded terminal ensemble. Earlier selected trajectory illustrations are labelled separately.</p>', 1)
    if traces:
        body += '<details><summary>Exact cruise and terminal paths for retained Kadri examples</summary><p>These are the 22 retained geometric witnesses from the earlier 680,000-candidate parent. They do not constitute a separately sampled event prior or an event-conditioned probability map. The figures retain their original source identities; the selector above refers to the current ensemble and does not reweight these illustrations.</p>'
        for figure in traces['figures']:
            encoded=base64.b64encode((output/figure['svg']).read_bytes()).decode()
            body += '<h2>'+html.escape(figure['family'].replace('-',' '))+'</h2><img style="width:100%;height:auto" alt="Cruise route, terminal route, altitude and vertical velocity for retained Kadri-compatible examples" src="data:image/svg+xml;base64,'+encoded+'">'
        body += '</details>'
    css = 'body{margin:0;background:#f5f7f8;color:#193240;font:17px/1.5 system-ui}main{max-width:1050px;margin:auto;padding:18px}h1{font-size:1.65em}label{display:block;margin:14px 0}select{display:block;width:100%;font:inherit;padding:9px;background:white;color:inherit}canvas{width:100%;height:auto;background:white;margin-top:22px}details{padding:14px;background:white;margin:20px 0}.scroll{overflow:auto}table{border-collapse:collapse;font-size:13px}td,th{padding:8px;border-bottom:1px solid #ccd8df;white-space:nowrap}#status{font-weight:600}'
    script = r'''
const packed="PACKED";let data;
const family=document.getElementById('family'),contact=document.getElementById('contact'),station=document.getElementById('station'),efficiency=document.getElementById('efficiency');
const esc=x=>String(x).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const fmt=(x,n=2)=>Number.isFinite(x)?x.toFixed(n):'—';
function current(){return data.find(x=>x.terminal_family===family.value&&x.contact_case===contact.value)}
function plot(id,limits,title,xlabel,curves,marker){
 const canvas=document.getElementById(id),c=canvas.getContext('2d');const [xmin,xmax]=limits,L=90,R=35,T=55,B=85,W=canvas.width-L-R,H=canvas.height-T-B;
 const x=v=>L+(v-xmin)/(xmax-xmin)*W,y=v=>T+H-v*H;
 c.clearRect(0,0,canvas.width,canvas.height);c.fillStyle='white';c.fillRect(0,0,canvas.width,canvas.height);c.font='21px system-ui';c.fillStyle='#193240';c.textAlign='center';c.fillText(title,canvas.width/2,28);
 c.font='17px system-ui';for(let i=0;i<=5;i++){const v=xmin+(xmax-xmin)*i/5;c.fillText(fmt(v,1),x(v),T+H+30);c.fillText(fmt(i/5,1),L-35,y(i/5)+6);c.strokeStyle='#dae3e7';c.beginPath();c.moveTo(L,y(i/5));c.lineTo(L+W,y(i/5));c.stroke();}c.fillText(xlabel,canvas.width/2,canvas.height-12);
 c.save();c.beginPath();c.rect(L,T,W,H);c.clip();curves.forEach(v=>{c.strokeStyle=v.color;c.lineWidth=2.8;c.setLineDash(v.dashed?[9,6]:[]);c.beginPath();v.x.forEach((xx,i)=>i?c.lineTo(x(xx),y(v.y[i])):c.moveTo(x(xx),y(v.y[i])));c.stroke();});
 if(marker!==null){c.strokeStyle='#8e2551';c.setLineDash([4,5]);c.beginPath();c.moveTo(x(marker),T);c.lineTo(x(marker),T+H);c.stroke();}c.restore();c.setLineDash([]);
}
function render(){const v=current();if(!v||!v.stations.length){document.getElementById('status').textContent='No scored computed impacts for this case.';return;}const s=v.stations.find(x=>x.name===station.value),eta=Number(efficiency.value);
 document.getElementById('status').textContent=v.terminal_family.replaceAll('-',' ')+' · '+v.contact_label;
 document.getElementById('stats').innerHTML=`Incoming mass with uncomputed selected-contact likelihood: ${fmt(100*v.incoming_uncomputed_likelihood_mass)}%. Computed impacts within scored support: ${fmt(100*v.impact_mass_within_scored_support)}%. Effective weighted impact rows: ${fmt(v.effective_weighted_impact_rows,1)}.<br>Kadri timing AND bearing subset: ${(100*v.event_geometry_compatible_impact_mass).toPrecision(3)}% of computed-impact weight; ${v.event_geometry_compatible_rows} rows, effective weight count ${fmt(v.event_geometry_effective_rows,1)}.`;
 plot('arrival',[15,110],s.name+' arrival-time cumulative probability','Minutes after 00:00 UTC',[{x:s.time_edges_minutes_utc,y:s.earliest_arrival_cdf,color:'#207aab'},{x:s.time_edges_minutes_utc,y:s.latest_arrival_cdf,color:'#207aab',dashed:true}],s.name==='H01W'?54.5:null);
 plot('bearing',[0,360],s.name+' source-bearing cumulative probability','True bearing from station (degrees)',[{x:s.bearing_edges_deg,y:s.bearing_cdf,color:'#207aab'}],s.name==='H01W'?306.18:null);
 const shift=eta>0?Math.log10(eta):0;plot('energy',[-3,11],eta>0?'Energy cumulative probability at fraction '+eta:'Zero fraction: all coupled energy is zero','log₁₀ scenario energy (joules)',eta>0?[{x:v.energy_log10_edges.map(x=>x+shift),y:v.total_energy_cdf,color:'#207aab'},{x:v.energy_log10_edges.map(x=>x+shift),y:v.vertical_energy_cdf,color:'#ba6121'}]:[],null);
 document.getElementById('examples').innerHTML=v.examples.length?'<table><tr><th>Source / draw / parent</th><th>Latitude</th><th>Longitude</th><th>Impact UTC</th><th>Velocity angle</th><th>Incident energy</th><th>Subset weight</th></tr>'+v.examples.map(p=>`<tr><td>${p.source_index} / ${p.draw} / ${p.parent_slot}</td><td>${fmt(p.latitude_deg)}</td><td>${fmt(p.longitude_deg)}</td><td>${new Date(p.impact_time_unix_s*1000).toISOString().slice(11,19)}</td><td>${fmt(p.impact_velocity_angle_deg,1)}°</td><td>${fmt(p.ground_frame_kinetic_energy_j/1e9,2)} GJ</td><td>${fmt(100*p.weight_within_geometry_subset,1)}%</td></tr>`).join('')+'</table>':'No positive-weight sample satisfies both geometry conditions in this case. This finite-sample result is not a proof of physical impossibility.';
}
function chooseContact(){const previous=contact.value;contact.innerHTML=data.filter(v=>v.terminal_family===family.value).map(v=>`<option value="${v.contact_case}">${esc(v.contact_label)}</option>`).join('');contact.value=data.some(v=>v.terminal_family===family.value&&v.contact_case===previous)?previous:'r600-no-startup-offset';render();}
async function start(){const bytes=Uint8Array.from(atob(packed),c=>c.charCodeAt(0));data=JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());family.innerHTML=[...new Set(data.map(v=>v.terminal_family))].map(v=>`<option>${esc(v)}</option>`).join('');family.value='openap26-initial-trim';station.value='H01W';efficiency.value='1';chooseContact();family.addEventListener('change',chooseContact);[contact,station,efficiency].forEach(e=>e.addEventListener('change',render));}
start().catch(e=>{document.getElementById('status').textContent='Saved prediction data could not load: '+e.message;});
'''.replace('PACKED', packed)
    document = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MH370 acoustic predictions</title><style>' + css + '</style><main>' + body + '</main><script>' + script + '</script></html>'
    if len(document.encode()) > 5 * 1024 ** 2:
        raise ValueError('Inline acoustic report exceeds 5 MiB')
    for path in [output / 'index.html', inline]:
        path.write_text(document)


def report(source, output, inline, trajectory_traces=None, history_status=None):
    output.mkdir(parents=True, exist_ok=True)
    summary, predictions = load_predictions(source)
    conditioned = Path(summary['source_conditioned'])
    if digest(conditioned / 'summary.json') != summary['source_condition_summary_sha256']:
        raise ValueError('Conditioned source changed')
    contact_summary = json.loads((conditioned / 'summary.json').read_text())
    cases = []
    plt.rcParams.update({'svg.fonttype': 'none', 'font.size': 10})
    for family in contact_summary['families']:
        values = [load_case(conditioned, family['name'], case, predictions[family['name']]) for case in family['cases']]
        figure(family['name'], values, output)
        cases.extend(values)
    result = dict(generated_utc=dt.datetime.now(dt.timezone.utc).isoformat(), cases=cases,
                  source_summary_sha256=digest(source / 'summary.json'), source=str(source),
                  report_source_sha256=digest(__file__), limitations=summary['limitations'])
    result['initial_cruise_candidates'] = sum(s['initial_candidates'] for s in contact_summary['source_summary']['sources'])
    if (trajectory_traces is None) != (history_status is None):
        raise ValueError('Both terminal traces and history status are required')
    if trajectory_traces is not None:
        result['trajectory_traces']=trace_figures(trajectory_traces,history_status,output)
    (output / 'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    browser(result, output, inline)
    command = shlex.join(['python', str(Path(__file__).resolve()), '--source', str(source), '--output', str(output), '--inline-output', str(inline)])
    if trajectory_traces is not None:
        command += ' '+shlex.join(['--trajectory-traces',str(trajectory_traces),'--history-status',str(history_status)])
    (output / 'README.md').write_text('# Conditional acoustic predictions\n\n```bash\n' + command + '\n```\n\nAll contact cases remain separate. Prediction JSONL and contact-weight CSV hashes are checked before composition. No hydroacoustic likelihood, body attitude or measured coupling law is introduced. Per-family PDFs/SVGs show the requested R600-first case; the browser includes all 120 cases.\n')
    print(json.dumps(dict(cases=len(cases), inline_bytes=inline.stat().st_size)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--inline-output', type=Path, required=True)
    parser.add_argument('--trajectory-traces',type=Path)
    parser.add_argument('--history-status',type=Path)
    args = parser.parse_args()
    report(args.source, args.output, args.inline_output,args.trajectory_traces,args.history_status)
