"""Download 6-10 March 2014 vertical waveforms + StationXML for island/coastal stations.
Tries EarthScope first, then GEOFON, then EPOSFR (RESIF). One file per station-day."""
import os, sys, json, warnings
from concurrent.futures import ThreadPoolExecutor
from obspy import UTCDateTime as U
from obspy.clients.fdsn import Client
warnings.filterwarnings('ignore')
WANT_PASS1={'II.COCO':'10.BHZ','II.DGAR':'10.BHZ','AU.XMIS':'.BHZ','AU.XMI':'.BHZ','G.AIS':'00.BHZ','G.PAF':'00.BHZ','G.CRZF':'00.BHZ',
'G.ROCAM':'00.HHZ','MR.MRIV':'.HHZ','G.RER':'00.BHZ','PF.RER':'90.HHZ','II.MSEY':'10.BHZ','GE.KAAM':'.HHZ','GE.HMDM':'.HHZ','II.PALK':'10.BHZ',
'GE.MNAI':'.HHZ','GE.CISI':'.HHZ','GE.UGM':'.HHZ','GE.JAGI':'.HHZ','GE.PLAI':'.HHZ','GE.SOEI':'.HHZ','GE.MMRI':'.HHZ',
'S1.AUCAR':'.HHZ','S1.AUALB':'.HHZ','AU.GIRL':'.BHZ','IU.NWAO':'10.HHZ','IU.MBWA':'10.BHZ'}
WANT={'G.ROCAM':'00.HHZ','G.CRZF':'00.BHZ','PF.RER':'90.HHZ','GE.KAAM':'.BHZ','GE.HMDM':'.BHZ','GE.MNAI':'.BHZ','GE.CISI':'.BHZ','GE.UGM':'.BHZ','GE.JAGI':'.BHZ','GE.PLAI':'.BHZ','GE.SOEI':'.BHZ','GE.MMRI':'.BHZ'}
# pass 2 (pass 1 targets above; EPOSFR alias not live, GE HHZ not archived for 2014)
DCS=['EARTHSCOPE','GEOFON','RESIF']
clients={}
def cl(n):
    if n not in clients: clients[n]=Client(n,timeout=300)
    return clients[n]
days=[U('2014-03-06')+86400*i for i in range(5)]
log=[]
def job(key):
    net,sta=key.split('.'); loc,cha=WANT[key].split('.')
    out=[]
    for dc in DCS:
        try:
            if not os.path.exists(f'data/resp/{key}.xml'):
                inv=cl(dc).get_stations(network=net,station=sta,location=loc or '--',channel=cha,starttime=days[0],endtime=days[-1]+86400,level='response')
                inv.write(f'data/resp/{key}.xml',format='STATIONXML')
            ok=0
            for d in days:
                fn=f'data/raw/{key}.{loc}.{cha}.{d.strftime("%Y%m%d")}.mseed'
                if os.path.exists(fn): ok+=1; continue
                try:
                    st=cl(dc).get_waveforms(net,sta,loc or '--',cha,d-60,d+86400+60)
                    st.write(fn,format='MSEED'); ok+=1
                except Exception as e: out.append(f'{key} {dc} {d.date} {type(e).__name__}')
            out.append(f'{key} {dc} days_ok={ok}')
            if ok>0: return out
        except Exception as e:
            out.append(f'{key} {dc} meta {type(e).__name__} {str(e)[:80]}')
    return out
with ThreadPoolExecutor(8) as ex:
    for r in ex.map(job, list(WANT)): 
        for l in r: print(l, flush=True)
