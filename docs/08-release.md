# Local candidate, audit and publication boundary

Local implementation, tests, license, distribution artifacts and the CI workflow are prepared; the current verified gate is recorded in IMPLEMENTATION-STATUS.md. Initial publication is authorized for the public repository ardaongl/cursorrace on main; the implementation ledger records progress. CursorRace remains a working title, not proof of available distribution names.

Before LOCAL_READY run the full unittest, fixture and package gates in docs/04-acceptance.md with CPython3.14.8; all eight local ACs need evidence, not only metadata. Confirm strict schema/prose consistency, README demo, artifact contents, MIT license, clean dependency-free install and Ubuntu24.04 workflow. Verify ignore rules exclude traces with real secrets and local evidence. User-supplied traces are never automatically added to version control.

Before AUDIT_PASS conduct a separate read-only pass with independent negative cases and inspect source, test blind spots and installed artifacts. Record candidate fingerprint, commands, findings and resolution. Do not treat specification review as product audit. Changed source, packaging or contract invalidates affected evidence and the audit candidate.

Remote creation/configuration, any push, visibility/permissions changes or metadata edits need exact user authorization naming owner/repository, visibility and permitted actions. The current user authorization permits creating this repository and its origin remote only; never overwrite an existing destination. Package publishing, GitHub Release and deployment each need their own scope. Do not check name availability by reserving a package or creating a repository. License/name checks before publication must be documented; they do not block local specification.

After an authorized push record final 40-character SHA, GitHub Actions run URL, run head_sha, success conclusion, runtime and artifact hashes. All required gates must run on that SHA. Failed, pending, skipped or different-SHA runs cannot establish RELEASE_READY. Re-run CI after final changes rather than carrying earlier green badges forward.

Keep post-commit attestation local/external with date, exact final SHA and matching hosted evidence. A committed status file cannot contain its own final commit hash. Do not fabricate self-referential attestations. No source or product acceptance evidence is present at spec; hosted status remains PENDING_HOSTED_CI, audit NOT_RUN, release false.
