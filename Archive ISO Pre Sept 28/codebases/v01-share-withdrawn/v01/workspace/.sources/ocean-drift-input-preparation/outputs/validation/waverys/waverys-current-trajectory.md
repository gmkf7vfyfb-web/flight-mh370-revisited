# Current-trajectory replay summary

Every selected path is included. A terminated forecast holds its last valid position to the target epoch while termination remains separately counted.

| Family | Year | Horizon | Attempts | Complete | Termination reasons | Median current / persistence / prior-velocity error (km) | Current better than persistence |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| cmems_glorys12_daily_currents | 2014 | 5 d | 600 | 99.8% | outside_spatial_support=1 | 59.3 / 95.8 / 82.6 | 72.2% |
| cmems_glorys12_daily_currents | 2014 | 15 d | 600 | 98.8% | missing_field_coverage=1, outside_spatial_support=6 | 152.6 / 236.6 / 280.1 | 71.7% |
| cmems_glorys12_daily_currents | 2014 | 30 d | 600 | 99.0% | missing_field_coverage=1, outside_spatial_support=5 | 268.4 / 398.2 / 559.4 | 67.5% |
| cmems_glorys12_daily_currents | 2015 | 5 d | 600 | 99.8% | outside_spatial_support=1 | 59.1 / 90.0 / 73.2 | 68.8% |
| cmems_glorys12_daily_currents | 2015 | 15 d | 600 | 99.8% | missing_field_coverage=1 | 139.8 / 209.4 / 268.3 | 67.0% |
| cmems_glorys12_daily_currents | 2015 | 30 d | 600 | 99.5% | outside_spatial_support=3 | 238.4 / 338.3 / 559.0 | 67.3% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 5 d | 600 | 99.5% | outside_spatial_support=3 | 58.5 / 95.8 / 82.6 | 70.5% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 15 d | 600 | 98.7% | missing_field_coverage=1, outside_spatial_support=7 | 150.5 / 236.6 / 280.1 | 69.2% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 30 d | 600 | 98.2% | missing_field_coverage=5, outside_spatial_support=6 | 258.7 / 398.2 / 559.4 | 65.3% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 5 d | 600 | 99.8% | outside_spatial_support=1 | 54.7 / 90.0 / 73.2 | 71.8% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 15 d | 600 | 99.5% | missing_field_coverage=2, outside_spatial_support=1 | 141.5 / 209.4 / 268.3 | 66.5% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 30 d | 600 | 99.2% | missing_field_coverage=1, outside_spatial_support=4 | 244.5 / 338.3 / 559.0 | 65.2% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 5 d | 600 | 99.2% | missing_field_coverage=1, outside_spatial_support=4 | 74.7 / 95.8 / 82.6 | 59.3% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 15 d | 600 | 96.8% | missing_field_coverage=7, outside_spatial_support=12 | 197.2 / 236.6 / 280.1 | 58.2% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 30 d | 600 | 94.7% | missing_field_coverage=13, outside_spatial_support=19 | 362.2 / 398.2 / 559.4 | 52.7% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 5 d | 600 | 99.5% | missing_field_coverage=1, outside_spatial_support=2 | 62.3 / 90.0 / 73.2 | 64.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 15 d | 600 | 99.0% | missing_field_coverage=5, outside_spatial_support=1 | 154.7 / 209.4 / 268.3 | 60.8% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 30 d | 600 | 97.3% | missing_field_coverage=12, outside_spatial_support=4 | 305.9 / 338.3 / 559.0 | 57.5% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 5 d | 600 | 99.3% | outside_spatial_support=4 | 64.5 / 95.8 / 82.6 | 65.8% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 15 d | 600 | 98.5% | missing_field_coverage=3, outside_spatial_support=6 | 169.0 / 236.6 / 280.1 | 64.0% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 30 d | 600 | 96.3% | missing_field_coverage=7, outside_spatial_support=15 | 299.9 / 398.2 / 559.4 | 60.3% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 5 d | 600 | 99.8% | outside_spatial_support=1 | 55.9 / 90.0 / 73.2 | 68.5% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 15 d | 600 | 99.2% | missing_field_coverage=3, outside_spatial_support=2 | 142.7 / 209.4 / 268.3 | 63.5% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 30 d | 600 | 98.2% | missing_field_coverage=8, outside_spatial_support=3 | 264.8 / 338.3 / 559.0 | 61.7% |

