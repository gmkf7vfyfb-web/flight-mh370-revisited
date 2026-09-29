# Rerun checkpoint 2 — bottleneck instrumentation and boundary reconciliation

19 September 2026. This extends checkpoint 1; it does not replace its archived results.

## Outcome

The exact synthetic source has now been traced through its actual blocked-filter execution route. A contact-level tracing API and BTO/BFO factor reconstruction helper have been implemented in an isolated candidate copy. Tests compare the new trace with the **unchanged** block method, including the subsequent random-number state. A separate fuel-boundary change-of-variables implementation and tests prevent silently moving a fuel prior to the wrong epoch.

These are implementation and source-reconciliation results, **not a new aircraft posterior**. No full-aircraft sampler was launched, no other thread's source or lease was changed, and no replacement estimator is validated. The relative contribution of measurements, proposal tails and support loss remains to be measured on actual particle banks. Hydroacoustics remains excluded.

## What the source establishes about 18:39–19:41

The archived runner selects the bootstrap algorithm and groups every BFO-only contact with the next BTO-bearing contact. It therefore processes 18:39:55 and 19:41:02 inside one block, at their original times, with no intermediate resampling. `ObservationBlockModel` does not forward the underlying model's `guide_log_likelihood`; its default auxiliary guide is zero. Moreover, the selected bootstrap algorithm does not use an auxiliary ancestor guide.

This distinguishes three mechanisms that should not be conflated:

1. The optional future-potential/auxiliary ancestor guide is **not active in this archived execution route**. Changing only its floor cannot fix this particular blocked run.
2. Guided command proposals, turn-time proposals and first-turn event oversampling **are active**, with prior/proposal corrections returned by propagation.
3. The actual call and handshake likelihoods are applied once at their own times, updating the shared BFO-bias state. They are accumulated before the block-end weight/resampling operation.

This is not proof that blocking is erroneous. Blocking deliberately avoids prematurely undoing a look-ahead proposal before the next range observation arrives. Splitting the block and adding resampling is an algorithm change, not a harmless diagnostic.

The configured 20% uniform component bounds an individual guided command or time-cell p/q factor above by 5. The 95% first-turn boost has a no-event branch whose p/q is 20 whenever that boost applies. Products across events can be more dispersed; a single-factor bound is not a bound on an entire trajectory's weight. These corrections are mathematically intended, not newly identified bugs. Their **realized** contribution must be logged before blaming them for collapse.

### Shared-bias contraction is part of the measurement model

With the archived 25 Hz prior bias SD and sequential 7 Hz BFO observations, the two 18:28 updates reduce conditional bias SD to 4.8555 Hz. The predictive BFO SD is then 8.5191 Hz at the 18:39 call and 8.0571 Hz at 19:41. This calculation is exact for the archived scalar static-bias update and is independent of the residual values, conditional on a supported path.

Consequently a large initial bias uncertainty does not remain a free 25 Hz adjustment later in each candidate's likelihood. But the mixture of conditional bias means across different paths may remain broad. These numbers **do not measure overall aircraft uncertainty or demonstrate which factor caused genealogical collapse**. Resetting bias for each contact would change the target and improperly discard cross-contact information.

## New implementation and tests

Candidate directory: `candidate-20260919T0334/`. Original archive remains unchanged and authenticated by SHA256 `2a6f995ebb143f86af510519374c7ad6b5abff5c992a8dcceda70a7c0298f8f3`.

- `propose_with_contact_trace` exposes contact time, transition log p/q, observation log likelihood, and pre/post-observation state. It does not introduce resampling or RNG draws. The existing production method remains untouched.
- `observation_factor_logs` reconstructs the separate BTO and BFO factors from the saved fit and **pre-update** bias variance. It does not re-assimilate the observation. Fuel and initial-guidance deltas remain separately identifiable by subtracting the SATCOM factor from the contact likelihood and reading corresponding state fields.
- New randomized tracing checks cover 32 fixed seeds, exactly equal state/likelihood/proposal sums and the next RNG output, and invalid time/empty-block rejection. SATCOM tests cover both measurements, either alone, disabled BFO and empty-observation rejection, and catch using the wrong post-update variance.
- Five new Python boundary tests cover inverse maps, normalized Jacobians, unit weights for transformed anchor-prior draws, corrected broad-uniform proposals, path-dependent support and invalid parameters.

The checked Rust package suite passes 73 particle-filter tests and 15 SATCOM tests. The five Python boundary tests and eight-run source audit also pass. See `verification.json` and logs for exact commands, hashes and compiler details. These unit tests are not matched-budget aircraft validation. The earlier finite-state smoother/bridge suites were not rerun.

