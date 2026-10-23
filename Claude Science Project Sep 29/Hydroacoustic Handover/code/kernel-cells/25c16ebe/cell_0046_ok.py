# --- I. Interface: emission location, NaN discipline, energy partition ---
ed("""Two further hooks exist, stubbed and documented, with no physics behind them yet: a debris-class
output and a **sink-versus-float** flag.""",
"""**Three emission rules, added 13 October after an audit found all three broken in the current
runs.** They are contract, not guidance.

- **Emitted means emitted in the impact sample.** The six energy-transfer columns are entirely
  non-finite in `impacts32.npy` and τ is carried in a per-seed sidecar joined by row order. A
  consumer that must join two arrays positionally to get a field the contract rules in does not
  have the field. Write them into the impact sample.
- **A quantity not computed for a family is NaN for that family.** Rule 4 already says NaN means
  "not computed"; a placeholder value breaks it, because a consumer cannot tell a placeholder from
  a measurement. Attitude at impact is currently assigned wings-level for the controlled families
  and 52 per cent of posterior weight carries exactly zero bank. Either compute it or emit NaN —
  not zero.
- **Energy delivered to the water is not total kinetic energy.** The transferred-energy field
  currently equals total kinetic energy to float32 precision, so the model delivers all of it to
  the sea with nothing going into structural deformation, fragmentation or airborne debris. Either
  carry the partition as a declared alternative with a sampled fraction, or label the field an
  upper anchor **everywhere it is quoted**, including in hydroacoustics' own figures.

Two further hooks exist, stubbed and documented, with no physics behind them yet: a debris-class
output and a **sink-versus-float** flag.""", "I emission rules")

# --- A. Build status ---
ed("""| The EoF **model** | **does not exist.** `hypotheses/arc-kernel` is plumbing whose own docs say "not a model"; its impact energies are NaN |
| Stage-4 composer | **not built**; `main.rs` rejects `[[compose]]`. Until it exists, use `mh370 evaluate` on an impacts file |

So: build the model, not the interface.
""",
"""| The EoF **model** | **built and run at full scale twice.** Run I (12 Oct, binary `mh370-eof-ri1`) and run-i-dive (13 Oct, `mh370-eof-ri3`), each 8 seeds × 4 strata × 100,000 m0011 hand-off rows, 6.40 M descents per stratum-seed. Run-i-dive supersedes run I. Notes: `results/eof-run-i-oct12.md`, `results/eof-run-i-dive-oct13.md` |
| Descent physics | **provisional on four counts, all declared in the run notes**: interim parametric pitch-down with the 6-DOF gate unpassed (§8), no transonic drag rise, provisional turn model, provisional in-flight structural model |
| Boeing calibration | **cruise half done, descent half not.** Burn and endurance reproduce the published tables over 27 items at −5.2 to +11.0 per cent; the phugoid period agrees at 78–86 s against 82–87 s when the module's own trim at loss of control is used. The ten engineering-simulator traces have **not** been fitted as traces — see the gate in §8 |
| The 22:41 arms (V1b, V2) | **not run on current physics.** Only the 11 Oct stand-in on core run D, itself unconverged, on physics that could not reach descent rates above 6,500 ft/min or unload the aircraft. Its Bayes factors are not to be carried forward |
| Stage-4 composer | **not built**; `main.rs` rejects `[[compose]]`. Until it exists, use `mh370 evaluate` on an impacts file |

So: the interface and the sampler are built; what is outstanding is descent fidelity, the 22:41
arms, and the sampling collapse of §8. **This table is updated at the end of every full sweep, not
at the next revision of this prompt.** It was six days stale on 13 October and told a reader the
model did not exist.
""", "A build status")
print(EDITS)
