# MH370 airborne position at the 00:11 UTC sixth arc

## Result

The refined random BFO measurement standard deviation is **0.995 Hz** (95% Gaussian reference interval **0.859–1.183 Hz**). This estimate uses 78 successive differences from the 18:39 and 23:14 call clusters. It removes the mean difference within each cluster, so a locally constant or slowly changing bias is not added to the random-noise variance.

| 00:11 airborne posterior | 2-D mode | Marginal median | 95% marginal latitude interval | P(south of 36°S) |
|---|---:|---:|---:|---:|
| Without ocean-drift evidence | 36.50°S, 89.29°E | 36.30°S, 89.60°E | 32.80–37.71°S | 61.7% |
| With drift evidence, backward-smoothed | 36.41°S, 89.43°E | 36.14°S, 89.83°E | 32.33–37.66°S | 55.1% |

The model-averaged drift evidence moves the marginal median about **14.8 nautical miles north-east**. It is deliberately weak relative to the satellite/RF posterior.

## BFO-noise estimate

For BFO reading \(y_{jt}=\mu_j+b_{jt}+\epsilon_{jt}\) in call cluster \(j\), successive differences satisfy

\[
d_{jt}=y_{jt}-y_{j,t-1}, \qquad \operatorname{Var}(d_{jt})\simeq 2\sigma_\epsilon^2
\]

when the bias is locally constant. After removing each cluster's mean difference,

\[
\widehat{\sigma}_\epsilon^2=
\frac{\sum_j\sum_t(d_{jt}-\bar d_j)^2}{2\times 76}.
\]

The separate cluster estimates are 0.958 Hz (18:39) and 1.060 Hz (23:14); their pooled estimate is 0.995 Hz. The raw within-cluster standard deviations are 1.260 and 1.688 Hz, and the pooled raw standard deviation is 1.429 Hz. Those raw values are higher because they retain within-cluster baseline movement as well as fast noise.

Under the ideal independent Gaussian-difference reference model, \(\sigma=1.5\) Hz is rejected against an unrestricted scale estimate (two-sided reference \(p=1.12\times10^{-5}\)). This p-value should not be over-read because the logged BFO values are integer-quantized and successive differences overlap. Agreement between the two independent call clusters is the more useful robustness check.

The earlier **12 Hz** value was not an estimate of receiver measurement noise. It was a deliberately conservative *effective* scale for an added vertical-rate likelihood, absorbing trajectory/satellite-state uncertainty and possible BFO bias. Labelling it as a BFO SD was therefore misleading. In this run, no intermittent-bias variance is added in quadrature to the 0.995 Hz random scale.

## Controlled-flight implications

With equal prior probability for three controlled-flight families, the no-drift posterior probabilities are:

| Flight family at 00:11 | Posterior probability |
|---|---:|
| High-altitude / near-level | 72.47% |
| Earlier descent completed / lower-level | 27.50% |
| Active controlled descent | 0.037% |

The result does **not** exclude an earlier descent followed by level flight. It strongly disfavors a material vertical rate at the exact 00:11 measurement under the ordinary-noise component. A separate, contemporaneous BFO bias event could rescue active-descent paths, but its occurrence probability and magnitude must be modelled as a distinct latent mixture; widening the random Gaussian to represent that event would repeat the error this refinement is intended to avoid.

Across the 95% interval for the estimated random SD, the active-descent probability ranges from 0.009% to 0.136%, while the median latitude changes by less than 0.001°. At the previous 1.5 Hz fast-noise setting, the active-descent probability is 0.493%.

## Treatment of drift and end of flight

The “with drift” map still shows the aircraft's **airborne 00:11 state**. Debris likelihood is evaluated only at sampled impact states and then smoothed backward through the marginalized terminal-flight kernel:

\[
p(x_{00:11}\mid D,\text{debris}) \propto
p(x_{00:11}\mid D)
\sum_h\int p(x_I\mid x_{00:11},h)\,p(\text{debris}\mid x_I)\,dx_I.
\]

The terminal model averages controlled descent/ditching, fuel-exhaustion plus controlled glide, and a short uncontrolled descent. The debris term averages equal-weight normalized approximations to the Davey drift result and the 12-study latitude meta-analysis. It is not applied directly at the sixth arc.

No 00:19 BTO, BFO, log-on, or other end-of-flight observation is used.

## Important limitation

The original refined-v3 particle checkpoint is not available in the project files. The reported multimodal BTO+BFO+received-power posterior is reconstructed from its published summary, then augmented with altitude, vertical-rate, performance, and terminal-state variables. Exact particle-level correlations among location, Mach, heading, antenna-gain survival, and the latent BFO bias are therefore unavailable. These are research-grade conditional maps, not an exact full SMC rerun from the radar epoch.
