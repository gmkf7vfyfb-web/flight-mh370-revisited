# Find episodes for the stringent nine — draft for the architect's ruling

Ocean Drift Module, 8–9 October 2026. **DRAFT, PROVISIONAL.** Brief §14.3; contract rules 2 and 8;
`results/davey-ch11-alignment.md` D4–D5. Nothing here has been run. The architect rules; this note
proposes.

**Recommendation in one paragraph.** Keep the nine recovered objects as nine likelihood factors,
each used once (rule 2), and let "episodes" enter as **detection blocks** — coast segment ×
discovery interval — whose unknown relative identification levels are part of the shared
environment η and are marginalised once, outside the product over objects (rule 8). Do not collapse
finds into fewer observations in the first pass, and do not couple pieces from the same parent
component until settling supplies a break-up model. Carry the Mossel Bay date both ways as a
labelled sensitivity (O_a: 23 Dec 2015; O_b: 21–22 Mar 2016). Grouping G2 (six coast-segment
episodes) is the robustness check; grouping G3 (parent-component coupling) is the refinement.

---

## 1. The nine records

From `engine/hypotheses/debris-drift/data/debris-evidence-audit.csv` on `hypothesis/debris-drift`
(byte-identical to the frozen original), rows with `stringent_nine = yes`. Days are counted from
2014-03-08 (00:19 UTC impact taken as day 0).

| object_id | Malaysian item | description | locality | discovery (table) | day | motion_class |
|---|---|---|---|---|---:|---|
| reunion-right-flaperon | 1 | right flaperon | Saint-André, Réunion | 2015-07-29 | 508 | flaperon |
| mossel-bay-engine-cowling-roy | 4 | engine (nose) cowling, "Roy" stencil | Klein Brak River, Mossel Bay, South Africa | 2015-12-23 † | 655 | low_exposure_exterior |
| paindane-right-flap-fairing | 2 | right No. 7 flap support fairing | Daghatane Beach, Paindane, Mozambique | 2015-12-27 | 659 | low_exposure_exterior |
| vilanculos-horizontal-stabilizer-panel | 3 | right horizontal stabilizer panel | Paluma sandbank, Vilanculos, Mozambique | 2016-02-28 | 722 | low_exposure_exterior |
| rodrigues-door-closet-panel | 5 | right door / stowage closet panel | Var-Brulé Beach, Rodrigues | 2016-03-30 | 753 | high_windage_interior |
| chidenguele-right-fan-cowling | 6 | right engine fan cowling | south of Chidenguele, Mozambique | 2016-04-24 | 778 | low_exposure_exterior |
| mauritius-left-outboard-flap | 10 | left outboard flap section | Ilot Bernache, Mauritius | 2016-05-10 ‡ | 794 | low_exposure_exterior |
| antsiraka-cabin-interior-panel | 16 | cabin interior panel, MAS laminate | Antsiraka Beach, Madagascar | 2016-06-12 | 827 | high_windage_interior |
| pemba-right-outboard-flap | 19 | right outboard flap, inboard section | Kojani Island, Pemba, Tanzania | 2016-06-23 ‡ | 838 | low_exposure_exterior |

† `decision = primary_date_conflicts_with_summary`. ‡ `decision = primary_date_from_durgadoo`.

**The Mossel Bay date, both ways.** The table's 2015-12-23 follows the date the prior archive
attributes to Durgadoo et al.'s nine-item table (DEBRIS-EVIDENCE.md, "Dates and coordinates");
Durgadoo's full text is not open access and was not re-read tonight. The Malaysian *Summary of
Possible MH370 Debris Recovered* (updated 30 December 2018) lists Item 4, "Engine Nose Cowl, Mossel
Bay, South Africa", against **22 March 2016**. Contemporaneous wire reporting places the find on
Monday 21 March 2016, by an archaeologist walking a lagoon near Mossel Bay, and Malaysia's transport
minister announced it on 22 March 2016. So:

- **O_a**: discovery 2015-12-23 (day 655), per the evidence table / Durgadoo as recorded;
- **O_b**: discovery 2016-03-21 (day 744), per the press account, with the MOT listing of
  2016-03-22 (day 745) one day later — the MOT date may be the report date.

The two differ by 89 days. One possible origin of the December date is a conflation with the
separate December 2015 find by a South African family on holiday in **Mozambique**, which is the
Paindane item; that is a hypothesis for the architect to check against Durgadoo's table, not a
finding. Nothing below picks one date.

