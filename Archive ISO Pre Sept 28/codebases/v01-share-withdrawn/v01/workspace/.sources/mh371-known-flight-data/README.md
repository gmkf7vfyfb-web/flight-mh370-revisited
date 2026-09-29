# MH371 truth-separated cruise control

This package turns frozen MH371 ACARS, SITA SATCOM, satellite ephemeris, and
correction workbooks into a blind inference file plus a scorer-only truth file.
It is a known-flight computational control, not evidence about MH370's final
location.

## Boundaries and selection

- cruise start: 2014-03-07 01:48:00 UTC, the first stable level-off;
- last observation: 2014-03-07 06:48:33.907 UTC;
- descent boundary: 07:04 UTC;
- six approximately hourly R1200 observations;
- aircraft AES identifier: 35200217;
- eligible rows require C/No at least 35 dB-Hz and exclude logon, logoff, and
  control messages;
- one row per declared window is the minimum SHA-256 rank under seed
  mh371-cruise-hourly-v1.

The final window is centred at 06:48 rather than 07:00. A pilot run exposed
that the 06:59 ACARS interpolation was already mixing the subsequent descent
turn, contrary to the declared cruise-only control.

Selected epochs are 01:56:47.921, 03:20:22.428, 04:04:57.916,
05:11:37.411, 06:09:44.409, and 06:48:33.907 UTC. The exact candidate counts,
channels, source rows, C/No values, and SHA ranks are in
outputs/channel-selection.csv.

## Truth separation

inputs/controls/mh371-inference.json contains only the 01:48 position and true
heading, Davey's 0.5 NM north/east and 1 degree heading uncertainties, the six
BTO/BFO observations, ephemeris, channels, and correction components. It has
no later position, trajectory, Mach, altitude, or heading fields; the Rust
parser recursively rejects truth-like keys.

inputs/controls/mh371-truth.csv contains the initial state and later
interpolated ACARS controls. The inference command has no truth argument. Only
score-known-flight loads that CSV and adds the red truth position and heading
arrow to each report page.

## Source identities

The restricted or bulky raw workbooks remain in the preserved source archive.
The extractor defaults give their exact retrieval paths.

- SITA workbook SHA-256:
  bbc71937198e748e5695d607c4192e5c873d0aa81f5e786a378cc929ce3f95a7
- ACARS workbook SHA-256:
  444f1e75a3edd17ed3666263cc8d54ef35665f0f4f1984212cfcf11a759386d4
- satellite ephemeris SHA-256:
  a1a84be75ebdcf642a77dd110a755b01c6e4be1adb5dbef2cfb42fc5585989d0
- correction workbook SHA-256:
  c90df112f70e4ac75dd1361e51bc1e70cb3319dd5db6490a50eebb1a65626c60

The ACARS workbook contains CAS but no labelled ground-speed field. Therefore
no knots-versus-km/h assumption enters inference. Held-back truth ground
velocity is a centred derivative of ACARS positions and is used only for
diagnostics; Mach, heading, and altitude remain separately reported.

## BFO correction trace

Ashton et al. define satellite translation frequency, Perth GES AFC, and fixed
aircraft bias as distinct terms. The Large dissertation, PDF page 131
(printed page 115), says the satellite and AFC values were interpolated from
proprietary Ashton data. The traced workbook has:

- FA: calculated pilot-frequency Doppler offset / satellite curve;
- FB: Perth GES AFC correction;
- FC formula contribution: FB - FA.

The package therefore stores satellite_oscillator_hz = -FA and
perth_ges_afc_hz = FB separately. Their sum is passed to the physical BFO
equation; neither is folded into the latent aircraft bias. The exact daily
knots and sheet names are in data/bfo-correction-knots.json.

Primary equation source:
https://doi.org/10.1017/S037346331400068X

Prior source:
https://doi.org/10.1007/978-981-10-0379-0

Dissertation catalogue identity: Peter O. Large, ProQuest 13857090, 2019.

## Reproduction and integrity

~~~bash
python3 .sources/mh371-known-flight-data/code/extract_control.py
~~~

- extractor SHA-256:
  88cd0e9139113e103adc178ce55964cb844e57b847c786d2f27a53498a213d22
- inference SHA-256:
  e097dcfb303acb515a8b6bee90450574b88968d647b82d5b3d3eea5bf56c37ec
- truth SHA-256:
  65de30cc4e20fc77a1d6048449d5654046fd78f83f325d14d2d26c6ccd9751c9
- correction-knot SHA-256:
  1c4270adfe98e89ba9b1627c61900e1172e93192afde3393f4f26bc2427a66fb
- selection-audit SHA-256:
  935430113c42e5e322c4e482c9f3bd4e68b2bebd685425367ba9efe2369beebc

## Final control result

| Family | BFO SD | Terminal mean error, seeds | Minimum terminal mass within 100 NM | Terminal root ESS |
| --- | ---: | ---: | ---: | ---: |
| Wide Mach/altitude | 7.0 Hz | 89.1, 86.7 NM | 35.5% | 28.1, 29.9 |
| MH370 analog, loose | 7.0 Hz | 76.1, 15.3 NM | 48.5% | 35.0, 33.5 |
| MH370 analog, medium | 4.0 Hz | 21.8, 30.9 NM | 57.2% | 33.2, 27.9 |
| MH370 analog, observed | 1.5 Hz | 28.4, 45.6 NM | 73.4% | 16.3, 20.9 |

Each two-seed 12,000-particle family took 0.78-0.79 seconds on eight threads.
The Rust/Python BTO equation closure is 0.308 microseconds maximum. The six
truth-implied aircraft BFO biases are 167.2, 171.6, 169.6, 169.7, 170.6, and
168.6 Hz; their consistency is an independent check on the correction signs.

The citation audit is data/citation-ledger.md.
