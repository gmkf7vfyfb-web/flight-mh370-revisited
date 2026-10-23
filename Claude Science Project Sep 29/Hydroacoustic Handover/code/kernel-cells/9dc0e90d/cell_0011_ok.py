ids=['mem_0d4d530892bf','mem_b356d2d6a3d9','mem_458ee4d8dc14','mem_8e514d86a6b4','mem_df92c4ee493a','mem_b39655e78492','mem_0fc441988001','mem_69b29fe84b9a']
import json
r=host.query("SELECT * FROM memories LIMIT 1")
print(r if not isinstance(r,list) else list(r[0].keys()))