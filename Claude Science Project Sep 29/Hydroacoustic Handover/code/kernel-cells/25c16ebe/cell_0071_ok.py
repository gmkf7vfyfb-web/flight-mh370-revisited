CPU_PER_DESC = j1["runtime_s"]*12/term["descents"]      # s of CPU, current 3-DOF
STEPS        = float(np.nansum(dur*w)/np.nansum(w))/2.0
CPU_PER_STEP = CPU_PER_DESC/STEPS
SWEEP_DESC   = 127_999_840
print(f"measured: {CPU_PER_DESC*1e6:.0f} us CPU/descent, {STEPS:.0f} steps, {CPU_PER_STEP*1e6:.2f} us CPU/step")
print(f"measured full sweep: {SWEEP_DESC/1e6:.1f} M descents, {SWEEP_DESC*CPU_PER_DESC/3600:.1f} CPU-h "
      f"= {SWEEP_DESC*CPU_PER_DESC/3600/12:.2f} wall-h at 12 threads\n")

opts = {
 # name:                 (step_s, per-step work multiplier lo, hi, extra states)
 "current 3-DOF point mass":            (2.00, 1.0, 1.0),
 "+ asymmetric thrust (trim drag, yaw)":(2.00, 1.2, 1.5),
 "+ bank dynamics and spiral mode":     (0.50, 1.6, 2.2),
 "+ pitch (short-period) dynamics":     (0.10, 2.2, 3.5),
 "full 6-DOF rigid body":               (0.05, 8.0, 25.0),
 "full 6-DOF with control loop":        (0.02, 10.0, 30.0),
}
rows=[]
for nm,(dt,lo,hi) in opts.items():
    for tag,mult in (("low",lo),("high",hi)):
        f = (2.00/dt)*mult
        cpu_h = SWEEP_DESC*CPU_PER_DESC*f/3600
        rows.append([nm, tag, dt, round(f,1), round(cpu_h,1), round(cpu_h/12,2), round(cpu_h/12/24,2)])
C = pd.DataFrame(rows, columns=["model","bound","step_s","cost_factor","sweep_CPU_h","sweep_wall_h_12t","sweep_wall_days_12t"])
print(C.to_string(index=False))

print("\n--- 6-DOF as a REFERENCE generator (not in the sweep) ---")
for n_desc in (10_000, 100_000, 1_000_000):
    for f,tag in ((2.00/0.05*8, "lean"), (2.00/0.05*25, "full")):
        print(f"  {n_desc:>9,} descents, {tag:5s}: {n_desc*CPU_PER_DESC*f/3600:8.1f} CPU-h "
              f"= {n_desc*CPU_PER_DESC*f/3600/12:7.2f} wall-h at 12 threads")
print("\n--- the fit itself: one likelihood evaluation over all ten Boeing traces ---")
trace_s = 10*500
for f,tag in ((2.00/0.05*8,"lean"),(2.00/0.05*25,"full")):
    per_eval = (trace_s/0.05)*CPU_PER_STEP*(f/(2.00/0.05))
    print(f"  {tag:5s}: {per_eval:.2f} CPU-s per evaluation; "
          f"1e4 evals = {per_eval*1e4/3600:.1f} CPU-h; leave-one-out x11 = {per_eval*1e4*11/3600:.0f} CPU-h")
