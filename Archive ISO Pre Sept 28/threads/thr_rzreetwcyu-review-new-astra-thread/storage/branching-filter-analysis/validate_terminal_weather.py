"""Independent binary and raw-pressure checks before a terminal-only grid extension."""
from pathlib import Path
import hashlib,json,struct,time,math
import numpy as np
B=Path('/jackbox/home/.iso/thread-storage/thr_rzreetwcyu/branching-filter-analysis')
OLD=Path('/jackbox/home/MH370/inputs/environment/mh370-era5-grid.bin')
NEW=B/'terminal-weather/grid.bin'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def load(p):
 with p.open('rb') as f:
  assert f.read(8)==b'MHERA5V1'
  shape=struct.unpack('<4I',f.read(16)); axes=[]
  for n,d in zip(shape,['<i8','<f4','<f4','<f4']): axes.append(np.frombuffer(f.read(n*np.dtype(d).itemsize),dtype=d).copy())
  offset=f.tell()
 assert p.stat().st_size==offset+3*math.prod(shape)*4
 return shape,axes,np.memmap(p,dtype='<f4',mode='r',offset=offset,shape=(3,*shape))
def pressure(h):
 z=h*.3048
 exponent=9.80665/(287.05287*.0065)
 if z<=11000:return 1013.25*(1-.0065*z/288.15)**exponent
 return 1013.25*(216.65/288.15)**exponent*math.exp(-9.80665*(z-11000)/(287.05287*216.65))
start=time.perf_counter(); m=json.loads((B/'terminal-weather/manifest.json').read_text()); oldm=json.loads(OLD.with_suffix('.manifest.json').read_text())
assert sha(OLD)=='73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4'
assert sha(NEW)==m['output_sha256']=='1d170bfbbcca5a1fadbf0ea3cc2a7a6545a0255353d2829be012fc0779ff2def'
assert m['source_chunk_identity_sha256']==oldm['source_chunk_identity_sha256']=='eed7079e6bbd5260d95f965071ed656d9667d43864f720207021fc1fb5bfb887'
assert m['source_chunk_objects']==oldm['source_chunk_objects']
assert m['deterministic_regeneration']['byte_for_byte_equal']
a,ax,old=load(OLD);b,bx,new=load(NEW)
assert a==(9,12,361,721) and b==(9,18,361,721)
assert all(np.array_equal(ax[i],bx[i]) for i in [0,2,3])
assert np.array_equal(ax[1],bx[1][:12])
assert list(bx[1][12:])==[46000,49000,52000,55000,58000,60000]
assert np.isfinite(new).all()
assert np.array_equal(old.view('<u4'),new[:,:,:12,:,:].view('<u4'))
assert np.array_equal(new[:,:,:,:,0],new[:,:,:,:,-1])
spot_checks=[]
for spot in m['raw_source_spot_checks']:
 t=int(__import__('datetime').datetime.fromisoformat(spot['time_utc']).replace(tzinfo=__import__('datetime').timezone.utc).timestamp())
 indices=[int(np.where(v==target)[0][0]) for v,target in zip(bx,[t,spot['pressure_altitude_ft'],spot['latitude_deg'],spot['longitude_deg']])]
 p=pressure(spot['pressure_altitude_ft'])
 assert abs(p/spot['target_pressure_hpa']-1)<2e-14
 lo,hi=spot['lower_source_hpa'],spot['upper_source_hpa']
 assert lo<=p<=hi
 u=(math.log(p)-math.log(lo))/(math.log(hi)-math.log(lo))
 for field,name in enumerate(m['variables_in_binary_order']):
  f=spot['fields'][name]; expected=np.float32((1-u)*f['raw_lower_source_value']+u*f['raw_upper_source_value'])
  actual=new[(field,*indices)]
  assert actual==expected==np.float32(f['output_value'])
  spot_checks.append({'altitude_ft':spot['pressure_altitude_ft'],'field':name,'expected':float(expected),'actual':float(actual)})
record={'status':'verified_terminal_only_altitude_extension','old_grid_sha256':sha(OLD),'new_grid_sha256':m['output_sha256'],'manifest_sha256':sha(B/'terminal-weather/manifest.json'),'old_fields_bit_identical':True,'original_float32_values_checked':int(old.size),'original_source_chunk_identities_equal':True,'new_shape':b,'upper_altitude_ft':60000,'independent_raw_pressure_spots':spot_checks,'elapsed_seconds':time.perf_counter()-start,'limitations':['Same hourly UTC domain through01:00; no temporal extrapolation.','Pressure altitude remains an approximation for geometric height in terminal propagation.','Weather availability does not validate aircraft aerodynamics or flight feasibility at high altitude.']}
(B/'terminal-weather/verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='independent_raw_pressure_spots'},indent=2))
