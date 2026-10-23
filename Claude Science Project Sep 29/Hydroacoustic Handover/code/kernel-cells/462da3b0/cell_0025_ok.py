for e in ("944f3fe7-24b5-490d-8b7d-140073850a09","26718174-0cba-4f64-a733-1fc7a09f2629"):
    p=host.exec_peek(e); print(p["status"], p["stdout"][-600:])