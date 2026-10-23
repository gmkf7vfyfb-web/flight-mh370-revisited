cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
python - <<'EOF'
p='run_j_windows.py'; s=open(p).read()
old='''        print(f"tasks {len(tasks)} workers {a.workers}", flush=True)
        with ProcessPoolExecutor(a.workers) as ex:
            for s, k, n, dt in ex.map(do_seed, tasks):
                print(f"done {s}/seed-{k} rows {n} {dt:.0f}s", flush=True)'''
new='''        print(f"tasks {len(tasks)} workers {a.workers}", flush=True)
        if a.workers <= 1:
            for tk in tasks:
                s, k, n, dt = do_seed(tk); print(f"done {s}/seed-{k} rows {n} {dt:.0f}s", flush=True)
        else:   # AMENDMENT 1 (22 Oct, plumbing only): the sandbox forbids POSIX semaphores, so ProcessPoolExecutor cannot start;
                # one single-threaded subprocess per seed instead, at most --workers at a time. No value changes.
            import subprocess
            env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
            running = []
            while tasks or running:
                running = [(pr, tk) for pr, tk in running if pr.poll() is None or print(f"ended {tk[0]}/{pathlib.Path(tk[1]).name} rc={pr.returncode}", flush=True)]
                while tasks and len(running) < a.workers:
                    s, sd, o = tasks.pop(0); k = pathlib.Path(sd).name.split("-")[1]
                    cmd = [sys.executable, str(HERE / "run_j_windows.py"), "seeds", "--eof", a.eof, "--out", o, "--workers", "1", "--strata", s, "--seeds", k]
                    running.append((subprocess.Popen(cmd, env=env, stdout=open(out / f"_w_{s}_{k}.log", "w"), stderr=subprocess.STDOUT), (s, sd, o)))
                time.sleep(5)'''
assert old in s; s=s.replace(old,new); s=s.replace("from concurrent.futures import ProcessPoolExecutor\n","")
open(p,'w').write(s)
EOF
python -m py_compile run_j_windows.py && echo OK
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows
time python run_j_windows.py seeds --eof /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j --out $OUT --workers 1 --strata run-j-free --seeds 1 2>&1 | tail -5
ls -la $OUT/run-j-free/