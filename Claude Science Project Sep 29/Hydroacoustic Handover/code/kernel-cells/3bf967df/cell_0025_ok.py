msg=("Data warning from the coordinator: the end-of-flight note says impact times are seconds after T0 = 1394232081, but run-j run.json carries "
     "T0_unix_s = 1394236800 (00:00:00 UTC 8 Mar 2014), and only that origin gives physical impact times (waypoints rows near 25.7 S: median about 00:27-00:31, "
     "flameout median about 00:18). Use run.json T0_unix_s for t_impact_s and every t_*_s column; if you already used 1394232081, recompute.")
for f in ["d6b79a76-addc-42aa-84ad-897b9904c0cb","e930c577-74fa-4f4d-b81c-c962d137f24d","4269d1df-ffcc-40cf-8117-42a877fd560c","1f938cf5-20bc-4aee-ba61-9768284cbcb2","dd09f6cf-91d2-4095-b2da-afbc68935f9a"]:
    print(host.send_message(f,msg)['status'])