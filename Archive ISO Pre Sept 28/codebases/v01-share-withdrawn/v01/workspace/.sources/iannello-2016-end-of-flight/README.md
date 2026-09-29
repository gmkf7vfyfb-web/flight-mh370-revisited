# Public Boeing end-of-flight trajectories

Paper: Iannello and Guillaume (2016), bundled at `paper/paper.pdf`.
The PDF SHA-256 is
`48ab64e32f564896f0e3f90e547edb51a17fc87508ae39b8beb89ec655506255`.
The ten-case trajectory archive SHA-256 is
`e400ac73478dff8698cd344a69d7969804f6adb0eb2121d5cacd3b58d63111db`.

Run the independent audit with:

```bash
node code/run.mjs
node --test code/audit.test.mjs
```

The calculation reproduces cases 03, 04, 05, 06, and 10 as exceeding both
15,000 ft/min descent and 0.67 g downward acceleration under one- and
eight-second acceleration windows. From the first 15,000 ft/min sample to the
last recorded point, those cases travel 4.707–7.974 NM.

This is not a distribution over real MH370 outcomes. The ten engineered cases
lack probability weights, local-to-geographic orientation, exact seventh-arc
alignment, water-contact samples, and complete simulator priors. The canonical
runner therefore exposes end-of-flight displacement only as a named conditional
model and leaves it disabled in the production baseline.
