# Fixtures and independent expected results

`fixtures/manifest.json` is the inventory: each case names the input, hand-authored expected stdout file, exact process exit, stderr (empty) and reason. Paths resolve relative to fixtures/. There are **17 cases**: 3 passes, 10 domain failures and 4 invalid inputs. Each `.expected.json` is canonical byte output including LF. All are synthetic, deterministic and platform independent; no RNG or clock. Invalid duplicate-key input is intentionally invalid and must not be repaired by a formatter.

| Fixture | Expected outcome | AC |
|---|---|---|
| pass-snapshot | 0 pass; snapshot a,b,c returned once; delete b and insert x recorded between pages | 01,05,07 |
| pass-empty | 0 pass; empty terminal traversal | 01,07 |
| pass-empty-continuation | 0 pass; empty first page advances token then returns a | 01,03,07 |
| fail-delete-gap | 1 MISSING_ID b at /snapshot/1 | 01,07 |
| fail-insert-shift | 1 DUPLICATE_ID b at /events/2/ids/0 | 02,07 |
| fail-order | 1 OUT_OF_ORDER a at /events/0/ids/1 | 02,07 |
| fail-unexpected | 1 UNEXPECTED_ID x at /events/1/ids/1 | 01,02,07 |
| fail-chain | 1 CHAIN_MISMATCH at /events/1/request_cursor | 03,07 |
| fail-cycle | 1 CURSOR_CYCLE then INCOMPLETE at /events/1/next_cursor | 03,07 |
| fail-incomplete | 1 INCOMPLETE, no MISSING_ID b | 03,07 |
| fail-overflow | 1 PAGE_OVERFLOW at /events/0/ids | 02,07 |
| fail-after-terminal | 1 AFTER_TERMINAL at /events/1 | 03,07 |
| fail-multiple | 1 PAGE_OVERFLOW, OUT_OF_ORDER a, DUPLICATE_ID a, UNEXPECTED_ID x, in that order | 02,05,07 |
| invalid-ledger | 2 LEDGER at /events/0/id; deleting absent z | 04,07 |
| invalid-version | 2 SCHEMA at /schema_version | 04,07 |
| invalid-no-page | 2 SCHEMA at /events | 04,07 |
| invalid-duplicate-key | 2 JSON at root; duplicate schema_version key | 04,07 |

Post-build execution from repository root: `.venv/bin/cursorrace check fixtures/NAME.json`; compare bytes with `fixtures/NAME.expected.json`. Automated harness asserts intentional nonzero exits rather than treating them as shell infrastructure failures. `tests.fixture_gate` must invoke an installed executable, not the pure checker. Package gate must rerun this inventory outside checkout.

These static fixtures cover the demo and high-value regressions; generated boundary fixtures in docs/06-test-plan.md are additionally mandatory. A fixture is a specified expectation, not executed proof that the absent product passes. Mutation names describe plausible captured schedules and do not prove causal attribution.
