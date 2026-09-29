---
name: pete-needs-images-not-pdfs
description: Pete cannot preview PDFs in iso; give him PNG images (or other viewable docs) linked in chat
metadata:
  node_type: memory
  type: feedback
  originSessionId: c924a4ee-d933-4d28-bd74-6dd738e4c3d8
  modified: 2026-09-25T23:44:18.577Z
---

Pete Large can't preview .pdf files in iso (said 2026-09-25). Give results as PNG images linked in chat, or another format iso renders; a PDF can still be produced alongside for the record.

**Why:** the PDFs linked so far (sensitivity reports, early_path.pdf) were unreadable for him.
**How to apply:** for every plot or report meant for Pete, write PNG pages (e.g. render the report PDF pages with pymupdf in .venv, or save figures as PNG) and link those. Nothing needed installing: pymupdf is already in .venv.
