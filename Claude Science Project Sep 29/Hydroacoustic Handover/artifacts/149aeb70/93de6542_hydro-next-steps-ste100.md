# What to do next, and what it will and will not tell us
13 Oct 2026. Written in simplified technical English. Standard statistical and scientific terms are
used as they are.

---

## Step 0. Settle which end-of-flight run is the one to use. Do this first.

**What it is.** Ask end of flight one question: does run I dive replace run I, or are the two
declared alternatives that the composer combines?

**Why it comes first.** The two runs are not the same model. In run I a push-over is levelled off
before the water, so only 4 in 100 of its impacts arrive at an angle between 10 and 45 degrees. In
run I dive, half of the push-overs carry on down, and 16 in 100 arrive in that band. That band is
short and loud, so it is the band hydroacoustics can detect. Every number in this module depends on
which run is used. If we run the tests first and the ruling comes later, we run them twice.

**What it tells us.** Which impact set is the one to predict from. It also tells the composer
something larger, because the same change moves the impact PDF itself.

**What it does not tell us.** Nothing about the sound. This is a question about the flight model.

**Cost.** No machine time. One question and one answer.

---

## Step 1. The Kadri northern conditional. Small, and it closes an open hypothesis.

Kadri's strongest signal carries a bearing of 306.18 degrees from Cape Leeuwin. That bearing crosses
the arc near 26.2 S, about 1,000 km north of where most of our impacts are. **No test we have run
could have found it**, because the two-station pair search only looks at time differences from 856 to
1,347 s, which covers the arc from 45.0 S to 28.9 S. A source at 26.2 S needs 1,493 s. The hypothesis
was left out by the way the test was built, not by evidence.

### Step 1a. Look at the digitised trace.

Plot the digitised Diego Garcia South record across 01:16:20 to 01:17:10, which is the predicted
arrival window, and across 01:11:30 to 01:14:10, which holds the only four energy outliers in the
whole record. We hold only per-shot summaries here, so this needs the module's own copy of the data.

### Step 1b. Pre-register the test before looking any further.

State, and commit, before any statistic is computed:

- the new time-difference span, 1,346 to 1,710 s, which joins the old span with no gap;
- the arrival windows: Diego Garcia South 01:16:19 to 01:17:33 and Perth Canyon 00:50:44 to 00:51:10
  for Kadri's text time, each at 95 per cent;
- the statistics: shot energy, inter-shot gap power, shape correlation against a local stacked shot
  template, windowed residuals on the leading and trailing shoulders, and a principal-component
  outlier score;
- the levels: screen at 0.3, mark at 0.1, report at 0.05, with the floor of 0.0101 stated;
- the null: the 98 background realisations we already hold.

### Step 1c. Run the tests.

At Perth Canyon over plus or minus 30 s, and at Diego Garcia South over plus or minus 37 s. Report
the p-value, the signal-to-noise ratio and the likelihood ratio for every candidate.

### Step 1d. Ask for the raw station data.

Request Diego Garcia South from 01:14 to 01:22. Kadri gives two different times for his own signal,
00:52:03 in his text and 00:54:30 in his caption. The second one puts the arrival at 01:19:23, which
is after the digitised record stops at 01:18:29. Only the raw data can test it.

**What Step 1 will tell us.** Whether anything at Diego Garcia South or Perth Canyon matches a source
at Kadri's own bearing, with a stated strength. If nothing matches and the power is good, the
northern locality is disfavoured by a number instead of by omission. If something matches at both
stations, that is two stations in agreement at a place our flight model also reaches at about the
right time, which is the strongest result available in this module.

**What Step 1 will not tell us.** It will not locate the impact: two stations give a curve, not a
point. It will not test Kadri's caption time until the raw data arrives. The digitised trace is a
drawing turned back into numbers, not a recording, so a null from it sets a bound and does not settle
the question. And one already-known fact limits the whole thing: each of Kadri's triggers at Cape
Leeuwin pairs with between 34 and 49 successive airgun shots at Diego Garcia South, so a match on
time alone is weak.

**Cost.** Under an hour of machine time. No heavy lock.

---

## Step 2. Option B, the main pass, on whichever run Step 0 names.

Predict what every receiver should have heard, screen out the receivers that can say nothing, scan
the ones that can, and measure the power by putting the predicted sound into the real noise.

**What it will tell us.** Which receivers could have heard a hard, fast impact; whether anything
matches; and what a silence is worth, as a 95 per cent upper limit on source loudness, a Bayes factor
and a figure in bits. The worth of a silence is the whole question: it is about 0.00005 bits if the
probability of detection is 0.1, and 0.199 bits if it is 1.0.

**What it will not tell us.** It will not prove the aircraft did not hit the sea hard. It will not
calibrate the source, because no public data gives the sound an aircraft makes hitting water. It will
not settle which reading of the 00:19 satellite data is right.

**Cost.** Two and a half to three and a half hours of machine time, about half of it needing the
heavy lock. Order against the ocean drift pilot is your decision.

---

## Step 3. The package for Kadri.

Send him the predicted arrival windows, the station geometry, the blocked paths and the test results.
Ask him two things: which of his two times for the main signal is right, and whether he examined the
end of his own Diego Garcia South panel against his northern bearing.

**What it will tell us.** It may resolve the time discrepancy, which decides whether the caption case
can be tested at all.

**What it will not tell us.** Nothing by itself about the impact.

**Cost.** No machine time.

---

## How this runs without a long thread

A hydroacoustic specialist profile already exists. The work can run as a sub-agent started from this
conversation, with the brief passed to it directly. It begins with a clean context, sees only what we
give it, and reports back here. You paste nothing, and the long thread is never loaded.

Two things change. The sub-agent is a child of this conversation, not its own thread, so the brief
must state the branch, the inbox and the commit rules instead of relying on habit. And it cannot see
what the long thread learned, which is the point, but it means the brief must carry the file paths,
the pre-registration rule and the agreed wording for the caveats.

---

## The order, and why

1. **Step 0**, because everything else inherits its answer.
2. **Step 1a and 1b**, because they cost almost nothing and because pre-registration must come before
   the statistics, not after.
3. **Step 1c**, the one genuinely new look at data we already hold.
4. **Step 1d and Step 3** together, since both are requests that take time to answer.
5. **Step 2**, the main pass, once the run is settled and the detection method has been exercised on
   a small target.
