# Implementation status — CursorRace

Current state: **AUDIT_PASS; initial publication authorized; hosted CI pending**. Target: public `ardaongl/cursorrace`, branch `main`. The user authorized repository creation, commits, initial/corrective pushes, description/topics, hosted CI inspection, narrow CI fixes and evidence recording. PyPI, GitHub Releases, deployment and force-push remain excluded.

| Gate | State | Evidence |
|---|---|---|
| SPEC / M0 | PASS | SPEC-VERIFICATION.md; BUILD-EVIDENCE.md |
| M1–M4 | COMPLETE | BUILD-EVIDENCE.md; ignored original build records preserved |
| AC-01–AC-08 | PASS locally | HARDENING-EVIDENCE.md; AUDIT-EVIDENCE.md; fresh publication gates |
| LOCAL_READY | YES | 41 unit tests, 17 fixture pairs, isolated package gate |
| Initial independent audit | BLOCKED historically | D1/P2/AC-06; preserved in audit_history and ignored prior report |
| Hardening | PASS locally | Four stream-availability lines, permanent red/green regressions |
| Independent re-audit | PASS | AUDIT-EVIDENCE.md; raw report/scripts archived locally |
| Initial publication | AUTHORIZED | Public ardaongl/cursorrace on main; exact scope in Factory metadata |
| Hosted CI | PENDING_HOSTED_CI | Must inspect actual run and matching final commit SHA |
| RELEASE_READY | NO pending hosted verification | Final SHA/run evidence belongs in ignored final attestation |

The publication candidate may include metadata, documentation and CI verification additions beyond the audited 83-file set. Product source, tests, schemas and fixtures remain unchanged. Fresh candidate manifests and command logs are retained under ignored `.local-verification/publish/`. Required gates are unit discovery, fixture gate, package gate and `python scripts/factory_validate.py --project-dir . --phase audit`; the portable metadata validator is included for hosted execution.

Known follow-up N1/P3: eight wheel README relative links require source documentation. This is nonblocking for initial GitHub publication and must be reviewed before future PyPI publication. No packaging redesign is included.

Final hosted success and the final intended commit are recorded in ignored `.local-verification/RELEASE-FINAL.json` after verification, avoiding a commit that purports to contain its own SHA. Tracked pending status describes the pre-push snapshot; the final attestation must independently verify its SHA and the public tree. No release is inferred from this ledger alone.

NEXT_ACTION: run publication gates, commit only approved files, create/push the authorized destination, and verify actual hosted CI. Preserve failed-run evidence and correct only narrowly scoped CI issues if needed.
