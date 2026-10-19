# Normative external contracts — v1

## CLI

`cursorrace check PATH` is the only analysis form; `python -m cursorrace` is equivalent to the console script. Exactly one positional UTF-8 filename; `--` may separate check from a filename beginning with `-`. PATH `-` is a literal filename, not stdin. Relative paths resolve against CWD; symlinks to regular files are followed. Reject directories, devices, sockets and FIFOs without reading (exit 3). No input-specific imports, subprocesses, environment expansion or URLs. The CLI obeys the application-level no-write boundary below.

`cursorrace --help`, `cursorrace check --help`: exit 0, stdout UTF-8 usage, stderr empty. Exact help prose is not stable but must describe syntax and exits. `cursorrace --version`: stdout `cursorrace 0.1.0\n`, exit 0. Invalid arguments/subcommands/unknown or repeated options: exit 2 with error envelope ARGUMENT, no usage prose or traceback. Help/version as sole global option; check help as sole check option. Option abbreviation forbidden. No color or TTY-dependent behavior.

## Input shape

`schemas/trace-v1.schema.json` (JSON Schema 2020-12) defines exact required keys/types/cardinality. Reject unknown keys at every object level. All integer fields are JSON integers without decimal/exponent syntax, and never booleans. Strings may use JSON escapes; decoded equality is exact and case sensitive. IDs match `[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}`; cursors are null or 1–256 printable ASCII non-space characters (`[!-~]`). No Unicode normalization. Cursors are opaque; no base64 decoding, comparison ordering or URL following.

Top-level keys: `schema_version` exactly integer 1; `policy` exactly `snapshot`; `snapshot` ordered unique ID array, 0–10,000 members; `page_size` integer 1–1,000; `events` ordered array, 1–10,000 members. At least one event must be a page. This input order is the entire timeline; no timestamps.

A page event has exactly `type: "page"`, `request_cursor`, `ids` (0–1,000 IDs), and `next_cursor`. The array may repeat IDs; repeats are domain findings. More than page_size items is a domain finding, not invalid shape. Insert/delete events have exactly `type: "insert" | "delete"` and `id`. At most 100,000 returned ID occurrences over all pages, independently of the byte limit.

File maximum is **1,048,576 bytes inclusive**, measured before decode. Reject UTF-8 BOM, malformed UTF-8, invalid JSON, trailing content, duplicate object keys (even if escaped spellings decode equal), NaN/Infinity, unpaired surrogate strings and lexical floats anywhere. Maximum JSON container nesting is 16 inclusive: root object depth 1, child array depth 2, object inside that array depth 3. Brackets inside strings do not count. Enforce nesting before decoder recursion can escape as an internal error.

## Validation order and ledger

Argument validation → file type/open/read → byte size → UTF-8/BOM → lexical/JSON/nesting → shape/cross-field counts → ledger replay → analysis. For simultaneous invalidity, return the earliest category in that sequence. Within parsing/shape/ledger category only one error is returned; the particular pointer among multiple errors is unspecified but must identify an actual offending value (root allowed for parser errors). Invalid input never yields partial domain findings.

Start `live` and `ever_seen` sets at snapshot IDs. Insert requires ID never in ever_seen; then add to both. Delete requires ID in live; then remove from live, never from ever_seen. No reinsertion, updates or identity reuse. These rules reject impossible or ambiguous ledgers, not page results. Mutations may precede the first page and follow a terminal page; the latter will be a domain finding. Snapshot stays frozen through all writes. Pages never mutate live and may legitimately return a previously deleted snapshot ID. IDs introduced by insert are still unexpected in snapshot pages. Unknown IDs in page results are also domain findings, not invalid ledger.

## Domain findings and traversal

All event indexes and item indexes are zero-based. `pointer` is an RFC 6901 JSON Pointer into the input. A finding always has exactly `code`, `pointer`, `id`; `id` is a string only for item/missing findings and null for all other findings. Do not echo cursors. All findings accumulate; no suppression except the specified missing rule.

Process events in order. Once any page has next_cursor null, every subsequent event produces AFTER_TERMINAL at `/events/i` (including a mutation). Continue all normal checks on those events. Mutations otherwise produce no findings.

For each page, emit in this exact order:

1. AFTER_TERMINAL if applicable (the check above).
2. CHAIN_MISMATCH at `/events/i/request_cursor` if first page request is non-null, or later request differs from the immediately previous page's next cursor. Mutations do not reset chain state.
3. CURSOR_CYCLE at `/events/i/next_cursor` if non-null next cursor equals any non-null request cursor encountered up to and including this page. Request cursors are recorded even if chain mismatch. A terminal null is never a cycle. A repeated next token that was never requested is handled only when another rule detects it; no token decoding.
4. PAGE_OVERFLOW at `/events/i/ids` if item count exceeds page_size.
5. For each item in array order: DUPLICATE_ID if seen earlier anywhere, then UNEXPECTED_ID if absent from snapshot, then OUT_OF_ORDER if this is a known snapshot ID whose rank is strictly less than the immediately previous *known* snapshot ID rank across all pages. Item findings point to `/events/i/ids/j` and carry that ID. Equal adjacent known ranks produce duplication only; unexpected IDs do not update rank. Record every ID seen and update last known rank even for duplicates.

