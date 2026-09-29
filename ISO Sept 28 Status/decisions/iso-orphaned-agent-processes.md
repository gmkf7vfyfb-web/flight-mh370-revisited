---
name: iso-orphaned-agent-processes
description: "iso daemon restarts orphan running Claude processes (PPID 1) that keep editing; `iso thread tell --mode auto` then starts duplicate agents on the same session"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b321a56a-4f19-4c04-acbd-d5031b94cf81
  modified: 2026-09-28T16:49:40.527Z
---

On 2026-09-26 the iso host daemon restarted several times (00:11 and about 00:21 UTC). Claude processes already running for threads were orphaned (PPID 1, no bridge parent). They kept working in their worktrees, unseen by iso.

`iso thread tell --mode auto` messages sent after the restart treated those threads as not running and started a new agent on the same session. The result was two or three agents per session in the ocean-drift, end-of-flight, core-stages, hydroacoustics and searched-areas worktrees: mixed uncommitted edits, duplicate jobs, and a shared regress directory.

The fix was to SIGTERM the PPID-1 copies. Each session had an attached copy (parent iso-claude-code-bridge) that carried on.

**Why:** the duplicates silently corrupt worktrees and session history, and nobody can steer an orphan.

**How to apply:**
- Before `--mode auto`, check that no process already serves that session: `for p in $(pgrep -f 'npm-global/bin/claude --output'); do echo $p $(ps -o ppid= -p $p) $(readlink /proc/$p/cwd); done`, and look for the same `--resume=<session>`.
- Prefer the default steer mode for threads that are active. Steer fails with "HTTP 409: Thread is not active" on idle or errored threads (e.g. after an outage); those need `--mode auto`, sent only after the process check above. After sending, confirm exactly one claude process per worktree (checked 2026-09-28).
- After any daemon restart, look for PPID-1 claude processes. A copy with a bridge parent is the live one.
- See [[thread-coordination]].
