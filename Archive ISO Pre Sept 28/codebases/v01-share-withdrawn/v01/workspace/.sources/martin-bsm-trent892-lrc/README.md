# Martin/BSM Trent 892 LRC release family

This package records the exact, narrow transcription used by the v0.1 conditional
end-of-flight runner from the user-supplied workbook
`Martin-full-model-BSMv7-9-4.xlsx`.

The workbook is **not redistributed**: authorship, public version history, licence, table
provenance, and the underlying Boeing/Rolls-Royce source are unresolved. Its supplied-byte
SHA-256 is `508d4288acac0b3eccf70ae200e0517d79979cbb47197155cee1b748142b8220`.
Excel formulas and macros are never executed.

## Implemented claim

The `FUELModel` sheet identifies cells P4/P6/P7 as B777-200ER, RR Trent 892,
long-range cruise. Cell P8 states the two-engine model

```text
total fuel flow (kg/s) = A + B * gross mass (kg)
```

Only the four altitude rows P12:R15 (FL350/370/390/410) are transcribed. Linear
interpolation is permitted inside that altitude interval; extrapolation is rejected. At a
declared constant flight level, the runner integrates the linear mass ODE analytically from
an independently declared fuel anchor to 00:10:59 UTC.

The independent coarse comparison is the user-supplied `Kong-fuel.csv.xlsx`, SHA-256
`5fee5196208c8655fb50af3f991df2e9a80298c84d800bb4990d5ca06f264437`.
The sheet has no units or aircraft/engine provenance. The check therefore states its
assumption—kg/h per engine—and only compares FL350/M0.829 at the official Arc-1 gross-mass
fixture. It cannot initialize fuel.

## Scientific status

`conditional_proxy_not_calibrated_performance_deck`

- The workbook is not Boeing or Rolls-Royce performance data.
- The release projection holds pressure altitude fixed and omits route, Mach, bank,
  temperature and engine-efficiency history.
- Total fuel does not identify physical left/right tank, feed, crossfeed, APU-accessible or
  unusable fuel. Those remain separately named sensitivity choices.
- No parameter is fitted to the 00:19 logon, BTO, BFO, an assumed exhaustion time, or an
  assumed impact position.

The product transcription and independent fixtures are in
`crates/end-of-flight/src/fuel_performance.rs`. Machine-readable cell pins are in
[`data/coefficient-pins.json`](data/coefficient-pins.json), and located passages are in
[`citation-ledger.md`](citation-ledger.md).

