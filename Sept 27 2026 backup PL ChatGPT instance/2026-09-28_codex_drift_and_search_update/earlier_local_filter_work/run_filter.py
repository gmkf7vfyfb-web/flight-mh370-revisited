"""Run/restart the reconstructed filter; checkpoints include RNG and all states."""
from pathlib import Path
import argparse,json,sys,platform
import numpy as np
from core import *

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default='inputs/mh371_dense.json');p.add_argument('--weather',choices=['era5','oracle'],default='era5');p.add_argument('--particles',type=int,default=100000);p.add_argument('--seed',type=int,default=101);p.add_argument('--bto-only',action='store_true');p.add_argument('--output',required=True);p.add_argument('--resume',action='store_true');p.add_argument('--stop-after',type=int);args=p.parse_args()
    file=ROOT/args.input;spec=json.loads(file.read_text());out=ROOT/args.output;out.mkdir(parents=True,exist_ok=True)
    magpath=ROOT/'inputs'/spec['magnetic'];mag=MagneticGrid(magpath)
    wp=ROOT/'inputs'/('era5_weather.npz' if args.weather=='era5' else spec['weather'])
    if args.weather=='era5':weather=GriddedWeather(wp)
    else:
        with np.load(wp) as z:weather=OracleWeather(z['time'],z['north'],z['east'],z['temperature'])
    cfg=Config(particles=args.particles,seed=args.seed,use_bfo=not args.bto_only,position_sd_deg=spec.get('position_sd_deg',.4/60))
    identity={'input_sha256':sha256(file),'core_sha256':sha256(ROOT/'core.py'),'runner_sha256':sha256(__file__),'weather_sha256':sha256(wp),'magnetic_sha256':sha256(magpath),'config':asdict(cfg)}
    checkpoint=out/'resume.npz'
    if args.resume:f=Filter.resume(checkpoint,weather,mag,identity)
    else:
        if checkpoint.exists():raise ValueError('Existing run: use --resume or a fresh output directory')
        f=Filter(cfg,weather,mag);f.initialize(spec['prior'])
    manifest={'classification':'new v12 reconstruction; not original binary/source reproduction','identity':identity,'weather':weather.classification,'input_classification':spec['classification'],'python':platform.python_version(),'configuration':asdict(cfg),'status':'running'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    for obs in spec['observations'][f.index:]:
        row=f.observe(obs)
        f.checkpoint(out/f'weighted_{f.index:02d}.npz',identity)
        row['resampled']=f.resample() if f.index<len(spec['observations']) else False
        f.checkpoint(checkpoint,identity)
        (out/'diagnostics.json').write_text(json.dumps(f.history,indent=2))
        print(json.dumps(row),flush=True)
        if args.stop_after is not None and f.index>=args.stop_after:break
    manifest['status']='completed' if f.index==len(spec['observations']) else 'checkpointed'
    manifest['observations_completed']=f.index
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
