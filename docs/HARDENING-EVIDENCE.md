# AC-06 closed-descriptor hardening — 2026-10-19

The independent release audit was **BLOCKED** by D1 (P2, AC-06). CPython exposes a standard stream as None when its descriptor is closed before interpreter startup. The CLI called `.write()` unconditionally: unavailable stdout became INTERNAL, while unavailable stderr raised an uncaught AttributeError and exited 1 instead of 3. Both installed entrypoints reproduced this. The prior report/results are retained under `.local-verification/hardening/prior-audit/`; the prior candidate fingerprint was `5fed33c493283f5cc7b186bb230ac6344725906bbfcf6601e7398911fc877b14` (SHA-256 of the sorted JSON file/hash mapping).

The local repair adds only two explicit stream checks in `src/cursorrace/cli.py`: unavailable stdout routes to OUTPUT_IO; unavailable stderr returns 3 without further diagnostic output. Existing write/flush failure handling remains intact. Validation output with only stderr unavailable still exits 2 on stdout; successful output still exits 0. No snapshot, cursor, ledger, schema, fixture/golden, dependency or filesystem contract changed. No catch-all AttributeError handler masks unrelated defects.

## Permanent regressions and executed results

Three methods were added to `tests.test_cli.CliTests`:

- `test_closed_descriptors_in_installed_entrypoints`: 16 subprocess comparisons (eight cases, two forms), covering missing input with stderr absent, version with stdout/both absent, successful/domain/validation reports with stdout absent, and validation/pass output with only stderr absent.
- `test_preclosed_pipe_peers_in_installed_entrypoints`: six subprocess comparisons covering stdout, stderr and simultaneous EPIPE; all readers close before launch.
- `test_normal_streams_in_installed_entrypoints`: eight subprocess comparisons preserving exact version and pass/fail/validation bytes, channels and exits.

Descriptor closure uses POSIX `preexec_fn` after subprocess pipe setup and before exec. It does not use DEVNULL, a Python stream double or sleep. macOS and Linux are supported; descriptor-specific methods explicitly skip Windows, outside v1 support. Exact tuples reject observable tracebacks, wrong INTERNAL categorization and inappropriate stdout fallback.

The new descriptor test was run before the product fix: exit 1, 12 failing subcases (`red-descriptors.json/.stderr`). This proves the regression detects the original installed defect. After reinstalling the corrected distribution, the targeted five-method command (three new methods plus existing real EPIPE and write/flush failure methods) exited 0: five tests (`stream-regressions.json/.stderr`). Six separately recorded observations reproduce the three original defects in both installed invocation forms; all now exit 3, with OUTPUT_IO when stderr is observable (`original-reproductions.json`).

All raw evidence below is under `.local-verification/hardening/`. Commands use CPython 3.14.8 with pip 26.2.1 and setuptools 80.9.0 on macOS arm64. The evidence runner sets PYTHONDONTWRITEBYTECODE=1 before subprocess startup and removes PYTHONPATH; safety tests deliberately remove bytecode suppression for ordinary cold-cache runs. JSON records include actual argv/CWD/exit, timestamps, interpreter/OS/tool versions, fixture/schema hashes, source-file maps and captured stdout/stderr paths.

| Check | Command | Executed result | Evidence |
|---|---|---|---|
| Full unit | `.venv/bin/python -m unittest discover -s tests -v` | exit 0; 41 tests, no skips | full-unit.json/.stderr |
| Fixture gate | `.venv/bin/python -m tests.fixture_gate` | exit 0; 17/17 pairs through both forms, 34 comparisons | fixture-gate.json/.stdout |
| Package gate | `.venv/bin/python -B -m tests.package_gate` in a disposable candidate copy | exit 0; both artifacts, 68 golden comparisons | package-preliminary.json; final refresh in package-final.json and package/result.json |
| Factory local metadata | `python -B scripts/factory_validate.py --project-dir . --phase local` | recorded in factory-local.json after final ledger update | factory-local.json/.stdout |

The unchanged package gate runs in a disposable source copy with the local venv linked solely to launch its orchestration; the gate itself creates clean isolated backend/build/install environments. This preserves the original M0–M4 `.local-verification/build/` evidence. Final hardening artifact bytes and command records are archived in `hardening/package/`; `invocation.json` records the copy CWD, source-file hashes and archive hashes. Artifact paths inside the gate's result identify their original execution-time locations; the same basenames under this archive retain their bytes. After the final documentation/status changes, the package gate is repeated to refresh the distributed candidate. Final artifact regression runs are recorded separately in `artifact-stream-regressions.json`.

AC-01–08 pass locally through these fresh gates. AC-05 includes the existing calibrated mutation-attempt/network guards, unchanged inputs/sentinels, ordinary cold-cache and pre-startup-suppressed entrypoints, and successful/domain/validation/IO outcomes. This is scoped Python instrumentation plus filesystem observation, not a universal OS/native zero-write guarantee. Canonical fixtures and repeated locale/process comparisons establish deterministic output. Final protected-file comparison and candidate fingerprint are in `final-attestation.json`, recorded outside packaged source to avoid self-referential attestations.

## Audit and release state

D1 is locally repaired and regression verified; the **independent audit remains unresolved** until a separately requested audit passes on the hardened candidate. No independent reaudit was performed in this hardening task. M0–M4 history is preserved. LOCAL_READY is distinct from AUDIT_PASS and RELEASE_READY. Hosted CI remains PENDING_HOSTED_CI. No Git repository, commit, remote, push, publication or deployment was created.

The P3 wheel README issue (eight unresolved relative documentation links) is **DEFERRED**, nonblocking. No packaging behavior or README rewrite was added to this AC-06 repair. Ubuntu hosted execution, name/legal checks and publication authorization remain outside this local result.

NEXT_ACTION: separately request an independent adversarial reaudit of the final hardened candidate; no initial push is ready or authorized.

Publication note: historical command spellings above use portable project/tool references. Exact original commands and host paths remain in ignored local evidence; no test outcome was changed.
