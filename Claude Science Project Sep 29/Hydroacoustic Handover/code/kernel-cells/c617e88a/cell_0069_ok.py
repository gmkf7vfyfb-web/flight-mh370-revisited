r=host.exec_peek("efb2b7fc-2902-4fcf-9daf-c18243689983"); print(r["status"], r.get("elapsed_s"), r["stdout"][-1500:], r["stderr"][-800:])
print(host.get_local_compute_stats()["machine"])