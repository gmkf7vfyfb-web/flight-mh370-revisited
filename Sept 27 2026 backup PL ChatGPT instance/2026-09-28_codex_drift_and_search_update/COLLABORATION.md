# Shared GitHub workflow

Use this repository as the canonical versioned project record. Computation happens in local clones or a chosen compute environment; GitHub is not a mounted disk and does not automatically synchronize local changes or chat histories.

For work by several people or AI systems:
1. Each participant uses its own clone/worktree and a separate task branch based on current main.
2. Read the repository AGENTS.md and latest research-state notes before changing models. Record the starting commit and assigned scope.
3. Save new results in versioned folders with model assumptions, evidence labels, input hashes, seeds and numerical checks. Keep immutable source inputs unchanged.
4. Commit bounded changes and open a pull request. Have another participant review scientific assumptions and validation, then merge and synchronize main before the next task. Avoid simultaneous changes on one branch or force-pushing shared history.
5. Exchange durable handoff notes in the repository; one model cannot infer another's private chat, uncommitted files or running processes. Each model needs its own authorized repository integration and compute/data access.

Keep code, manifests, summaries and selected figures in Git. Use release assets or a suitable data store for large immutable ensembles, with checksummed links. GitHub blocks individual normal-Git files above 100 MiB. Do not put credentials or restricted third-party documents in this public repository.

This backup addition is additive on main as requested; the branch/PR workflow is the recommendation for subsequent concurrent development.
