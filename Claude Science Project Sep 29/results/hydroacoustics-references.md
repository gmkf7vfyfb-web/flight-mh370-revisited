# Hydroacoustics module: citation ledger

**Standing rule ~01:20 UTC, 9 Oct.** This ledger is at `results/` and not in `engine/hypotheses/hydroacoustics/`
because `ARCHITECTURE.md` allows only three `.md` files in `engine/` and this module's instructions forbid
writing new ones. It is the same reversible choice ocean drift made, pending the same ruling.
`references.bib` (same keys) is in the module directory.

**DOIs:** all verified against CrossRef or DataCite on 2026-10-09.

**Pages:**
- Printed pages, taken from the running headers or footers of the copies named.
- **Brown 2026** pages are arXiv **manuscript** pages; the Icarus pagination is not yet held.
- **CMST 2014-30** page numbers are the report's own; they coincide with the PDF pages.

**Repo copies:** `ISO Sept 28 Status/inputs/papers/hydroacoustics/` is abbreviated to `papers/`.

**Copyright:** nothing cited here is an unauthorised copy. Closed works are cited only through what open
sources report about them, and are marked "not held".

## Literature

**[Blackman2004UCRL]** Blackman, D.K., de Groot-Hedlin, C., Orcutt, J.A., Harben, P.E. (2004). *Methods for
Calibrating Basin-Wide Hydroacoustic Propagation in the Indian Ocean.* Lawrence Livermore National
Laboratory, UCRL-TR-207323. doi:10.2172/15011808.
- **Obtained:** OSTI, public US-government report. Repo `papers/ucrl-tr-207323.pdf`; artifact 3b556efc.
- **Extracted tables:** branch zip `Blackman_2004_extracted_data_2026-09-27.zip` (repaired), sha256
  96b0cb89…70d8f7 (`data/blackman/MANIFEST.txt`).
- **Values used:**
  - p. 7: airgun array of 8,465 in³; source level 230–240 dB re 1 µPa at 1 m; Fig. 2, near-source
    spectrum (`air9_tl_validation.py`).
  - p. 8 (§4.1):
    - air9 recorded at H01, 1,665 km;
    - "about 4825 km" to H08S, wrong (ruling H1);
    - "only shots … clearly visible in the VLF band";
    - air8 "blockage … not known to be significant" (`air8_negative_control.py`).
  - p. 21: Fig. 22 and **Fig. 23, measured TL**, digitised by `digitise_blackman_fig23.py` from the page
    image (artifact 99b55187) into `data/blackman/fig23_air9_digitised.csv`; resolution 0.28 dB and 0.35 Hz
    per pixel.
  - p. 24: Appendix B timings, including JD144 10:54:57.77 (A4, not A3).
- **Supports:** amended sequence item 1 (air9 validation, air8 control). Results notes `e95705a` and
  `hydroacoustics-blackman-validation.md`.

**[Blackman2004JASA]** Blackman, D.K., de Groot-Hedlin, C., Harben, P., Sauter, A., Orcutt, J.A. (2004).
Testing low/very low frequency acoustic sources for basin-wide propagation in the Indian Ocean.
*J. Acoust. Soc. Am.* 116, 2057–2066. doi:10.1121/1.1786711.
- **Not held** (closed). Cited for context only; no values are taken from it.

**[Kadri2024]** Kadri, U. (2024). Underwater acoustic analysis reveals unique pressure signals associated with
aircraft crashes in the sea: revisiting MH370. *Scientific Reports* 14, 10102.
doi:10.1038/s41598-024-60529-1.
- **Obtained:** gold OA, CC BY 4.0; repo `papers/kadri2024.txt`.
- **Digitised data:** the withdrawn-archive bundle `.sources/kadri-2024-hydroacoustics/data/` (Table 1 csv;
  Fig. 9 vector traces). No bundle `.md` was read.
- **Values used:**
  - p. 9: Fig. 9; text "no observed signals" (9b); the two Fig. 9c signals, 57° and "recorded at
    00:52 UTC" at 306°.
  - p. 11: bearing "accurate to ±0.4°" at 99.5% (claimed); 2–40 Hz band-pass.
  - p. 14: Table 1, 19 transients, and its caption (00:52 at 57°; 00:54:30 at 306.18°).
  - p. 15: Sinabang M2.7 bearing 63.7° against geographic 67.12°, "deviation of 3.3°". This is the
    **demonstrated** bearing sd in brief §5.
- **Supports:** 2a test (`kadri_table1_test.py`, `0b14da9`/`e0ad490`; note
  `hydroacoustics-kadri-table1-test.md`, `8ae2534`/`cedbf3e`); bearing mixture (`bearing_mixture_rerun.py`).

