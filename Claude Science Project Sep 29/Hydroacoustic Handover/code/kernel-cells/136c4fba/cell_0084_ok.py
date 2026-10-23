print(host.findings.mark_addressed(
    ["5f5b5f3f-f952-4097-b9f6-fcc1dc0cfd12"],
    note=("Fixed in commit 3bfa6b6. Two separate defects were in the flagged artifact version "
          "(63c9c2e8 = candidates.csv v1). (1) The E_shot/P_gap rows in the caption window carried "
          "computable=True with blank values; the guard now tests for all-NaN as well as an empty "
          "window, and those four rows read computable=False with the reason. Verified in the current "
          "artifact version 957e8f60. (2) The real inconsistency: pre-registration declaration 2 "
          "stated all five cycle statistics are untestable in the caption window, which is wrong and "
          "over-cautious. Only shot energy and inter-shot gap power need a CLOSED cycle (a following "
          "shot 9-11 s later, last one starting 01:18:19); shape correlation, the three shoulder "
          "residuals and the principal-component score need only a shot peak and its own [-3,+6] s "
          "window, and shot peaks continue to 01:19:09, so those four ARE computable on 2 shots. The "
          "digitised record itself runs to 01:19:58.998, so the work order's 'record ends 01:18:29' "
          "is also wrong; that is the end of the shot train. The pre-registered wording was left in "
          "place and a CORRECTION DISCLOSED block added beneath it recording the measured split, "
          "following the module's existing practice for defects found after a run. The results note, "
          "the RUN-STATE file and the inbox entry all already carried the corrected split; the "
          "pre-registration docstring was the one place that did not.")))
