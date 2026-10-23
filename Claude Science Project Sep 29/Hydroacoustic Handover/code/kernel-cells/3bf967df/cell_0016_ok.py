msg=("Steer from Pete (18 Oct): the Haixun 01 position is a SENSITIVITY case only - do not force the test onto it. The primary locality is Kadri's 306.18 deg bearing "
     "at its sea-level 7th-arc crossing (25.732 S 101.369 E) and the simulated run J impacts the evidence selects along/near that bearing. Report Haixun-centred numbers "
     "as a secondary sensitivity line, not as a co-equal centre. Everything else in your task stands.")
for f in ["d6b79a76-addc-42aa-84ad-897b9904c0cb","e930c577-74fa-4f4d-b81c-c962d137f24d","4269d1df-ffcc-40cf-8117-42a877fd560c","dd09f6cf-91d2-4095-b2da-afbc68935f9a"]:
    print(host.send_message(f,msg))