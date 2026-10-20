# Ashton et al. — The Search for MH370

Chris Ashton, Alan Shuster Bruce, Gary Colledge, and Mark Dickinson, “The
Search for MH370,” The Journal of Navigation 68(1), 2015, pp. 1-22.
DOI: https://doi.org/10.1017/S037346331400068X

The exact CC-BY paper is paper/paper.pdf, SHA-256
2ff0f10c1cf0bad299e5398ad9019a113963f6a5bd86b96bf4d04d330bc08028.

## Claim checked

Pages 9-10 define BFO as separate uplink Doppler, downlink Doppler, aircraft
frequency compensation, satellite translation-frequency variation, GES AFC,
and fixed bias terms. Pages 13-14 explain the Perth pilot-frequency AFC and
thermal satellite-oscillator behaviour. Page 20 reports satellite and AFC as a
combined tabular contribution while retaining aircraft bias separately.

The canonical SATCOM spoke implements the smallest equation-level result:
Doppler and aircraft compensation are calculated from state and geometry;
the time-varying satellite and Perth corrections are inputs; aircraft bias is
a distinct analytical latent state.

## Recreation status

The published equations and sign roles were independently mapped to the Rust
component calculation and truth-flight implied-bias audit.

Not integrated: the paper does not publish the proprietary full-day correction
curves needed to recreate numerical interpolation from the PDF alone. The
MH371 data package therefore traces each interpolated component to the
hash-pinned workbook columns FA and FB and reports this limitation explicitly.
