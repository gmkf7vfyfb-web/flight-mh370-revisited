# the 11 Oct 22:41 stand-in: 2 arms x 4 strata x 4 seeds x 100,000 parents x 4 children x 4 descents, 3 h 11 min at 8 threads
standin_desc = 2*4*4*100_000*4*4
standin_cpu  = (3 + 11/60)*3600*8
print(f"22:41 stand-in: {standin_desc/1e6:.1f} M descents, {standin_cpu/3600:.1f} CPU-h "
      f"-> {standin_cpu/standin_desc*1e6:.0f} us CPU/descent")
print(f"run-i-dive 00:11 baseline:                      -> {CPU_PER_DESC*1e6:.0f} us CPU/descent")
ratio = (standin_cpu/standin_desc)/CPU_PER_DESC
print(f"22:41 integration is {ratio:.2f}x the 00:11 cost per descent\n")
for nm, nd in [("run-I scale (16 children, as run-i-dive)", 127_999_840),
               ("8 children (as run I)", 102_399_904),
               ("4 children x 4 descents, 8 seeds x 4 strata", 4*4*100_000*8*4)]:
    cpu = nd*CPU_PER_DESC*ratio
    print(f"  {nm:44s} {nd/1e6:6.1f} M descents -> {cpu/3600:6.1f} CPU-h = {cpu/3600/12:5.2f} wall-h at 12 threads")
print(f"\nmean 00:11-to-impact flight currently integrated: {STEPS*2:.0f} s")
print("22:41 to a 00:35 median impact:                   ~6,800 s  (6.2x the flight time)")
print(f"but measured cost ratio is only {ratio:.2f}x -> the pre-onset cruise segment is NOT the expensive part")
