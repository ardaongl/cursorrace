# Goal — CursorRace

## Authorized phase and outcome

The local build objective reached LOCAL_READY, hardening passed and the separate independent re-audit passed. Current authorization permits publishing `ardaongl/cursorrace` publicly on `main`, commits/pushes, repository description/topics, hosted CI inspection, narrow CI corrections and final evidence. PyPI, GitHub Releases, deployment, force-push and repository overwrite remain excluded. Final RELEASE_READY requires successful hosted CI matching the final intended SHA.

Deliver a dependency-free Python CLI that checks one bounded offline JSON trace against the snapshot-at-start contract. A pass requires exact once-only ordered snapshot membership, valid cursor continuity and a terminal final page. Writes explain the trace context; they never alter the frozen membership oracle.

## Verification surface

All AC-01 through AC-08 in docs/04-acceptance.md must have executed, independent evidence before LOCAL_READY. Required later commands are `.venv/bin/python -m unittest discover -s tests -v`, `.venv/bin/python -m tests.fixture_gate` and `.venv/bin/python -m tests.package_gate`. Each exits 0 only when its assertions pass, including expected product exits 1 and 2. Check real installed CLI behavior outside the source tree.

## Constraints and stop conditions

Follow docs/02-architecture.md and docs/03-contracts.md. No network, dynamic plugins, live adapters, persistent state, database, UI, daemon or runtime third-party dependencies. Only snapshot membership/order is assessed; no guarantee of payload immutability or real concurrency. Preserve strict parser/limits and output/error behavior.

Implement M0–M4 in docs/07-build-plan.md only after authorization. Stop and report exact evidence if the pinned toolchain cannot be provisioned, binding documents conflict, the independent oracle disagrees with a fixture, a required check cannot run, or a dependency would change the offline boundary. Routine internal choices do not require scope expansion. Do not weaken acceptance to get green results.

## Release boundary

LOCAL_READY means all local AC evidence exists and hosted CI is pending. A separate adversarial read-only audit must challenge fresh cases on the final candidate. Changes invalidate affected evidence and audit. Remote operations require exact owner/name/visibility/action authorization. Package publication, GitHub release and deployments require separate authorization. RELEASE_READY requires hosted success on the final SHA; resolve attestation outside the commit whose SHA it records.
