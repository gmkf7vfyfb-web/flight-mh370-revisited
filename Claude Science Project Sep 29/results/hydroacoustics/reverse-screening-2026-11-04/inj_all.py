import subprocess, sys, time
RS=sys.argv[1]; NREP=sys.argv[2]
for st in ["IMOS3275","IMOS3274","IMOS3250","IMOS3315","IMOS3376"]:
    t=time.time()
    r=subprocess.run([sys.executable,RS+"/code/shard.py","14",sys.executable,RS+"/code/inj_imos.py",RS,st,NREP],capture_output=True,text=True)
    print(st,r.stdout.strip(),round(time.time()-t),flush=True)
