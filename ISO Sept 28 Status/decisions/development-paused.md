---
name: development-paused
description: "Pete paused all MH370 development on 29 Sep 2026 (~19:00 UTC); don't resume or message module threads until he lifts it"
metadata:
  node_type: memory
  type: project
  originSessionId: b321a56a-4f19-4c04-acbd-d5031b94cf81
  modified: 2026-09-29T19:07:04.052Z
---

On 2026-09-29 at about 19:00 UTC, Pete said: "Let's also pause all development at this point." At that moment:
- no thread was running: six were stopped in an error state by a host restart at about 16:08 UTC, and the rest were idle;
- no compute job was running. The core estimator's chained job (corrected make report into runs/davey2016-next, then the MH371 control) had been killed by the restart, and never got past seed 1.

The ISO Sept 28 Status folder on GitHub is being refreshed in place with all code as of the pause. That is Pete's one-time override of the no-overwrite rule.

**Why:** Pete wants a complete, stable snapshot of all code, and no further changes, until he decides the next steps.
**How to apply:**
- Don't resume, steer or message any module thread, and don't restart the core estimator's chained job, until Pete lifts the pause.
- If a thread wakes on its own, tell it to stand still.
- On resuming, restart the chained job (report, then MH371) first.
- See [[github-recovery-export]], [[thread-coordination]].
