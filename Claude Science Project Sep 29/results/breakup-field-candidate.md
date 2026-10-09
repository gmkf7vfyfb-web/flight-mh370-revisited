# Breakup field — candidate definitions (settling, 2026-10-09)

**Status: candidate for the shared breakup-field freeze, PROVISIONAL.** Written by ocean settling at
architecture's request (`coordination/OCEAN_SETTLING.md`, ruling 4 of 8 October). Every number is an
educated estimate, declared as such; none is a measurement of MH370. The machine-readable source is
`engine/hypotheses/settling/breakup.toml` on branch `hypothesis/settling` (commit `f32d1c2`); where this
note and that table disagree, **the table is authoritative** and this note is wrong. The tables below
were generated from it, not retyped.

## 1. Two different things share the word "class"

- **Breakup family** — one value per *impact sample*: how the airframe came apart at first water contact.
  Three values: `intact`, `broken`, `fragmented`. **This is what `ImpactView`'s `debris_class` is.**
- **Element class** — six values *within one wreckage field*: what kinds of pieces exist and how they
  behave in water. Settling generates the pieces of every class from the family plus the impact's mass
  and energy (brief §2: the impact sample carries a class, settling generates the object ensemble).
  End of flight does not emit element classes.

## 2. The three families and the selection rule

| family | physical definition | anchor (calibration, not test) |
|---|---|---|
| `intact` (0) | Ditching-like contact. The airframe stays in a few large pieces (1–3 wing pieces, 1–4 fuselage sections), floats first on empty tanks and trapped air, and sinks later as large pieces; engines and gear tear off. | US Airways 1549, about 64 m/s, 3.8 m/s down → P(intact) 0.882 |
| `broken` (1) | Hard contact at high descent rate but modest speed. Large sections, engines and gear separate; tens of structural pieces, hundreds to thousands of panels; debris floats briefly. | AF447, about 55 m/s down, 78 m/s total → P(broken) 0.848 |
| `fragmented` (2) | Fast contact. Everything but the densest parts is in small pieces: hundreds of structural fragments, thousands to ~10⁵ panel pieces. | Swissair 111, about 154 m/s, 20° nose down → P(fragmented) 0.843 |

**Inputs.** The vertical and total *specific* kinetic energy at first contact,
e_v = `vertical_kinetic_energy_j` / `mass_kg` and e = `kinetic_energy_j` / `mass_kg`, written as the
equivalent speeds V_d = √(2 e_v) and V = √(2 e). The flight-path angle is implied, sin²γ = e_v / e, so
the three quantities brief §2 names carry two degrees of freedom and the rule uses two. Attitude and the
energy-transfer duration are **not** inputs in this first pass (brief §2 and §6).

**Rule.** With L(x) = 1 / (1 + e^(−x)), V_d floored at 0.01 m/s (a level contact):

```
P(intact)     = L( ln(a / V_d) / s ) · L( ln(c / V) / s )
P(fragmented) = (1 − P(intact)) · L( ln(V / b) / s )
P(broken)     = 1 − P(intact) − P(fragmented)
a = 8.0 m/s   (intact_descent_mps:   descent rate at which an otherwise gentle contact is even odds intact)
c = 100.0 m/s (intact_speed_mps:     speed at which a shallow contact is even odds intact)
b = 110.0 m/s (fragmented_speed_mps: speed at which a non-intact contact is even odds fragmented)
s = 0.2       (log_width:            width of each transition in ln speed)
```

Smooth in both inputs, no hard thresholds, a probability for every impact with finite positive speed
(rule 5). Outside that domain (no mass, NaN energy, e_v > e) the rule **refuses** — not computed, never
a default family.

**Fixtures any implementation must reproduce** (hand calculation, AF447: V_d 55, V 78):
L(ln(8/55)/0.2) = L(−9.6395) = 6.51×10⁻⁵; L(ln(100/78)/0.2) = L(1.2423) = 0.7760; P(intact) = 5.05×10⁻⁵;
L(ln(78/110)/0.2) = L(−1.7189) = 0.1520; **P = (5.05×10⁻⁵, 0.8479, 0.1520)**. Also US1549 (3.8, 64) →
(0.8817, 0.1109, 0.0074) and Swissair 111 (154 sin 20° = 52.67, 154) → (8.4×10⁻⁶, 0.1568, 0.8432).
These are `breakup::tests::analogue_anchors` in settling.

## 3. Recommendation to end of flight: draw the family once per impact sample

