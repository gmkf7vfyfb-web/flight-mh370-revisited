v5 = v4
EDITS = []
def ed(old, new, label):
    global v5
    assert v5.count(old) == 1, (label, v5.count(old))
    v5 = v5.replace(old, new); EDITS.append(label)

# --- L. Mission ordering at the head of §1 ---
ed("""The module exists to produce an honest posterior, not to decide what happened. Simulations are for
learning physics, not for settling the question.
""",
"""**The ordering is the method, and it is not negotiable.** Simulate what the aircraft is likely to
have actually done after fuel exhaustion, as faithfully as the available information and resources
allow. *Then* test those simulations against the evidence. Never shape the simulation to match the
evidence. Because the 00:19 measurements are questioned — the R1200 channel particularly — the
purpose of scoring subsets of them is to see which fit the simulated population and which do not,
and so to learn which data to use and which to set aside. That inference is only available if the
simulated population was built without reference to the fit. A model tuned until it matches 00:19
cannot then be used to ask whether 00:19 is trustworthy.

The module exists to produce an honest posterior, not to decide what happened. Simulations are for
learning physics, not for settling the question.

Rule 11 of §2 and test 6 of §11 are the mechanisms that make the ordering demonstrable rather than
merely asserted. Neither existed in the previous version, and the first support change made without
them — the dive branch of 13 October — had to be audited after the fact to establish that it was
sound. It was; the point is that the contract could not have told you so.
""", "L mission ordering")

# --- H. ESS reporting ---
ed("""6. **Measure ESS and split-half replicate agreement; report unconverged as unconverged.** The fix
   is the sampler, never the smoothing. Use `skill("mh370-run-reporting")` for the conventions.""",
"""6. **Measure ESS, the weight concentration, and split-half replicate agreement; report unconverged
   as unconverged.** ESS alone is not sufficient and has already misled once: under both 00:19
   bursts on the raw measurement model a stratum-seed shows ESS 38.8 over 100,000 parents **and**
   a largest-single-trajectory share of 12.3 per cent with a top-ten share of 33.5 per cent. The
   second pair is what tells you a shape is not estimated. Report **per seed and per stratum beside
   the pooled figure** — pooled "effective impacts" over 8 seeds × 4 strata reads an order of
   magnitude healthier than any replicate actually is. The fix is the sampler, never the smoothing.
   Use `skill("mh370-run-reporting")` for the conventions.""", "H ess + concentration")

# --- F. New contract rule 11: support changes ---
ed("""10. **Descent physics lives in this module**; the measurement model lives in `satcom`; composition
    lives in the composer. Do not reimplement a measurement model here.
""",
"""10. **Descent physics lives in this module**; the measurement model lives in `satcom`; composition
    lives in the composer. Do not reimplement a measurement model here.
11. **A change of proposal and a change of support are different events, and the second is logged.**
    §8's exact importance weighting makes a change of *proposal* harmless, and that is provable —
    see test 6 of §11. It says nothing about a change of what the model can *reach*. Every change to
    the model's reach — a new branch, a widened bound, a probability moved off zero — is recorded in
    the run note with: the physical justification; **whether it was prompted by a fit failure**; and
    the held-out log-evidence and held-out impact median before and after. A reach change that moves
    the held-out answer is a different event from one that does not, and the distinction is what
    settles a forcing question later rather than by argument.
12. **Run the silent-exclusion review before every sweep.** List every bound, every configured
    range and every zero weight in the envelope, and for each state whether its justification is
    independent of how well anything fits 00:19. This exists because the sampler's own diagnostics
    cannot find these: a fit failure makes the model press on the exclusions the data cares about,
    so those get found and removed, while exclusions the data is silent about survive indefinitely
    and quietly make one hypothesis better explored than its alternative. The review is the only
    procedure that corrects the asymmetry. §§4 and 10 name the current answers.
""", "F support-change rules 11-12")
print(EDITS)
