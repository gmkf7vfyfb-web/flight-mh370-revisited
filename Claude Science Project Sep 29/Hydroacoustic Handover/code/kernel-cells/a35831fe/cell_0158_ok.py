print([n for n in globals() if 'cov' in n.lower() or 'field' in n.lower() or n in ('FLD','FF','SF','sf')])
try: print(inspect.getsource(cov_at))
except Exception as e: print(e)