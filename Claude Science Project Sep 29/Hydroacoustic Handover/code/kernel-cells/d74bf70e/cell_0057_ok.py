msg = ("Overnight rules from the architecture session (binding until ~08:30 MT): the core 16-hour run is live. "
       "Use at most 4 CPU threads (set OMP_NUM_THREADS=4, no parallel pools wider than 4). Download nothing beyond "
       "the paper PDFs/full texts your task needs (each a few MB); check `df -g .` stays above 25 GiB free; never save "
       "a multi-GB artifact. Do not commit or push. Nobody can answer questions tonight: choose the more reversible "
       "option, label it provisional in your outputs and deviations, and keep going.")
for f in ["95790ff1-95f1-4b29-b51a-bed538c1797b","43360090-fdd3-4918-a664-de9fef7e80f6"]:
    print(host.send_message(f, msg))