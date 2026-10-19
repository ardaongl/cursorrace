# Specification verification — 2026-10-19

The original verification below is historical evidence for the original specification fingerprint. Subsequent read-only preflight found the AC-05 bytecode boundary blocker. The user-approved remediation and its verification are recorded in the final section; the original fingerprint must not be presented as evidence for the revised documents.

PHASE: spec. STATUS: SPEC_READY. Executed at 2026-10-18T23:00:58.612609+00:00; user-facing date uses Europe/Istanbul. CWD: ${PROJECT_ROOT}.

## Executed checks

| Actual command | Exit | Result / scope |
|---|---|---|
| `python3.14 --version` | 0 | CPython3.14.8 observed |
| `python3.14 -m pip --version` | 0 | pip26.2.1 observed |
| `python3.14 -m venv ${SPEC_VALIDATION_ENV}` | 0 | Temporary spec-validator environment created |
| `${SPEC_VALIDATION_ENV}/bin/python -m pip install jsonschema==4.25.1` | 0 | Validation-only tooling installed outside project; no runtime dependency added |
| `${SPEC_VALIDATION_ENV}/bin/python .local-verification/spec-check.py` | 0 | Both schemas meta-valid, 17 static inputs/expected reports consistent, canonical output bytes/counters/exits, intentional invalid shapes/duplicate key, newline regex rejection, links/placeholders, eight NOT_RUN ACs and spec-only file inventory |
| `python3 scripts/factory_validate.py --project-dir ${PROJECT_ROOT} --phase spec` | 0 | Metadata PASS, no errors; warning explicitly says metadata cannot verify source, external CI or authorization |

Local logs: `.local-verification/spec-check.txt`, `.local-verification/factory-spec.txt`. The custom check and file hashes are retained locally for reproduction, excluded from version control. Validation-tool resolved environment: jsonschema4.25.1, attrs26.1.0, jsonschema-specifications2025.9.1, referencing0.37.0, rpds-py2026.9.1. These are not product dependencies.

Artifact fingerprint: SHA-256 `894f5136895ff4ed5f0cae5d63d2084101431723ebd80c9b696296866e44e70d` over the sorted per-file hash manifest `.local-verification/spec-files.sha256`. Covers 52 specification/schema/fixture files; excludes this report and local logs/scripts so it is not self-referential. No Git commit SHA exists.

## Interpretation and remaining risk

Schema checks verify shape and static reports; ledger/oracle expected findings were reviewed against the prose, not executed against a product. All product ACs remain NOT_RUN. No product test, packaging install, product audit, CI or release evidence exists. No Git initialization/remotes/push/publication occurred. Scope consists of Markdown, JSON schemas/static fixtures and ignore rules. No product code was written.

No unresolved specification blockers. Remaining limitations are declared: independent snapshot/capture trust, snapshot-only policy, no causal or concurrency proof, no validated customer demand and no name/package clearance. Build gates remain planned. No user authorization is needed to complete spec; an explicit later phase request is needed to begin preflight/build, and exact remote/publication authorization is separate.

NEXT_ACTION: preflight on explicit request; stop this phase at SPEC_READY.

## Spec remediation — approved CPython bytecode boundary

The user approved Option 1: exclude only CPython interpreter-managed import bytecode artifacts from the application's no-write guarantee. AC-05, the technical contract, test plan, architecture, README and the ADR reference now use that boundary. Application-controlled user-data/input/artifact mutation and intentional application logs, temporary files, caches and state remain forbidden. The documented stricter procedure activates PYTHONDONTWRITEBYTECODE=1 or -B before interpreter startup and makes no universal OS-level zero-write claim.

Future tests must cover ordinary cold-cache and pre-startup-suppressed invocation, passing and failing audits, input preservation, interpreter-artifact attribution, and calibrated mutation-attempt detection as well as visible filesystem differences. Additional regression plans cover oversized integer lexemes, nonregular-file substitution between inspection/open, and missing bytecode caches. No product tests were written or executed in this remediation.

The machine-readable lifecycle remains SPEC_READY, all eight product ACs remain NOT_RUN, and independent M0 review is pending. A factory preflight metadata check cannot pass until M0_PASS is appropriately recorded after that review; this workflow-status prerequisite is distinct from a specification defect. Remediation does not assert M0_PASS or authorize implementation.

Verification recorded 2026-10-19T10:14:13Z (2026-10-19 in Europe/Istanbul), from ${PROJECT_ROOT}:

| Executed specification check | Exit/result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3.14 -B scripts/factory_validate.py --project-dir ${PROJECT_ROOT} --phase spec` | 0; metadata PASS, with its metadata-only warning retained |
| `PYTHONDONTWRITEBYTECODE=1 ${SPEC_VALIDATION_ENV}/bin/python -B .local-verification/spec-check.py` | 0; both schemas and all 17 fixture/golden pairs consistent, canonical output expectations intact; product behavior not tested |
| Inline CPython3.14 document-reference and boundary-consistency check | 0; 10 local references/heading anchors valid; approved boundary, startup suppression, A–F test obligations and three regression plans present |
| In-memory before/after SHA-256 and document-content assertions | PASS; all 35 fixture/manifest files and both schemas byte-identical; all eight AC numbers preserved, only AC-05 row changed; GOAL, AGENTS, milestones and machine status unchanged; other CLI/input/ledger/traversal/output/error and trust/versioning rules preserved |

Exact check commands, stdout, exit codes and original file hashes are retained in `.local-verification/spec-remediation-verification.json`. Revised artifact fingerprint: SHA-256 `1e3c4542b2c9ad4eca131888f068fd992f35f08c757e72f2400205755b7bbf32` over `.local-verification/spec-remediation-files.sha256`, covering 52 specification/schema/fixture files and excluding this report and local evidence to avoid self-reference. The historical manifest above remains historical; it is not overwritten.

REMEDIATION_STATUS: PASS. READY_FOR_READ_ONLY_PREFLIGHT: YES. No remaining blocker identified within this approved remediation; fresh independent preflight is still required. Product acceptance remains NOT_RUN. No product code, dependencies, commits or remotes changed. Stop here; do not begin implementation.

Publication note: historical command spellings above use portable project/tool references. Exact original commands and host paths remain in ignored local evidence; no test outcome was changed.
