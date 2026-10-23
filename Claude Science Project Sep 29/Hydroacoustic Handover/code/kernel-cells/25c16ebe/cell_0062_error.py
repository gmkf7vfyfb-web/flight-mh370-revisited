v6 = open("end-of-flight.md").read()
def ed6(old,new,label):
    global v6
    assert v6.count(old)==1, (label, v6.count(old)); v6 = v6.replace(old,new); print("ok:",label)

ed6("""**Single flame-out event for the first working version.** Per-engine flame-out (right engine first,
gap unpublished, single-engine phase never modelled) is agreed in principle and comes after, so its
effect on the impact PDF can be measured rather than assumed.
""",
"""**Correction, 13 October: the two-engine structure is already built, and the previous versions of
this paragraph were wrong.** They said "single flame-out event for the first working version" and
"single-engine phase never modelled". Measurement of run-i-dive contradicts both. What exists:

- **Core** carries two tanks (`fuel.tanks = 2`), a single-engine fuel and performance phase
  (`fuel.single_engine = true`, `inop_flow_scale = 0.5`, a hold-taper driftdown at 207–227 KCAS,
  300–1,000 ft/min, 7–11 kt/min deceleration, L/D 20.7), and `require_power_until = "m0011"` with
  `hard_reject = true` — so **loss of the second engine before 00:11 is excluded by construction,
  while loss of the first is permitted**.
- **The hand-off carries real per-trajectory fuel state.** Core request 1 has landed. The
  `fallback_fuel_kg = 2000` path is not in use: realised flame-out times take 711,648 distinct
  values with no mass at the 00:31:48 the fallback would imply.
- **This stage takes over with two tank states** (`two_tank_takeover = true`) and tracks the engine
  count at onset. Measured, held-out weighting: 56.9 per cent no engine thrusting, **36.9 per cent
  exactly one**, 6.2 per cent both.
- **`t_realised_flameout_s` is the FINAL flame-out, not the first.** For the 325,071 rows that take
  over with no engine running it sits at takeover within a few seconds. For the 85,018 that take
  over with one engine running it is a median **288 s later**, reaching 1,113 s at the 95th
  percentile. So 22.5 per cent of the fuel-exhaustion families fly a real single-engine phase of
  several minutes inside this stage, and 46.2 per cent of the deliberate family begin their descent
  with one engine running.

So the first and second engine losses are both present **for fuel and gross performance**. Two
things are genuinely missing, and they are what the deferral should now refer to:

1. **The first flame-out time is not emitted.** Only the final one is. Takeover time is a proxy for
   it in the fuel-exhaustion families and is not one in the deliberate family, where takeover is the
   descent onset. Emit both, and name them so the distinction cannot be lost: this column has been
   described in the trait doc as "the first flame-out" and is the opposite.
2. **No asymmetric-thrust dynamics exist anywhere.** This stage's envelope contains no yaw, rudder,
   autopilot-response or thrust-asymmetry parameter — `windmilling_per_engine` is a symmetric drag
   increment and the core's `single_engine_*` parameters govern its own pre-00:11 phase, not this
   one. The single-engine minutes above are therefore flown as a symmetric point mass, against a
   ruling that assigned this module the yaw, autopilot response, drift-down and turn before the
   second flame-out in its 6-DOF simulation. Until that exists, every single-engine segment is a
   declared approximation and the 36.9 per cent figure above belongs beside it.
""", "§5 engine structure")

ed6("""- **Per-engine flame-out.** After the single-event version works.""",
"""- **Per-engine flame-out** — superseded as written; see the correction in §5. The fuel and
  performance half is built in both stages. What remains deferred is narrower and should be stated
  as such: the **asymmetric-thrust dynamics** of the single-engine phase, and emission of the first
  flame-out time alongside the final one.""", "§13 deferral")

ed6("""8. **The output of §2 rule 12**, the silent-exclusion review, as a table in each run note.""",
"""8. **The output of §2 rule 12**, the silent-exclusion review, as a table in each run note.
9. **The first flame-out time as an emitted column**, beside the final one, with the engine count
   through the terminal trajectory rather than only at onset — see §5. Without it the single-engine
   segment cannot be measured by a consumer or diagnosed by this module, and 36.9 per cent of weight
   has one engine running at descent onset.""", "deliverable 9")

ed6("| L | the ordering — simulate, then test, never shape — leads the mission | §1 |",
    "| L | the ordering — simulate, then test, never shape — leads the mission | §1 |\n| M | **correction**: the two-engine flame-out structure is already built; the deferral is narrowed to asymmetric dynamics and first-flame-out emission | §5, §13, §10.9 |")
ed6("Twelve changes. A–C alter what the module is obliged to produce",
    "Thirteen changes. A–C alter what the module is obliged to produce")
ed6("**Version 5, 13 October 2026.**", "**Version 6, 13 October 2026.**")
ed6("Twelve changes, listed in §0.", "Thirteen changes, listed in §0. Change M corrects a factual error carried by versions 1 to 5.")
open("end-of-flight.md","w").write(v6)
print(f"\nv5 {len(v5):,} -> v6 {len(v6):,} chars")
