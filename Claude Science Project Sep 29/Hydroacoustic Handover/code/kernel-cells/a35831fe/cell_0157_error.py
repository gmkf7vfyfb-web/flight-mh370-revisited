import inspect
print(type(fields), list(fields.keys()) if hasattr(fields,'keys') else '')
try: print(inspect.getsource(cov_at))
except Exception as e: print('cov_at src n/a',e)