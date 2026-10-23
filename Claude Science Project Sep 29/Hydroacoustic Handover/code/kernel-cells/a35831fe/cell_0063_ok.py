foot=("Plain words: Each mark is one possible signal. Panel a shows the place and time of impact that the signal needs. Panel b shows how much of the impact energy must become sound for the signal to be the impact. "
"The F-35A crash (Japan, 2019) is the only aircraft crash with a measured sound record. All values are predictions; the sound model is not calibrated. Candidates that fail on time or place are not shown in panel a.\n"
"Technical: Prior = end-of-flight run J, 00:19 options D0', D2, D3, D4 averaged, dive probability 0.5, 8.85 M-row geometry sample. Loci from arrival-time differences at c = 1.482 km/s (Kadri rows: Table 1 bearing). "
"Coupling = loudness-match eta (ranked tables 22 Oct, max over sites, at locus median energy) x E_med/E_q99 (q99 approx. 12 GJ), divided by the Metz-derived F-35A anchor 2.26e-3 (10 m source, f^-2, KRAKEN+RAM). "
"Diego Garcia levels are airgun pulses (94 % of candidates within 1.5 s of a shot). Caveats C1, C2; digitised Kadri traces; IMOS has no bearing; no candidate set is above chance. Exploratory review, 22 Oct 2026.")
import textwrap
fig.text(0.02,-0.005,'\n'.join(textwrap.fill(p,190) for p in foot.split('\n')),fontsize=5.5,va='top',ha='left')
fig.savefig('candidates_location_time_coupling.png',dpi=300,bbox_inches='tight')
print('ok')