
t=open('source-access-ledger-2026-10-22.md').read()
t=t.replace("1. 7 Oct: the literature-review track of the hydroacoustics thread wrote `open_access=closed`, read level `secondary only` in `hydroacoustics-bibliography.csv`.",
 "1. 7-8 Oct: the literature-review sub-task (frame 43360090) of the thread \"Hydroacoustic Module Initialization\" (frame d74bf70e) wrote `open_access=closed`, read level `secondary only` in `hydroacoustics-bibliography.csv`.")
t=t.replace("2. 9 Oct ~03:00 and ~05:00 UTC: the module thread wrote 'closed and not held' and 'unobtainable' in architecture.md after one fetch tool run and one web search; at ~06:50 and ~07:40 it corrected itself ('Pete is buying', then 'in hand'). Its own references note was fixed ('Obtained: publisher PDF purchased by Pete').",
 "2. 9 Oct ~03:00 and ~05:00 UTC: the same thread (\"Hydroacoustic Module Initialization\") wrote 'closed and not held' and 'unobtainable' in architecture.md after two automated fetches and one web search; at ~06:50 and ~07:40 it corrected itself ('Pete is buying', then 'in hand'), and its references note was fixed ('Obtained: publisher PDF purchased by Pete').")
t=t.replace("3. 21-22 Oct: the bibliography was never corrected, so the overnight tracks (digitisation, TL recalibration, Kadri package) copied",
 "3. 21-22 Oct: the bibliography was never corrected, so the overnight tracks run from the thread \"Hydroacoustic Module Brief Review\" (frame 676a6e64) — digitisation (block 1, frame 7adf9568), TL recalibration (block 9, frame 02f53ca7) and Kadri package (block 12, frame 1814d527) — copied")
t=t.replace("4. 22 Oct: the metz-f35a track corrected","4. 22 Oct: the metz-f35a track (same thread) corrected")
open('source-access-ledger-2026-10-22.md','w').write(t); shutil.copy2('source-access-ledger-2026-10-22.md', os.path.join(P,'results/source-access-ledger-2026-10-22.md'))
print(t[-1500:])
