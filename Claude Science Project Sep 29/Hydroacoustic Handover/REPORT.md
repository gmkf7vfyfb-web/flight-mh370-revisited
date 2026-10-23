# Hydroacoustics: handover report (23 Oct 2026)

*ASD-STE100 for work-specific text; standard statistical terms as they are. Every number below comes from a file in this package,
the registry, or the session records. Ids in brackets point to `errors/error_register.json`.*

## 1. What this report covers

- 46 Claude Science sessions worked on hydroacoustics from 7 to 23 Oct 2026: 11 root threads and 35 sub-agent tracks
  (`sessions/sessions_index.json`). Recorded models: {'claude-opus-5-5': 30, 'claude-opus-5': 4, 'claude-fable-5-1': 11, 'claude-sonnet-5-5': 1}.
- The worst period was 21-22 Oct: one module thread started 17 sub-agent tracks (11 overnight on Fable 5.1, 6 the next morning on
  Opus 5.5), then a critical-review thread (Opus 5.5) found many defects and made new ones. Pete withdrew candidates A-F on 23 Oct.
- On 23 Oct one session (a6559afa, Opus 5.5) did the clean-up that Pete approved: registry, checks in code, detection register,
  corrected notes, brief and profile, and this handover.

## 2. The errors, by class

The register has 137 entries: 19 registry defects (R), 50 automated reviewer findings (A), 28 errors that Pete
reported (P), 23 errors of the 23 Oct sessions (S), 17 errors that the independent verifier found in the clean-up and the overnight run (V). One error can appear in more than one source. The classes:

| class | what happened | examples (ids) |
|---|---|---|
| Sources blocked by false labels | Held papers (Metz 2023, Kadri 2019) were labelled "closed access" after one failed download; later tracks copied the label; the overnight run used a coupling value 10.3 dB low as a result | P-05, P-09, P-10, R-D12 |
| Work without the data | stand-in noise and second-hand numbers used without approval; work started without the inputs | P-12, R-D06 |
| Instructions not kept | test on the digitised panels (said more than once); compute estimates before any run; no conservative thresholds | P-01, P-04, P-07 |
| Definitions not read | files, columns and layers used by name (the flight-only Pleiades layer used as conditional; band columns) | P-18, P-20, R-D09 |
| Physically impossible inputs kept | bands below the receiver pass band; a no-information receiver; airgun shots; land paths; coupling above 1 | R-D02, R-D03, R-D04, R-D08 |
| Known events not removed | Kadri's text time is time-consistent with Royer's icequake A; caption time 6 s from Royer event 5 | R-D07 |
| Corrections not propagated | the old coupling value and the old IMOS table stayed in downstream products after correction | R-D01, R-D22 |
| Certainty without uncertainty | "recorded no signal"; "no detection, chance level, all on searched seabed, I am confident"; point estimates for areas | P-02, P-21, R-D24 |
| Charts that do not show the claim | coincident signals claimed but not visible; predicted and observed curves orthogonal | P-06, P-17, P-24 |
| Unsupported claims about other researchers | Kadri's crash-panel times stated as minutes off, from an exploratory model | P-13, P-28, R-D13 |
| Agent proposals recorded as Pete's rules | "one sequential track" went from an agent offer to "Pete requires" through a summary and memory | P-25, S-01 |
| Reviewer-caught factual slips | 50 findings, for example misquoted gap statuses, wrong checksums in a note, a wrong physics comment | A-01 ... A-50 |
| Errors in the clean-up itself | wrong reason text on 2,779 pair and 195 triple flags; a defect not linked to two items; a coupling range that left out the f^-4 value; overstated identity of v3 and v2; two certainty statements; a timing dependence not stated; provenance slips | V-01 ... V-08; overnight V-09 ... V-17 |
| Operational | 11 parallel conversations used about 42 % of Pete's weekly limit; concurrent commits overwrote a coordination file; disk use about 70 GB | P-11 |

## 3. Root causes

1. Definitions of files, columns, layers, bands and constants were spread over many READMEs, notes and papers. Agents guessed meanings from names.
2. Physical and wording rules were prose in long prompts, not code. Nothing stopped a bad result before it reached Pete.
3. Very long threads (one has 3,413 messages), compaction summaries and parallel tracks lost caveats and Pete's instructions, and changed a proposal into a rule.
4. The brief and profile were large and had rules that conflict ("keep going, do not ask" against "estimate first, wait for approval; stop if data is missing").
5. The same agent checked its own work. The review thread made errors of the same kind as the work it reviewed.
6. Methods were applied to MH370 before they were validated on known events (real arrivals).

The same classes of error occurred on Fable 5.1 and on Opus 5.5 (section 1), so the causes are structural, not one model.

## 4. What the 23 Oct clean-up did