**Verifiable distances between pieces.** Great-circle, from the table's locality coordinates:
flaperon–Pemba flap 2,452 km; flaperon–Paindane fairing 2,098 km; Pemba flap–Paindane fairing
2,166 km; Mossel Bay cowl–Chidenguele fan cowl 1,544 km; Rodrigues–Antsiraka cabin panels 1,485 km;
Paindane–Vilanculos 221 km; Paindane–Chidenguele 164 km; flaperon (Réunion)–Mauritius flap 236 km;
Mauritius–Rodrigues 604 km.

---

## 2. The three axes, stated once

**Parent component** (from the official item descriptions in the table):

| parent | members |
|---|---|
| P1 right-wing trailing edge | flaperon (1), right No. 7 flap support fairing (2), right outboard flap section (19) |
| P2 left-wing trailing edge | left outboard flap section (10) |
| P3 engine nacelles | engine nose cowl (4, side not stated in the table), right engine fan cowling (6) |
| P4 empennage | right horizontal stabilizer panel (3) |
| P5 cabin interior | R1-door closet panel (5), interior panel with MAS laminate (16) |

**Coast segment**: S1 Réunion; S2 Mauritius–Rodrigues; S3 southern Mozambique (Vilanculos to
Chidenguele, ~330 km of coast); S4 South African south coast (Mossel Bay); S5 north-east Madagascar
(Antsiraka); S6 Tanzania (Pemba). S1 and S2 can be merged as "Mascarene" if detection is modelled
at that scale.

**Discovery interval**: I1 = before 29 July 2015 (no deliberate search); I2 = 29 July 2015 to
end-February 2016 (post-flaperon awareness); I3 = March–June 2016 (the period of most finds). The
boundaries are a proposal: the alignment note's requirement is only that `P_I(y, t)` be
non-stationary, with search effort rising sharply after July 2015.

---

## 3. What a grouping changes in the marginalisation

The target structure is rule 8:

```
L(x) = Σ_m π_m ∫ p(η | m) Π_j L_j(x | m, η) dη ,
```

with the ocean model `m` (declared as `ocean-model`), shared environment `η`, and object-specific
parameters integrated inside each `L_j`. Under D5 (λ cancelled by conditioning on the number of
finds), each factor is a ratio:

```
L_j(x | m, η) = q_j(y_j, t_j | x, m, η) / Q(x | m, η),
q_j        = ∫ p(ψ | class_j) Σ_b ν_b · a_b(y_j, t_j | x, m, η, ψ) dψ ,
Q(x|m,η)   = Σ_b ν_b · A_b(x | m, η) ,
```

where `ψ` is the object response (drawn once per particle, per class — review §4.1), `a_b` is the
density of beaching at locality `y_j` with discovery at `t_j` inside detection block `b`, `A_b` is
the total identified-arrival probability in block `b` over all coasts, and `ν_b` is the **relative**
identification level of block `b`. A single global constant in `ν` cancels; differences between
blocks do not. A grouping decides three things: which finds share a factor, which share latent
detection levels `ν_b`, and which share object-level latent variables (response or break-up time).

---

## 4. The alternative groupings

### G0 — the prior archive (for reference, not proposed)

Nine singleton "episodes", each a bounded proximity score, no `Q(x)`, one fixed response per class,
no detection model, one ocean model per run (review §1.2, E6). Structure:
`log L(x) = Σ_j log(1e-9 + score_j(x))`. Nothing is marginalised. Listed so the departure is
traceable.

### G1 — nine object factors, detection blocks shared (RECOMMENDED for the first pass)

- **Factors:** nine, one per object ID, each used once (rule 2).
- **Shared outside the product (η):** diffusivity K and current-error scale (owned by the shared
  ocean), plus the block levels `ν_b` for blocks `b ∈ {S1…S6} × {I1, I2, I3}`, with a declared
  prior — first pass: `log ν_b ~ N(μ_I, 1²)` independently by block, where `μ_I1 < μ_I2 < μ_I3`
  encodes the rise in effort after July 2015 (values to be set by the architect; a ruling is
  needed). Australian, Indonesian and other coasts with zero finds appear only in `Q(x)` with
  their own `ν_b`.
