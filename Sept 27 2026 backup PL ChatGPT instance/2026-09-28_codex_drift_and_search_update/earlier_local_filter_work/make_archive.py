"""Create a portable evidence/code/input/final-checkpoint backup with SHA256 inventory."""
from pathlib import Path
import hashlib,json,zipfile,datetime
ROOT=Path(__file__).resolve().parent

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    files=[]
    for p in ROOT.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(ROOT)
        if any(x in rel.parts for x in ['.venv','.git','__pycache__','.pytest_cache','mpl-cache']):continue
        if p.name in ['archive_manifest.json'] or p.suffix in ['.zip','.tmp']:continue
        if rel.parts[0]=='runs':
            run=ROOT/rel.parts[0]/rel.parts[1]
            manifest=run/'manifest.json'
            if not manifest.exists() or json.loads(manifest.read_text())['status']!='completed':continue
            allowed=['manifest.json','diagnostics.json','resume.npz']
            allowed+=['weighted_10.npz','weighted_12.npz'] if 'mh370_' in run.name else ['weighted_08.npz']
            if p.name not in allowed:continue
        files.append(p)
    inventory={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'description':'Portable reconstruction, frozen inputs, evidence, plots, all completed-run final checkpoints and MH370 00:11 weighted checkpoints. Intermediate checkpoints remain in the local working directory. Environment excluded; install requirements-lock.txt.','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(files)]}
    manifest=ROOT/'archive_manifest.json';manifest.write_text(json.dumps(inventory,indent=2));files.append(manifest)
    target=ROOT.parent/'mh370_v12_reconstruction_era5.zip'
    temp=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for p in sorted(files):
            compression=zipfile.ZIP_STORED if p.suffix in ['.npz','.png','.xlsx','.pdf'] else zipfile.ZIP_DEFLATED
            z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)),compress_type=compression)
    temp.replace(target)
    result={'path':str(target),'bytes':target.stat().st_size,'sha256':digest(target),'files':len(files)}
    target.with_suffix('.zip.sha256').write_text(result['sha256']+'  '+target.name+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
