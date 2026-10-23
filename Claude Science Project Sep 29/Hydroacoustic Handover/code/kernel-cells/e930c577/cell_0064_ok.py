r=host.exec_peek("f50f8ffc-fbf4-418c-8dcf-8641ffcdc1e9"); print(r.get('status'), str(r.get('stdout'))[-500:])
print(host.get_local_compute_stats())