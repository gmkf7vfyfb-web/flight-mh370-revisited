import subprocess, sys
N=int(sys.argv[1]); cmd=sys.argv[2:]
ps=[subprocess.Popen(cmd+[str(i),str(N)],stdout=open(f"/tmp/shard_{i}.log","w"),stderr=subprocess.STDOUT) for i in range(N)]
rc=[p.wait() for p in ps]; print("return codes",rc)
