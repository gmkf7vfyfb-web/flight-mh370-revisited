# Pete's style, measured from the dissertation

Source: Large, P. O. (2019). *A Meta-Analysis of Geospatial Estimates in the Case of Malaysian
Airlines Flight MH370*. Doctor of Education, Oklahoma State University. ProQuest 2303836555.
Pete supplied his own source PDF (250 pages, text layer clean) on 12 October 2026 and confirmed
he owns the rights and published it open access. **Printed page = PDF page − 14**, checked at 14
sampled pages with no exceptions.

Measured 12 October 2026 over the whole document. These notes govern *suggested rewording only*,
never meaning.

## 1. Sentences

- **Median 27 words, mean 30.** Tenth to ninetieth percentile 6 to 60 words; longest 104. These
  are long, information-dense sentences that carry several qualifications in one structure, not
  short declaratives. My first proposed draft used noticeably shorter sentences than this and
  read as someone else's voice.
- One idea per sentence, but the idea arrives fully qualified: the condition, the instrument and
  the caveat are inside the sentence rather than split across three.
- Signposting is explicit and forward-looking: *"The results of the systematically sampled
  residuals … are first presented, both for … and for …"*; *"Finally, the probability density
  estimates … are also presented."* Sections announce their own contents before delivering them.

## 2. Person and voice

- **First person is almost absent**: 8 instances of "I" and 17 of "we" in 357,000 characters.
- Method is written in the **passive past**: "was performed", "were tested", "were estimated",
  "were calculated" — 75 instances of that construction.
- The study is the agent where an agent is needed: "this study" appears 26 times.
- Interpretation shifts to the active present: "the latter can be seen to be approximately
  Gaussian", "The Q-Q plot … suggests autocorrelation".

## 3. Numbers and units

- Sample sizes are given inline, in the sentence that uses them: "n=11", "n=42",
  "~100,000 systematically sampled … residuals".
- **Units are closed up to the number**: "150.1Hz", "−5.1Hz", "+4.4Hz", "12dBi". Not "150.1 Hz".
- Statistical results are reported with the test named, the statistic, the p-value and the
  significance level in one sentence: "A statistic = 0.56476, p-value = 0.135 … accepted at an
  α=0.05 level of significance".
- Times carry the Z suffix throughout: "04:04Z", "00:11Z", "18:25Z".
- Increments are stated as compound adjectives: "1-degree increments", "-0.1 increments".

## 4. Mathematics — the format to adopt

This is the pattern to copy, taken from printed pages 98 and 123.

1. **A lead-in sentence that ends in a colon**, naming the method and citing its source:
   *"the data were tested at an α = 0.05 level of significance using Cochran's Q statistic
   (Cochran, 1954):"*; *"A linear mixed-effects meta-regression (Schwarzer, Carpenter & Rücker,
   2015) of the form:"*
2. **A displayed equation, numbered on the right** in plain parentheses. Chapter-decimal
   numbering where chapters are long — `(3.1)`, `(3.2)` — and plain sequential numbering
   elsewhere — `(18)`, `(19)`.
3. **A running "where" clause immediately after**, in prose, defining every symbol in the order
   it appears, comma-separated, each with its physical meaning and its reference frame:
   *"where φ₇ is the estimate of arc-latitude crossing the 7th BTO arc considered here as the
   dependent variable, φ is an intercept, t_TS is the assumed time of the turn south after
   18:25Z, V_range is the range of ground track velocities for the constituent trajectories …"*
   **Not a symbol table.** A prose where-clause. (This also matches the journal: not one of the
   nine surveyed papers has a nomenclature list.)
4. **Mnemonic subscripts, not indices.** Observed: `φ₇` arc-latitude at the 7th arc; `t_TS` turn
   south; `V_range`, `A_range`, `C_course`; `μ_HL` hull-loss mean; `R_HullLoss`; `n_dec` decade.
   Subscripts are short words or recognised abbreviations, not running integers.
5. **Latin and Greek letters in their conventional roles**: φ for latitude, μ for a mean, σ for a
   standard deviation, τ² for a between-study variance, β for regression coefficients, ε for
   noise, α for a significance level, Q and χ² for named statistics. No invented glyphs.
6. A follow-up sentence stating what was done with the equation and on what data: *"was performed
   on the data from the 26 studies on sub-group 2"*.

## 5. Terminology to use

- **"arc-latitude"** for the latitude at which a trajectory crosses a satellite arc. His term,
  and a good one.
- "state vector" for the aircraft's position and velocity; "the aircraft state vector was known"
  for the periods with independent data.
- "sensitivity analysis" for a sweep over an assumption, which is what this project calls a
  sensitivity.
- Channel and burst identifiers written in full: "R1200-0-36ED", "R600-36E1".
- "probability density estimates" rather than "PDFs" in prose.

## 6. Spelling — and the one place to depart from him

The dissertation is **US-spelled**: "modeling" (2 against 1), "behavior" (2 against 0), "center"
(6 against 0), "meter" (37 against 0).

**The journal requires English (United Kingdom)** (`paper/JON-RULES.md` §4). So the paper departs
from the dissertation here and only here: UK spelling, his sentence structure and register.
"Modelling", "behaviour", "centre", "metre", "favours".

## 7. Citation habits — and the second place to depart

He writes "Ashton et al (2014)" — no comma before the year, no full stop after "al". The journal's
Harvard style requires "(Ashton et al., 2015)" with both. Use the journal's form.

He also cites by the online-first year in places where the printed issue is the following year;
`paper/CITATIONS-LEDGER.md` §4.1 records where that applies and which year the paper uses.

## 8. What not to copy

- The dissertation's chapter-decimal equation numbering is right for a 250-page document and
  wrong for a 19-page paper: the journal wants sequential numbering from (1).
- Its tables are numbered in a separate series with titles above in APA form; the journal wants
  its own form, caption above the table, figures captioned below.
- Its reference style is APA. The journal's is Harvard as set out in `paper/JON-RULES.md` §6.
