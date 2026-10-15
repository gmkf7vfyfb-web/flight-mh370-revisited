# Islands check (core, 15 Oct 2026): do more, smaller independent filters keep more northern lineages?
Pete: no run K, so the northern sampling fix goes into run J. Run I's 7M-per-seed waypoints seeds keep 11–77
effective lineages north of 33 S, weighted by the composer's evidence ratio r(lat) = drift + searches (D0) ÷
flight data only. This test flies the same waypoints chain as run I with the same total particles split into
more seeds:
- 4 × 1.75M (`islands-4.toml`);
- 8 × 0.875M (`islands-8.toml`).
Hand-offs, look-ahead and trace are off; they are output-only and do not change the filter.

Pooled effective lineages are compared with run I's single 7M seeds. If 4 islands give about 4× the lineages of
one 7M seed, more seeds is the run-J fix. If not, the fix is an evidence-tilted filter.

Chain: run I next-i-waypoints config_paths without handoff-lookahead-d.toml and server-i-sampler.toml, then
the islands file.
