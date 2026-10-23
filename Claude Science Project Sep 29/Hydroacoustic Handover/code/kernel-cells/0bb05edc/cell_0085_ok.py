
sub('coordination/architecture.md',"the overnight tracks of 21-22 Oct copied it, and they could not look further because their operating note\nsaid never to ask.","the overnight tracks of 21-22 Oct copied it, and their operating note told them to record gaps and not to ask, so\nthe label passed through unchallenged.")
cnt=collections.Counter(r['copy_status'] for r in LED)
md=["# Source access ledger — 22 October 2026","",
"Prepared at Pete's request (22 Oct 2026). Pete's ruling: the project has the right to use every source stored in the repo, the Google Drive and the project source folders; a publisher's access status is not a reason to avoid a source. This ledger records, for every source that had a blocking label, whether a copy is held and where. The machine-readable table is `source-access-ledger-2026-10-22.csv` (78 rows).","",
"## Counts","","| copy status | rows |","|---|---|"]
for k,v in cnt.most_common(): md.append(f"| {k} | {v} |")
md+=["","## Labels that were wrong (copy held, or open access)","","| id | source | copy status | where | label removed |","|---|---|---|---|---|"]
for r in LED:
    if r['id'].startswith('L'):
        md.append(f"| {r['id']} | {r['source'][:95]} | {r['copy_status']} | {r['copy_location'][:150]} | {r['previous_label'][:110]} |")
md+=["","## Still without a copy in the project store (no licence block; a PDF has to be supplied)","",
"Load-bearing for current notes (supply first): Duncan & Dall'Osto (2023, JASA abstract only; the lay-language paper is held), Prario (2023), Dall'Osto (2019, JASA, San Juan), Blackman et al. (2004, JASA; the companion UCRL report is held), Heaney (2017), Arons (1954), Chapman (1988), Taylor (1921), LaCasce (2008). Public documents that need a browser download because the host refuses scripted clients: Chu & Fan (2006), Anderson (2018), DKI574, DNV-RP-F107, MDPI papers (Hao 2024 and the 2025 sub-aperture paper). The three Journal of Navigation particle-filter papers are paywalled; they are listed in `paper/JON-MODEL-PAPERS.md` as metadata only. All other rows in the CSV are background references (`known reference`, `metadata only`) that no note relies on for a number.","",
"## Not labels (unchanged)","",
"- Raw IMS waveforms at H01W, H08S and H08N: data not held; access is through the CTBTO vDEC or a national data centre.",
"- Commercial archive logins and API keys (Space-Track, USGS M2M, DLR, Maxar, Planet, SI Imaging, Bhoonidhi, CNES): credentials, to be added in Customize > Credentials where wanted.",
"- Copyrighted PDFs are used internally but not committed to the public repo; the restricted-source ledger (`results/restricted-sources-ledger.md`) is untouched.","",
"## How the Metz label arose","",
"1. 7 Oct: the literature-review track of the hydroacoustics thread wrote `open_access=closed`, read level `secondary only` in `hydroacoustics-bibliography.csv`.",
"2. 9 Oct ~03:00 and ~05:00 UTC: the module thread wrote 'closed and not held' and 'unobtainable' in architecture.md after one fetch tool run and one web search; at ~06:50 and ~07:40 it corrected itself ('Pete is buying', then 'in hand'). Its own references note was fixed ('Obtained: publisher PDF purchased by Pete').",
"3. 21-22 Oct: the bibliography was never corrected, so the overnight tracks (digitisation, TL recalibration, Kadri package) copied 'closed access, not held' into their notes, and the parent summary carried it into architecture.md and HYDROACOUSTICS.md. The paper was in the artifact store the whole time as `art%3A10.1007%2Fs00024-022-03117-6.pdf` (a raw-DOI filename), which a title search does not find.",
"4. 22 Oct: the metz-f35a track corrected G4/G5 and extracted both papers; this ledger and the edits remove the remaining labels.",""]
open('source-access-ledger-2026-10-22.md','w').write('\n'.join(md))
shutil.copy2('source-access-ledger-2026-10-22.md', os.path.join(P,'results/source-access-ledger-2026-10-22.md'))
print('\n'.join(md[:14]))
