# AADC Gazetteer 137992 normalized provenance record

This record preserves the fields used by the fixed-waypoint conditional after a
fresh retrieval of the mutable Australian Antarctic Data Centre Gazetteer page.
It does **not** recreate, replace, or authenticate the earlier raw response whose
SHA-256 is recorded in the parent ledger as `04217d542e420925d353bbeb85159f4befc071345ee902578bcde65b0e5ddf28`.

## Retrieval

- URL: `https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id=137992`
- Retrieval completed locally: `2026-08-31T03:48:26.065163907Z`
- Server `Date` header: `Mon, 31 Aug 2026 03:47:15 GMT`
- Request: HTTPS GET followed with redirects using curl; no authentication.
- Response: `HTTP/1.1 200 OK`; `Content-Type: text/html;charset=UTF-8`;
  `Transfer-Encoding: chunked`; `Vary: Accept-Encoding`;
  `Server: nginx/1.31.3`.
- A transient `Set-Cookie` response header is deliberately not retained.
- Fresh raw response length: `23862` bytes.
- Fresh raw response SHA-256:
  `34c942a0af7d51ab5c568bf0ccafe3c79c8f3185af4a4b942494f8a5eb837eb8`.
- The fresh raw HTML is not committed because redistribution permission was not
  established. Its hash differs from the earlier inspected response, as is
  expected for this mutable page.

## Normalization

The durable payload is
[`aadc-gazetteer-137992.normalized.tsv`](aadc-gazetteer-137992.normalized.tsv).
HTML entities were decoded, repeated display whitespace was collapsed for
location, and only the labelled Gazetteer fields used by the analysis were
transcribed into UTF-8 TSV in a fixed field order. DMS symbols were expanded to
ASCII words. Decimal signs, displayed precision, names, method, institution,
and source-person/epoch values were retained. The seasonal-variation and
point-meaning rows are concise normalized statements of the located Narrative
and Comments fields, rather than claims of verbatim archival reproduction.

- Normalized payload length: `545` bytes.
- Normalized payload SHA-256:
  `c7a43771ddd56b03d333c187a7b469227282bac2eb5ab36e1f0d466bc4852554`.

## Claim boundary

The record supports the published landing-area centre coordinate, stated
accuracy, seasonal movement, GPS source method, institution, and 2009/10 source
epoch. It does not establish a WGS84 datum, an historical runway threshold,
Boeing 777 suitability, inclusion in 9M-MRO's navigation database, or selection
of this point by the aircraft.
