# CursorRace repository instructions

## Authority and scope

User instructions > GOAL.md > docs/04-acceptance.md > docs/03-contracts.md and schemas > docs/02-architecture.md > docs/09-decisions.md > factory templates. A contradiction within binding contracts is a blocker; document the smallest resolution. Never silently weaken an AC. JSON Schemas cover shape; prose adds cross-field rules and overrides no conflicting schema rule.

Current authorization includes publishing the public GitHub repository `ardaongl/cursorrace` on `main`, local commits, initial and narrowly scoped corrective pushes, description/topics configuration, hosted CI inspection and release evidence. The user granted this scope after independent re-audit PASS. PyPI publication, GitHub Releases, deployments, force-pushes and overwriting existing repositories remain unauthorized. Preserve the AC-05 application-level boundary and approved snapshot semantics. No delegation is required. Source changes require affected checks and a separate review pass using fresh hypotheses.

## Toolchain

CPython **3.14.8**, pip **26.2.1**, stdlib unittest, setuptools **80.9.0** as the sole isolated build requirement. No product runtime dependencies, no lockfile for an empty runtime dependency set. Build requirement pinned in pyproject.toml. Pin development bootstrap pip explicitly; no pytest, coverage or schema library required for product execution. CI baseline is ubuntu-24.04 with CPython 3.14.8. macOS is also a local verification target; Windows is outside v1 support.

Spec inspection found `python3` is 3.9.6; `python3.14` is 3.14.8 and its pip is 26.2.1. Discover paths afresh in preflight; do not hardcode this macOS path into product or CI. Before build: `python3.14 -m venv .venv`, `.venv/bin/python -m pip install pip==26.2.1`, `.venv/bin/python -m pip install --no-deps .`. Packaging dependency acquisition may need network; running/checking traces must not.

## Verification and maintenance

Required gate commands: `.venv/bin/python -m unittest discover -s tests -v`, `.venv/bin/python -m tests.fixture_gate`, `.venv/bin/python -m tests.package_gate`. These modules are implemented. Package gate details live in docs/06-test-plan.md. Capture commands, exit codes, interpreter/OS, tree fingerprint and limitations in `.local-verification/`; reference them in docs/IMPLEMENTATION-STATUS.md. All ACs were NOT_RUN during specification; executed results are recorded separately. Expected negative fixture exits are successes only when an independent harness asserts them.

Keep implementation small, parser strict and findings stable. Test the installed distribution and closed stdout. Do not read environment secrets, log raw input errors or add telemetry. A source/spec change invalidates affected earlier verification. Use ADRs for actual decisions only. Follow docs/08-release.md; remote actions are limited to the authorized repository and operations above.

## Phase report

Report PHASE, STATUS, FILES_CHANGED, actual VERIFICATION with exits, UNRESOLVED_RISKS, USER_AUTHORIZATION_REQUIRED and NEXT_ACTION. Distinguish planned tests from executed evidence and LOCAL_READY from RELEASE_READY.
