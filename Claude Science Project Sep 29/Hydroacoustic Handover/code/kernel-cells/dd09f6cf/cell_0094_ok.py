txt=open('out/README.md').read().replace('TABLE_ROWS','\n'.join(lines))
open('out/README.md','w').write(txt)
import shutil
for f in ['fig1-seabed-coverage-bearing.png','fig1-seabed-coverage-bearing.pdf','fig2-surface-search-locality.png','fig2-surface-search-locality.pdf','fig3-search-likelihood-terms.png','fig3-search-likelihood-terms.pdf',
          'search-likelihood-terms-summary.csv','search-likelihood-terms-all-cases.csv','surface-search-days-locality.csv','locality-search-summary.json','lib/reduce_kh.py','lib/surface_drift.py','lib/pool_terms.py']:
    shutil.copy(f,'out/'+os.path.basename(f))
print(sorted(os.listdir('out')), 'TABLE_ROWS' in txt.replace('TABLE_ROWS',''))