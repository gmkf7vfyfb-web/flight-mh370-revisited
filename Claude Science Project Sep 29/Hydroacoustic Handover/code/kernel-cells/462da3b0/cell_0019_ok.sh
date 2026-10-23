python3 -c "
import json; d=json.load(open('handoff/module_cells.json'))
for k in ['1576','1578','1580','1588']: print('#####',k); print(d[k])
"