# Bluefin-21, 2014: 771.4 km² measured against ATSB's 860 km²

Searched-areas module, 9 October 2026. The brief's campaign table (§4) asks for this difference to be
**reconciled or reported**. It is reported, with the reason it cannot be closed from the available
geometry — and with a bound showing it cannot matter.

## The two numbers

**Measured, 771.41 km².** Geoscience Australia's published display geometry for the Bluefin-21
(Phoenix International *Artemis* AUV) search is two polygons:

| | vertices | area | extent |
|---|---|---|---|
| main | 30 | 758.14 km² | 103.8446–104.1869°E, 21.2636–20.9407°S |
| secondary | 5 (a rectangle) | 13.27 km² | 103.8217–103.8728°E, 20.9860–20.9129°S |
| **total** | | **771.41 km²** | |

on the authalic sphere, which is the module's embedded raster to 0.04 km² (771.37 km² at 0.01°).

**Stated, 860 km².** ATSB (2017), *The Operational Search for MH370*, **printed p. 42**, verified
9 October against the Drive copy: thirty AUV missions at 3,800–5,000 m collected 120 kHz side-scan at
a 400 m range scale and 45 m altitude; the tasking focused on "a 10 km radius around TPL detection
number two and a 3 km radius area around TPL detections one, three and four"; the search "was
completed on 28 May 2014 and covered 860 km² with no aircraft debris detected on the seafloor".

## What the gap is, and what it is not

The difference is **88.6 km², 10.3% of the stated area**, and it runs in the informative direction:
**the published display geometry is smaller than the stated coverage.** A display envelope normally
*over*-states coverage, because it fills the gaps between survey lines. That this one is 10% short
means the 860 km² includes ground outside the polygons GA published — most plausibly the outer or
later missions, which the display geometry does not enclose. So the display polygons are not an upper
bound on where the AUV looked, and treating them as the coverage layer is conservative, not generous.

Two things it is *not*. It is not the tasking: the circles named on p. 42 come to only
π·10² + 3·π·3² = **399 km²**, so both figures describe a search that went well beyond its nominal
boxes, consistent with thirty missions. And it is not a units or projection artefact: the two
polygons were integrated on the same authalic sphere as every other layer in the module.

**It cannot be closed without the AUV track or swath data**, which are not public. Recorded as a
reported difference, as the brief allows.

## Why it does not matter

The Bluefin-21 search lies at **21.0–21.3°S, 103.8–104.2°E**, around the towed-pinger-locator
detections. The impact distribution's support is **34–42°S**. There is no overlap at all: the centre
of the searched area is **2,473 km (1,335 NM)** from the leading candidate block of the residual
posterior at 39.5°S 89.0°E.

That is why the campaign removes **0.0000** of the mass both on the arc-kernel placeholder and on the
end-of-flight impacts, at every ρ in the sweep, and it is a stronger statement than the number alone:
the likelihood is exactly 1 there for every sample in the posterior's support, so the campaign's
coverage value is irrelevant to the result whether it is 771 km², 860 km², or anything else. Even at
the stated figure it is 0.71% of the Phase 2 union (0.64% as measured).

**It is kept in the campaign list** because the module's job is to represent the search record, and
because a future impact distribution — a different end-of-flight model, a northern conditional — could
in principle put mass there. The difference is flagged in the layer's own documentation so that no one
later reads 771.4 km² as the ATSB's figure.

---

*Searched areas, 9 October 2026.*
