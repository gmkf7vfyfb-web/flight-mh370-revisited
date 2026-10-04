# Davey et al. (2016), the reference this project reproduces

Samuel Davey, Neil Gordon, Ian Holland, Mark Rutten, Jason Williams,
*Bayesian Methods in the Search for MH370*, SpringerBriefs in Electrical and Computer
Engineering, Springer Singapore, 2016. DOI [10.1007/978-981-10-0379-0](https://doi.org/10.1007/978-981-10-0379-0).
© Commonwealth of Australia 2016. 124 pp.

**Licence: CC BY-NC 4.0** — Creative Commons Attribution-NonCommercial 4.0 International,
stated per chapter in the book's Open Access notices. Noncommercial use, duplication,
adaptation, distribution and reproduction are permitted with attribution. Note this is
**not** plain CC BY: the non-commercial restriction is real and applies to any redistribution.

## Where the PDF lives

`paper.pdf` in this directory is **deliberately gitignored** and is not in the repository: the
non-commercial clause makes redistribution of the binary from a public repository a question
not worth leaving to interpretation, and the publisher serves it free to anyone. The copy the
project works from is on the shared Drive, in `Claude Science Project Sep 29`, as
*Davey et al 2016 - Bayesian Methods in the Search for MH370 (CC BY-NC 4.0).pdf*.

To obtain it directly from the publisher:

```sh
curl -L -c /tmp/sp.jar -b /tmp/sp.jar \
  -o .sources/davey-2016/paper.pdf \
  https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf
# 6,898,866 bytes, sha256 37554ca5f0c0ef14fddb825748d9f9dc9059a26563f783a3e4dfafcd0ced91b2
```

The cookie jar matters: the download redirects through `idp.springer.com` to set an anonymous
session cookie before the file is served, and a plain `curl -L` without `-c/-b` ends at the
redirect. The OAPEN mirror (`library.oapen.org/bitstream/20.500.12657/27976/1/1002023.pdf`)
carries the same file but sits behind a proof-of-work bot challenge.

## Why it is worth keeping track of

This book is not background reading, it is the specification. `results/davey-2016-reference.md`
records what it actually says about the filter parameters, the resampling scheme and the
convergence criterion, and audits the engine against it. Several things this project had been
treating as settled were in fact inferred from secondary sources while the PDF was absent; that
note marks which ones survived contact with the original.

`fig10-3-bfo-latitude-pdf.csv` in this directory is the digitised published posterior from
Fig. 10.3 (bottom panel), the curve `config/davey2016.toml` compares against.