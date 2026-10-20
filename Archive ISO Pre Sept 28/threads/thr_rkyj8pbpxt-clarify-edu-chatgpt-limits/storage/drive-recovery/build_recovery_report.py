"""Render the recovery record from local verification receipts; no inference."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = Path('/jackbox/home/MH370')
receipt = json.loads((ROOT / 'recovery-receipt.json').read_text())
comparison = receipt['stable_source_comparison']
audit = receipt['rerun_factor_audit']
waypoint = receipt['waypoint_weight_audit']
archives = receipt['archives']
assert audit['semantic_comparison_passed'] and waypoint['passed']
assert all(not row['failures'] for row in receipt['member_verification']['checks'])

def link(label, relative):
    return f'[{label}]({ROOT / relative})'

archive_rows = '\n'.join(
    f"| `{Path(a['path']).name}` | {a['bytes']:,} | `{a['sha256']}` |"
    for a in archives
)
text = f'''# Recovered EDU research work

Recovered and checked on 20 September 2026 from the authenticated `mh370:`
Google Drive remote. This is an intake and verification record, not a new
aircraft-location estimate. Original Drive files were read only. The full
background library and original review package were inventoried, not duplicated.
Three superseded waypoint working ZIPs were also left on Drive; the later
complete waypoint archive was recovered instead.

## Recovery and source identities

The local recovery is outside the product workspace:
`{ROOT}`.
It contains the returned code, original inputs, weather, results, reports,
failed trials, historical snapshots, and the preserved offline Rust environment.

- {link('Machine-readable recovery receipt', 'recovery-receipt.json')}.
- {link('Drive file inventory', 'drive-inventory.json')}:
  {receipt['inventory']['files']:,} files, including unretrieved background material.
- {link('Product file identities at intake', 'current-product-files.json')}.
- {link('Current versus returned source comparison', 'source-comparison.json')} and
  {link('Rust source diff', 'stable-source-comparison.patch')}.

The copied workspace has no `.git` directory. File identities above define the
comparison; no Git revision or merge is claimed.

| Returned work | Entry point | Status established here |
|---|---|---|
| Rerun | {link('Latest factor-attribution findings', 'rerun/inspection/MH370-Rerun-checkpoint-24-20260919T234221Z/MH370-Rerun-findings-24.md')} | Stable source is the original checkpoint 20; later bridge experiments remain separate. The Gaussian ensemble and its subsequent audit are both recovered. |
| IGOGU and FIR | {link('Earlier final handoff', 'igogu/download/IGOGU_FINAL_20260919_START_HERE.md')} | Six archives restored in their declared order, including original weather and survivor bytes. |
| Later waypoint analysis | {link('Latest waypoint README', 'igogu/waypoint/README.md')} | Later work supersedes the earlier statement that no waypoint controls ran. Spatial controls are present; full reconstruction-null calibration remains unfinished. |
| Resolution | {link('Final scientific and recovery index', 'resolution/handoff/START-HERE_HANDOFF_VERIFIED_20260919T2205Z.md')} | Final synthesis and 21 embedded dependency ZIPs recovered. Its older Rerun source does not supersede the later Rerun handoffs. |

## Checks actually executed

- Downloaded and retained {len(archives)} reconstructed or standalone archives.
  Nine main archives match published whole-archive SHA-256 values, after checking
  all {sum(a.get('parts', 0) for a in archives)} manifest-listed payload files.
- Verified the core archive CRC and restored its 16,056 file/symlink entries
  with the supplied content-addressed restorer, which verifies each content blob.
- Verified 873 original IGOGU research members, 37 final-supplement members,
  344 later waypoint members, and 63 final Resolution members by SHA-256.
  All 21 nested Resolution ZIP CRC checks passed.
- Verified the returned stable-source, Gaussian-ensemble and factor-audit
  manifests: 233, 257 and 66 files respectively.
- Reran all eight factor-audit tests, including joint-Gaussian covariance,
  observation-order, shared-bias ablation, ancestry and weighted-CDF controls.
  Recalculated the full saved-bank audit in a separate validation directory.
  Maximum absolute numeric difference from the saved result:
  `{audit['maximum_absolute_numeric_difference']:.12g}`; no semantic mismatch.
- Independently normalized the waypoint archive's saved log contributions:
  {waypoint['contributions']:,} contributions, importance ESS
  {waypoint['importance_ess']:.9f}, largest weight
  {100 * waypoint['largest_weight']:.6f}%. These reproduce its summary.

The test run took {audit['runs'][0]['elapsed_seconds']:.3f} seconds; the saved-bank
audit took {audit['runs'][1]['elapsed_seconds']:.3f} seconds, with peak child RSS
{audit['runs'][1]['max_rss_kib']:,} KiB on this host. The waypoint arithmetic took
{waypoint['elapsed_seconds']:.3f} seconds. Versions and original environments are
retained in the returned packages. These local checks used the existing project
Python environment, not a claim of an exact recreation of the EDU environment.

No new flight simulation, full Rust test suite, aircraft calibration, destination
significance claim, or sonar-coverage validation was performed during intake.
Passing integrity and arithmetic checks does not make an unconverged estimate
a calibrated posterior.

## Integration decisions

The returned stable source has {len(comparison['identical'])} files identical to
the current product, {len(comparison['changed'])} changed files, and
{len(comparison['new'])} additional files. It is not a drop-in replacement:

- Its workspace and runner manifests omit the current `search-evidence` spoke.
- Its spatial report replaces the actual source-population count with a
  hard-coded count of four.
- Its cruise configuration re-enables an initial proposal where the current
  configuration explicitly has `null`.
- It retains rejected sampler alternatives and experimental bridge modules;
  test success alone does not justify importing those into the product.

Not integrated: wholesale replacement of the current runner/source, the
unconverged waypoint location measure, and unvalidated physical bridge
alternatives. The canonical estimator and its configured scientific target are
preserved. Returned investigations remain in external recovery storage; no
parallel product implementation or Cargo dependency on that storage was added.

The accepted addition to the project is the recoverable evidence and this
verified status record. The local audit confirms the returned finding of large
between-seed CDF differences and strong proposal-correction concentration.
Removing the required prior/proposal corrections or deleting a stored BFO
factor without refitting the shared bias would change the target incorrectly.
The waypoint calculation remains an explicit route-conditioned alternative.
Neither set of weights is multiplied into the current posterior.

## Reproduce the local continuation check

All numerical outputs go to a validation copy; archived files stay unchanged:

```bash
cd {ROOT / 'validation/factor-audit'}
{PROJECT / '.venv/bin/python'} -m unittest -v test_audit.py
{PROJECT / '.venv/bin/python'} audit.py --source audit-inputs
```

The copied audit/test source is byte-identical to the verified returned source.
The `audit-inputs` and replay directories point to the restored data. The
{link('verification receipt', 'validation/factor-audit/verification.json')}
records the comparison against the archived result.

To recover on another host, copy the exact archive payloads from
`mh370:IGOGU conditional`, `mh370:MH370 Review/Rerun`, and
`mh370:MH370 Review/Resolution/Final_recovery_bundle_20260919`.
The downloaded manifest files preserve byte counts and SHA-256 values; the
Drive inventory also preserves file IDs. Follow each linked handoff's restore
command into a fresh directory. The waypoint archive has its separate
`MH370_analysis_REASSEMBLY.json` and must be joined in listed part order.

The next implementation target is to port the opt-in factor/ancestry diagnostics
into the current runner while preserving its current source-count reporting,
search-evidence spoke and proposal configuration. Validate exact replay equality
before considering any new sampler. Then compare corrected, same-target
proposals with independent synthetic recovery and matched compute budgets.
Current evidence does not justify a larger location claim or new evidence fusion.

Regenerate this intake report from the verification receipts:

```bash
python3 {ROOT / 'build_recovery_report.py'}
```

## Archive ledger

Hashes identify received bytes, not peer-reviewed scientific correctness.

| Archive | Bytes | SHA-256 |
|---|---:|---|
{archive_rows}
'''
destination = PROJECT / 'publication/review/RECOVERED-WORK.md'
destination.write_text(text)
(ROOT / 'README.md').write_text(
    '# MH370 Drive recovery\n\n'
    f'The recovery and integration record is [{destination.name}]({destination}).\n\n'
    'See `recovery-receipt.json` for verified identities, checks and scope.\n'
)
print(destination)