**[CMST2014]** Duncan, A.J., Gavrilov, A.N., McCauley, R.D. (2014). *Analysis of low frequency underwater
acoustic signals possibly related to the loss of Malaysian Airlines Flight MH370.* Centre for Marine Science
and Technology, Curtin University, Project CMST 1308, Report 2014-30, prepared for the ATSB, 23 June 2014.
- **Obtained:** public (ATSB). Repo `papers/CMST_1308_Report_2014-30_MH370_PassiveAcoustics_-_Final.pdf`.
- **Values used:** pp. 3, 6 and 28: HA01 bearing 301.6° ± 0.75° (the Curtin event). This is a demonstrated
  bearing accuracy, and it is NOT the core region; it must not be used as a prior.
- **Supports:** the bearing-mixture core (`bearing_mixture_rerun.py`).

**[DuncanDallOsto2023]** Duncan, A.J., Dall'Osto, D.R. (2023). Long-range underwater acoustic detection of
aircraft surface impacts — the influence of acoustic propagation conditions and impact parameters.
*J. Acoust. Soc. Am.* 154, A49 (abstract). doi:10.1121/10.0022761.
- **Not held** beyond the abstract.

**[DuncanDallOsto2023lay]** Duncan, A.J., Dall'Osto, D.R. (2023). The loss of an F35 fighter aircraft and the
search for Malaysian Airlines flight MH370. Acoustical Society of America lay-language paper, 185th meeting.
https://acoustics.org/the-loss-of-an-f35-fighter-aircraft-and-the-search-for-malaysian-airlines-flight-mh370/
- **Obtained:** free web; image copy at repo `papers/duncan-fig3.png`.
- **Digitised:** Fig. 3, the signal and depth panels, by `digitise_duncan_fig3.py`, into the module's
  `data/` csvs.
- **Note:** the "MH370 path" in that figure is the CMST 301.6° bearing, not the core region.

**[Brown2026]** Brown, P., McFadden, L., McCormack, D., Adams, M., Vida, D. (2026). A search for hydroacoustic
signals from bolides. *Icarus* (accepted 14 Apr 2026). arXiv:2604.12723, doi:10.48550/arXiv.2604.12723.
- **Obtained:** arXiv, CC BY 4.0. Repo `papers/brown2026.pdf` and `.txt`.
- **Values used** (manuscript pages):
  - p. 9: Eq. 2 (Arons), P_peak = 52.4×10⁶ (R/W^(1/3))^−1.13.
  - p. 17: F-35A, 9 Apr 2019: impact energy 900 ± 200 MJ; peak 0.7 Pa at H11; range 3,300 km;
    coupling "of order 10⁻⁴"; shallow SOFAR at 500–700 m.
- **Supports:** the F-35A η inversion (η = 2.08×10⁻⁴; amended sequence item 1, blocked) and the η prior
  span.

**[Metz2023]** Metz, D., Obana, K., Fukao, Y. (2023). Remote hydroacoustic detection of an airplane crash.
*Pure Appl. Geophys.* 180, 1343–1351. doi:10.1007/s00024-022-03117-6.
- **Not held** (closed). No values are taken from it; the crash position and waveform are to be requested
  under §9.

**[Arons1954]** Arons, A.B. (1954). Underwater explosion shock wave parameters at large distances from the
charge. *J. Acoust. Soc. Am.* 26, 343–346. doi:10.1121/1.1907339.
- **Not held** (closed). The equation is used as given in Brown2026 Eq. 2.

**[Davey2016]** Davey, S., Gordon, N., Holland, I., Rutten, M., Williams, J. (2016). *Bayesian Methods in the
Search for MH370.* SpringerBriefs in Electrical and Computer Engineering. doi:10.1007/978-981-10-0379-0.
- **Gold OA.** The project's base reference; this module takes no hydroacoustic values from it.

**[CMST2014ScottReef]** Duncan, A., McCauley, R., Gavrilov, A. (2014). *Results of analysis of Scott Reef IMOS
underwater sound recorder data for the time of the disappearance of Malaysian Airlines Flight MH370 on 8th
March 2014.* Centre for Marine Science and Technology, Curtin University, 4 September 2014 (5 pp.).
- **Obtained:** inside IMOS `MH370.zip`
  (`MH370/Scott Reef IMOS logger data analysis for 2014_03_08_Release.pdf`); read after pre-registration
  `0ffa244`.
- **Values used:**
  - p. 1: the Curtin event at Scott Reef at 01:32:49 UTC; recordings "dominated by Bryde's whale calls"
    at 25–50 Hz.
  - p. 2: drift-corrected record start 01:29:45.9 UTC, which is the clock check; Fig. 1 caption.
  - p. 3: Table 1 fix, 2.11°N 69.31°E, 00:25:13.3 ± 85 s.
