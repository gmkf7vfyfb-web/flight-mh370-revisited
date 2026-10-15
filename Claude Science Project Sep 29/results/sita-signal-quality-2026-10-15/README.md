# Signal quality of the bursts the filter uses (run-J item 3a, 15 October 2026)

**Source.** `Unredacted Raw 35200217 Logs for SITA 08Mar2014(p).xlsx` (Downloads), sheet `SU Log`, columns
`C/No`, `Estimated BER`, `CRC Correct`, `Frequency Offset (Hz)`, `Burst Timing Offset (microseconds)`.
Eb/N0 = C/N0 − 10 log10(bit rate), with the R600 channel at 600 bit/s and R1200 at 1200 bit/s.

| burst | channel | C/N0 (dB-Hz) | Est. BER | Eb/N0 (dB) | CRC | BFO (Hz) | BTO raw (µs) |
|---|---|---|---|---|---|---|---|
| 18:25:27.421 log-on request | IOR-R600 | **30.28** | **5** | **2.5** | Yes | 142 | 17,120 |
| 18:25:34.461 log-on ack | IOR-R1200 | 42.65 | 0 | 11.9 | Yes | 273 | 51,700 |
| 18:28:05.904 | IOR-R1200 | 43.22 | 0 | 12.4 | Yes | 144 | 12,500 |
| 18:28:14.904 | IOR-R1200 | 42.02 | 0 | 11.2 | Yes | 143 | 12,480 |
| 00:19:29.416 log-on request | IOR-R600 | 40.59 | 0 | 12.8 | Yes | 182 | — |
| 00:19:37.443 log-on ack | IOR-R1200 | 43.38 | 0 | 12.6 | Yes | −2 | — |

**Context: all 135 R600 bursts in the log.**
- C/N0 has a mean of 41.07 dB-Hz (sd 3.62), with a median of 40.59.
- Only 4 have BER > 0: 01:44:23, 01:47:16, 04:03:36 and 18:25:27.
- The 18:25:27 burst is in the lowest 1.5% by C/N0. The 00:19:29 R600 burst sits exactly at the median.

## Reading
- The 18:25:27 R600 burst decoded correctly (CRC Yes) but is weak: about 10 dB below a typical R600 burst, with
  5 estimated bit errors. Holland's exclusion of it for signal quality has a basis in the log.
- The weak signal mainly widens the frequency (BFO) and timing (BTO) estimation error. A frequency
  estimator's variance scales about as 1/(C/N0), so about 3× the fast random component.
  - This is inferred from estimation theory, NOT measured here.
- Pete's ruling for run J stands: BFO at 4.32 Hz, BTO flagged. Core suggests a declared sensitivity with the
  18:25:27 BFO sd at about 5–6 Hz.
- Every other burst the filter and end of flight use is normal (C/N0 40–43 dB-Hz, BER 0). The BFO values in the
  log match `engine/data/satcom-1825-sequence.csv` and `satcom-observations.csv` (142, 273, 144, 143, 182, −2 Hz).
  The 18:25:27 R600 raw BTO, 17,120 µs, matches too.
