# Current-trajectory replay summary

Every selected path is included. A terminated forecast holds its last valid position to the target epoch while termination remains separately counted.

| Family | Year | Horizon | Attempts | Complete | Termination reasons | Median current / persistence / prior-velocity error (km) | Current better than persistence |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| cmems_glorys12_full_domain | 2014 | 5 d | 600 | 100.0% | none | 59.3 / 95.8 / 82.6 | 72.2% |
| cmems_glorys12_full_domain | 2014 | 15 d | 600 | 99.8% | missing_field_coverage=1 | 153.5 / 236.6 / 280.1 | 71.7% |
| cmems_glorys12_full_domain | 2014 | 30 d | 600 | 99.8% | missing_field_coverage=1 | 268.0 / 398.2 / 559.4 | 67.5% |
| cmems_glorys12_full_domain | 2015 | 5 d | 600 | 100.0% | none | 56.9 / 87.1 / 82.8 | 67.0% |
| cmems_glorys12_full_domain | 2015 | 15 d | 600 | 99.8% | missing_field_coverage=1 | 142.2 / 216.5 / 290.9 | 66.2% |
| cmems_glorys12_full_domain | 2015 | 30 d | 600 | 100.0% | none | 241.5 / 352.5 / 564.2 | 66.8% |
| cmems_glorys12_full_domain | 2016 | 5 d | 600 | 100.0% | none | 55.7 / 82.9 / 74.9 | 69.3% |
| cmems_glorys12_full_domain | 2016 | 15 d | 600 | 100.0% | none | 136.7 / 202.3 / 269.9 | 70.3% |
| cmems_glorys12_full_domain | 2016 | 30 d | 600 | 99.8% | missing_field_coverage=1 | 226.6 / 320.0 / 543.6 | 68.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 5 d | 600 | 100.0% | none | 64.9 / 95.8 / 82.6 | 65.7% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 15 d | 600 | 99.5% | missing_field_coverage=3 | 169.9 / 236.6 / 280.1 | 63.8% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 30 d | 600 | 98.8% | missing_field_coverage=7 | 307.6 / 398.2 / 559.4 | 59.5% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 5 d | 600 | 100.0% | none | 55.8 / 87.1 / 82.8 | 68.3% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 15 d | 600 | 99.2% | missing_field_coverage=5 | 149.0 / 216.5 / 290.9 | 65.2% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 30 d | 600 | 99.2% | missing_field_coverage=5 | 254.1 / 352.5 / 564.2 | 61.8% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 5 d | 600 | 100.0% | none | 53.3 / 82.9 / 74.9 | 68.2% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 15 d | 600 | 99.7% | missing_field_coverage=2 | 140.6 / 202.3 / 269.9 | 63.8% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 30 d | 600 | 99.7% | missing_field_coverage=2 | 244.3 / 320.0 / 543.6 | 62.0% |

## Drogue-state separation

Explicit surface Stokes drift is evaluated against undrogued segments separately from drogued segments; intervals spanning a recorded drogue-loss time remain a distinct transition group.

