# End of flight: report on the items completed 14–16 Oct 2026

Prepared 16 Oct 2026 for Pete Large. Source notes in the repository (branch `claude-science-sep29`):
`results/eof-item7-dive-prob-oct15/`, `results/eof-item8-round3-oct15/`, `results/eof-order-b-oct15/`, `results/eof-both-burst-oct16/`.
Every figure has two footnotes: one in plain words and one technical. The figures are made from the stored result files by
[make_figs.py]({{artifact:art_aea3bec2-f52f-4ace-8ac2-68cf70cc53ec}}).

## Summary

| Item | What was done | Kind of run | Main result | Status |
|---|---|---|---|---|
| 7 Dive probability | Exact re-weighting of run-i-dive samples over p = 0–1 | Re-weighting of a full run | With both 00:19 frequencies and the transient bias, p moves the 10–45° impact share from 0.04 to 0.87 and the median energy from 1.1 to 10.2 GJ. Latitude and families do not move. | Done; p = 0.5 is the headline (Decision 4) |
| 8 Round-3 descent laws | Full re-run with the round-3 fit | Full run, 4 strata x 8 seeds | Latitude moves at most 0.06°, ln evidence moves −0.20 to −0.02. Steep impacts fall from 0.073 to 0.007. | Done; labelled sensitivity (Boeing gate still failed) |
| (b) 2 Final transmission imposed | Samples on the sea before 00:19:37 removed | Re-weighting of a full run | 13.0 per cent (not 32.8 per cent) of the old held-out weight was impossible. Loud-impact share rises from 0.100 (no 00:19 data) to 0.193 with the transient bias. | Done |
| (b) 3 Bank limit | Bank limit sampled from 52 to 90°, and fixed at 90° | Two full runs, 4 x 8 each | Steep impacts come only from limits above 70°. With the transient bias, a 90° limit raises A1 from 0.10 to 0.58 (Δ ln Z +0.82). | Done; the prior on the limit is a declared choice |
| (b) 4 Uniform onset | Exact onset-only re-weighting (U1), compared with the binned method | Re-weighting of a full run | Planned-descent share, no 00:19 data: 0.108 → 0.098 (U1), or 0.197 (binned). | Done; Pete ruled U1 (16 Oct 02:08Z) |
| Both-burst fix | Aimed selection and 8x descents | Trial run, 1 seed | Neither fix reaches 1,000 effective impacts. | Trial only. Supplementary pass approved for after run J |

## 1. Item 7: the dive probability

![Dive probability]({{artifact:art_ad9a5d49-6507-4bf3-bfe1-8ee550b0450e}})

**Question.** After a push-over, does the aircraft continue to the sea (dive) or level off? Run I assumed that it always levels
off, which is p = 0. Run-i-dive samples both branches equally, with p = 0.5.

**Result.** The latent `pushover_to_surface` is recorded for each row, so any p is an exact re-weighting of the same samples. The three
readings of a uniform prior on p (one coin per trajectory, a hyper-prior, or a global p) give identical results. When no 00:19 data are
used, p moves the 10–45° share only from 0.035 to 0.162. With both 00:19 frequency values and the transient bias (D4), it moves the share
from 0.036 to 0.865, and the median impact energy from 1.06 to 10.19 GJ. The latitude and the family shares do not change.

**Meaning.** Under D4 the impact condition that hydroacoustics needs depends on a parameter that the satellite data do not constrain.
This must be shown as a sensitivity range in the paper, not as one number.

## 2. Item 8: round-3 descent laws

![Round-3 laws]({{artifact:art_f57d5fc6-c34c-4219-a21d-03e79334914d}})

**Question.** Does the round-3 fit to the Boeing traces change the answer?

**Result.** This was a full re-run at run-I scale. The median latitude moves by at most 0.06° for every 00:19 treatment. The change in
ln evidence is −0.20 to −0.02 (held out −0.10), which is small against the differences between the 00:19 treatments. The impact angles do change. Steep
impacts (above 45°) fall from 0.073 to 0.007, because the round-3 bank cap (52.5°) stops the spiral before it becomes steep. Item 3 then
took this up.

**Status.** Labelled sensitivity. The Boeing leave-one-out gate failed in all three rounds, so the uncontrolled-arm dynamics stay
uncalibrated (verbatim caveat in every technical footnote).

## 3. Order (b) item 2: the final transmission imposed on the held-out case

![Transmission imposed]({{artifact:art_2ebb181d-2d9b-4227-a379-fd11503bd497}})

**Question.** The aircraft transmitted at 00:19:37.443. Some held-out samples were already on the sea before that time. How many were
there, and what changes when they are removed?

