for e in ["efb2b7fc-2902-4fcf-9daf-c18243689983","104a4faa-f3e7-4330-9166-7f84633d9491"]:
    r=host.exec_peek(e); print(r["status"], r.get("elapsed_s"), r["stdout"][-1500:], r["stderr"][-1500:])