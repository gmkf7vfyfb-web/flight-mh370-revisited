import importlib.metadata as im_, hashlib, sys
vers={p:im_.version(p) for p in ["pypdfium2","Pillow","pandas","numpy"]}
pdfsha=hashlib.sha256(open(pdfp,"rb").read()).hexdigest(); txtsha=hashlib.sha256(open("repo/ISO Sept 28 Status/inputs/papers/hydroacoustics/ucrl-tr-207323.txt","rb").read()).hexdigest()
spd=hav(*A4s,*A3)/((tsec("10:54:57.77")-tsec("10:23:11.56"))/3600)
print(vers, sys.version.split()[0], pdfsha[:16], txtsha[:16], round(spd))