Two development failures are retained: a Rust test initially moved a non-Copy observation, and a later test incorrectly expected an empty observation to be accepted. Both were corrected in test setup/expectations; the failed logs and receipt remain. Neither produced an inference result.

## Radar epoch and fuel boundary

All ten final-radar CSV rows independently imply an origin of **18:22:12 UTC**. That is 1,223 seconds after the broad reference's 18:01:49 origin. Keeping the same physical anchor at 18:28:05.9 means its new offset is **353.9 seconds**, not 1,576.9 seconds. The conditional exhaustion windows become:

| Hypothesis | Offsets from 18:22:12 |
|---|---:|
| 00:15–00:17 | 21,168–21,288 seconds |
| 00:15–00:19 | 21,168–21,408 seconds |

This resolves configuration time arithmetic, **not radar measurement provenance**. The supplied 6.578 N, 96.340 E coordinates and 2 NM / 2 degree scales remain configuration choices whose original measurement/covariance basis has not been verified. The ATSB's 18 August 2014 report confirms a last primary-radar fix around 18:22 and discusses radar-based fuel estimates; it does not establish those exact configuration precision assumptions in the text examined. [ATSB, Definition of Underwater Search Areas, pp. 3 and 16](https://www.atsb.gov.au/sites/default/files/investigation-reports/ae-2014-054_mh370_-_definition_of_underwater_search_areas_18aug2014.pdf).

The exact legacy fuel model initializes its maps **at the future anchor**, and its advance method returns without integrating any segment ending at or before that anchor. Thus the old 32,524.10–34,524.10 kg uniform anchor prior is not an estimate at the radar epoch, and the old state contains no reconstructed pre-anchor fuel burn. Fuel performance support is separate from the `CruiseParticle.supported` environmental flag; record both in a physical diagnostic.

For a forward radar-to-anchor gross-mass map `M_a = A M_r + B`, with `A > 0` and zero-fuel weight `Z`, the correct conditional transformation is:

`F_r = (Z + F_a - B)/A - Z`.

Given the legacy anchor prior uniform on `[L,U]`, its density in radar-fuel coordinates is `A/(U-L)` on the transformed interval. An independent radar-fuel proposal therefore needs `log(A) - log(U-L) - log(q_r)`, within support. If the proposal draws anchor fuel uniformly and transforms it, that particular density ratio is one. The path and shared flow-scale proposal ratios still remain.

`boundary_transport.py` implements this map and density, not aircraft fuel burn. Its example maps are explicitly illustrative. A real application must compute A and B from the actual intervening trajectory and common fuel-flow discrepancy, preserve static state/control memory and no-jettison assumptions, and respect the mass-independent kinematic approximation of this source. Fuel exhaustion time remains an explicit conditional hypothesis, not a measured terminal location.

## Next executable work

1. Integrate the tracing hook through an opt-in isolated runner wrapper, keeping root/child IDs and actual initial physical states alongside every pre/post-contact row. Include environmental and fuel support, event counts, separate SATCOM factors and initial-guidance deltas; retain rejected rows and pre-resampling weights. Avoid serializing nonfinite weights as ambiguous nulls.
2. Prove full scientific replay identity with tracing disabled/enabled at fixed seeds and particle budgets before interpreting factors. The current 32-seed generic unit test is necessary but not sufficient for this.
3. At 18:39 and 19:41, calculate row and ancestral ESS on the same proposal bank under chronological cumulative factors. Also examine order sensitivity or a symmetric factor allocation; ESS changes are nonlinear and correlated, so these are attribution diagnostics, not unique causal percentages or independent likelihoods. Never reset the bias when removing a past factor without re-deriving the intended diagnostic target.
4. Evaluate guided bridges on the preserved historical target before adopting a separately labelled radar-boundary target. Positive potentials require the usual new/old potential ratio and explicit initial/final untwisting; a hard endpoint band that excludes prior support is not support-preserving. Endpoint q must be divided out and is not an observation.
5. Complete radar source/covariance provenance and forward pre-anchor fuel maps before physical two-ended bridge trials. Keep 00:15–00:17 and 00:15–00:19 as separate hypotheses. Do not add 00:19 measurement likelihoods to a through-00:11 target implicitly.

The other review's A/B lanes retain their recorded ownership. Heartbeats were inspected, but this process namespace cannot establish that another thread is idle. No lease was acquired or rewritten. This checkpoint is an independent diagnostic and does not alter Resolution work or automations.