Hydroacoustics and settling will both condition on the family. If each drew it independently, one impact
sample could be `intact` to the acoustics and `fragmented` to the wreckage — two modules disagreeing about
one physical event, which rule 3 exists to prevent. So:

1. **`debris_class`** = the family index (0, 1, 2) **drawn once per impact sample** from the probabilities
   above, on that sample's own random stream. Every consumer conditions on that one draw.
2. Also emit the three probabilities, as `breakup_p_intact`, `breakup_p_broken`, `breakup_p_fragmented`,
   so a consumer can Rao-Blackwellise or check the draw, and so the composer can report family evidence
   *before* any within-family normalisation (brief §9).
3. Implement the rule from §2 with the constants quoted verbatim and a test reproducing the three fixtures.
   That makes two implementations checked against one set of numbers, which is the honest form of "one
   definition" while the constants live in settling's table.

**Settling's side, until `debris_class` is readable** (core request 4 lifts latents into `ImpactView`;
today a non-terminal module sees an empty `latents` slice): settling draws the family per wreckage draw
from the same rule, labelled provisional. When the field becomes readable, settling conditions on it and
stops drawing.

## 4. The six element classes

| class | physical definition |
|---|---|
| `engine` | Rolls-Royce Trent 892 core and fan case, with or without nacelle remnants; two per aircraft. Steel and nickel alloys, titanium, aluminium, composite. Dense and compact: sinks at once, falls fast, barely glides. |
| `landing-gear` | Two six-wheel main gears and a nose gear: steel structure, aluminium wheels, carbon brakes; tyres buoyant while inflated and compressed below about 140 m. Dense and compact. |
| `wing-box` | Wing and centre-section primary structure — spars, ribs, skins, flooded tanks — aluminium with composite control surfaces. Large, flat, moderately dense: can glide; floats first when intact. |
| `fuselage-section` | Fuselage pieces that keep frames and floor structure (skin-only pieces are `flat-panel`). Falls broadside; traps air when intact, so floats first. |
| `flat-panel` | Skin panels, control surfaces, fairings and floor panels that sink: 2–4 mm aluminium skin with stringers, or solid laminate. Light per unit area, so slow and gliding. Honeycomb sandwich panels that float for months are this class's `stays afloat` share — surface-drift debris (the flaperon is one). |
| `cabin-contents` | Payload, baggage, cargo, seats and galley equipment. Waterlogged soft goods just denser than sea water; metal frames and carts much denser; cushions, foam and many bags float for days. The slowest sinkers in the table. |

Mass shares sum to one in every family (checked on load); in `broken` and `fragmented`, mass moves from
`wing-box` and `fuselage-section` into `flat-panel`. Piece area follows from mass conservation:
area = mass share × impact mass / (pieces × areal density).

