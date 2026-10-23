cd "audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/data/ims_response_2003"; ls -la; python3 -c "
from obspy import read_inventory
import numpy as np
for n in ['H01W1','H08S1','H08N1']:
    inv=read_inventory(n+'_2003.xml'); ch=inv[0][0][0]
    f=np.array([5,10,20,40,63.])
    r=np.abs(ch.response.get_evalresp_response_for_frequencies(f,output='DEF'))
    print(n, ch.start_date, ch.end_date, ch.response.instrument_sensitivity.value, ch.response.instrument_sensitivity.input_units, np.round(r,1))
"