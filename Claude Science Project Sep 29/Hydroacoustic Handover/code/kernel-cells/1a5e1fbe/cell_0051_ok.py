print(re.findall(r'https?://[^\s]*jacc[^\s]*',j)[:5]); print(re.findall(r'web\.archive\.org[^\s]*',j)[:5])
z_names=[n for n in names]; print(z_names[:3])
print([x for x in z.namelist() if not x.endswith('.pdf')][:5])