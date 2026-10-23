python -c "
import json;o=json.load(open('child_reports.json'))
for k in ['0f0b1c26','31b10b13','1fcb15df']: print('=====',k); print(o[k][-3500:])
"