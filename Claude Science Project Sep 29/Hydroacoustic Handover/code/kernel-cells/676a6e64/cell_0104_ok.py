p='hydro-track-operating-note.md'
s=open(p).read()
old = s[s.index('1. NEVER call `request_network_access`'):s.index('2. Do not delete')]
new = """1. SOURCES ARE NEVER DROPPED (Pete, 22 Oct 2026). Before you call any paper, figure or dataset unavailable, search, in this order:
   the artifact store (`host.artifacts(search=...)` in the python tool), the repo papers folders on BOTH branches
   (`ISO Sept 28 Status/inputs/papers/`, the archive `.sources/` and `published-figures/` folders), and the project Google Drive
   (Drive connector from the repl tool). Pete holds rights to the papers he has; use them. A failed download is recorded as
   'NOT RETRIEVED — ask Pete' with the full citation and the list of places searched. Never write 'closed access', and never
   leave a source out of an analysis because one fetch failed. Keep a 'needs Pete' list in your note and carry on with work that
   does not depend on it; do not stop and wait. In an unattended run do not raise approval cards (nobody can answer); put the
   request on the 'needs Pete' list instead. Already granted: `/Users/pete/Downloads` (rw), www.osti.gov, www.nature.com,
   drive.google.com, plus the standard science/package allowlist. `fetch_article_fulltext(doi)` works for open-access papers.
   The one hard exclusion: never open, quote or commit the private funding note in the Kadri bundle; every other file there
   (data, code, published figures) may be used.
"""
s = s.replace(old, new)
open(p,'w').write(s); print('NOT RETRIEVED' in s, len(s))