| Family | Year | Horizon | Drogue status | Attempts | Complete | Median current / persistence error (km) | Current better than persistence |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| cmems_glorys12_full_domain | 2014 | 5 d | drogue_transition | 6 | 100.0% | 91.0 / 79.5 | 33.3% |
| cmems_glorys12_full_domain | 2014 | 5 d | drogued | 334 | 100.0% | 50.8 / 86.3 | 74.3% |
| cmems_glorys12_full_domain | 2014 | 5 d | undrogued | 260 | 100.0% | 71.0 / 110.4 | 70.4% |
| cmems_glorys12_full_domain | 2014 | 15 d | drogue_transition | 18 | 100.0% | 121.5 / 269.3 | 94.4% |
| cmems_glorys12_full_domain | 2014 | 15 d | drogued | 337 | 100.0% | 130.4 / 204.2 | 71.2% |
| cmems_glorys12_full_domain | 2014 | 15 d | undrogued | 245 | 99.6% | 192.0 / 277.5 | 70.6% |
| cmems_glorys12_full_domain | 2014 | 30 d | drogue_transition | 40 | 97.5% | 176.2 / 355.4 | 70.0% |
| cmems_glorys12_full_domain | 2014 | 30 d | drogued | 307 | 100.0% | 227.2 / 351.5 | 67.4% |
| cmems_glorys12_full_domain | 2014 | 30 d | undrogued | 253 | 100.0% | 317.2 / 460.2 | 67.2% |
| cmems_glorys12_full_domain | 2015 | 5 d | drogue_transition | 3 | 100.0% | 33.0 / 47.3 | 66.7% |
| cmems_glorys12_full_domain | 2015 | 5 d | drogued | 220 | 100.0% | 52.1 / 87.9 | 69.5% |
| cmems_glorys12_full_domain | 2015 | 5 d | undrogued | 377 | 100.0% | 58.6 / 86.5 | 65.5% |
| cmems_glorys12_full_domain | 2015 | 15 d | drogue_transition | 15 | 100.0% | 219.5 / 261.5 | 60.0% |
| cmems_glorys12_full_domain | 2015 | 15 d | drogued | 187 | 100.0% | 120.0 / 220.1 | 67.4% |
| cmems_glorys12_full_domain | 2015 | 15 d | undrogued | 398 | 99.7% | 149.0 / 213.5 | 65.8% |
| cmems_glorys12_full_domain | 2015 | 30 d | drogue_transition | 24 | 100.0% | 252.5 / 337.1 | 62.5% |
| cmems_glorys12_full_domain | 2015 | 30 d | drogued | 196 | 100.0% | 213.9 / 363.7 | 73.0% |
| cmems_glorys12_full_domain | 2015 | 30 d | undrogued | 380 | 100.0% | 258.4 / 343.9 | 63.9% |
| cmems_glorys12_full_domain | 2016 | 5 d | drogue_transition | 5 | 100.0% | 93.6 / 70.3 | 60.0% |
| cmems_glorys12_full_domain | 2016 | 5 d | drogued | 223 | 100.0% | 48.4 / 81.6 | 68.6% |
| cmems_glorys12_full_domain | 2016 | 5 d | undrogued | 372 | 100.0% | 58.7 / 83.9 | 69.9% |
| cmems_glorys12_full_domain | 2016 | 15 d | drogue_transition | 7 | 100.0% | 162.4 / 305.2 | 57.1% |
| cmems_glorys12_full_domain | 2016 | 15 d | drogued | 216 | 100.0% | 111.7 / 182.3 | 69.9% |
| cmems_glorys12_full_domain | 2016 | 15 d | undrogued | 377 | 100.0% | 155.1 / 209.0 | 70.8% |
| cmems_glorys12_full_domain | 2016 | 30 d | drogue_transition | 25 | 100.0% | 189.2 / 252.3 | 72.0% |
| cmems_glorys12_full_domain | 2016 | 30 d | drogued | 235 | 100.0% | 193.9 / 280.5 | 64.7% |
| cmems_glorys12_full_domain | 2016 | 30 d | undrogued | 340 | 99.7% | 238.4 / 352.1 | 70.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 5 d | drogue_transition | 6 | 100.0% | 104.2 / 79.5 | 50.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 5 d | drogued | 334 | 100.0% | 69.8 / 86.3 | 59.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 5 d | undrogued | 260 | 100.0% | 54.8 / 110.4 | 74.6% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 15 d | drogue_transition | 18 | 100.0% | 155.1 / 269.3 | 66.7% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 15 d | drogued | 337 | 99.7% | 186.9 / 204.2 | 57.6% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 15 d | undrogued | 245 | 99.2% | 139.5 / 277.5 | 72.2% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 30 d | drogue_transition | 40 | 97.5% | 277.3 / 355.4 | 67.5% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 30 d | drogued | 307 | 99.3% | 357.6 / 351.5 | 50.5% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2014 | 30 d | undrogued | 253 | 98.4% | 245.2 / 460.2 | 69.2% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 5 d | drogue_transition | 3 | 100.0% | 65.1 / 47.3 | 0.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 5 d | drogued | 220 | 100.0% | 67.1 / 87.9 | 65.9% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 5 d | undrogued | 377 | 100.0% | 50.1 / 86.5 | 70.3% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 15 d | drogue_transition | 15 | 100.0% | 230.9 / 261.5 | 66.7% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 15 d | drogued | 187 | 98.9% | 164.9 / 220.1 | 62.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 15 d | undrogued | 398 | 99.2% | 140.8 / 213.5 | 66.6% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 30 d | drogue_transition | 24 | 100.0% | 320.4 / 337.1 | 41.7% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 30 d | drogued | 196 | 98.5% | 313.8 / 363.7 | 56.1% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2015 | 30 d | undrogued | 380 | 99.5% | 231.7 / 343.9 | 66.1% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 5 d | drogue_transition | 5 | 100.0% | 31.9 / 70.3 | 80.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 5 d | drogued | 223 | 100.0% | 68.0 / 81.6 | 57.8% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 5 d | undrogued | 372 | 100.0% | 43.4 / 83.9 | 74.2% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 15 d | drogue_transition | 7 | 100.0% | 198.6 / 305.2 | 57.1% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 15 d | drogued | 216 | 99.5% | 173.9 / 182.3 | 50.5% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 15 d | undrogued | 377 | 99.7% | 119.0 / 209.0 | 71.6% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 30 d | drogue_transition | 25 | 100.0% | 334.9 / 252.3 | 44.0% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 30 d | drogued | 235 | 99.1% | 342.6 / 280.5 | 48.9% |
| cmems_glorys12_full_domain_plus_distinct_stokes | 2016 | 30 d | undrogued | 340 | 100.0% | 195.3 / 352.1 | 72.4% |

The regional CSV contains the same metrics for western 10°E–60°E, central 60°E–100°E, and eastern 100°E–150°E starts. GDP is observational climatology; HYCOM+NCODA and GLORYS12 are assimilative, so no replay is guaranteed statistically held out.
