import tomllib, re, os
Lnodes={}
for name,la,lo in pts:
    Lnodes[name]=snap(la,lo); print(name, Lnodes[name])
os.makedirs('jobL',exist_ok=True)
ID_SEGS = '''
[[hypotheses.debris-drift.segments]]
name = "ID-sumatra-west"
# PROVISIONAL (Kadri-Haixun drift leg, 18 Oct 2026): Sumatra Indian Ocean coast and its islands south of the equator (domain edge 0 N).
boxes = [[95.0, 106.2, -6.2, 0.0]]

[[hypotheses.debris-drift.segments]]
name = "ID-java-south"
# PROVISIONAL: Java south coast (north coast excluded by the latitude limits).
boxes = [[105.1, 108.0, -9.0, -6.65], [108.0, 111.5, -9.0, -7.3], [111.5, 114.7, -9.0, -8.0]]

[[hypotheses.debris-drift.segments]]
name = "ID-nusa-tenggara-south"
# PROVISIONAL: Bali to Timor (Lesser Sunda islands), south of 8 S.
boxes = [[114.4, 125.5, -11.2, -8.0]]
'''
IDN=['ID-sumatra-west','ID-java-south','ID-nusa-tenggara-south']
def idlist(v): return "".join(f'  {{ segment = "{s}", ln_mean_by_period = [{v}, {v}, {v}] }},\n' for s in IDN)
def make_cfg(model, label, nodes_, ppc, t_release):
    s=open(R+f'arc-latitude-scan/arclat-{model}-north.toml').read()
    hdr=(f"# KADRI-HAIXUN CONDITIONAL, drift leg (pre-registration Q7), 18 Oct 2026: arclat-{model}-north.toml unchanged except\n"
         f"# node_subset, particles_per_class, release_unix_s, output_dir, three PROVISIONAL Indonesian segments (base level off, so B/C/off/A/\n"
         f"# searcher/populated equal the arclat definitions) and Indonesian level alternatives. Label {label}.\n")
    s=hdr+s
    s=re.sub(r'(?m)^node_subset = \[.*\]$', f'node_subset = {nodes_}', s)
    s=re.sub(r'(?m)^particles_per_class = .*$', f'particles_per_class = {ppc}', s)
    s=re.sub(r'(?m)^release_unix_s = .*$', f'release_unix_s = {t_release:.1f}', s)
    s=re.sub(r'(?m)^output_dir = .*$', f'output_dir = "OUTROOT/{label}"', s)
    s=re.sub(r'(?m)^name = "debris-drift-australia160-(\w+)"', rf'name = "debris-drift-kadri-{label}"', s)
    s=s.replace('\n[hypotheses.debris-drift.recovery]', ID_SEGS+'\n[hypotheses.debris-drift.recovery]',1)
    # base override list: append ID off
    i=s.index('[hypotheses.debris-drift.levels]'); j=s.index('\n]\n', i)
    s=s[:j]+'\n'+idlist('-30.0').rstrip('\n')+s[j:]
    # each alternative with a list: append ID off ; alternative A gets a list with ID off only
    parts=s.split('[[hypotheses.debris-drift.levels.alternatives]]')
    out=[parts[0]]
    for p in parts[1:]:
        if 'segment_ln_mean_by_period' in p.split('[hypotheses.debris-drift.splitting]')[0]:
            k=p.index('\n]\n'); p=p[:k]+'\n'+idlist('-30.0').rstrip('\n')+p[k:]
        else:
            nm=re.search(r'name = "(\w+)"',p); p=p.replace(nm.group(0), nm.group(0)+'\nsegment_ln_mean_by_period = [\n'+idlist('-30.0')+']',1)
        out.append(p)
    s='[[hypotheses.debris-drift.levels.alternatives]]'.join(out)
    # new alternatives, inserted before splitting
    cfgp=tomllib.loads(s)['hypotheses']['debris-drift']['levels']
    base=cfgp['segment_ln_mean_by_period']; alts={a['name']:a for a in cfgp['alternatives']}
    def lst(entries): return "".join(f'  {{ segment = "{e["segment"]}", ln_mean_by_period = [{", ".join(str(x) for x in e["ln_mean_by_period"])}] }},\n' for e in entries if not e['segment'].startswith('ID-'))
    new=''
    for nm,src,v in [('B_ID_low',base,-2.302585),('B_ID_mid',base,-1.203973),('B_ID_full',base,0.0),('populated_ID_mid',alts['populated']['segment_ln_mean_by_period'],-1.203973),('off_ID_mid',alts['off']['segment_ln_mean_by_period'],-1.203973)]:
        new+=f'[[hypotheses.debris-drift.levels.alternatives]]\nname = "{nm}"\nsegment_ln_mean_by_period = [\n'+lst(src)+idlist(v)+']\n\n'
    s=s.replace('[hypotheses.debris-drift.splitting]', new+'[hypotheses.debris-drift.splitting]',1)
    tomllib.loads(s); return s
legs=[]
for model in ('globcurrent','glorys12'):
    for r in rel:
        nd=Lnodes[r['point']][0]; ppc=83334 if r['point'] in ('crossing','haixun') else 25000
        lab=f"kadri-{model}-{r['branch']}-{r['point']}"
        open(f'jobL/{lab}.toml','w').write(make_cfg(model,lab,[nd],ppc,r['unix'])); legs.append(lab)
    lab=f"kadri-{model}-ref-anchors"; open(f'jobL/{lab}.toml','w').write(make_cfg(model,lab,[9506,14576,27230],25000,1394237977.0)); legs.append(lab)
open('jobL/legs.txt','w').write("\n".join(legs)+"\n")
c0=tomllib.load(open('jobL/kadri-glorys12-T-crossing.toml','rb'))['hypotheses']['debris-drift']
print(len(legs), [s['name'] for s in c0['segments']][-4:], [ (a['name'],len(a.get('segment_ln_mean_by_period',[]))) for a in c0['levels']['alternatives']], len(c0['levels']['segment_ln_mean_by_period']), c0['release_unix_s'], c0['node_subset'], c0['particles_per_class'])
print(c0['transport'])
