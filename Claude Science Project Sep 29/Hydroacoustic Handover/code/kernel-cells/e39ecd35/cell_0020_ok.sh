cd src && python3 -c "
t=open('easa_tcds_777.txt').read().split('\n===PAGE===\n')
import re
blk=t[8]
i=blk.find('Maximum Operating Altitude')
print('--- p9 ---'); print(blk[max(0,i-1500):i+300])
"