# Product brief and competing approaches

Research date: 2026-10-19. Sources below are primary project/vendor documentation, inspected for positioning; no competitor installations or performance tests were performed.

## Problem and workflow

Backend engineers maintaining a snapshot export endpoint need more than individual response assertions: every original ID must appear once, in the original order, even when integration tests insert/delete records between page reads. A skipped row can silently corrupt an export despite every response being valid JSON with HTTP 200. The engineer already controls seeding, the independent snapshot query and write scheduling. CursorRace turns a captured traversal into a reproducible CI verdict without coupling to an API framework.

## Research and substitutes

| Substitute | Documented capability | Where CursorRace differs |
|---|---|---|
| [Schemathesis stateful testing](https://schemathesis.readthedocs.io/en/latest/guides/stateful-testing/) | Chains API operations using discovered or explicit relationships; customization supports setup and request hooks. | CursorRace consumes a supplied trace and fixed ordered oracle; it does not discover/generate HTTP workflows. |
| [Dredd](https://dredd.io/en/latest/) | Validates API description examples against a running implementation; hooks support setup/customization. | CursorRace focuses on whole-traversal membership and continuity rather than description/example conformance. |
| [Postman collection workflows](https://learning.postman.com/docs/tests-and-scripts/running-collections/building-workflows/) | Scripts select next requests and implement loops. | A team can script the same checks there; CursorRace supplies a small versioned trace contract and standardized verdict offline. |
| [PactumJS](https://pactumjs.github.io/guides/api-testing.html) | Request construction and response assertions form programmable API tests. | A capable alternative with custom oracle logic; CursorRace packages that narrow oracle independently of transport and JS runner. |
| [Behind the Search pagination tester](https://behindthesearch.in/tools/pagination-rel-next-prev-testing) | Audits HTML rel-next/prev chains, canonical/noindex signals and circular links. | It addresses web crawl structure; this MVP addresses ordered backend record membership against a snapshot. |

The [Relay connection specification](https://relay.dev/graphql/connections.htm) supplies useful background on opaque cursors and consistent edge ordering. CursorRace is not a Relay compliance suite and does not infer snapshot isolation from cursor pagination.

**Differentiation is a design inference from the reviewed capabilities, not a claim that no equivalent tool exists.** No exhaustive market/name/package search or customer validation has been done. Existing runners can implement equivalent assertions. The proposed original contribution is the combination of a transport-neutral mutation ledger, frozen ordered-ID oracle, deterministic finding locations and explicit incomplete-traversal verdict in one bounded artifact.

## Selected micro promise

One file in, one stable JSON report out. The <60-second post-build demo audits pass-snapshot.json (exit 0), then fail-delete-gap.json (exit 1, MISSING_ID b). Deleting an unseen original ID does not excuse omission under the declared snapshot policy. Inserting a new ID does not add it to the expected traversal. The tool validates the write ledger to reject internally impossible captures, but cannot authenticate it.

## Exclusions and cost

No live HTTP, adapters, randomized scheduling, threads, load/performance benchmarking, offset/keyset implementation, database, payload comparison, descending/composite-key inference, GraphQL/OpenAPI discovery, JUnit, text reporter, stdin, batch inputs or report files. Ordered IDs encode all tie-break decisions explicitly. No repair or cursor decoding.

No service cost or paid API. Trace content stays local; IDs may be sensitive, and opaque tokens must be scrubbed before sharing. Report tokens are never echoed. The project will use MIT licensing at build; no third-party code copied. Name/package availability and legal clearance remain outside this spec and must be checked before publication. Research establishes a plausible engineering pain point, not validated demand.

## Selection judgment

Differentiation 3/5 ×5 =15; utility 4/5 ×4 =16; technical signal 4/5 ×4 =16; micro feasibility 5/5 ×4 =20; demo 4/5 ×3 =12: **79/100**. This is an internal judgment. Biggest tradeoff: requires a trustworthy independent snapshot and normalized capture; reducing integration work with adapters is intentionally deferred.
