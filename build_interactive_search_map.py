#!/usr/bin/env python3
"""Build a self-contained (data-inline) interactive MH370 search-evidence map fragment."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "outputs" / "mh370_search_evidence" / "map_data.json"
OUT = ROOT / "outputs" / "mh370_search_evidence" / "mh370-searched-areas.html"

payload = json.dumps(json.loads(DATA_PATH.read_text()), separators=(",", ":"))

template = r'''<div id="mh370-search-evidence" class="mh370-viz">
  <style>
    #mh370-search-evidence {
      --mh-bg: var(--color-background-primary, #f7f9fc);
      --mh-panel: var(--color-background-secondary, #ffffff);
      --mh-ink: var(--color-text-primary, #172033);
      --mh-muted: var(--color-text-secondary, #58657a);
      --mh-border: var(--color-border-primary, #cfd7e5);
      --mh-grid: var(--color-border-secondary, #dde3ee);
      --mh-sea: #edf6fb;
      --mh-land: #ded8c8;
      --mh-land-edge: #8b836e;
      --mh-official: #4c78a8;
      --mh-official-edge: #28567e;
      --mh-oi2018: #f2a541;
      --mh-oi2018-edge: #a75e00;
      --mh-outboard: #3d9b64;
      --mh-inboard: #d04f56;
      --mh-density: #bd3d47;
      --mh-track: #7651a1;
      --mh-arc: #252b35;
      --mh-context: #7d73a3;
      --mh-focus: #2878d0;
      box-sizing: border-box;
      width: 100%;
      max-width: 1180px;
      margin: 0 auto;
      padding: 14px;
      border: 1px solid var(--mh-border);
      border-radius: 16px;
      background: var(--mh-bg);
      color: var(--mh-ink);
      font: 14px/1.35 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    #mh370-search-evidence * { box-sizing: border-box; }
    #mh370-search-evidence .mh-head { display: flex; gap: 16px; align-items: start; justify-content: space-between; margin-bottom: 10px; }
    #mh370-search-evidence h2 { margin: 0 0 4px; font-size: 20px; line-height: 1.15; }
    #mh370-search-evidence .mh-sub { margin: 0; color: var(--mh-muted); max-width: 760px; }
    #mh370-search-evidence .mh-stat { min-width: 170px; padding: 9px 11px; border-radius: 10px; background: var(--mh-panel); border: 1px solid var(--mh-border); text-align: right; }
    #mh370-search-evidence .mh-stat strong { display: block; font-size: 19px; letter-spacing: -0.02em; }
    #mh370-search-evidence .mh-stat span { color: var(--mh-muted); font-size: 12px; }
    #mh370-search-evidence .mh-toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 9px; }
    #mh370-search-evidence button { appearance: none; border: 1px solid var(--mh-border); background: var(--mh-panel); color: var(--mh-ink); padding: 7px 10px; border-radius: 8px; cursor: pointer; font: inherit; }
    #mh370-search-evidence button:hover { border-color: var(--mh-focus); }
    #mh370-search-evidence button:focus-visible, #mh370-search-evidence input:focus-visible { outline: 2px solid var(--mh-focus); outline-offset: 2px; }
    #mh370-search-evidence button[aria-pressed="true"] { background: var(--mh-focus); color: var(--mh-panel); border-color: var(--mh-focus); }
    #mh370-search-evidence .mh-spacer { flex: 1; }
    #mh370-search-evidence .mh-map-wrap { position: relative; min-height: 470px; border: 1px solid var(--mh-border); border-radius: 12px; overflow: hidden; background: var(--mh-sea); }
    #mh370-search-evidence svg { display: block; width: 100%; height: 100%; min-height: 470px; touch-action: none; }
    #mh370-search-evidence .mh-controls { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 7px 12px; padding: 10px 2px 2px; }
    #mh370-search-evidence label { display: flex; gap: 7px; align-items: start; cursor: pointer; font-size: 12px; color: var(--mh-muted); }
    #mh370-search-evidence label input { margin-top: 2px; accent-color: var(--mh-focus); }
    #mh370-search-evidence .mh-swatch { flex: 0 0 18px; height: 9px; margin-top: 4px; border-radius: 2px; background: var(--swatch); opacity: var(--opacity, 1); }
    #mh370-search-evidence .mh-note { display: grid; grid-template-columns: 1fr auto; gap: 14px; align-items: start; margin-top: 10px; padding: 10px 12px; border: 1px solid var(--mh-border); border-radius: 10px; background: var(--mh-panel); }
    #mh370-search-evidence .mh-note p { margin: 0; }
    #mh370-search-evidence .mh-note small { color: var(--mh-muted); }
    #mh370-search-evidence .mh-grade { white-space: nowrap; border: 1px solid var(--mh-border); border-radius: 999px; padding: 3px 8px; color: var(--mh-muted); font-size: 11px; }
    #mh370-search-evidence .mh-tooltip { position: absolute; pointer-events: none; opacity: 0; z-index: 5; max-width: 310px; padding: 9px 10px; border-radius: 8px; border: 1px solid var(--mh-border); background: var(--mh-panel); color: var(--mh-ink); box-shadow: 0 8px 25px rgb(0 0 0 / 16%); font-size: 12px; }
    #mh370-search-evidence .mh-tooltip strong { display: block; margin-bottom: 3px; }
    #mh370-search-evidence .mh-tooltip span { display: block; color: var(--mh-muted); }
    #mh370-search-evidence .graticule { fill: none; stroke: var(--mh-grid); stroke-width: .65; }
    #mh370-search-evidence .coast { fill: var(--mh-land); stroke: var(--mh-land-edge); stroke-width: .65; }
    #mh370-search-evidence .layer { vector-effect: non-scaling-stroke; }
    #mh370-search-evidence .axis-label { fill: var(--mh-muted); font-size: 11px; paint-order: stroke; stroke: var(--mh-panel); stroke-width: 3px; }
    #mh370-search-evidence .map-label { fill: var(--mh-ink); font-size: 12px; font-weight: 650; paint-order: stroke; stroke: var(--mh-panel); stroke-width: 4px; }
    @media (max-width: 760px) {
      #mh370-search-evidence .mh-head { display: block; }
      #mh370-search-evidence .mh-stat { margin-top: 9px; text-align: left; }
      #mh370-search-evidence .mh-controls { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      #mh370-search-evidence .mh-note { grid-template-columns: 1fr; }
    }
  </style>
  <div class="mh-head">
    <div>
      <h2>MH370 searched-area evidence audit</h2>
      <p class="mh-sub">Published high-resolution sonar coverage is separated from reconstructed Ocean Infinity outlines, vessel-track proxies, and planning envelopes. Hover for source quality and model-use warnings.</p>
    </div>
    <div class="mh-stat"><strong>7,428.54 km²</strong><span>official contracted area remaining after 23 Jan 2026</span></div>
  </div>
  <div class="mh-toolbar" role="group" aria-label="Map view">
    <button type="button" data-view="overview" aria-pressed="true">Ocean overview</button>
    <button type="button" data-view="detail" aria-pressed="false">Renewed-search detail</button>
    <span class="mh-spacer"></span>
    <button type="button" data-action="reset">Reset pan / zoom</button>
  </div>
  <div class="mh-map-wrap">
    <svg role="img" aria-label="Map of MH370 seabed searches, seventh arc, inferred renewed-search bands, and impact density"></svg>
    <div class="mh-tooltip" role="status" aria-live="polite"></div>
  </div>
  <div class="mh-controls" aria-label="Map layers">
    <label><input type="checkbox" data-layer="density" checked><span class="mh-swatch" style="--swatch:var(--mh-density);--opacity:.55"></span><span>Stage-1 impact density (context)</span></label>
    <label><input type="checkbox" data-layer="official" checked><span class="mh-swatch" style="--swatch:var(--mh-official);--opacity:.7"></span><span>ATSB / Bluefin official sonar footprint</span></label>
    <label><input type="checkbox" data-layer="oi2018" checked><span class="mh-swatch" style="--swatch:var(--mh-oi2018);--opacity:.65"></span><span>OI 2018 approximate outline</span></label>
    <label><input type="checkbox" data-layer="renewed" checked><span class="mh-swatch" style="--swatch:var(--mh-inboard);--opacity:.6"></span><span>Renewed-search inferred bands</span></label>
    <label><input type="checkbox" data-layer="tracks" checked><span class="mh-swatch" style="--swatch:var(--mh-track)"></span><span>2025–26 vessel-track proxies</span></label>
    <label><input type="checkbox" data-layer="arc" checked><span class="mh-swatch" style="--swatch:var(--mh-arc)"></span><span>Official 7th arc (FL400)</span></label>
    <label><input type="checkbox" data-layer="context"><span class="mh-swatch" style="--swatch:var(--mh-context);--opacity:.35"></span><span>Official ±100 NM context — not searched</span></label>
  </div>
  <div class="mh-note">
    <p id="mh370-map-note"><strong>Interpretation:</strong> historical searches strongly reduce probability near the arc, but do not justify a binary exclusion. Exact OI AUV swaths and the official remaining polygon are not public.</p>
    <span class="mh-grade">A = official · C = reconstruction</span>
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
(() => {
  const root = document.getElementById('mh370-search-evidence');
  const data = __MAP_DATA__;
  const svg = d3.select(root).select('svg');
  const wrap = root.querySelector('.mh-map-wrap');
  const tooltip = d3.select(root).select('.mh-tooltip');
  const css = getComputedStyle(root);
  const C = name => css.getPropertyValue(name).trim();
  const layers = {density:true, official:true, oi2018:true, renewed:true, tracks:true, arc:true, context:false};
  const views = {
    overview: {bbox:[83,-42,116,-18], note:'Historical high-resolution coverage extends roughly 1,800 km along the 7th arc. Wide ±100 NM planning context is optional and was not fully searched.'},
    detail: {bbox:[90.5,-37,96.5,-32.2], note:'Best-supported inference: the remaining contracted work is concentrated in the inboard / northwest band plus infill and boundary differences; no exact official residual polygon is public.'}
  };
  let currentView = 'overview';
  let width = 1000;
  let height = 570;
  let projection;
  let path;
  const scene = svg.append('g').attr('class','scene');
  const map = scene.append('g').attr('class','map');
  const zoom = d3.zoom().scaleExtent([1,12]).on('zoom', e => map.attr('transform', e.transform));
  svg.call(zoom);

  const byId = new Map(data.footprints.features.map(f => [f.properties.id, f]));
  const featureTip = f => {
    const p = f.properties || {};
    const lines = [p.status, p.geometry_quality, p.detection_note, p.inference, p.warning].filter(Boolean);
    return `<strong>${p.name || p.id || 'Search feature'}</strong>${lines.map(x => `<span>${x}</span>`).join('')}`;
  };
  const showTip = (event, html) => {
    const box = wrap.getBoundingClientRect();
    const left = Math.min(event.clientX - box.left + 12, box.width - 325);
    const top = Math.min(event.clientY - box.top + 12, box.height - 135);
    tooltip.html(html).style('left', `${Math.max(8,left)}px`).style('top', `${Math.max(8,top)}px`).style('opacity',1);
  };
  const hideTip = () => tooltip.style('opacity',0);
  const bindTip = sel => sel.on('pointerenter', (e,d) => showTip(e,featureTip(d))).on('pointermove', (e,d) => showTip(e,featureTip(d))).on('pointerleave', hideTip);
  const bboxFeature = bbox => ({type:'Polygon',coordinates:[[[bbox[0],bbox[1]],[bbox[2],bbox[1]],[bbox[2],bbox[3]],[bbox[0],bbox[3]],[bbox[0],bbox[1]]]]});
  const binFeature = d => ({type:'Feature',properties:d,geometry:{type:'Polygon',coordinates:[[[d.lon,d.lat],[d.lon+.25,d.lat],[d.lon+.25,d.lat+.25],[d.lon,d.lat+.25],[d.lon,d.lat]]]}});

  function redraw() {
    const rect = wrap.getBoundingClientRect();
    width = Math.max(520, Math.round(rect.width));
    height = Math.max(470, Math.min(670, Math.round(width * .56)));
    wrap.style.height = `${height}px`;
    svg.attr('viewBox', `0 0 ${width} ${height}`);
    map.selectAll('*').remove();
    projection = d3.geoMercator().fitExtent([[38,28],[width-24,height-35]], bboxFeature(views[currentView].bbox));
    path = d3.geoPath(projection);

    const grat = d3.geoGraticule().step(currentView === 'overview' ? [5,5] : [1,1])();
    map.append('path').datum(grat).attr('class','graticule').attr('d',path);
    map.selectAll('.coast').data(data.land.features).join('path').attr('class','coast').attr('d',path);

    const context = map.append('g').attr('data-layer','context');
    bindTip(context.selectAll('path').data([byId.get('initial_100nm_wide_area_context')]).join('path')
      .attr('class','layer').attr('d',path).attr('fill',C('--mh-context')).attr('fill-opacity',.13).attr('stroke',C('--mh-context')).attr('stroke-opacity',.45));

    const bins = data.posterior_bins.filter(d => d.density >= .04).map(binFeature);
    const density = map.append('g').attr('data-layer','density');
    density.selectAll('path').data(bins).join('path').attr('class','layer').attr('d',path)
      .attr('fill',C('--mh-density')).attr('fill-opacity',d => .05 + .38*d.properties.density).attr('stroke','none')
      .on('pointerenter',(e,d)=>showTip(e,`<strong>Stage-1 impact-density cell</strong><span>Relative cell density: ${d.properties.density.toFixed(3)}</span><span>Context only; not yet updated by search non-detection.</span>`))
      .on('pointermove',(e,d)=>showTip(e,`<strong>Stage-1 impact-density cell</strong><span>Relative cell density: ${d.properties.density.toFixed(3)}</span><span>Context only; not yet updated by search non-detection.</span>`)).on('pointerleave',hideTip);

    const officialFeatures = ['atsb_phase2_2014_2017','bluefin21_2014_1','bluefin21_2014_2'].map(id=>byId.get(id)).filter(Boolean);
    const official = map.append('g').attr('data-layer','official');
    bindTip(official.selectAll('path').data(officialFeatures).join('path').attr('class','layer').attr('d',path)
      .attr('fill',C('--mh-official')).attr('fill-opacity',.45).attr('stroke',C('--mh-official-edge')).attr('stroke-width',.85));

    const oi = map.append('g').attr('data-layer','oi2018');
    bindTip(oi.selectAll('path').data([byId.get('oi2018_total_outline_approx')]).join('path').attr('class','layer').attr('d',path)
      .attr('fill',C('--mh-oi2018')).attr('fill-opacity',.20).attr('stroke',C('--mh-oi2018-edge')).attr('stroke-width',1.3).attr('stroke-dasharray','6 4'));

    const renewedFeatures = ['oi2024_proposed_outboard_southeast','oi2024_proposed_inboard_northwest'].map(id=>byId.get(id));
    const renewed = map.append('g').attr('data-layer','renewed');
    bindTip(renewed.selectAll('path').data(renewedFeatures).join('path').attr('class','layer').attr('d',path)
      .attr('fill',(d,i)=>i?C('--mh-inboard'):C('--mh-outboard')).attr('fill-opacity',(d,i)=>i?.20:.27)
      .attr('stroke',(d,i)=>i?C('--mh-inboard'):C('--mh-outboard')).attr('stroke-width',1.7).attr('stroke-dasharray',(d,i)=>i?'5 3':null));

    const tracks = map.append('g').attr('data-layer','tracks');
    bindTip(tracks.selectAll('path').data(data.tracks.features).join('path').attr('class','layer').attr('d',path)
      .attr('fill','none').attr('stroke',C('--mh-track')).attr('stroke-width',1.1).attr('stroke-opacity',.78));

    const arcFeature = byId.get('seventh_arc_fl400');
    const arc = map.append('g').attr('data-layer','arc');
    bindTip(arc.selectAll('path').data([arcFeature]).join('path').attr('class','layer').attr('d',path)
      .attr('fill','none').attr('stroke',C('--mh-arc')).attr('stroke-width',1.7).attr('stroke-dasharray','8 5'));

    if (currentView === 'overview') {
      map.append('text').attr('class','map-label').attr('x',projection([114,-25])[0]).attr('y',projection([114,-25])[1]).attr('text-anchor','middle').text('Western Australia');
    } else {
      map.append('text').attr('class','map-label').attr('x',projection([93.25,-33.4])[0]).attr('y',projection([93.25,-33.4])[1]).attr('text-anchor','middle').text('Likely residual concentration');
    }
    applyLayerVisibility();
    svg.call(zoom.transform,d3.zoomIdentity);
    root.querySelector('#mh370-map-note').innerHTML = `<strong>Interpretation:</strong> ${views[currentView].note}`;
  }

  function applyLayerVisibility() {
    Object.entries(layers).forEach(([name,on]) => map.select(`[data-layer="${name}"]`).style('display',on?null:'none'));
  }

  root.querySelectorAll('[data-view]').forEach(btn => btn.addEventListener('click', () => {
    currentView = btn.dataset.view;
    root.querySelectorAll('[data-view]').forEach(b => b.setAttribute('aria-pressed',String(b===btn)));
    redraw();
  }));
  root.querySelector('[data-action="reset"]').addEventListener('click',()=>svg.transition().duration(250).call(zoom.transform,d3.zoomIdentity));
  root.querySelectorAll('[data-layer]').forEach(input => {
    if (input.tagName !== 'INPUT') return;
    input.addEventListener('change',()=>{ layers[input.dataset.layer]=input.checked; applyLayerVisibility(); });
  });
  const observer = new ResizeObserver(() => redraw());
  observer.observe(wrap);
  redraw();
})();
</script>'''

rendered = template.replace("__MAP_DATA__", payload)
OUT.write_text(rendered)
print(OUT)
print(OUT.stat().st_size)
