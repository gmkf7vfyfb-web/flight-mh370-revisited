import re, inspect
src=inspect.getsource(power_fig)
src=src.replace('loc="center right")','loc="lower left")').replace('bottom=0.30','bottom=0.28')
src=src.replace('f"The data held can give a weak result at most; raw H01W and H08S recordings would often give a moderate or strong one ({optname})"',
 'f"With the data held the test usually stays within noise; raw H01W and H08S recordings would give |ln R| ≥ 1 about half the time ({optname})"')
src=src.replace("the event list from H01W is incomplete","the H01W event list is probably incomplete")
exec(src); fig=power_fig(p,"r600-bto-only","00:19 R600 BTO Only")