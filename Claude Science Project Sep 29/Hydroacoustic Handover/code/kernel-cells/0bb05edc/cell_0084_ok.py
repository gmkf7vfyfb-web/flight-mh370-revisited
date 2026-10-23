
def append(rel, text):
    t=rd(rel)
    if not t.endswith('\n'): t+='\n'
    wr(rel, t+'\n'+text)
ENTRY = """## 2026-10-22 — Pete's ruling on source access: blocking labels removed (OPERON session, at Pete's request) -> ALL MODULES

**Ruling (Pete, 22 Oct 2026):** the project has the right to use every source stored in the repo, the Google Drive and the project
source folders. A publisher's access status ("closed access", "paywalled") is not a reason to avoid, discount or mark a source as a gap.

**What went wrong.** A false "closed access / not held (GAP)" label on Metz, Obana & Fukao (2023) blocked the F-35A route for a
fortnight. Pete bought the paper on 9 Oct (artifact 7e4d336f; the 9 Oct 07:40 entry says so), but `hydroacoustics-bibliography.csv`
(7 Oct) kept the old label, the overnight tracks of 21-22 Oct copied it, and they could not look further because their operating note
said never to ask. Also, "Kadri 2019 closed access (G5)" mixed two papers: the JASA 2019 ARA San Juan paper is Dall'Osto's, and
Kadri (2019) is Sci. Rep. 9:912, gold open access. A draft line in the Kadri package ("his own 2019 paper") carried the same mistake.
The module's own 22:00Z entry (track metz-f35a) corrected G4 and G5 and extracted both papers; this entry removes the same labels
from the older notes.

**What changed.** `results/source-access-ledger-2026-10-22.csv` lists every flagged source with its copy status and location (78 rows).
`hydroacoustics-bibliography.csv` no longer has an `open_access` column; it has `copy_status` and `copy_location`. Stale labels were
replaced in this file and in the hydroacoustics notes, the references notes, the JON model-paper list, the satellite register (O10,
O13), the evidence-sweep note on OHASISBIO, the drift note on Durgadoo (open access, CC BY 4.0) and the hydroacoustics brief.
Royer (2016) is held (artifact e6fa6f46), not "not obtained". ATSB First Principles Review is held (artifact 5b08ea64).
Four open-access papers were fetched and filed: Kadri 2019, Williams 2023, Nosov 2007, Chu & Fan 2024.

**Rule from now.** Before writing "not held" about any source, search the artifact store, the Drive, ~/Downloads and the repo (artifact
filenames can be raw DOIs, such as `art%3A10.1007%2F...pdf`), and write the location in the ledger. Never write "closed access" as
a reason for a gap. A source with no copy is "no copy in the project store yet"; say who has to supply it.

**Unchanged, because they are facts and not licence labels:** raw IMS waveforms (H01W, H08S, H08N) are data not held; commercial
archive logins and API keys are credentials; public documents whose hosts refuse scripted downloads (Chu & Fan 2006, Anderson 2018,
DKI574, DNV-RP-F107, MDPI papers) need a browser download by Pete; copyrighted PDFs are not committed to the public repo.
The restricted-source ledger (internal use authorised in full; redistribution settled at the paper's provenance review) is untouched.
-- OPERON session (for Pete)
"""
append('coordination/architecture.md', ENTRY)
append('coordination/HYDROACOUSTICS.md', """## 2026-10-22 — OPERON session (for Pete) -> HYDROACOUSTICS inbox: blocking labels removed from your notes

Pete ruled that closed access is not a blocker (full text in the architecture.md entry of the same date). In your area I replaced the
stale labels: G4 and G5 wording in `hydroacoustics-digitised-sources.md`, `-blackman-validation.md`, `-kadri-package-v2.md`,
`-overnight-2026-10-22-summary.md`, `hydroacoustics-references.md` (the Copyright paragraph and six "Not held (closed)" lines),
`hydroacoustics-bibliography.csv` (column `open_access` -> `copy_status`, `copy_location`), the prior-work critique (Royer is held) and the
brief (San Juan 2019 is Dall'Osto's JASA paper, not Kadri's; the Metz paper is held, only the waveforms remain to be asked).
On `hypothesis/hydroacoustics` the same stale lines in `digitise_brown_2026.py`, `tl_recal_block9.py`, `REQUESTS.txt` (and the exchange
copy `kadri-package-v2/REQUESTS.md`), `data/blackman/extraction_method.txt` and `receiver_observations_diff_vs_drive.csv` were reworded.
One point to reconcile: your 22:00Z entry calls G5 "Kadri 2019 (Sci. Rep.)"; the gap as first written meant the JASA San Juan paper
(Dall'Osto 2019, no copy in the store). Both are now stated in the notes. `REQUESTS.txt` item 2 no longer calls the San Juan paper "his own".
-- OPERON session
""")
append('coordination/PAPER.md', """## 2026-10-22 — OPERON session (for Pete) -> PAPER: RECOMMENDATION 14 — record the held copies in the citation ledger

Pete ruled on 22 Oct 2026 that closed access is not a blocker (architecture.md, same date). `paper/CITATIONS-LEDGER.md` is generated, so
the change belongs in the generator inputs. Copies now held that the ledger shows as '-' or 'candidate': Metz2023 (artifact 7e4d336f,
bought by Pete 9 Oct), Kadri2019 Sci. Rep. 9:912 (artifact 133c4968, gold OA), Williams2023, Nosov2007, ChuFan2024 (artifacts c4f35150,
1ca81b26, 95c75a93, all open access), Royer2016 (artifact e6fa6f46), ATSB First Principles Review (artifact 5b08ea64). The full list is
`results/source-access-ledger-2026-10-22.csv`. In `paper/JON-MODEL-PAPERS.md` the three Journal of Navigation particle-filter papers now read
"no copy in the project store" instead of "closed access"; Pete can supply them. Priority: low.
-- OPERON session
""")
print(len(rd('coordination/architecture.md').splitlines()))
