import inspect
src2c=src2b.replace(" Sea-floor maps do not use any hydroacoustic result. C1, C2.\")"," Sea-floor maps do not use any hydroacoustic result.\")")
assert src2c!=src2b and 'C1, C2' not in src2c
print(re.findall(r'def chart2\([^)]*\)',src2c))
exec(src2c)
print(inspect.signature(chart2))