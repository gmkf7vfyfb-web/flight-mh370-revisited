# Migration and GitHub guide

## Local preparation

The current workspace is prepared with:

- Git LFS rules in `.gitattributes`;
- a conservative `.gitignore`;
- receiving-agent instructions in `AGENTS.md`;
- handoff, provenance and reproducibility documents;
- an immutable archive, file inventory and SHA-256 manifests under
  `migration/package/` after the packaging script runs.
- a complete 148-file Library provenance layer under
  `library_full_audit/MH370/`.

## GitHub repository creation

Create an empty **private** repository named `flight-mh370-revisited`. Do not
initialize it with a README, `.gitignore` or license because those files already
exist locally.

The eventual authenticated push should be performed using an OAuth-authorized
GitHub integration, GitHub CLI, or SSH key. Never send a password, recovery
code or personal access token through chat.

## Suggested branch and review model

- `main`: reviewed, reproducible baseline.
- short-lived topic branches for modelling, evidence and manuscript work.
- pull requests for changes to priors, likelihoods, source data or reported
  headline results.
- tag the initial imported state `migration-2026-08-14`.

The full `.tar.gz` snapshot should be attached to a private GitHub Release for
that tag rather than committed as a normal Git/LFS repository file.

The working repository can use Git LFS for large PDFs, spreadsheets and image
artifacts according to `.gitattributes`. The immutable migration archive is a
separate release asset and should not be added to the Git history. Before the
first push, confirm that the receiving GitHub account or organization has
sufficient LFS storage and bandwidth for the retained binary corpus.

## Conversation history

Obtain the account data export, select only MH370-related conversations, and
place the sanitized outputs under `history/`. Do not commit an account-wide
ChatGPT export.
