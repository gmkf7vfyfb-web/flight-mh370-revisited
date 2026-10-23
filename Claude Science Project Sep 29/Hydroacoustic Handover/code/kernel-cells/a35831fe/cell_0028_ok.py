import glob
T0=1394236800  # 2014-03-08 00:00:00 UTC
base='/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/'
held={}
for lg,d in [('3315','MH370/3315_PerthCanyon'),('3376','MH370/3376_PerthCanyon'),('3250','MH370/3250_ScottReef'),('3274','Portland_MH370/3274_Portland'),('3275','Portland_MH370/3275_Portland')]:
    fs=sorted(glob.glob(base+d+'/*.DAT'))
    st=[int(os.path.basename(f)[:8],16)-T0 for f in fs]
    st=[s for s in st if -3600<=s<=3*3600]
    held[lg]=[(s,s+307.3) for s in st]
    print(lg, len(fs), [fmt(s) for s in st][:14])