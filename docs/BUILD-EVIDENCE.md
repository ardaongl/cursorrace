# Build evidence — CursorRace

M0: independent preflight PASS from the preceding read-only review. Build authorized by the attached goal objective. Status transition is administrative; product acceptance remains NOT_RUN.

Runtime reverified: CPython3.14.8, pip26.2.1 on macOS. All eight ACs, 17 immutable fixture/golden pairs, snapshot-only policy and AC05 bytecode exception remain binding. No remote or publication authorization. Raw build logs belong in .local-verification/build/.

Executed M0 metadata transition check: `PYTHONDONTWRITEBYTECODE=1 python3.14 -B scripts/factory_validate.py --project-dir ${PROJECT_ROOT} --phase preflight` exited 0, metadata PASS. This records the prior verified preflight; it is not product acceptance.

M1 completed: `.venv/bin/python -m unittest tests.test_validation tests.test_cli -v` exited 0, 15 tests passed. Raw command/output: `.local-verification/build/m1.json`. Installed wheel tested for CLI errors and help. Traversal deliberately unavailable until M2.

M2 completed: `.venv/bin/python -m unittest tests.test_oracle tests.test_traversal tests.test_reporting tests.test_validation tests.test_cli -v` exited 0, 27 tests passed, including 13 analysis goldens, ordered snapshot partitions, mutation semantics and traversal boundaries. Raw evidence `.local-verification/build/m2.json`.

M3 completed: targeted installed CLI/report/schema/fixture tests exited 0 (18 tests); full unittest discovery exited 0 (37 tests). All 17 immutable fixtures were exercised through console and module entry points outside checkout. Initial safety-harness failures identified unmapped CPython-owned FileIO descriptors and a calibration control that did not import the product; provenance mapping was corrected in the test harness, with no product contract weakening. Guarded ordinary/suppressed executions and real EPIPE/SIGINT/substitution regressions now pass.

M4 CI action tag references were resolved read-only through the official GitHub API: actions/checkout v4 -> 11d5960a326750d5838078e36cf38b85af677262; actions/setup-python v6 -> ece7cb06caefa5fff74198d8649806c4678c61a1. Workflow is prepared only; no hosted run exists.

M4 first package-gate attempt failed on textual Requires-Python ordering; the metadata had equivalent constraints in canonical order. The test now compares the exact two constraints as a set (no range change). Failure commands preserved in `.local-verification/build/package-first-failure.json`. Second run of `.venv/bin/python -m tests.package_gate` exited 0: direct wheel and sdist-rebuilt wheel each installed into a clean venv with network denied, both entry points matched all 17 goldens, 68 process comparisons. Artifacts and backend hashes recorded in `.local-verification/build/package/result.json`. Final candidate refresh follows.

## Final local acceptance

The final local unit command `.venv/bin/python -m unittest discover -s tests -v` exited 0: **38 tests, no skips**, including generated subcases and real installed subprocesses. Raw stdout/stderr and command: `.local-verification/build/final-unit.json`.

The final installed fixture command `.venv/bin/python -m tests.fixture_gate` exited 0: **17/17 immutable fixture/golden pairs**, each through the console and module entry point outside checkout (34 process comparisons). Deliberate exits 0/1/2 were compared exactly; they were not converted into unconditional success. Raw evidence: `.local-verification/build/final-fixtures.json`.

The isolated package command `.venv/bin/python -m tests.package_gate` exited 0: direct wheel, sdist and sdist-rebuilt wheel built with the pinned backend; two fresh offline installations, zero runtime requirements, packaged README/schemas/MIT license present; both entrypoints matched every fixture (68 comparisons). `.local-verification/build/package/result.json` retains actual commands, exits, tool output, artifact locations and SHA-256. It is refreshed after final documentation/status changes before completion.

| AC | Independent local evidence | Result |
|---|---|---|
| AC-01 | SnapshotTests plus frozen-membership goldens, including deleted original and inserted unexpected IDs | PASS |
| AC-02 | FindingTests plus overflow/order/duplicate/unknown and combined-finding goldens | PASS |
| AC-03 | TraversalTests plus incomplete/chain/cycle/post-terminal cases | PASS |
| AC-04 | ValidationTests and SchemaTests: byte/depth/cardinality/encoding/lexical/ledger boundaries, 5,000-digit and near-cap integers, invalid tails | PASS |
| AC-05 | ReportTests: canonical bytes/counters, ordinary cold-cache and pre-startup-suppressed runs, guarded writes/network, input hashes/metadata, IO and domain/error outcomes | PASS |
| AC-06 | CliTests: exact help/version/errors/channels, literal paths, actual EPIPE and SIGINT, bounded FIFO substitution, read failures and stream doubles | PASS |
| AC-07 | final-fixtures.json: all 17 goldens, actual installed console/module processes | PASS |
| AC-08 | package/result.json: clean backend/build/install environments, wheel and sdist routes, metadata/assets and 68 installed golden comparisons | PASS |

AC-05 calibration deliberately attempts 11 forbidden operations, including same-bytes rewrite, transient create/delete, rename/restore, bytecode-looking application paths, file-descriptor mutation, logging/tempfile creation and socket creation. Denials are recorded even when caught. Ordinary cold-cache runs classify CPython import operations by provenance; environment and -B suppression runs create no bytecode within the inspected sandbox. This is a Python-level instrumentation plus filesystem-inspection boundary, not universal native/OS syscall tracing. Product source inspection shows only bounded read-only file access in cli.py, with checking/report modules free of filesystem/network operations. Startup instrumentation and build/install writes are test-harness behavior outside normal auditing.

No numeric line-coverage threshold was specified or invented. Behavioral partitions and negative cases are the quality gate; a separate adversarial product audit remains mandatory before publication. Runtime/platform verified locally: macOS arm64, CPython3.14.8, pip26.2.1, setuptools80.9.0. Ubuntu24.04 is prepared in CI but no hosted execution is claimed.

Protected fixture/schema hashes are compared against `.local-verification/build/protected.json`. Final source/toolchain/command/artifact attestation is recorded outside the source distribution at `.local-verification/build/final-attestation.json`, avoiding self-referential hashes. No commit SHA is invented. LOCAL_READY does not imply AUDIT_PASS or RELEASE_READY, and READY_FOR_INITIAL_PUSH remains NO.

## Independent audit blocker and AC-06 hardening

The subsequent independent audit was BLOCKED by D1 (P2, AC-06), despite the original 38-test success. CPython streams initialized as None after pre-startup descriptor closure escaped intended IO handling. The prior report is preserved in `.local-verification/hardening/prior-audit/`.

The narrowly scoped repair adds explicit missing-stream checks, with three permanent subprocess regression methods. Before the fix, the descriptor regression exited 1 with 12 failing subcases; after reinstall, the targeted five-method stream command exited 0. Fresh full discovery exited 0 with **41 tests, no skips**; fixture gate exited 0 with **17 pairs / 34 comparisons**; isolated package gate exited 0 with **68 installed comparisons**. Final packaging is refreshed after ledger updates. See [hardening evidence](HARDENING-EVIDENCE.md), fresh `.local-verification/hardening/` logs and external final-attestation.json. Original build evidence above remains historical and intact.

All eight ACs are locally verified on the hardened candidate; independent audit remains unresolved pending a separate reaudit. No AUDIT_PASS, hosted CI success or RELEASE_READY is claimed. The P3 wheel README links are deferred. No commits, remote changes or publication occurred.

Publication note: historical command spellings above use portable project/tool references. Exact original commands and host paths remain in ignored local evidence; no test outcome was changed.
