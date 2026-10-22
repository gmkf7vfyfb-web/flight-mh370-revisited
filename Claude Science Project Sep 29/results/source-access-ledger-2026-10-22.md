# Source access ledger — 22 October 2026

Prepared at Pete's request (22 Oct 2026). Pete's ruling: the project has the right to use every source stored in the repo, the Google Drive and the project source folders; a publisher's access status is not a reason to avoid a source. This ledger records, for every source that had a blocking label, whether a copy is held and where. The machine-readable table is `source-access-ledger-2026-10-22.csv` (78 rows).

## Counts

| copy status | rows |
|---|---|
| not retrieved — ask Pete | 68 |
| FETCHED (22 Oct 2026) | 4 |
| HELD | 3 |
| HELD (later revisions only) | 1 |
| OPEN; copy location not confirmed | 1 |
| LANDING PAGE ONLY | 1 |

## Labels that were wrong (copy held, or open access)

| id | source | copy status | where | label removed |
|---|---|---|---|---|
| L01 | Metz, Obana & Fukao (2023) Remote hydroacoustic detection of an airplane crash, Pure Appl. Geop | HELD | artifact 7e4d336f-aeb4-4369-b709-570cf133c7a4 (since 9 Oct 2026); ~/Downloads/art%3A10.1007%2Fs00024-022-03117-6.pdf; ~/Downloads/mh370-exchange/hydro | closed; not held (GAP); unobtainable; secondary only |
| L02 | Royer (2016) OHASISBIO report LDO-201608 (Search for the flight MH370 impact site in the Indian | HELD | artifact e6fa6f46 / 4a46c695 (royer-2016-LDO-201608.pdf); ~/Downloads/mh370-exchange/hydroacoustics/run-j-digitisation/sources/royer-2016-LDO-201608.p | not obtained; not public in a citable repository; secondary only (news, blogs) |
| L03 | Kadri (2019) Effect of sea-bottom elasticity on the propagation of acoustic-gravity waves from  | FETCHED (22 Oct 2026) | artifact 133c4968-4c14-4416-ace2-e44f16670a84; ~/Downloads/mh370-exchange/hydroacoustics/sources/open-access-fetched-2026-10-22/ | 'Kadri 2019 JASA, closed access (G5)' - a misattribution: the JASA paper is Dall'Osto (2019); this Sci. Rep. p |
| L04 | Dall'Osto (2019) Source triangulation utilizing three-dimensional arrivals: application to the  | not retrieved — ask Pete | abstract only (fetch 22 Oct 2026: no open location) | filed as 'Kadri 2019 (ARA San Juan)', closed access, GAP G5 |
| L05 | Williams et al. (2023) On the propagation of acoustic-gravity waves due to a slender rupture in | FETCHED (22 Oct 2026) | artifact c4f35150-c9c5-4d7b-bd70-53d98df38c19; exchange open-access-fetched-2026-10-22/ | gold OA; read level snippet |
| L06 | Nosov et al. (2007) Elastic oscillations of water column in the 2003 Tokachi-oki tsunami source | FETCHED (22 Oct 2026) | artifact 1ca81b26-0a34-4444-87de-b24b84ea2800; exchange open-access-fetched-2026-10-22/ | read level abstract/secondary |
| L07 | Chu & Fan (2024) Global climatological dataset of undersea acoustic parameters from WOA 2023, S | FETCHED (22 Oct 2026) | artifact 95c75a93-ed7c-4dd4-a490-4940bfc46d2a; exchange open-access-fetched-2026-10-22/ | read level secondary (Brown2026) |
| L08 | ATSB (Dec 2016) MH370 - First Principles Review / Search and debris examination update | HELD | artifact 5b08ea64 (atsb_first_principles_review_dec2016.pdf); Drive 1gHUVNMzjnh0LSD_LqOjzGGMiRuo_nzaq (Search and debris examination update, 2 Nov 201 | search snippet only; satellite register O13: not retrieved, not on Drive, ATSB site unreachable |
| L09 | ATSB Definition of Underwater Search Areas (AE-2014-054), later revisions | HELD (later revisions only) | artifacts 7203665a (3 Dec 2015) and 5af6ca76 (30 Jul 2015); Drive 1lDHdjQhdoyiqRIck6Gkmdyur7g1ua_Lw (30 Jul 2015) | search snippet only |
| L10 | Durgadoo et al. (2021) J. Oper. Oceanogr. 14(1):1-12 | OPEN; copy location not confirmed | drift thread read it from nora.nerc.ac.uk (memory record); no file in the artifact store under that name | not open access; not re-read |
| L11 | Renzi & Dias (2014) Hydro-acoustic precursors of gravity waves, JFM 754:250-262 | LANDING PAGE ONLY | Drive 1nHzJ3h-IcsCkTzvTJwYK0V7-A20F-BHE (Cambridge abstract page printout, not the paper) | closed; metadata only |

## Not retrieved — ask Pete (a PDF has to be supplied; this is not a licence block)

Load-bearing for current notes (supply first): Duncan & Dall'Osto (2023, JASA abstract only; the lay-language paper is held), Prario (2023), Dall'Osto (2019, JASA, San Juan), Blackman et al. (2004, JASA; the companion UCRL report is held), Heaney (2017), Arons (1954), Chapman (1988), Taylor (1921), LaCasce (2008). Public documents that need a browser download because the host refuses scripted clients: Chu & Fan (2006), Anderson (2018), DKI574, DNV-RP-F107, MDPI papers (Hao 2024 and the 2025 sub-aperture paper). The three Journal of Navigation particle-filter papers are paywalled; they are listed in `paper/JON-MODEL-PAPERS.md` as metadata only. All other rows in the CSV are background references (`known reference`, `metadata only`) that no note relies on for a number.

## Reworded on Pete's instruction (22 Oct 2026)

- Raw IMS waveforms at H01W, H08S and H08N, and the commercial archive logins and API keys (Space-Track, USGS M2M, DLR, Maxar, Planet, SI Imaging, Bhoonidhi, CNES): now "not retrieved — ask Pete". IMS access is through the CTBTO vDEC or a national data centre; archive access needs an account or key (Customize > Credentials).
- Kept on Pete's instruction: the "DO NOT USE: fig10-3-bfo-latitude-pdf.csv (superseded)" lines in the coordination inboxes and the "Do not use these maps for a search" captions in the composer figure scripts.
- Not touched: generated products that carry "not held" as a category (arrival-window matrix and its README, run J levels table) and the module's own acoustic-path terms ("blocked path", "blockage"), because changing them means regenerating charts or changing a computed result.
- Copyrighted PDFs are used internally but not committed to the public repo; the restricted-source ledger (`results/restricted-sources-ledger.md`) is untouched.

## How the Metz label arose

1. 7-8 Oct: the literature-review sub-task (frame 43360090) of the thread "Hydroacoustic Module Initialization" (frame d74bf70e) wrote `open_access=closed`, read level `secondary only` in `hydroacoustics-bibliography.csv`.
2. 9 Oct ~03:00 and ~05:00 UTC: the same thread ("Hydroacoustic Module Initialization") wrote 'closed and not held' and 'unobtainable' in architecture.md after two automated fetches and one web search; at ~06:50 and ~07:40 it corrected itself ('Pete is buying', then 'in hand'), and its references note was fixed ('Obtained: publisher PDF purchased by Pete').
3. 21-22 Oct: the bibliography was never corrected, so the overnight tracks run from the thread "Hydroacoustic Module Brief Review" (frame 676a6e64) — digitisation (block 1, frame 7adf9568), TL recalibration (block 9, frame 02f53ca7) and Kadri package (block 12, frame 1814d527) — copied 'closed access, not held' into their notes, and the parent summary carried it into architecture.md and HYDROACOUSTICS.md. The paper was in the artifact store the whole time as `art%3A10.1007%2Fs00024-022-03117-6.pdf` (a raw-DOI filename), which a title search does not find.
4. 22 Oct: the metz-f35a track (same thread) corrected G4/G5 and extracted both papers; this ledger and the edits remove the remaining labels.
