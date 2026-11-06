import sys, os; sys.path.insert(0, os.getcwd())
import numpy as np, pandas as pd
from multiprocessing import Pool
import imos_inject as I
I.SNRS = np.array([-300.0])
def f(a): return I.case(a)
if __name__ == '__main__':
    import network14 as N
    jobs = [(lg, 'R1', 900000 + 1000 * i + k) for i, lg in enumerate(N.LOGGERS) for k in range(200)]
    with Pool(16) as p: R = p.map(f, jobs, chunksize=4)
    D = pd.DataFrame([r for rr in R for r in rr]); D.to_csv(os.environ.get('INJ_OUT', 'imos_injections_purenull.csv'), index=False)
    print(D.groupby('station').agg(p01=('p_combined', lambda v: (v < 0.01).mean()), p05=('p_combined', lambda v: (v < 0.05).mean()), p20=('p_combined', lambda v: (v < 0.2).mean()), n=('p_combined', 'size')).round(3).to_string())
    print('all', round((D.p_combined < 0.05).mean(), 4), round((D.p_combined < 0.2).mean(), 4))
