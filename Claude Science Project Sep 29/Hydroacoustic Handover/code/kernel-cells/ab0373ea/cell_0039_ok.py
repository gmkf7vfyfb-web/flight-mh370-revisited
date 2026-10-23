time.sleep(1750)
lines = [l for l in open(OUT / "run2.log").read().splitlines() if "ok ram" in l or "failed" in l]
print(proc.poll(), len(lines), lines[-1:])
print(subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip(), subprocess.run(["df", "-k", "/System/Volumes/Data"], capture_output=True, text=True).stdout.splitlines()[-1].split()[3])