| item | result | where |
|---|---|---|
| Registry | 80 entries (CURRENT 42, CURRENT_WITH_CAVEATS 23, KNOWN_DEFECT 5, PENDING_RULING 2, SUPERSEDED 3, UNCHECKED 3, WITHDRAWN 2), 10 constants, 19 defects; sha256 for 10,341 files (78.4 GB); definitions extracted from cited lines by code; 0 build errors; `check_registry.py --verify` 0 differences | module branch 5d2960d `registry/` |
| Checks in code | band, receiver, airgun-shot label with shot-subtraction residual, land path (GEBCO 2026), Royer known events, impact time, coupling; 9 tests reproduce the Take 2 counts (the 2 Royer tests need `HYDRO_ART` and skip without it) | `prepare/gates/` |
| Detection register | singles 184, pairs 3,321, triples 12,331; rows with no flag: 38 / 10 / 2 (no flag is not a detection claim). Coupling not assessed: pairs 2,577 infinite coupling (Scott Reef 3250), 202 NaN, 119 no arc locus; triples 11,850 no locus, 195 NaN | `mh370-exchange/hydroacoustics/register-2026-10-23/` |
| Kadri package | v2 KNOWN_DEFECT, not to be sent; v3 draft predictions (corrected IMOS table, 2.26e-3 column pending ruling; IMS rows differ from v2 only in `labels`; IMOS TL change q05/q50/q95 -26.9/0.0/+10.7 dB); errata for the v2 text | `kadri-package-v3-draft-predictions/` |
| Notes | 13 notes carry a one-line status banner; 3 hits in CURRENT notes reviewed, no change needed | `results/hydroacoustics/INDEX.md` |
| Brief | coupling paragraph corrected (D18); registry and data rules added at the top | `threads/master-prompts/hydroacoustics.md` |
| Profile | HYDROACOUSTIC_MODULE prompt replaced (8,378 to 4,804 characters); old and new text saved | `results/hydroacoustics/profile-prompt-*` |
| Pete's rulings | 52 quotes, each checked as an exact substring of his message | `results/hydroacoustics/decisions.md` |
| Memory | 15 project memory rows with known-wrong claims replaced; 418 hydro rows exported before the change | private archive `memory/` |

## 5. Independent verification

A separate sub-agent (frame e5e68baf) checked the clean-up twice (`verification/VERIFICATION.md`). Pass 1 reproduced the core numbers
from raw files and found 8 errors (V-01 to V-08). Pass 2, against module be85de9 and work f2a2b5c, found 6 FIXED and 2 PARTLY, with no
regression. The small residuals from pass 2 were then fixed (module 394707d, work 27de2ee), except one: line 171 of the Metz note
keeps the old range text, because notes are not rewritten. INDEX lists that line as STALE. Pass 3 was not run.
The verifier is the same model family as the clean-up agent, so it is independent in context, not in model.

## 6. What holds and what is open

Holds (checked in this run and by the verifier, `verification/`):
- The Take 2 counts that the tests target (35 and 1,111 rows below band; 63, 2,584, 11,067 Scott Reef rows; 44 of 47 airgun coincidences; 201 of 2,000 land points).
- The Kadri v3 predictions have the same 1,720 keys as v2. On IMS rows only the `labels` column differs; 36 IMOS columns change (new IMOS table).
  The 2.26e-3 column is 10.3 dB (1,035 rows) or 10.4 dB (240 rows, rounding) above the 2.1e-4 column; the exposure ratio is 10.7619.
- Every Pete quote in decisions.md is exact.

Open (rulings for Pete; `proposals.md`): adopt 2.26e-3 as the F-35A point (X02); the coupling prior bounds (X03; the upper bound 1e-2 truncates the F-35A one-factor range, D20); the energy ladder (X01);
the shot window and Royer tolerances (X04, X05). Open science (next work cards): validate the detector and timing on real arrivals
(Royer events, CMST 01:34) (X06); search all held IMOS records (X07); San Juan test (X08); amplitude-aware likelihood (X09);
pre-registered crash-panel timing test (X10); Kadri package text (X12); source-depth sensitivity (X16); Curtin background data (X17).

The withdrawal notice of 23 Oct (artifact 269947b9) states: "No impact signal is identifiable in the records held. This is not a claim
that no signal exists." This report adds no new detection statement. The detector has not been validated on real long-range arrivals
(D05) and coupling is not calibrated, so no absence statement with stated power exists yet.

## 7. Limits of this package

- The error register is complete for the registry defects and the reviewer findings in the 46 transcripts. The P- entries are the errors
  Pete named in his messages; the S- entries are those found in this session. Errors that nobody noticed are not in it.
- Transcripts, tool outputs, memory and licensed PDFs are in the private archive only.
- The kernel-cell log may be incomplete for the earliest sessions; the transcripts hold every tool-call input.
