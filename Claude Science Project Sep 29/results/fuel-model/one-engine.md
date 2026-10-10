# One engine inoperative: ceiling, speed schedule, drift-down, and the autoflight response (for C-7(a))

Fuel session, 10 Oct 2026, commissioned by architecture overnight (`coordination/OVERNIGHT-2026-10-10.md`).
**PROVISIONAL-OVERNIGHT: a derived model, not a simulation; no filter was run.** Code:
`engine/fuel-model/one_engine.py`, run at 2 threads.

**Files.**
- `one-engine-ceiling.csv`
- `one-engine-ceiling-table-frontier.csv`
- `one-engine-speed-schedule.csv`
- `one-engine-driftdown.csv`

These hold derived values only. **Local only, git-ignored:** `engine/data/external/fuel-model/one-engine-v1.json`
(core's schema: speed grids at FL070–300 × 150–250 t, the ceiling table against weight and ΔISA, and the
drift-down model).

## Sources

| source | grade | used for |
|---|---|---|
| Ulich 9M-MRO fuel model v5.6: LRC INOP Mach and flow grids (`data/fuel-tables.json`; 296 fppm-open cells, 1 fppm-confidential); holding INOP KIAS and Mach, read from the workbook sheet *Holding INOP Mach* | secondary; FPPM-derived; internal use authorised (ledger) | the ceiling (table frontier) and the speed schedule |
| Ulich v5.6 workbook, *Endurance Model* C36–C41 | secondary. Ulich cites forum contributors ("Gysbreght", "Andrew") and "ALSM simulator runs"; these are not primary | a cross-check only: highest level for level INOP flight FL300; KCAS deceleration −10 kt/min to minimum KCAS 208 kt; then a descent of about 600 ft/min; live-engine flow 4,000 kg/h at FL360 |
| SIR App. 1.6E, printed p. 8 | primary | after the right engine's flame-out, thrust asymmetry compensation (TAC) applied left rudder; the autopilot disconnected only when the left engine spooled down; the driftdown ratio of 0.0034 NM/ft, which gives L/D = 20.7 |
| SIR App. 1.6E, printed p. 5 | primary | Boeing's analyses include the right engine's higher SFC |
| ATSB AE-2014-054, *Definition of Underwater Search Area Update*, 3 Dec 2015, printed p. 11, as quoted on the ATSB's own *Inaccuracies in reporting on the search for MH370* page | primary, via the ATSB's quotation; the PDF itself could not be downloaded (server timeout), so the page is not re-verified | the right engine flamed out first, and on one engine the aircraft "could not maintain any altitude above 29,000 feet" |
| ATSB AE-2014-054, *Definition of Underwater Search Areas*, 26 June 2014 (upd. Aug 2014), p. 33, via the same ATSB page | primary, via the ATSB's quotation | one engine flamed out, "followed, within minutes, by the other engine" |
| ATSB AE-2014-054, *MH370 – Search and debris examination update*, 2 Nov 2016, printed p. 8 (from the PDF's text) | primary | in an electrical configuration where losing one engine's power **did** cause loss of the autopilot, the aircraft descended turning either way. So in the other configurations the autopilot stayed engaged on one engine. Some aircraft stayed airborne about 20 min after the second flame-out |

## Declared deviations and assumptions

1. **Temperature dependence is an assumption.** The tables are standard day. The thrust loss is taken
   between 0 (flat-rated) and 0.7 %/°C above ISA (turbine-temperature-limited), with 0.35 %/°C central. No
   gain is assumed below ISA.
2. **L/D = 20.7** comes from Boeing's glide figure, with both engines windmilling. On one engine L/D is a
   little higher, so the descent rates here are slightly high.
3. **The drift-down speed** is the holding-INOP KIAS, used as the minimum-drag (E/O) speed proxy. The
   minimum-drag factor c = D(LRC INOP)/D_min = 1.038 comes from the public polar (delivery 3).
4. **The descent model** uses the energy method with no kinetic-energy correction (the rate is overstated
   by up to ~8 %). It assumes no wind and a constant weight during the descent; the weight falls by only
   ~0.1 t per min.
5. **The ceilings at ≤ 170 t sit at the table's top (FL300).** Above it they are extrapolated by the
   thrust-lapse fit.
6. **Finding about `extract.py`.** It concatenates the two blocks of *Holding INOP Mach* (KIAS and Mach)
   into one table with a repeated FL axis, `holding_inop_mach` in `fuel-tables.json`. The INOP grid in
   internal-v1 happens to read the Mach half: it is identical at 14,115 test states. **No delivered number
   changes**, but the table entry is malformed. Fix `extract.py` (`.sources`, core-owned) to read the
   block under each label.

## 1. One-engine ceiling against weight and ΔISA (`one-engine-ceiling.csv`)

**The data.** The LRC-INOP table frontier — the highest FL with a non-filler cell — runs:

| weight | ≤ 170 t | 180 t | 190 t | 200 t | 210 t | 220 t |
|---|---|---|---|---|---|---|
| frontier | FL300 (table top) | FL280 | FL270 | FL260 | FL240 | FL230 |

**The fit.** Over the five frontier points inside the table, W_c(FL) ∝ δ^0.864 with rms 1.0 %. This is the
max-continuous-thrust lapse.

**Standard-day ceilings:**

| weight t | thrust-limited ceiling at LRC INOP speed | level-off at minimum-drag speed |
|---|---|---|
| 150 | FL329 | FL338 |
| 170 | FL298 | FL307 |
| **175** | **FL290** | **FL300** |
| 180 | FL283 | FL292 |
| 190 | FL269 | FL278 |
| 200 | FL255 | FL265 |

**This agrees with the ATSB.** The flight's end weight is ~175 t (ZFW 174.2 t plus ~1 t of fuel), and the
ATSB says no altitude above 29,000 ft could be held on one engine (Dec 2015, p. 11, via the ATSB quotation).
Ulich's FL300 for level INOP holding also agrees.

**Temperature** (central 0.35 %/°C; band 0 to 0.7 %/°C): −9 FL per +10 °C (band 0 to −19). Near the 7th arc
the hand-off states give ΔISA ≈ +2.4 °C, so the effect is −2 FL (band 0 to −5) **at the end of the flight**.

## 2. Speed schedule (`one-engine-speed-schedule.csv`; the full grid is in the local JSON)

At 177.5 t:

| FL | LRC INOP Mach | LRC INOP KCAS | drift-down (holding-INOP) KCAS | drift-down Mach |
|---|---|---|---|---|
| 150 | 0.534 | 269 | 207 | 0.414 |
| 200 | 0.582 | 267 | 207 | 0.456 |
| 250 | 0.638 | 265 | 208 | 0.507 |
| 270 | 0.666 | 266 | 216 | 0.548 |
| 280 | 0.682 | 267 | 220 | 0.569 |
| 290 | — (above the LRC-INOP frontier) | — | 223 | 0.590 |
| 300 | — | — | 227 | 0.610 |

- **The one-engine cruise speed (LRC INOP) is about 265 KCAS, or M0.64–0.68 at FL250–280.** TAS is
  390–410 kt, against ~470 kt in twin cruise.
- **The drift-down speed is about 207–227 KCAS** (M0.51–0.61 at FL250–300), with TAS 300–350 kt.
- For heavier weights see the CSV: +1 to +4 KCAS per 10 t.

## 3. Drift-down after the first flame-out from cruise at M0.80 (`one-engine-driftdown.csv`)

The phases are:
- **(A) altitude held while the speed decays to the drift-down KCAS** (the autopilot holding altitude,
  autothrottle at the thrust limit);
- **(B) a descent at the drift-down KCAS.**

"To ROD < 100 ft/min" ends about 1,000–1,500 ft above the asymptotic level-off.

| start | weight | ΔISA | (A) decel time / mean rate | (B) time to ROD < 100 ft/min | (B) initial / mean ROD | level-off (min drag) |
|---|---|---|---|---|---|---|
| FL350 | 175 t | 0 | 7.0 min / 6.8 kt/min | 18.0 min | 346 / 198 ft/min | FL300 |
| FL350 | 175 t | +10 | 6.3 min / 7.6 kt/min | 20.4 min | 409 / 219 ft/min | FL291 |
| FL370 | 175 t | 0 | 4.2 min / 8.6 kt/min | 22.9 min | 486 / 243 ft/min | FL300 |
| FL400 | 175 t | 0 | 1.7 min / 10.8 kt/min | 28.0 min | 703 / 306 ft/min | FL300 |
| FL400 | 185 t | +10 | 1.8 min / 12.6 kt/min | 31.8 min | 829 / 340 ft/min | FL276 |
| FL300 | 175–185 t | 0 | about 30 min to several hours (thrust ≈ drag): it effectively holds FL300 and bleeds speed slowly | — | — | FL286–300 |

**Reading for C-7(a).** The single-engine phase lasts 3–14 min (best 7–8; delivery 1). That is **shorter
than the drift-down itself**, so before the second flame-out:
- **from FL350 at 175 t,** the aircraft spends ~7 min decelerating at constant altitude, then descends only
  ~0–700 ft;
- **from FL400,** it decelerates for ~2 min, then loses ~3,000–4,500 ft in the next 6 min;
- **at FL300 or below,** it holds altitude.

The loss of TAS (470 → ~350–410 kt) costs about 8–15 NM along track over a 7–8 min phase, against twin
cruise.

## 4. What the autopilot and autothrottle do (public sources only)

**Documented:**
- **Thrust asymmetry.** After the right engine's fuel-starvation flame-out, TAC applied left rudder to
  minimise the yaw (SIR App. 1.6E p. 8).
- **The autopilot.** It stayed engaged until the left engine spooled down and electrical power was lost
  (p. 8). The ATSB's 2016 simulations (p. 8) show that only "an electrical configuration where the loss of
  engine power from one engine resulted in the loss of autopilot" made the aircraft descend turning. In the
  other configurations the autopilot held the commanded lateral path on one engine.
- **Altitude.** On one engine the aircraft "could not maintain any altitude above 29,000 feet" (ATSB Dec
  2015 p. 11, via the ATSB quotation).
- **The second engine.** It followed "within minutes" (ATSB June 2014 p. 33, via the same page). The
  maximum is up to 15 min (ATSB Dec 2015 p. 9, via the audit).

**Secondary (Ulich, citing simulator runs by other analysts):**
- with the autopilot engaged, the speed decays at about 10 kt/min to the minimum manoeuvre speed plus
  1 kt (≈ 208 KCAS);
- the aircraft then sinks at about 600 ft/min;
- the live engine burns ~4,000 kg/h at FL360, scaling with pressure.

**Inferred, not from a public primary source:** with no crew, the autothrottle advances the live engine to
its thrust limit. The autopilot keeps the selected altitude (ALT HOLD, or VNAV path) while the speed bleeds
off. A descent starts only when the speed reaches the low-speed limit; how the 777's speed protection acts
in this mode is not given in any public source I found. A deliberate drift-down at the E/O speed (as §3B)
needs crew or FMC engine-out mode, which is unlikely with no crew.

**Bracket for core and end of flight:**

| case | behaviour | rate and duration |
|---|---|---|
| (i) altitude hold to minimum speed, then a sink (Ulich/simulator) | speed decays to about 208 KCAS, then sinks | about 10 kt/min, then about 600 ft/min |
| (ii) physics drift-down (§3) | decelerates at altitude, then descends at the E/O speed | 2–7 min at constant altitude, then 350–830 ft/min, decaying to 0 near the level-off |

Both keep the lateral mode.

## 5. Against core's C-7(a) derivation

Core's design (architecture, ~03:55 UTC): a drift-down rate U(300, 1,000) ft/min per path; speed from the
one-engine schedule with a Mach-band fallback; lateral mode unchanged; ceiling and speed from `grid_inop`.
Core's code is `4b67733` and `7d42052`. The comparison is §5.1; the points it checks:

1. **The ceiling.** The `grid_inop` frontier should give FL280–290 at 175–180 t (holding FL300 at
   ≤ 180 t). If core uses the holding-INOP nodes (FL250/300 only), the ceiling can be off by up to 50 FL
   between nodes.
2. **The descent rate.** A constant U(300, 1,000) ft/min from the moment of flame-out has no
   altitude-held deceleration phase and no taper towards the ceiling.
   - Physics says the rate is 0 for the first 2–7 min, then 350–830 ft/min, falling.
   - Over a 7.5 min phase from FL350, core's draw loses 2,250–7,500 ft, against ~0–700 ft here. From
     FL400 it loses the same 2,250–7,500 ft, against ~3,000–4,500 ft here.
3. **The speed.** The LRC-INOP Mach (≈ M0.64–0.68) is the one-engine cruise speed. The drift-down speed is
   lower (M0.51–0.61).

### 5.1 Comparison with core's C-7(a) as built (`4b67733`, `7d42052`; `one-engine-vs-core-c7a.csv`)

Core's ceiling was reproduced exactly from `grid_inop`: the highest FL node with any Mach cell not flagged
above the ceiling, linear between 1-t weight nodes. Core's speed comes from `lrc_inop_mach` at
min(altitude, ceiling); above the frontier it takes the nearest covered level below, ± 0.02. At 176 t that is
the FL280 value, M0.678.

**Ceiling.**

| weight t | core | fuel, LRC INOP | fuel, level-off at minimum drag | core − fuel (ft) |
|---|---|---|---|---|
| 174 | FL300 | FL292 | FL301 | +830 / −120 |
| 176 | FL300 | FL289 | FL298 | +1,120 / +170 |
| 178 | FL300 | FL286 | FL295 | +1,410 / +460 |
| 180 | FL300 | FL283 | FL293 | +1,700 / +740 |
| 185 | FL270 | FL276 | FL286 | −590 / −1,550 |
| 190 | FL270 | FL269 | FL279 | +100 / −870 |
| 200 | FL260 | FL256 | FL265 | +450 / −530 |

- Core's FL300 at ≤ 180 t is the holding-INOP node at FL300, which is also the grid's top. It equals the
  level-off at minimum-drag speed (within −120 to +740 ft) and is about 1,000 ft above the ATSB's FL290.
- The step from FL300 to FL270 at 181–182 t is an artefact of the grid nodes: holding INOP is tabulated only
  every 50 FL.
- **Whether it matters:** no. At the first flame-out the total fuel is ~0.3–1.0 t (§4 of delivery 1), so the
  weight is ~174.5–175.2 t and the ceilings agree to within about 1,000 ft.

**Drift-down and speed.** Physics (§3) against core's constant U(300, 1,000) ft/min at M0.678, at 176 t:

| start | single-engine phase | altitude lost: physics / core at 300 · 650 · 1,000 ft/min | along-track distance, core − physics | vertical rate at the end: physics / core |
|---|---|---|---|---|
| FL350 | 4 min | 0 / 1,200 · 2,600 · 4,000 ft | −3 NM | 0 / 300-1,000 ft/min |
| FL350 | 7.5 min | 270 / 2,250 · 4,875 · 5,000 ft | −3 NM | 340 / 300 · 650 · 0 ft/min |
| FL350 | 14 min | 2,040 / 4,200 · 5,000 · 5,000 ft | −1 to −2 NM | 215 / 300 · 0 · 0 ft/min |
| FL370 | 7.5 min | 1,560 / 2,250 · 4,875 · 7,000 ft | −3 NM | 390 / 300 · 650 · 0 ft/min |
| FL400 | 7.5 min | 3,450 / 2,250 · 4,875 · 7,500 ft | −4 NM | 465 / 300 · 650 · 1,000 ft/min |
| FL400 | 14 min | 5,880 / 4,200 · 9,100 · 10,000 ft | −3 to −4 NM | 295 / 300 · 650 · 0 ft/min |

**Whether it matters.**
1. **Along-track distance: no.** Core − physics is −1 to −4 NM over 4–14 min. The one-engine aircraft is
   8–15 NM behind twin cruise either way, and core captures most of that.
2. **Altitude at the second flame-out: moderately.** Core's draw puts the aircraft 1,000–5,400 ft lower
   from FL350–370. From FL400 it is −1,700 to +4,000 ft. At Boeing's driftdown ratio of 0.0034 NM/ft that is
   ≤ 18 NM of glide reach for a piloted glide. For the uncontrolled descents the end-of-flight module flies,
   it is a few NM.
3. **The BFO, if 00:11 falls inside the single-engine phase: yes.** A vertical rate of 1,000 ft/min is
   about 18 Hz of BFO (5.1 m/s × f/c, with sin(elevation) ≈ 0.64 near the 7th arc). In the first 2–7 min
   physics has 0 ft/min, against core's 300–1,000 ft/min: a 5–18 Hz bias in the 00:11 BFO for those paths,
   comparable to the BFO noise.

**Recommendation to core (for after tonight's run; the run itself is not affected unless the two-tank
diagnostic shows weight with the first flame-out before 00:11):**
- (i) Add a constant-altitude deceleration phase of t_A = (KCAS_cruise − KCAS_dd)/a. Here
  a ≈ g/(L/D)·(D/D_min − c W_c/W): about 7–11 kt/min (Ulich's simulator figure is 10 kt/min), and
  KCAS_dd = holding-INOP KIAS (`driftdown_kcas` in the local JSON).
- (ii) Then descend at ROD(h) = V_TAS/20.7 × (1 − 1.038 W_c(h)/W), with
  W_c(h) = exp(lnA) δ(h)^0.864 (lnA in the local JSON). This tapers to 0 at the ceiling.
- (iii) Or, keeping the simple form, draw the rate from U(0, 600) ft/min and start it after t_A. That
  matches the physics mean of 200–340 ft/min to within the draw.
- (iv) Speed during the descent is the drift-down KCAS (M0.55–0.61), not the LRC-INOP Mach. The distance
  effect is ≤ 4 NM.
