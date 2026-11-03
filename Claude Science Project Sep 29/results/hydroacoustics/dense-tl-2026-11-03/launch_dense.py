import os, sys
for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[k] = "1"      # one thread per worker; the pool supplies the parallelism
sys.path.insert(0, "./tlchain/tl-chain-2026-10-27")
from tlchain.run import main
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
