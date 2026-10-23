cd "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/462da3b0-2381-4cf6-84db-fe178606bed4/repo/Claude Science Project Sep 29/coordination"
cat > /tmp/standin_entry_body.md <<'EOF'
`results/hydroacoustics-next-run-b-standin.md` (+ `.png/.pdf`, data in `results/hydroacoustics-next-run-b-standin/`). **Labels:** core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; uncorrected fuel; provisional sampler. **Run by an architecture stand-in on the module's behalf; module to review.**
- **Recipe:** the module's `prepare/search_windows.py` @ `438c9e9` (unchanged, sha256 `1b05492b…`). Weights: EoF `option_posteriors` @ `15ba915` (byte-identical at `3c6319f`). It ran once per stratum on `end-of-flight/next-run/`, at 1-2 threads, with no code changes. A stand-in wrapper combines strata by core's P(family) (0.6948 / 0.1527 / 0.1376 / 0.0149, held fixed) and reproduces the script per stratum exactly (0 of 4,896 quantiles differ).
- **Validation:** the pre-registered gate was NOT run, because EoF has no impact-time-shares JSON for next-run. ESS matches EoF's sweep summaries and `mixture.json` to ≤ 1e-13 relative.
- **Held out +alive (mixture):** 0.5 / 50 / 99.5 % at 00:19:58 / 00:40:16 / 01:11:26 UTC (ref-289: 00:19:58 / 00:40:18 / 01:29:24). Share after 01:15:56 is 0.26 % (ref-289 2.1 %). Medians and early edges are within about 1 min; the late tails of `other`-cause arms are 3-21 min shorter. The descent idle floor is now ON; the cause of the shift has not been attributed.
- **Recommended SOFAR windows, +alive / +silent:**
  - H01W 00:25-02:05 / 00:25-01:50
  - H08S 00:45-02:30 / 00:45-02:15
  - H08N 00:50-02:30 / 00:50-02:15
  - Perth Canyon 00:25-02:05 / 00:25-01:55
  - Scott Reef 00:35-02:25 / 00:35-02:10
  - Portland 00:50-02:30 / 00:50-02:20
  - Starts are unchanged and ends are 5-20 min earlier than on reference-289. **The module's raw IMS request (H01W 00:25-02:20, H08S/H08N 00:45-02:50) still covers everything; no change is needed.**
- **The end edges are still UNCONVERGED:** 134 of 640 estimable +alive/+silent rows, all `other`-cause, with a replicate spread of 5.0-13.9 min.
- **H1 and H2 are NOT ESTIMABLE:** ESS 86 and 124.
EOF
ts="2026-10-10 ~$(date -u +%H:%M) UTC"
for f in HYDROACOUSTICS.md architecture.md SEARCHED_AREAS.md PLEIADES.md; do
  { printf "\n## %s - architecture (stand-in for hydroacoustics): search windows re-derived on core (b) impacts. PROVISIONAL-OVERNIGHT\n\n" "$ts"; cat /tmp/standin_entry_body.md;
    if [ $f = HYDROACOUSTICS.md ]; then printf "\n**Hydroacoustics, please review:** the P(family) mixture and the replicate-convergence rule are a stand-in construction, not in your pre-registered script. Adopt, amend or replace them. Re-run yourself if you disagree.\n"; fi
    printf "\n- Modular Architecture (stand-in for Hydroacoustics)\n"; } >> $f
done
{ printf "\n## %s - architecture (stand-in for hydroacoustics): request for an impact-time-shares file on next-run\n\n" "$ts"
  printf "Hydroacoustics' search windows on \`end-of-flight/next-run/\` (\`results/hydroacoustics-next-run-b-standin.md\`) could not pass their pre-registered validation gate. That gate needs your impact-time-shares JSON for the same impacts, as in \`results/eof-impact-time-oct10/impact-time-shares-reference-289.json\`. **Request (not overnight-urgent):** when you review the stand-in sweep, please produce one for next-run. Please also attribute the shorter late tail (held out +alive, share after 01:15:56: 0.26%%, against 2.1%% on reference-289) to the hand-offs or to the descent idle floor. ESS already matches your sweep summaries to <= 1e-13.\n\n- Modular Architecture (stand-in for Hydroacoustics)\n"; } >> END_OF_FLIGHT.md
tail -3 HYDROACOUSTICS.md; git -C .. status --short | head