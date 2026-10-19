# CursorRace

A small, offline auditor for **snapshot-at-start pagination traces under recorded writes**. Feed it ordered snapshot IDs, a mutation ledger and captured pages. It reports duplicate, missing and unexpected IDs, ordering defects, broken cursor chains and incomplete traversal as stable JSON.

Profile: micro. Category: Backend Engineering / Developer Tooling. Python 3.14.8; no runtime dependencies.

## Install and run

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install pip==26.2.1
.venv/bin/python -m pip install --no-deps .
.venv/bin/cursorrace check fixtures/pass-snapshot.json
# exit 0, status pass
.venv/bin/cursorrace check fixtures/fail-delete-gap.json
# exit 1, MISSING_ID for b
```

The second trace deletes b after page one and omits it from later pages. It fails because its declared contract freezes membership at the start. Live keyset pagination may legitimately omit that row; CursorRace v1 does not assess that policy.

Your integration test must capture the starting snapshot independently, schedule writes between reads and normalize responses into the trace format. CursorRace reads that file; it neither contacts the API nor executes supplied code. It verifies trace consistency, not capture authenticity, timing, isolation level or every possible interleaving.

The application must leave inputs and user data unchanged and create no application logs, temporary files, caches or persistent state, for passing and failing audits. Ordinary Python imports may create interpreter-managed `__pycache__`/`.pyc` artifacts; these alone are excluded from the application-level no-write guarantee. Optionally suppress bytecode generation before interpreter startup with either command:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/cursorrace check fixtures/pass-snapshot.json
.venv/bin/python -B -m cursorrace check fixtures/pass-snapshot.json
```

These procedures do not remove existing bytecode caches or establish a universal OS-level zero-write guarantee. The [execution boundary](docs/03-contracts.md#privacy-compatibility-and-trust) defines the application guarantee and required future verification.

See [product and research](docs/01-product-brief.md), [architecture](docs/02-architecture.md), [normative contract](docs/03-contracts.md), [acceptance](docs/04-acceptance.md), [fixtures](docs/05-fixtures.md), [build plan](docs/07-build-plan.md) and [goal](GOAL.md).

No services, accounts, credentials or paid APIs are required. Package name availability and trademark clearance have not been checked. GitHub publication is authorized for ardaongl/cursorrace. PyPI publication, GitHub Releases and deployment require separate authorization.

## Verify locally

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m tests.fixture_gate
.venv/bin/python -m tests.package_gate
```

The package gate permits network only to bootstrap the pinned build backend, then builds and installs wheel/sdist artifacts in fresh environments and runs the installed CLI outside the checkout. Expected fixture exits 1 and 2 are asserted as intentional outcomes. No line-coverage percentage is mandated; the test plan defines behavioral partitions. The prepared workflow is not evidence of hosted CI success. Release still requires a separate adversarial audit and explicit publication authorization.

Known packaging limitation: the wheel bundles this README, but eight relative documentation links require the source repository. Wheel documentation is not fully self-contained; review these links before any future PyPI publication.