| class | family | pieces | mass share | areal density s (kg/m²) | material density (kg/m³) | sink speed range (m/s, surface) | sinks at once | stays afloat | float time (s) | glide ratio G | glide memory l (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| engine | intact | 2 | 0.08 | 400–1300 (log) | 3500–6000 | 2.12–5.08 | 1.0 | 0.0 | 0 | 0–0.2 | 20–200 (log) |
| engine | broken | 2 | 0.08 | 400–1300 (log) | 3500–6000 | 2.12–5.08 | 1.0 | 0.0 | 0 | 0–0.2 | 20–200 (log) |
| engine | fragmented | 2–6 | 0.08 | 400–1300 (log) | 3500–6000 | 2.12–5.08 | 1.0 | 0.0 | 0 | 0–0.2 | 20–200 (log) |
| landing-gear | intact | 1–3 | 0.05 | 350–1200 (log) | 2500–5500 | 1.74–4.56 | 1.0 | 0.0 | 0 | 0–0.2 | 20–200 (log) |
| landing-gear | broken | 3 | 0.05 | 350–1200 (log) | 2500–5500 | 1.74–4.56 | 1.0 | 0.0 | 0 | 0–0.2 | 20–200 (log) |
| landing-gear | fragmented | 3–10 | 0.05 | 350–1200 (log) | 2500–5500 | 1.74–4.56 | 1.0 | 0.0 | 0 | 0–0.2 | 20–200 (log) |
| wing-box | intact | 1–3 | 0.22 | 60–150 (log) | 2300–2800 | 0.70–1.67 | 0.0 | 0.0 | 600–21600 (log) | 0–0.3 | 100–2000 (log) |
| wing-box | broken | 3–20 (log) | 0.18 | 40–200 (log) | 2300–2800 | 0.57–2.23 | 0.8 | 0.0 | 60–3600 (log) | 0.1–0.6 | 10–200 (log) |
| wing-box | fragmented | 20–500 (log) | 0.1 | 20–150 (log) | 2300–2800 | 0.40–1.93 | 0.95 | 0.0 | 60–600 (log) | 0.2–0.8 | 2–50 (log) |
| fuselage-section | intact | 1–4 | 0.27 | 150–350 (log) | 1800–2700 | 1.01–2.96 | 0.0 | 0.0 | 600–21600 (log) | 0–0.3 | 100–2000 (log) |
| fuselage-section | broken | 5–30 (log) | 0.22 | 60–250 (log) | 2000–2800 | 0.68–2.53 | 0.7 | 0.0 | 60–3600 (log) | 0–0.4 | 20–300 (log) |
| fuselage-section | fragmented | 50–2000 (log) | 0.12 | 30–150 (log) | 2000–2800 | 0.48–1.96 | 0.9 | 0.0 | 60–1800 (log) | 0.1–0.6 | 5–100 (log) |
| flat-panel | intact | 10–100 (log) | 0.03 | 5–40 (log) | 1500–2800 | 0.15–1.39 | 0.6 | 0.2 | 60–7200 (log) | 0.2–1 | 1–10 (log) |
| flat-panel | broken | 100–2000 (log) | 0.12 | 5–40 (log) | 1500–2800 | 0.15–1.39 | 0.6 | 0.2 | 60–7200 (log) | 0.2–1 | 1–10 (log) |
| flat-panel | fragmented | 2000–100,000 (log) | 0.3 | 5–40 (log) | 1500–2800 | 0.15–1.39 | 0.6 | 0.2 | 60–7200 (log) | 0.2–1 | 1–10 (log) |
| cabin-contents | intact | 50–500 (log) | 0.35 | 20–200 (log) | 1100–2000 | 0.14–1.44 | 0.3 | 0.4 | 600–86400 (log) | 0–0.5 | 1–20 (log) |
| cabin-contents | broken | 500–5000 (log) | 0.35 | 20–200 (log) | 1100–2000 | 0.14–1.44 | 0.3 | 0.4 | 600–86400 (log) | 0–0.5 | 1–20 (log) |
| cabin-contents | fragmented | 2000–50000 (log) | 0.35 | 20–200 (log) | 1100–2000 | 0.14–1.44 | 0.3 | 0.4 | 600–86400 (log) | 0–0.5 | 1–20 (log) |

Sink-speed ranges are the extreme combinations of the drawn ranges at surface density 1,025 kg/m³, for
orientation; individual elements are drawn inside them. The **slowest sinkers (~0.14–0.15 m/s for the
lightest panels and soft goods) take about 8 h to reach 4 km**, which is why the time axis of the ocean
product matters to settling more than its horizontal resolution.

## 5. The sink-versus-float partition — settling owns it

`stays afloat` is the share of each class, in each family, that does not sink within hours and belongs to
the surface-drift branch, not to settling. Settling emits those elements with fate `afloat` and their
surface position after carry (the hook queued with Pete). **This is the partition drift and Pléiades need,
and it comes from the same element physics as settling.** End of flight currently declares a
`sinks_not_floats` NaN hook as well; two owners of one partition is the failure architecture's open item 5
describes, so settling recommends that hook be retired in favour of settling's emitted fates. Raised in
`coordination/architecture.md`; not decided here.

## 6. What the other consumers can state requirements against

- **Hydroacoustics:** the family index (draw once, §3) and the probabilities. Element classes are probably
  too fine for a source term; say so if not.
- **Drift:** the `stays afloat` share and float-time range per class and family, and the leeway range. These
  are educated estimates; drift's own measurement that object response dominates (Stokes ×0.5/1/1.5 moved
  the mode to 11.9/18.0/34.9° S) says they deserve more scrutiny than settling alone can give them.
- **Searched areas:** pieces per class and piece area, from which the detectable fraction of a field follows.

## 7. Known weaknesses, stated now

- The family thresholds (a, b, c, s) are three anchors and judgement. Settling's report will carry a
  sensitivity to them; a defensible calibration needs more cases with known contact speed (the analogue
  survey, `hypotheses/settling/data/analogues.csv`).
- Piece counts span orders of magnitude within a family and are log-uniform by assumption. The upper end
  for `fragmented` panels (10⁵) is set by Swissair 111's roughly two million recovered pieces, most far
  smaller than a panel.
- Mass shares for a 777-200ER are educated estimates, not from a Boeing weight statement.
- No class has an implosion model; trapped-air sections are where one would enter (deferred, brief §13).

— ocean settling
