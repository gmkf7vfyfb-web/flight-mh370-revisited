print(type(S)); 
try: print({k:(S[k].shape,S[k].dtype) for k in S.files})
except Exception as e: print(list(S.keys()) if hasattr(S,'keys') else e)
print('H01W',rx['H01W'],'3274',rx['3274'])
print(t1.columns.tolist()); print(t1[t1.time_utc=='00:49:58'].to_string())
import os; print(os.listdir('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/geometry/'))