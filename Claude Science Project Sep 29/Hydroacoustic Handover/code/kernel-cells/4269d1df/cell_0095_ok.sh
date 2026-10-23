python3 - <<'EOF'
s=open('rowcond.py').read()
s=s.replace("""                ok = vm[sel]; r['vec_'+vk] = np.bincount(nid[sel][ok].ravel(), weights=(m[ok, None]*W[sel][ok]).ravel(), minlength=NC); r['den_'+vk] = m[ok].sum()""",
"""                ok = vm[sel]; r['vec_'+vk] = np.bincount(nid[sel][ok].ravel(), weights=(m[ok, None]*W[sel][ok]).ravel(), minlength=NC); r['den_'+vk] = m[ok].sum()
                for fc, fn in ((1, 'A1'), (2, 'A2'), (3, 'B')):
                    okf = ok & (f4[sel] == fc)
                    r[f'vec_{vk}_{fn}'] = np.bincount(nid[sel][okf].ravel(), weights=(m[okf, None]*W[sel][okf]).ravel(), minlength=NC); r[f'den_{vk}_{fn}'] = m[okf].sum()
                    r[f'sum_{fn}'] = m[f4[sel] == fc].sum()""")
open('rowcond2.py','w').write(s)
EOF
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
SEEDSEL=0:12 python rowcond2.py rc2-wp-a.npz run-j-waypoints=0.9982 > rc2-a.log 2>&1 &
SEEDSEL=12:24 python rowcond2.py rc2-wp-b.npz run-j-waypoints=0.9982 > rc2-b.log 2>&1 &
python rowcond2.py rc2-other.npz run-j-free=0.0013 run-j-repro-radar=0.0003 run-j-descent-climb=0.0002 > rc2-c.log 2>&1 &
wait; tail -1 rc2-a.log rc2-b.log rc2-c.log