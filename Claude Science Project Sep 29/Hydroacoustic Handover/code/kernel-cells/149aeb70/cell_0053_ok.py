exec(open("make_hydro_figs.py").read())
import numpy as np
print("coverage histogram (unblocked loggers):", np.bincount(ncov, minlength=5))