**Result.** 13.0 per cent of the raw held-out weight was on the sea before 00:19:37. The 32.8 per cent quoted earlier was the weight
with an empty `last_burst` latent: 0.1176 of it on the sea and 0.2099 still in core cruise. The new held-out case D0′ = held out ×
airborne at 00:19:37 × survival. Its shares are A1 0.140, A2 0.341 and B 0.518, the median latitude is −37.16°, and the ESS is
9.78M impacts. For loudness, the threshold is set at the 90th percentile of D0′, so D0′ = 0.100. Using 00:19 data raises the loud
share to 0.119–0.236, and D4/D0′ = 1.93 (not the 3.2 quoted earlier).

## 4. Order (b) item 3: the bank limit in an uncontrolled spiral

![Bank limit]({{artifact:art_c582d419-2d6d-47a1-acdb-0b76ce6024c8}})

**Question.** The fixed 52.5° cap is a gap in the model's reach. An uncontrolled 777 can bank past 60° and up to 90°. What happens when
the limit is sampled?

**Result.** These were two full runs. In the first, the limit is sampled from a mixture: U[52, 63]° with weight 0.8 (Boeing traces 53–60°,
widened over the leave-one-out range) and U[63, 90]° with weight 0.2. In the second, the limit is fixed at 90°. The drawn limit is
recorded, so the tail weight re-weights exactly.
- **Panel a.** Steep impacts come almost entirely from limits above 70°: 0.007–0.010 below 70°, 0.053 at 70–80° and 0.149 at 80–90°.
- **Panel b.** Without 00:19 data the families hardly move (Δ ln Z −0.05 and −0.08). With both frequencies and the transient bias they
  move a lot. A 90° limit gives A1 0.58, against 0.10 at 52.5°, with Δ ln Z +0.82; with cause C2 silent it is +1.03 and A1 0.62.

**Meaning.** Under D4, the family answer depends on how far an uncontrolled 777 can bank. The Boeing traces cannot settle this, so the
paper must state it as a conditional result. Limits above 90° (overbank) are outside the model; this is a declared reach gap.

## 5. Order (b) item 4: a uniform start time for a planned descent

![Onset prior]({{artifact:art_cae0b17a-5633-4b3e-b33d-e83ccbcb5bd4}})

**Question.** Does the planned-descent share depend on when the descent may start?

**Result.** There are two ways to make the start time uniform.
- **U1** changes only the start time and keeps the core posterior. With it, the share falls slightly: D0 0.108 → 0.098, D2 0.077 →
  0.076, D4 0.044 → 0.044.
- **The binned method** doubles the D0 share to 0.197. It does this only because it also re-weights the aircraft's fuel state at 22:41.
  82 per cent of the 22:41 deliberate weight has predicted exhaustion before 00:11, so late bins can only be filled by aircraft with more
  fuel.

**Ruling (Pete, 16 Oct 02:08Z).** U1 is the declared sensitivity, and the binned method is not adopted. The direct 22:41-arm run waits
for run J's end-of-flight pass. "00:11 selects cruise" holds under both onset priors.

## 6. Both-burst sampling fix (trial run only)

![Both-burst trial]({{artifact:art_010b4823-c0fc-4576-938e-6a84d047d269}})

**Trial run, one seed, one stratum: not evidence.**
- Aimed selection raised the both-burst cells (D3, D4) from 228 / 32 to 758 / 683 effective impacts. More descents (256 per parent)
  raised them to 845 / 790.
- Neither fix reached 1,000.
- Aimed selection cost the held-out cell a factor of 4 in ESS. On prior recovery it is marginal: 0.0105 against the 0.0030 standard.
- Agreed plan: a supplementary pass with 256 descents per parent for the both-burst cells, after run J.
- A three-arm check on run J's waypoints hand-off is running now. Base for that stratum: D3 219, D4 252.

## 7. Coverage

- **(a) Feasible set.** It now excludes impacts before the final transmission (item 2). It includes bank limits up to 90° (item 3), dives
  and level-offs at any p (item 7), and any planned-descent start time before exhaustion (item 4).
- **(b) Model's reach.** The 52.5° cap gap is closed up to 90°; overbank above 90° is a declared gap. The descent laws are uncalibrated
  (Boeing gate failed).
- **(c) Proposal's coverage.** Held-out D0′ has 9.78M effective impacts. D4 has 8.9k–55k pooled, depending on the arm.
- **Gaps.** The both-burst cells D3 and D4 are thin per seed (32–250 effective impacts on one stratum in the production recipe); this
  is the open gap that the run-J supplementary pass will address. Pre-00:11 planned descents under D2 and D4 are not estimable
  (1–11 effective impacts per seed), and are reported as such, not as absent. The B-uncontrolled family (share 0.001) is not estimable
  in the both-burst cells.