## Drogue-state separation

Explicit surface Stokes drift is evaluated against undrogued segments separately from drogued segments; intervals spanning a recorded drogue-loss time remain a distinct transition group.

| Family | Year | Horizon | Drogue status | Attempts | Complete | Median current / persistence error (km) | Current better than persistence |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| cmems_glorys12_daily_currents | 2014 | 5 d | drogue_transition | 6 | 100.0% | 91.0 / 79.5 | 33.3% |
| cmems_glorys12_daily_currents | 2014 | 5 d | drogued | 334 | 99.7% | 50.8 / 86.3 | 74.3% |
| cmems_glorys12_daily_currents | 2014 | 5 d | undrogued | 260 | 100.0% | 71.0 / 110.4 | 70.4% |
| cmems_glorys12_daily_currents | 2014 | 15 d | drogue_transition | 18 | 100.0% | 121.5 / 269.3 | 94.4% |
| cmems_glorys12_daily_currents | 2014 | 15 d | drogued | 337 | 98.2% | 128.3 / 204.2 | 71.2% |
| cmems_glorys12_daily_currents | 2014 | 15 d | undrogued | 245 | 99.6% | 192.0 / 277.5 | 70.6% |
| cmems_glorys12_daily_currents | 2014 | 30 d | drogue_transition | 40 | 97.5% | 176.2 / 355.4 | 70.0% |
| cmems_glorys12_daily_currents | 2014 | 30 d | drogued | 307 | 99.0% | 227.2 / 351.5 | 67.4% |
| cmems_glorys12_daily_currents | 2014 | 30 d | undrogued | 253 | 99.2% | 317.7 / 460.2 | 67.2% |
| cmems_glorys12_daily_currents | 2015 | 5 d | drogue_transition | 8 | 100.0% | 49.2 / 126.2 | 75.0% |
| cmems_glorys12_daily_currents | 2015 | 5 d | drogued | 208 | 100.0% | 48.8 / 93.0 | 75.5% |
| cmems_glorys12_daily_currents | 2015 | 5 d | undrogued | 384 | 99.7% | 66.3 / 88.4 | 65.1% |
| cmems_glorys12_daily_currents | 2015 | 15 d | drogue_transition | 15 | 100.0% | 135.0 / 207.1 | 73.3% |
| cmems_glorys12_daily_currents | 2015 | 15 d | drogued | 187 | 100.0% | 123.0 / 206.1 | 63.6% |
| cmems_glorys12_daily_currents | 2015 | 15 d | undrogued | 398 | 99.7% | 148.7 / 209.6 | 68.3% |
| cmems_glorys12_daily_currents | 2015 | 30 d | drogue_transition | 24 | 100.0% | 236.7 / 277.3 | 70.8% |
| cmems_glorys12_daily_currents | 2015 | 30 d | drogued | 183 | 99.5% | 207.5 / 340.9 | 69.9% |
| cmems_glorys12_daily_currents | 2015 | 30 d | undrogued | 393 | 99.5% | 255.9 / 340.1 | 65.9% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 5 d | drogue_transition | 6 | 100.0% | 101.2 / 79.5 | 33.3% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 5 d | drogued | 334 | 99.1% | 55.2 / 86.3 | 69.5% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 5 d | undrogued | 260 | 100.0% | 61.6 / 110.4 | 72.7% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 15 d | drogue_transition | 18 | 100.0% | 136.4 / 269.3 | 83.3% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 15 d | drogued | 337 | 97.9% | 141.2 / 204.2 | 66.8% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 15 d | undrogued | 245 | 99.6% | 162.4 / 277.5 | 71.4% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 30 d | drogue_transition | 40 | 97.5% | 203.1 / 355.4 | 62.5% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 30 d | drogued | 307 | 98.0% | 258.3 / 351.5 | 62.9% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2014 | 30 d | undrogued | 253 | 98.4% | 274.8 / 460.2 | 68.8% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 5 d | drogue_transition | 8 | 100.0% | 64.8 / 126.2 | 75.0% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 5 d | drogued | 208 | 100.0% | 52.8 / 93.0 | 72.1% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 5 d | undrogued | 384 | 99.7% | 55.4 / 88.4 | 71.6% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 15 d | drogue_transition | 15 | 100.0% | 195.1 / 207.1 | 73.3% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 15 d | drogued | 187 | 99.5% | 141.1 / 206.1 | 64.2% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 15 d | undrogued | 398 | 99.5% | 139.6 / 209.6 | 67.3% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 30 d | drogue_transition | 24 | 100.0% | 239.8 / 277.3 | 66.7% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 30 d | drogued | 183 | 98.4% | 257.2 / 340.9 | 59.0% |
| cmems_glorys12_daily_currents_plus_0.5x_distinct_stokes | 2015 | 30 d | undrogued | 393 | 99.5% | 231.0 / 340.1 | 67.9% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 5 d | drogue_transition | 6 | 100.0% | 108.6 / 79.5 | 50.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 5 d | drogued | 334 | 98.5% | 87.5 / 86.3 | 50.9% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 5 d | undrogued | 260 | 100.0% | 59.1 / 110.4 | 70.4% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 15 d | drogue_transition | 18 | 100.0% | 185.6 / 269.3 | 66.7% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 15 d | drogued | 337 | 95.8% | 224.7 / 204.2 | 48.4% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 15 d | undrogued | 245 | 98.0% | 136.2 / 277.5 | 71.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 30 d | drogue_transition | 40 | 97.5% | 386.5 / 355.4 | 55.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 30 d | drogued | 307 | 92.8% | 417.1 / 351.5 | 43.6% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2014 | 30 d | undrogued | 253 | 96.4% | 292.9 / 460.2 | 63.2% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 5 d | drogue_transition | 8 | 100.0% | 83.7 / 126.2 | 75.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 5 d | drogued | 208 | 99.5% | 75.6 / 93.0 | 56.2% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 5 d | undrogued | 384 | 99.5% | 53.0 / 88.4 | 68.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 15 d | drogue_transition | 15 | 100.0% | 214.1 / 207.1 | 60.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 15 d | drogued | 187 | 98.9% | 196.1 / 206.1 | 49.2% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 15 d | undrogued | 398 | 99.0% | 139.7 / 209.6 | 66.3% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 30 d | drogue_transition | 24 | 100.0% | 335.7 / 277.3 | 50.0% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 30 d | drogued | 183 | 96.7% | 409.7 / 340.9 | 46.4% |
| cmems_glorys12_daily_currents_plus_1.5x_distinct_stokes | 2015 | 30 d | undrogued | 393 | 97.5% | 262.5 / 340.1 | 63.1% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 5 d | drogue_transition | 6 | 100.0% | 104.2 / 79.5 | 50.0% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 5 d | drogued | 334 | 98.8% | 69.1 / 86.3 | 59.3% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 5 d | undrogued | 260 | 100.0% | 54.8 / 110.4 | 74.6% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 15 d | drogue_transition | 18 | 100.0% | 155.1 / 269.3 | 66.7% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 15 d | drogued | 337 | 97.9% | 184.9 / 204.2 | 57.9% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 15 d | undrogued | 245 | 99.2% | 139.5 / 277.5 | 72.2% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 30 d | drogue_transition | 40 | 95.0% | 264.0 / 355.4 | 67.5% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 30 d | drogued | 307 | 95.1% | 348.2 / 351.5 | 52.1% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2014 | 30 d | undrogued | 253 | 98.0% | 245.2 / 460.2 | 69.2% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 5 d | drogue_transition | 8 | 100.0% | 75.9 / 126.2 | 75.0% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 5 d | drogued | 208 | 100.0% | 61.6 / 93.0 | 64.9% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 5 d | undrogued | 384 | 99.7% | 50.4 / 88.4 | 70.3% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 15 d | drogue_transition | 15 | 100.0% | 192.1 / 207.1 | 73.3% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 15 d | drogued | 187 | 99.5% | 162.5 / 206.1 | 56.7% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 15 d | undrogued | 398 | 99.0% | 129.7 / 209.6 | 66.3% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 30 d | drogue_transition | 24 | 100.0% | 262.2 / 277.3 | 50.0% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 30 d | drogued | 183 | 98.4% | 337.5 / 340.9 | 51.4% |
| cmems_glorys12_daily_currents_plus_1x_distinct_stokes | 2015 | 30 d | undrogued | 393 | 98.0% | 236.3 / 340.1 | 67.2% |

The regional CSV contains the same metrics for western 10°E–60°E, central 60°E–100°E, and eastern 100°E–150°E starts. GDP is observational climatology; HYCOM+NCODA and GLORYS12 are assimilative, so no replay is guaranteed statistically held out.