After all events: if final page next_cursor is non-null emit INCOMPLETE at that page's `/next_cursor`, id null. Otherwise emit MISSING_ID for each absent snapshot member in snapshot order, pointing to `/snapshot/j` with that ID. Never emit MISSING_ID on an incomplete trace. A prior terminal followed by later pages still gets AFTER_TERMINAL; completeness for missing is determined only by the final page. No required fullness of nonterminal pages: short/empty continuation pages are legal when chain tokens progress. Empty snapshot passes with one empty null/null page. Repeated empty pages can fail continuity/cycle/termination rules. No separate timeout or inferred max-pages finding: bounded input prevents infinite checker execution.

Pass iff findings is empty; fail otherwise. This judges the supplied snapshot contract, not live-page policies. The ledger does not establish that a particular mutation caused a finding.

## JSON report and errors

`schemas/report-v1.schema.json` specifies two envelope variants. Successful analysis always emits exactly:

```
{"schema_version":1,"status":"pass","stats":{"snapshot_count":0,"page_count":1,"mutation_count":0,"observed_count":0},"findings":[]}
```

For domain failure change status to fail and include all findings. Stats count snapshot IDs, page events, insert+delete events, and returned ID occurrences (including repeats/unexpected), respectively. No durations, input filename, timestamps, hashes, cursors or machine-dependent fields. Every emitted JSON report uses sorted keys recursively, compact separators, ensure_ascii=true and one LF; sample layout above is explanatory, byte-canonical order comes from sorting. Identical bytes yield byte-identical analysis reports across supported OSes. Error envelope has exactly `schema_version:1`, `status:"error"`, `error:{"code":CODE,"pointer":STRING_OR_NULL}`; no stats/findings/message. No raw values, paths or platform exception messages.

| Exit | Meaning | stdout | stderr |
|---|---|---|---|
| 0 | pass, help or version | analysis report or requested help/version | empty |
| 1 | valid trace with findings | fail report | empty |
| 2 | invalid arguments/input/ledger | error JSON | empty |
| 3 | IO/internal failure | empty if analysis not already written | fixed ASCII `cursorrace: CODE\n` |
| 130 | caught KeyboardInterrupt | empty if not already written | `cursorrace: INTERRUPTED\n` |

Exit-2 codes: ARGUMENT (pointer null), LIMIT (root pointer empty string), ENCODING (root), JSON (root), SCHEMA (offending pointer), LEDGER (offending event `/id`). Version mismatch is SCHEMA at `/schema_version`; missing page or aggregate-ID count violation uses `/events`, with count violation code LIMIT. Shape limits (array/string lengths etc.) use SCHEMA, while file/depth/aggregate occurrences limits use LIMIT. Nested duplicate key and nonfinite/float lexemes are JSON errors. Depth precedence over other JSON defects is unspecified within lexical/JSON/nesting validation.

Exit-3 stderr codes: INPUT_IO (file/read/type failures), OUTPUT_IO (write/flush/broken pipe), INTERNAL (unexpected exception, no traceback). On output failure a partial stdout report may exist; exit 3 wins over 0/1/2. Best-effort stderr only if usable; if stderr itself fails still exit 3 without traceback. Handle stdout flush before deciding success, including buffered EPIPE; never attempt to append a second report. Catchable interrupts produce exit 130; OS signals other than KeyboardInterrupt retain OS semantics and need not emit JSON. Memory exhaustion and hard process kill cannot guarantee reports.

## Privacy, compatibility and trust

No execution-time network or telemetry. During auditing CursorRace must not create, modify, delete or rename user data files, input traces, snapshots or application-managed artifacts. It must not intentionally create application logs, temporary files, caches or persistent state. This application-level no-write boundary applies to successful and unsuccessful audit outcomes; input files must remain unchanged. Writing the contracted report/diagnostic to stdout/stderr remains permitted; caller-controlled stream redirection is outside the application's file-management boundary.

Ordinary CLI and module execution may generate CPython interpreter-managed `__pycache__` directories and `.pyc` files during imports. Only these interpreter-managed bytecode artifacts are excluded from the application-level no-write guarantee. This exception does not authorize application-controlled writes, even to paths named `__pycache__` or ending in `.pyc`.

For optional stricter execution, set `PYTHONDONTWRITEBYTECODE=1` in the child environment before launching the console script, or invoke the module with the interpreter's `-B` option: `python -B -m cursorrace check PATH`. These suppress bytecode generation from interpreter startup; they do not remove existing caches. Changing `sys.dont_write_bytecode` after package initialization cannot prevent earlier import/startup writes. Neither the ordinary nor the stricter procedure claims universal OS-level zero writes: future tests must state the isolated filesystem/process boundary actually observed and distinguish mutation attempts from visible differences. See [AC-05 verification](06-test-plan.md#application-level-no-write-verification-ac-05).

Input may be untrusted; no eval, pickle, YAML or shell. Reports expose snapshot/observed IDs by design; use synthetic IDs for shared fixtures. Reports never include cursor tokens. Ledger and snapshot are caller assertions; do not describe passing as proof of isolation or exhaustive race safety. v1 accepts only schema_version 1; new policies/fields need explicit future version/contract work. Finding codes, locations, order and envelope are stable for v1. Internal library imports and help prose are not public interfaces.
