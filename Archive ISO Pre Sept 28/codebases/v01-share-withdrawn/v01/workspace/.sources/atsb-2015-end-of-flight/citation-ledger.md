# Citation ledger

| Claim | Source | Locator | Located passage | Status |
| --- | --- | --- | --- | --- |
| APU fuel availability after left-engine exhaustion depends on attitude and acceleration, so it is not a deterministic tank-volume calculation. | ATSB, 2015, AE-2014-054 | PDF p. 9, report lines 233-241 | “pitch attitude would have an effect”; the following sentences identify phugoid motion and acceleration as fuel-distribution factors. | FOUND |
| Following loss of both AC transfer buses, APU auto-start to generator online is approximately 60 seconds. | ATSB, 2015, AE-2014-054 | PDF p. 9, report lines 242-244 | “taking approximately 60 seconds” | FOUND |
| The SDU power-to-log-on interval was revised from the earlier 2 min 40 s advice to approximately 60 s after further SDU-manufacturer testing. | ATSB, 2015, AE-2014-054 | PDF p. 10, footnote 6, report lines 317-319 | “approximately 60 seconds is the correct time” | FOUND |
| Under small pitch changes and positive acceleration, the nominal residual APU fuel was assessed sufficient through the two-minute sequence. | ATSB, 2015, AE-2014-054 | PDF p. 11, report lines 343-347 | “2 minutes” | FOUND |
| ATSB initially ignored the 00:19:37 R1200 BTO, used 00:19:29 R600 for the seventh arc, and later applied an empirical N×~7820 µs offset without an identified equipment cause. | ATSB, 2015, AE-2014-054 | PDF p. 21, report lines 577-590 | “unable to determine a specific reason” | FOUND |
| R600 messages require a 4,600 µs calibration subtraction before comparison with R1200, including the 00:19:29 message. | ATSB, *Update to Signalling Unit Logs*, amended 30 March 2017 | Web page lines 485-500 | “a 4,600 microseconds calibration needs to be subtracted” | FOUND |

## Inference boundary

The approximately 119-second reverse lag from the first R600 burst at
00:19:29.416 to a nominal second-flameout/dual-bus-loss time is calculated from
two approximate component delays. It is not independently observed. The public
ATSB material does not publish the SDU manufacturer's underlying timing trials
or a lag standard deviation.
