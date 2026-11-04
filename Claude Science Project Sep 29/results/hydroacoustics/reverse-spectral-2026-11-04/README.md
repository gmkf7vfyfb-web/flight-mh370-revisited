# Reverse-sensing spectral search (S10) and source classifier, 4 Nov 2026

This folder holds Amendment 2 to the reverse-sensing methods specification (folder `reverse-methods-2026-11-04/`).

Commit 1 (this commit) holds only the amendment and the fixed S10 code. It was made BEFORE S10 or the classifier ran on any arrival window. The results follow in a later, separate commit.

- `reverse-methods-amendment-2-spectral-search-2026-11-04.md` - Amendment 2 (S10 spectral-template search, source classifier, Pete's steer of 4 Nov 2026 on the loose impact-like class).
- `reverse_spectral.py` - module, S10 part fixed (sha256 in `amendment-2-fixed-code.json`).
- `amendment-2-fixed-code.json` - hash of the fixed S10 code, bank seed and sizes.

S10 is post hoc in origin (added after screening began), with its parameters fixed before it runs. Propagation is used for travel time only.
