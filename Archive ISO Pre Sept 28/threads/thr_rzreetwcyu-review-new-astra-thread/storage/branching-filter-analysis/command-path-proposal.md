# Command-history proposal experiment

This is an isolated computational correction in
`/tmp/mh370-cruise-command-proposal`; it is not yet integrated or a stability
claim. It changes no flight, SATCOM or fuel prior. Existing guided proposals
can accumulate a separate command-density correction at every manoeuvre.
The experiment mixes complete command histories over each physical
observation interval, including any fuel-anchor split inside that interval.

For a complete latent interval history z, write the target density as
`p(z) = p_t(z) p_c(z)`. Here `p_c` is the product of physical command densities;
`p_t` includes all remaining transition densities. The existing guided
component has command-density product `g_c`. Its event-time proposals and
other transition densities, `q_t`, are common functions of a complete
history under both command components, including history dependence.

Choose one component before propagating the interval:

```
q(z) = q_t(z) [rho p_c(z) + (1-rho) g_c(z)]
p(z)/q(z) = [p_t(z)/q_t(z)] /
           [rho + (1-rho) exp(log g_c(z) - log p_c(z))]
```

Both branches evaluate the same cell probabilities at every realised command.
The prior branch chooses a uniform prior cell; the guided branch uses the
existing corrected cell sampler. The event-time correction is accumulated
separately. The complete command correction is applied once, after propagation.
It is at most `1/rho`, irrespective of the number of command changes. This
bound applies to this importance factor, not to posterior weights, sampling
error, likelihood concentration or the full-flight product across intervals.

The experiment reuses the existing `uniform_mixture` as rho (0.2 in the planned
controls), with `mix_command_paths=true`. A missing or false flag preserves
the original random stream and correction path. Commands inside the existing
minimum guide horizon keep their common prior density in both components.
Forecast failures retain the same positive prior support.

The independent control enumerates every history of four binary command/time
pairs, with both command guides and timing densities dependent on history.
It verifies the joint target probability of every path, both normalizers,
an event probability, the correction bound and extreme logarithmic ratios.
All 64 estimator and 72 particle-filter checks pass. A default-path coupled
run must reproduce the archived 1,000-candidate CSV, histories and evidence
before fresh synthetic pilots are launched. Those pilots will use the same
four fixed fuel-conditioned fixtures 0, 2, 4, 6, without reading their truth.
They will compare against both the original guide and the completed unguided
diagnosis; no outcome-based fixture selection or physical-model averaging.
