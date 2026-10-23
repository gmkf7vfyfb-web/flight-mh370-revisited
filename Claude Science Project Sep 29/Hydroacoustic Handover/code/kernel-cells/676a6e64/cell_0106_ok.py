p='hydro-track-operating-note.md'
s=open(p).read()
gate = """
## Data-readiness gate (Pete, 22 Oct 2026) — do this BEFORE any compute
1. List every input your task needs (papers, figures, recordings, backgrounds, tables, run outputs). For each, record where you found
   it, its version/path/checksum, and that it is the right one (right station, days, table version, units). Commit or write this list
   in your note before running anything heavy.
2. NO SILENT STAND-INS. If a required input is missing, do not substitute a proxy, a neighbouring station, a model signal, a second-hand
   number or an older table and carry on. Stop that part, report what is missing and where you searched, and work only on parts that
   have their real data.
3. A stand-in may be used only after the parent approves it (and Pete, where it affects a reported result). A stand-in used without
   approval is a defect, not a deviation. Already-approved stand-ins: raw IMS hydrophone data are unavailable (Pete's ruling), so
   H01W/H08S noise comes from the digitised Kadri panels and Blackman (2004) App. B, labelled as proxies.
"""
s = s.replace("\n## Setting up (about 2 minutes)", gate + "\n## Setting up (about 2 minutes)")
open(p,'w').write(s); print('Data-readiness gate' in s)