- **Supports:** item 1d (`hydroacoustics-imos-noise.md`) and the 2b/2c positive controls.

## Data

**[GEBCO2026]** GEBCO Bathymetric Compilation Group (2026). *The GEBCO_2026 Grid — a continuous terrain model
for oceans and land at 15 arc-second intervals.* NERC EDS British Oceanographic Data Centre NOC.
doi:10.5285/4f68d5c7-45eb-f999-e063-7086abc036fa.
- **Obtained:** CEDA OPeNDAP (`gebco_2026` elevation and TID grids); GEBCO licence (public domain, with
  attribution).
- **Used:** path bathymetry and TID in the provisional stub (`build_path_stub.py`); the air8 ridge crest of
  1,116 m at 28.55°S 97.78°E.

**[WOA23]** Reagan, J.R., Boyer, T.P., García, H.E., Locarnini, R.A., Baranova, O.K., Bouchard, C., et al.
(2023). *World Ocean Atlas 2023.* NOAA National Centers for Environmental Information. doi:10.25921/va26-hv25.
- **Obtained:** NCEI THREDDS: the 95A4 decade, season 16, 1.00° temperature and salinity (URLs in
  `build_path_stub.py`).
- **Used:** stub sound-speed profiles. The subset netCDF is artifact 64c7fd97.

**[IMOS-ANMN-PA]** Integrated Marine Observing System (IMOS), Australian National Mooring Network, passive
acoustic loggers; Curtin University CMST.
- **Loggers:** Perth Canyon 3315 and 3376; Scott Reef 3250. Logger metadata in repo
  `papers/3315_3250_3376__MetaData.txt` and `CalibrationNotes.txt`.
- **Obtained:** primary public copy, `https://imos-data.s3-ap-southeast-2.amazonaws.com/IMOS/ANMN/Acoustic/`
  (`MH370.zip`, `Portland_MH370.zip`); sha256 in `SHA256SUMS.txt`, recorded at retrieval.
- **Licence:** IMOS data are CC BY 4.0, with the IMOS/NCRIS acknowledgement.
- **Used:** items 1d and 2b (pending).

**[FDSN-IM]** IMS hydroacoustic stations, FDSN network code IM; station metadata from the EarthScope FDSN
station service (`https://service.earthscope.org/fdsnws/station/1/query`), epoch valid 2014-03-08.
- **Used:** H01W, H08S, H08N, H11N and H11S positions (`fetch_stations.py`, `data/stations.csv`).

## Software and standards

**[Porter1992]** Porter, M.B. (1992). *The KRAKEN Normal Mode Program.* Naval Research Laboratory,
NRL/MR/5120-92-6920.
- **Engine:** Acoustics Toolbox source `at_2026_8_29.zip` (oalib.hlsresearch.com; GPL-3), sha256
  307773ce…20d7; built arm64, artifact 1bd321c2.
- **Used:** `kraken_tl.py`.

**[FrancoisGarrison1982a]** Francois, R.E., Garrison, G.R. (1982). Sound absorption based on ocean
measurements. Part I: Pure water and magnesium sulfate contributions. *J. Acoust. Soc. Am.* 72, 896–907.
doi:10.1121/1.388170.

**[FrancoisGarrison1982b]** Francois, R.E., Garrison, G.R. (1982). Part II: Boric acid contribution and
equation for total absorption. *J. Acoust. Soc. Am.* 72, 1879–1890. doi:10.1121/1.388673.
- **Used:** volume attenuation inside KRAKEN (T 4 °C, S 34.7, pH 8, z̄ 1000 m).

**[TEOS10]** IOC, SCOR, IAPSO (2010). *The International Thermodynamic Equation of Seawater 2010.*
Intergovernmental Oceanographic Commission, Manuals and Guides No. 56, UNESCO.
- **Implementation:** McDougall, T.J., Barker, P.M. (2011), *Getting started with TEOS-10 and the Gibbs
  Seawater (GSW) Oceanographic Toolbox*, SCOR/IAPSO WG127; Python gsw 3.6.
- **Used:** SA, CT and sound speed in `build_path_stub.py`.

**[Vincenty1975]** Vincenty, T. (1975). Direct and inverse solutions of geodesics on the ellipsoid with
application of nested equations. *Survey Review* 23(176), 88–93. doi:10.1179/sre.1975.23.176.88.
- **Used:** `physics.rs`.

**[Karney2013]** Karney, C.F.F. (2013). Algorithms for geodesics. *J. Geodesy* 87, 43–55.
doi:10.1007/s00190-012-0578-z.
- **Used:** the reference check of `physics.rs`; GeographicLib/pyproj in the prepare scripts.

*Hydroacoustics module, 2026-10-09. Update in the same commit as any new use.*
