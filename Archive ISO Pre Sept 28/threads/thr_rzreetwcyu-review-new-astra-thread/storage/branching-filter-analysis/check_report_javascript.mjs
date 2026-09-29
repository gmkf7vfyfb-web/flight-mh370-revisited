// Execute saved report scripts and every selector in a small DOM/canvas fixture.
// This catches loading/selection/nonfinite drawing errors, not browser layout.
import fs from 'node:fs';
import vm from 'node:vm';
const outputs=[];
for(const filename of process.argv.slice(2)){
 const documentText=fs.readFileSync(filename,'utf8'),elements=new Map();let draws=0;
 const context2d=new Proxy({}, {get(target,key){if(key in target)return target[key];if(key==='measureText')return t=>({width:String(t).length*10});return (...args)=>{if(args.some(v=>typeof v==='number'&&!Number.isFinite(v)))throw Error('Nonfinite canvas '+key);draws++;return {addColorStop(){}}};},set(t,k,v){t[k]=v;return true;}});
 function element(id,select=false){if(elements.has(id))return elements.get(id);let html='',value='';const node={id,select,options:[],width:1000,height:720,textContent:'',classList:{toggle(){}},getContext(){return context2d},addEventListener(){},after(){}};
 Object.defineProperties(node,{innerHTML:{get(){return html},set(v){html=v;if(node.select){node.options=[...String(v).matchAll(/<option(?:\s+value="([^"]*)")?[^>]*>(.*?)<\/option>/g)].map(m=>({value:m[1]??m[2]}));value=node.options[0]?.value??'';}}},value:{get(){return value},set(v){v=String(v);value=node.select&&!node.options.some(o=>o.value===v)?'':v;}}});elements.set(id,node);return node;}
 for(const m of documentText.matchAll(/<select[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g))element(m[1],true).innerHTML=m[2];
 for(const m of documentText.matchAll(/<canvas[^>]*id="([^"]+)"[^>]*width="(\d+)"[^>]*height="(\d+)"/g)){const e=element(m[1]);e.width=+m[2];e.height=+m[3];}
 for(const m of documentText.matchAll(/<section id="([^"]+)" class="bin"/g))element(m[1]);
 const document={getElementById:id=>element(id),querySelectorAll:s=>s==='.bin'?[...elements.values()].filter(e=>e.id.startsWith('latitude-')):[...elements.values()].filter(e=>e.id.startsWith('plot-')),createElement:()=>element('generated-'+elements.size)};
 const sandbox={document,Blob,Response,DecompressionStream,Uint8Array,atob,console,setTimeout};const ctx=vm.createContext(sandbox);
 const script=documentText.match(/<script>([\s\S]*?)<\/script>/)[1];await vm.runInContext(script,ctx);
 const status=element('status').textContent;if(/could not|couldn.t|error/i.test(status))throw Error(filename+': '+status);
 let cases=0,hypotheticalChecks=0,attributionChecks=0;
 if(filename.includes('impact-context')){
  cases=vm.runInContext(`(()=>{let n=0;for(const m of data.maps){el('family').value=m.terminal_family;el('contact').value=m.contact_case;render();if(!el('map').innerHTML.includes('<svg'))throw Error('Missing paired impact map');for(const t of data.targets.filter(x=>x.position)){el('target').value=t.id;renderRoute();if(!el('route').innerHTML.includes('<svg'))throw Error('Missing exact route figure');n++}}return n})()`,ctx);
 }
 else if(filename.includes('flight-drift-comparison')){
  cases=vm.runInContext(`(()=>{let n=0;for(const v of report.comparisons){f.value=v.terminal_family;c.value=v.contact_case;e.value=v.evidence_model;replica.value=v.numerical_run;for(const p of ['0011','impact'])for(const x of ['south','full']){phase.value=p;extent.value=x;render();n++}}for(let i=0;i<report.routes.length;i++){byId('route').value=String(i);showRoute();if(!byId('route-chart').innerHTML.includes('<svg'))throw Error('Missing exact route figure')}return n})()`,ctx);
  attributionChecks=vm.runInContext(`(()=>{let n=0;if(!report.evidence_attribution)return n;for(const family of Object.keys(report.family_labels))for(const v of report.evidence_attribution.variants)for(const run of ['Original','Repeat 1','Repeat 2'])for(const p of ['0011','impact'])for(const x of ['south','full']){f.value=family;byId('attribution').value=v.id;replica.value=run;phase.value=p;extent.value=x;renderAttribution();if(!byId('attribution-stats').innerHTML.includes('<table>'))throw Error('Missing contribution table');n++}return n})()`,ctx);
 }
 else if(filename.includes('acoustic-comparison'))cases=vm.runInContext(`(()=>{let n=0;for(const v of data){family.value=v.terminal_family;chooseContact();contact.value=v.contact_case;for(const st of ['H01W','H08S']){station.value=st;for(const e of ['1','.01','.0001','.000001','.00000001','0']){efficiency.value=e;render();n++}}}return n})()`,ctx);
 else if(filename.includes('impact-comparison')||filename.includes('impact-replication'))cases=vm.runInContext(`(()=>{let n=0;for(let i=0;i<data.groups.length;i++){family.value=String(i);caseSelect.innerHTML=data.groups[i].cases.map((v,j)=>'<option value="'+j+'">x</option>').join('');for(let j=0;j<data.groups[i].cases.length;j++){caseSelect.value=String(j);for(const q of ['south','all']){view.value=q;render();n++}}}return n})()`,ctx);
 else if(filename.includes('search-comparison')){
  cases=vm.runInContext(`(()=>{let n=0;for(const v of data.cases){family.value=v.terminal_family;chooseContact();contact.value=v.contact_case;chooseEvidence();evidence.value=v.evidence_model;for(const z of ['5','10','25','50']){size.value=z;render();n++}}return n})()`,ctx);
  hypotheticalChecks=vm.runInContext(`(()=>{if(typeof hypotheticalSearch==='undefined')return 0;if(Math.abs(hypotheticalSearch(.75,.5,.3,.8).selected-.85)>1e-12||hypotheticalSearch(1,1,1,1)!==null)throw Error('Search finite-reference failure');let n=0;for(const c of data.cases)for(const p of c.plans)for(const f of c.footprint_overlap)for(const d of [0,.5,.9,.99,1]){const v=hypotheticalSearch(p.captured_probability,f.probability,p.selected_probability_inside_context_footprints[f.id],d);if(v&&(!Number.isFinite(v.selected)||v.selected<0||v.selected>1||!Number.isFinite(v.footprint)||v.footprint<0||v.footprint>1))throw Error('Invalid hypothetical search probability');n++}return n})()`,ctx);
 }
 else if(filename.includes('route-examples')){cases=vm.runInContext(`(()=>{for(const o of chosen.options)showBin(o.value);return chosen.options.length})()`,ctx);if([...elements.values()].filter(e=>e.id.startsWith('plot-')).some(e=>!e.innerHTML.includes('<svg')&&!e.innerHTML.includes('No history retained')))throw Error('Missing gallery SVG');}
 else cases=vm.runInContext(`(()=>{let n=0;for(const v of data){family.value=v.terminal_family;chooseContact();contact.value=v.contact_case;chooseEvidence();evidence.value=v.evidence_model;render();n++}return n})()`,ctx);
 outputs.push({filename,selector_combinations:cases,drift_evidence_selector_combinations:attributionChecks,hypothetical_search_cases:hypotheticalChecks,finite_canvas_operations:draws,scope:'JavaScript fixture; no authenticated phone-browser test'});
}
console.log(JSON.stringify(outputs,null,2));
