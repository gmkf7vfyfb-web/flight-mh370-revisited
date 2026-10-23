C=~/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo/seed-1; ls -la $C/handoff-m0011 $C | head -30; gzip -dc $C/handoff-m0011/handoff.toml.gz | head -80; python3 -c "
import numpy as np
h=np.load('$C/handoff-m0011/handoff.npy',mmap_mode='r');print(h.shape,h.dtype);print(np.asarray(h[:3]))
f=np.load('$C/final.npy',mmap_mode='r');print('final',f.shape,f.dtype)"; head -c 2500 $C/diagnostics.json