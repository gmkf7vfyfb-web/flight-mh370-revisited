cat > module-thread-method-plain-english.md <<'EOF'
# One module, many short threads
13 Oct 2026. Written in simplified technical English.

## 1. What I am suggesting

Keep the module. Replace the thread.

A **module** is a role: the hydroacoustic specialist, with its master prompt, its inbox file, its
branch in the repository and its saved files. A **thread** is one conversation with that role. At
present the two are treated as the same thing, so one conversation has run since 8 October and now
holds 3,398 messages.

I suggest that each run gets its own thread, and that the module carries its state across threads in
files, not in conversation.

## 2. Why this works better

**The valuable state is already in files.** The branch, the saved files, the pre-registration
commits, the inbox: all on disk. A long conversation does not hold anything that those do not,
except habits and small facts that were never written down.

**A long thread costs on every turn.** The whole conversation is re-read each time the module does
anything. Most of what is re-read is old tool output that will never matter again.

**Folding loses the wrong things.** When a thread gets long, earlier parts are compressed into
summaries. Compression keeps the narrative and drops the detail: exact file paths, commit
identifiers, the name of the sidecar file that holds the pulse duration. Those are exactly the
things the module needs later. The current hydroacoustic thread has six folds.

**It makes the module write things down.** A handover note that a new thread must read is a
discipline, not an overhead. If a fact cannot be written into the note, it was not a fact, it was a
habit.

## 3. How to do it, step by step

**Step 1. Ask the current thread for a handover note.** One file in the repository, named
RUN-STATE.md, holding only these items:

- the branch name and the commit identifier at the head;
- where the inputs are, by full path, including anything written by another module;
- what is pre-registered and where that commit is;
- what is built, what is a stub and what is not started;
- the declared gaps, by their register identifiers;
- the agreed wording for the caveats, copied exactly;
- the open questions waiting on a ruling, and from whom;
- the next three actions, in order.

**Step 2. Have the thread commit the note and post one line to the architecture inbox** saying the
note exists and giving its commit.

**Step 3. Let the thread finish.** Do not keep it open as a spare.

**Step 4. Start a new thread on the same module profile.** The opening message is short and always
the same shape:

> You are the hydroacoustic module. Read your master prompt, then your inbox at
> coordination/HYDROACOUSTICS.md, then RUN-STATE.md at commit <id>. Confirm in ten lines what you
> hold, what is blocked, and what you will do first. Do not start work until I reply.

**Step 5. Check the ten lines.** If the module has a fact wrong, the handover note was incomplete.
Correct the note, not just the thread.

**Step 6. Run the work.** One thread, one run, one results note, one commit.

**Step 7. At the end of the run, go back to step 1.** The handover note is updated, not rewritten.

## 4. What can go wrong

- **A fact lives only in the old conversation.** Prevented by step 5: the first ten lines expose it
  before any work is done.
- **The note becomes a diary.** It must not. It holds state, not history. History is in the commits.
- **Two threads for one module at the same time.** Do not do this. Two threads will write to the
  same branch and the same inbox, and the second one to write will silently win.

## 5. What this does not change

The module threads stay independent of each other and keep talking through the architecture inbox,
as now. The rule that a module keeps moving and does not wait to be told the next step is unchanged;
it simply applies inside a shorter thread.
EOF
wc -w module-thread-method-plain-english.md