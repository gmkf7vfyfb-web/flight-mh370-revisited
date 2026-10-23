import shutil, subprocess, time
shutil.copy(host.artifact_path('a74cc2b4-988c-4dad-95ff-468f16dfeaff'),'ocean/surface_search_2014.geojson')
t=time.time()
r=subprocess.run(['python','lib/surface_drift.py','ocean/test_cells.npy','ocean/test_drift.npz','0.012'],capture_output=True,text=True)
print(r.stdout[-500:], r.stderr[-1500:], time.time()-t)