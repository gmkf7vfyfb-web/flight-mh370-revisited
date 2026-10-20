"""Accident-flight adapter: Davey Table 10.1 message selection, ERA5 substitution.
Initial location/track reconstructed in earlier project notes, not exact radar KF.
"""
from pathlib import Path
from datetime import datetime
import json,shutil
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from core import *

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'inputs'
RAW=Path('/Users/pete/Downloads/MH370_particle_filter_validation_bundle/data/raw/mh370_sita_logs_unredacted_1odSiOq2J3b2LsWk5y8xF6Nzav5gnPFIj.xlsx')

def main():
    w=load_workbook(RAW,read_only=True,data_only=True);rows={i:r for i,r in enumerate(w['SU Log'].iter_rows(values_only=True),1)}
    selected=[7013,7021,7032,7037,7126,7128,7130,7132,7185,7187,7188,7194]
    with np.load(OUT/'orbit.npz') as z:ot=z['time'];op=z['position'];ov=z['velocity']
    fg=pd.read_excel(OUT/'inmarsat_figure11_pilot_error_1rN7Hz5Kybnn-dIYbdV5vF4KhrcRsseRE.xlsx',sheet_name='Figure11')[['Hours UTC','Hz']].apply(pd.to_numeric,errors='coerce').dropna().sort_values('Hours UTC').to_numpy(float)
    observations=[];rawaudit=[]
    for i in selected:
        row=rows[i];t=(row[0]-datetime(2014,3,7)).total_seconds()
        if t<ot[0] or t>ot[-1]:raise ValueError('Orbit outside support')
        sat=np.array([np.interp(t,ot,op[:,j]) for j in range(3)]);vel=np.array([np.interp(t,ot,ov[:,j]) for j in range(3)])
        if i in [7188,7194]:
            afc=0. # no BFO used, so common BFO correction is irrelevant
        elif i==7187:
            afc=-37.7 # ATSB Appendix G Table 4, 00:11; digitized pilot ends at 23:59
        else:
            if t/3600<fg[0,0] or t/3600>fg[-1,0]:raise ValueError('Pilot correction outside support')
            afc=np.interp(t/3600,fg[:,0],fg[:,1])+F_UP/C*np.dot(vel,unit(sat-ecef(53.284722,6.215333,0)))-F_DOWN/C*np.dot(vel,unit(PERTH-sat))
        bto=row[27];bfo=row[25];sd=29.;delay=-495679.;correction=0
        if i in [7013,7194]:correction=(5 if i==7013 else 4)*7820;bto-=correction;sd=43.;bfo=None
        if i==7188:delay=-491079.;sd=63.;bfo=None
        observations.append({'time':t,'timestamp':str(row[0]),'bto':bto,'bfo':bfo,'bto_sd':sd,'delay_us':delay,'satellite':sat.tolist(),'sat_velocity':vel.tolist(),'afc':float(afc),'channel':row[3],'source_row':i})
        rawaudit.append({'source_row':i,'timestamp':str(row[0]),'channel':row[3],'raw_bto_us':row[27],'anomaly_subtracted_us':correction,'used_bto_us':bto,'raw_bfo_hz':row[25],'used_bfo_hz':bfo,'bto_sd_us':sd})
    pd.DataFrame(rawaudit).to_csv(OUT/'mh370_message_audit.csv',index=False)
    spec={'classification':'Davey-model reconstruction with ERA5, public TLE orbit and reconstructed radar mean; not exact Davey reproduction',
          'prior':{'time':18*3600+109,'lat':5.624829,'lon':99.048157,'track':295.66,'mach_uniform':[.73,.84],'bias':152.5},
          'position_sd_deg':.5/60,'observations':observations,'weather':'ERA5_required','magnetic':'wmm2010_grid.npz',
          'provenance':{'source_workbook':str(RAW),'source_workbook_sha256':sha256(RAW),'observation_selection':'Davey Table 10.1; exact raw timestamps; one C-channel reading at each listed epoch, 7-Hz noise not divided by sqrt(N)',
                        'radar_mean':'Earlier refined-v3 notes, reconstructed mean; no exact smoothed radar state available','position_prior':'Chapter 4 0.5 NM interpreted as 0.5 arcminute per coordinate; longitude cos(latitude) discrepancy <1% at initial latitude',
                        'initial_mach':'Chapter 4 uniform 0.73--0.84','initial_altitude':'Reconstruction choice: uniform 25--43 kft in 1000-ft steps','bias_mean':'Published ATSB 152.5 Hz, 25-Hz SD; not re-estimated from final-flight data','afc':'Ashton Figure 11 pilot-error reconstruction through 23:15; ATSB Table 4 -37.7 Hz at 00:11; final BFO excluded','delay':'Recovered v11 full-path constants -495679 R1200 / -491079 R600; public TLE orbit not operator ephemeris'}}
    (OUT/'mh370_davey_era5.json').write_text(json.dumps(spec,indent=2))
    print(pd.DataFrame(rawaudit).to_string(index=False))

if __name__=='__main__':main()
