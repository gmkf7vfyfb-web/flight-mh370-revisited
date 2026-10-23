cd hydro; grep -rIl -E "D preferred|00:26:22|00:28:38-00:30" . 2>/dev/null | head; cd ../repo; grep -rIl -E "D preferred|00:26:22|00:28:38" . 2>/dev/null | head
cd ..; X=/Users/pete/Downloads/mh370-exchange; python -c "
import numpy as np
z=np.load('$X/hydroacoustics/run-j-searches/geometry/sample.npz'); [print(k,z[k].shape,z[k].dtype,z[k][:3]) for k in z.files]"