- **Inside each factor:** the object response `ψ_j` by `motion_class`.
- **Mossel Bay:** two runs, O_a and O_b, reported as a labelled sensitivity. If the architect
  prefers a single answer, the coherent form is a declared mixture over the uncertain datum,
  `L_4 = w·L_4(O_a) + (1 − w)·L_4(O_b)` with `w` stated (this is marginalisation over an
  observation error of one object, so it does not use the find twice).
- **Argument for:** it uses each find exactly once, keeps object class information (the two cabin
  panels and the flaperon have different responses), and puts the main known dependence between
  finds — that they were found by the same, time-varying search effort on the same coasts —
  where it belongs, in shared latent detection levels. Conditional on the ocean `(m, η)`, separate
  pieces that separated early drift nearly independently, so the product inside the integral is
  the right approximation.
- **Cost:** 18 block levels to marginalise (most poorly constrained); the result's sensitivity to
  the `ν` prior must be reported.

### G2 — six coast-segment episodes (robustness sensitivity)

- **Factors:** six, one per coast segment S1–S6, each scored as "n_s identified arrivals on segment
  s, first at time t_s". Under D5 the count part is a multinomial over segments,
  `Π_s (Q_s(x)/Q(x))^{n_s}`, times a timing term for the first discovery on each segment.
- **Shared outside the product:** K, current error; one `ν` per segment (no interval split).
- **Inside each factor:** an inventory-weighted mixture over the response classes present on that
  segment (S2 mixes the interior Rodrigues panel with the exterior Mauritius flap).
- **Argument for:** robust to within-segment dependence of detection (S3's three finds lie within
  ~330 km of coast and four months) and to per-object timing error; closest to Durgadoo et al.'s
  emphasis on discovery-time uncertainty. It is also the grouping the prior archive's comments
  intended ("co-located pieces from one discovery episode belong in one event",
  `observations.rs` lines 19–21) without implementing.
- **Argument against:** it discards the identity and class of each piece and the second and third
  discovery times on a segment, and it needs an inventory prior over classes that nobody has.
  Under rule 2 it is legitimate (each find enters once, inside a count), but it throws away
  information G1 can use.

### G3 — parent-component coupling (refinement, after settling)

- **Factors:** five parent groups P1–P5. Within a group, pieces share a break-up time τ_g: before
  τ_g they move as one assembly with an assembly response; after it, independently. Then
  `L_g = ∫ p(τ_g) ∫ p(ψ_assembly) Π_{j∈g} L_j(x | m, η, ψ_j, τ_g, path up to τ_g) …`.
- **Argument for:** physically real if pieces stayed attached for weeks — a cowl attached to its
  nacelle, a flap section still carrying its fairing.
- **Argument against, for now:** pieces from the same parent were found 1,544–2,452 km apart and
  four to eleven months apart (P1: days 508, 659, 838; P3: days 655/744 and 778; P5: days 753 and
  827). Any shared drift must therefore have ended early relative to 17–28 months at sea, and for
  τ_g → 0 G3 reduces exactly to G1. There is no evidence about break-up timing in this module; it
  belongs with settling's element classes and family-dependent release (brief §6: the refinement).
  Coupling also re-opens the profile-over-laws error of the prior archive (review E3) unless the
  assembly response is marginalised.

---

## 5. Recommendation and what is needed from the architect

1. **Adopt G1 for the first pass**, with the declared `ν_b` prior to be ruled.
2. **Run G2 as a robustness sensitivity** on the pilot grid; report the TV between G1 and G2
   updated impact posteriors, not between drift maps.
3. **Defer G3** to the refinement, and ask settling for break-up timing by element class.
4. **Mossel Bay**: run O_a and O_b as labelled sensitivities; rule whether a declared mixture with
   weight `w` is wanted for the headline.
5. **Check Durgadoo's table** for the Mossel Bay date source when the full text is available; if
   the December date proves to be a conflation with the Paindane find, the evidence table needs a
   correction through the architect (the table is byte-identical to a frozen file and must not be
   edited by this module).

Sources: the evidence table above; Malaysian ICAO Annex 13 Safety Investigation Team, *Summary of
Possible MH370 Debris Recovered* (updated 30 December 2018), mot.gov.my (Item 4 and Item 6 dates
read from the indexed text of that PDF); AP/Fox News and Inquirer reports of 22 March 2016 on the
Mossel Bay find; [Durgadoo et al. 2021](https://doi.org/10.1080/1755876X.2019.1602102) (abstract
only re-read); `results/debris-drift-review.md` for the response classes and errors cited.
