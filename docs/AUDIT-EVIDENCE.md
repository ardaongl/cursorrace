# Independent re-audit evidence — 2026-10-19

RELEASE_AUDIT: PASS. This records the separately performed read-only post-hardening re-audit; it does not claim hosted CI success. Exact raw report, scripts and observations are archived under ignored `.local-verification/reaudit/`.

The reviewed 83-file hardened candidate fingerprint was `490288eff5d54e36b2bfc1322dee755f2efcb2bc74beb1a8729a2d753dcc3657`, computed as SHA-256 of the sorted JSON path-to-content-hash mapping. Before publication reconciliation, all 83 current hashes matched that manifest. This is a tree fingerprint, not a commit SHA. Subsequent publication changes affect documentation, metadata and CI only; product source, tests, schemas and canonical fixtures remain unchanged.

The initial independent audit was BLOCKED by D1 (P2, AC-06): pre-startup closed standard descriptors became None, producing incorrect diagnostics or escaping AttributeError. Hardening added four product lines checking unavailable stdout/stderr and three permanent regression methods. The failed audit and red-before-fix evidence remain archived locally; their history is preserved in Factory metadata and HARDENING-EVIDENCE.md.

The independent re-audit directly executed all three original reproductions through both installed entrypoints: missing input with stderr closed; version with stdout closed; version with both closed. Each returned 3, emitted OUTPUT_IO when stderr was usable, and produced no traceback or stdout diagnostic fallback. Fresh wheel and sdist-derived installations confirmed the same outcomes.

| Independent verification | Executed result |
|---|---|
| Full unittest discovery | Exit 0; 41 tests; no skips |
| Canonical fixture gate | Exit 0; 17 pairs, 34 console/module comparisons |
| Isolated package gate | Exit 0; wheel/sdist builds and offline installations, 68 golden comparisons |
| Fresh stream/process harness | Exit 0; 242 descriptor/EPIPE/help/version/validation/error/interrupt cases |
| Hand-derived snapshot review | Exit 0; 96 installation/entrypoint/locale comparisons plus 12 original-descriptor artifact checks |
| Independent filesystem/security guard | Exit 0; 32 stream-boundary cases, seven detected calibration controls |
| Independent archive review | Exit 0; product/assets matched source, two additional offline installations |

Real descriptors were closed before interpreter startup; pipe readers were removed before launch. No DEVNULL substitution or timing-dependent sleep was used. Expected outputs were hand-authored without importing product checker logic. All 37 canonical fixture/manifest/schema files matched the original build and hardening records. Original workspace preservation covered 1,970 files by content, mode and modification time. Audit execution occurred exclusively in external temporary copies.

Review confirmed frozen snapshot membership, separate ledger replay, ordered findings, cursor continuity/history and final-page completeness. No new application-controlled writes, runtime dependencies, credential access, nondeterminism or blocking diagnostic defects were found. AC-01 through AC-08 passed locally. Python-level instrumentation and scoped filesystem observation do not claim universal native/OS zero writes; only interpreter-managed import bytecode is exempt under AC-05.

N1 remains P3/nonblocking: eight relative documentation links in the wheel README lack bundled targets. Required wheel assets and source/sdist links are present. Keep this as a follow-up before any future PyPI publication; the wheel documentation is not fully self-contained.

The audit-phase Factory validator initially exited 2 solely because read-only metadata still recorded LOCAL_READY and the prior blocked audit. Publication authorization permits reconciliation to AUDIT_PASS. Publication preparation reruns the audit validator and local gates; hosted success must refer to the actual final pushed SHA. No product audit result is inferred from metadata alone.
