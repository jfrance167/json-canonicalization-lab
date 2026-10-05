# Proposed plan: JSON canonicalization lab

Tier 3 educational portfolio lab. Research/planning authorized October 5, 2026,
01:45 coordinator checkpoint under Jake's directly verified successor mandate.
Stages 1–5 APPROVED at October 5, 02:01 coordinator checkpoint. Same chat/sole writer; separate directory.
No new chat, scheduler, remote publication, merge or live system work.

## Problem and success

Explain why two byte-distinct JSON documents can express equivalent values under
a declared representation profile, while a digest over either representation
does not establish origin, truth or intended consumer meaning. The prior Merkle
lab hashes exact leaf bytes; this lab makes its byte-input choice explicit.

Success: a bounded offline comparator reports exact original-byte equality and
canonical-byte equality separately, with fixed SHA-256 inputs and honest unsupported
outcomes. It handles the difficult UTF-16 ordering, duplicate-name and Unicode
boundaries with published independent known answers. It does not silently round,
normalize, discard or coerce unsupported data.

Assumptions: synthetic local UTF-8 documents; Python 3.13 standard library;
`jcs-integer-subset-v1` is the only profile; no full floating-point JCS. Restriction
is an application teaching choice, not a claim the broader RFC forbids fractions,
exponents, negative zero or every integer outside the safe interoperability range.

## Frozen proposed contract

CLI: `python -m canonical_lab compare LEFT.json RIGHT.json [--output NEW.json]`.
JSON report only, escaped ASCII, no emitted raw canonical-document file, browser,
HTML or text interpretation. Inputs are ordinary JSON documents, any supported
top-level value; arbitrary payload property names are data, not application schema
fields. There is no input envelope with ignored/unknown settings. Unknown CLI
options/profile switches fail. Same-file left/right comparison is valid.

Runtime API: `compare(left: bytes, right: bytes)` and `canonicalize(data: bytes)`
accept exact built-in bytes, with all CLI-equivalent limits. No arbitrary objects,
custom serializers, iterators, tuple coercion, `toJSON` or object deserialization.
Parsed structures are built-in containers/literals, with private unsupported-number
markers. Nothing caller-controlled is executed. Canonical bytes are available only
for a fully validated supported document; unsupported cannot leak partial output.

Admission rules:

- Each regular input file ≤16 KiB; strict UTF-8, no BOM, exactly one JSON document.
  No UTF-16/32 sniffing, replacement decoding, comments, trailing text or NaN/Infinity.
- Scan quote/escape-aware container depth before decoding; maximum eight nested
  containers. Enforce decoded shape: ≤256 total nodes per document, counting every
  value/container and every object key; ≤64 elements/members in each container.
- Each decoded string/key ≤1024 Unicode scalar characters, aggregate strings/keys
  ≤4096 scalar characters. Reject lone/reversed surrogates and noncharacters
  U+FDD0–FDEF and every plane's U+FFFE/U+FFFF. Valid escaped surrogate pairs decode
  to their scalar and match literal UTF-8. Never normalize Unicode or use locale.
- Duplicate decoded names fail at all depths before constructing a lossy dict,
  including `"a"` versus `"\u0061"`. Canonically equivalent but distinct Unicode
  strings remain distinct names. Do not NFC-collapse them.
- Numeric lexemes ≤64 ASCII characters before conversion. JSON grammar must still
  validate completely. Only integer-form tokens from −9007199254740991 through
  9007199254740991 are supported, with `-0` deliberately unsupported. Safe ints
  become exact ints; booleans remain distinct literals.
- Fractions/exponents (including mathematically integral `1.0`/`1e0`), `-0` and
  out-of-range integer values become bounded unsupported markers, never floats,
  rounded ints or strings. Fully validate the rest of the document before returning
  unsupported. Syntax, Unicode, duplicate or resource violations take precedence
  over unsupported markers; numeric lexemes >64 are resource errors.

Canonical representation for supported values:

- Null/true/false and exact integers use fixed JSON spellings with no whitespace.
- String escape rules follow RFC 8785 §3.2.2.2: quote/backslash escaping, short
  escapes for five designated controls, lowercase `\u00xx` for the other C0
  controls, other accepted characters unchanged and then UTF-8 encoded.
- Object names sort recursively by unsigned UTF-16 code-unit sequences, conveniently
  strict UTF-16BE byte keys without BOM; no Python code-point or locale sorting.
  Preserve array element order; sort objects inside arrays. No slash escaping,
  last-key-wins or Unicode normalization.
- Canonical bytes ≤32 KiB per document. Validate/render both completely before
  report creation. A full RFC numeric example outside the subset gets unsupported,
  not fabricated canonical output. No universal JCS-conformance claim.

Report version 1 exact fields: `report_version`, `profile`, `hash_algorithm`,
`status`, `raw_bytes_equal`, `canonical_relation`, `left`, `right`,
`origin_authenticated`, `limitation`. Profile fixed above, hash `sha256`,
origin_authenticated always false. Status is exactly `supported-equal`,
`supported-different` or `unsupported`. Each side contains `raw_length`, `raw_sha256`,
`canonical_length`, `canonical_hex`, `canonical_sha256`, `unsupported_reasons`.
Canonical fields are null for an unsupported document, reasons from fixed codes
`fraction-or-exponent`, `unsafe-integer`, `negative-zero` (deduplicated, fixed order).
Other side may retain its valid canonical representation, but relation is unsupported
if either side is unsupported. Supported relation `equal`/`different` comes from
exact canonical bytes, not Python's loose value equality or hash comparison alone.
Raw equality comes from exact input bytes; hashes are diagnostic commitments.

SHA-256 inputs are explicitly the original bytes or the canonical bytes, without
hidden BOM/newline/profile prefix. Profile is reported separately; hash alone does
not bind an application profile, protocol context, sender or meaning. Display exact
canonical bytes as hex so control/Unicode data stays inert. No raw leaves/documents
echoed in error messages. Final report ≤256 KiB; stderr fixed/escaped errors.

Exits: 0 supported/equal; 1 supported/different; 2 invalid input/resource/I/O or
output failure; 3 valid bounded JSON outside the declared numeric subset. An
unsupported report may establish raw equality, but establishes no canonical equality.
All-or-nothing validation; invalid input emits no success/comparison report.

Filesystem: regular bounded reads checked before/after open, bounded read catches
post-stat growth. Exclusive output creation; refuse existing files and input aliases
(including symlinks/hardlinks). Preserve originals. Final bytes/size known before
creating output. Short writes/errors are failures; no atomic stdout guarantee, and
disk failure can leave a partial newly created file. Hostile concurrent filesystem
replacement is outside the local educational threat model.

## Architecture and alternatives

`bounded bytes → strict parser/unsupported markers → shape/Unicode validation →`
`UTF-16 ordered restricted serializer → exact byte comparison/SHA-256 → bounded report`.

Modules `canonical_lab/contract.py`, `canonical.py`, `report.py`, `__main__.py`;
tests/ independently sourced vectors; samples/ inert demonstrations; scripts/
fixed demo regeneration. No runtime dependency. Prepared dev SAST uses existing
reviewed Bandit environment, no new packages needed.

Recommendation: original bounded stdlib wrapper/subset plus attributed Apache
published fixture bytes. Full rfc8785 adoption has reviewed no-runtime-dependency
source and richer numeric coverage, but still needs strict raw-input admission and
artifact/advisory review; unnecessary for the approved research objective.
Forking reference runtimes adds maintenance/PSF attribution without solving admission.
Sorted Python JSON fails the general ordering/numeric contract; no casual substitution.
Length-prefixed raw records solve boundary ambiguity (`ab`+`c` vs `a`+`bc`), preserve
representation differences and do not solve single-document equivalence. Document
this alternative only; no framing engine or transport in initial scope.

## Threat model and limits

Adversary controls synthetic document bytes, escaped keys/Unicode, numeric tokens,
nesting and CLI input paths. Assets: original evidence, deterministic declared
representation, bounded execution/output and honest claims. Controls: strict
decoding/duplicate checks, pre-parse depth/byte/lexeme bounds, post-parse aggregate
limits, no float conversion, no executable interpretation, exact comparison,
exclusive output and escaped diagnostics. Canonical equivalence deliberately erases
formatting/key-order/escape spelling; raw evidence remains distinct and unchanged.

Primary risk is a misleading verdict through lossy parsing, loose bool/int equality,
wrong sort order or normalization; independently fixed golden bytes and negative
cases mitigate this. Digest equality under hash assumptions never authenticates
origin, timestamps, schema intent or downstream business semantics. No application
schema validation, real documents, signatures/keys/credentials, custom crypto,
network verifier, remote service or bypass of TLS/TUF artifact gates. No claim of
production suitability, global JSON equality or complete RFC conformance.

## Ordered implementation tasks and definitions of done

Authoritative acceptance list: [todo.md](todo.md). All five tasks approved;
a checkpoint record does not create a second approval gate within an
approved scope. Concepts explained briefly before substantial stages; optional
learning check after completion does not block progress.

1. Provenance/admission (medium): retain exact published originals/license/manifest
   before test adaptation; implement bounded bytes parser and unsupported markers.
   Files: contract, admission tests, manifest, vector originals/NOTICE as one data
   unit. Done: length/Git blob/SHA256 provenance and strict/unsupported distinction
   tests pass. Stop if independently sourced bytes/license cannot be verified.
2. Supported canonical statements (medium, depends 1): exact integer/literal/string
   serialization, UTF-16 ordering, exact byte comparator and digest input labels.
   Files: canonical, report, core/golden tests. Done: three published pairs, RFC
   UTF-16 order, escaping and independent hand-fixed controls pass; no roundtrip-only
   oracle. Checkpoint: complete in-memory supported/unsupported flow.
3. CLI/demo slice (medium, depends 2): bounded file input, exclusive output/aliases,
   exact status codes and eight fixed synthetic cases/reproducible check mode.
   Files: __main__, CLI tests, demo script, samples as one data unit. Done: supported
   equal/different, numeric unsupported and invalid paths behave as contracted;
   original evidence unchanged, short-write/error paths covered.
4. Adversarial verification/review (medium, depends 3): ECC actual-code self-review,
   normal/optimized suite, five isolated mutation checks, compile/SAST and evidence
   report. Files: behavioral tests, private mutation runner/results, REVIEW,
   VALIDATION. Done: detected/restored weakenings, zero unfixed actionable defects,
   precise platform/coverage limits. No independent-review claim.
5. Portfolio/local security records (medium, depends 4): README, SECURITY, license/
   attribution, prepared CI/CodeQL/dependency baseline and state/learning decisions.
   Group docs/config records as coherent units, preserve previous labs. Done:
   appropriate workflow/signature checks, exact sample reproduction, local clean
   commit and verified Obsidian milestone. No hosted pass, push, merge or publish.

## Verification strategy

Freeze at least 20 independently justified behavioral cases before implementation:
whitespace/key/escape equality; true versus 1 distinct; integer versus quoted number
distinct; arrays reordered distinct; nested objects; literal versus escaped astral
scalar equal; UTF-16 versus code-point keys; composed/decomposed Unicode distinct;
five short controls/other C0 escaping; three published pairs; exact safe-int endpoints
and just-outside values; fraction/exponent/negative-zero unsupported; huge exponents
without conversion; duplicate decoded names at depth; malformed UTF-8/BOM/reversed
or lone surrogates/noncharacters invalid; unsupported plus later duplicate/invalid
Unicode still invalid; all inclusive/excess resource bounds; deterministic report,
output limits, aliases/unchanged originals and exclusive/failed writes.

Five mutations: UTF-16 sort→code-point sort; disable duplicate detection; add NFC
normalization; accept unsafe integer; drop output bound. Selected independently
fixed tests must fail on isolated copies, originals hashed unchanged. Avoid relying
on external canonicalizer execution or deriving every expected value from this
implementation. Preserve full commands/exits/logs and case labels.

Planned commands: `python -m unittest discover -v`, same with `python -O`;
`python scripts/demo_reports.py --check`; `python -m compileall -q canonical_lab tests scripts`;
`python -m bandit -r canonical_lab scripts`. Focused checks first, rerun affected
checks after fixes, no redundant broad loops. Hosted CI/CodeQL and other runtime/
platform checks remain not-run unless separately available/authorized.

Eight fixed demonstration cases: formatting/key-order equality; literal/escaped
astral equality; UTF-16 ordering equality; composed/decomposed Unicode difference;
bool/integer difference; array-order difference; unsupported decimal/exponent;
duplicate decoded-name rejection. Golden case inputs/expected bytes/exits are
reviewed before implementation. The invalid demo records an expected error/exit
in the teaching summary, never a fabricated successful comparison report.

## Worker and authorization next step

Planning-and-task-breakdown skill applied; one bounded local Ollama extraction
accepted after sandbox permission correction (5.710 seconds, three reviewed labels).
Raw output separate from this reviewed plan. Codex retains interpretation/security
judgments; no remote worker needed, zero additional spending. Existing project,
parent/shared tooling and previous lab records preserved.

Approved addendum read/recorded before code: complete validation of both documents,
invalid precedence, reversible synthetic-only hex output, actual fixture/licensing
gate and honest bounds/mutation reachability. Preflight imposes bounds while strict
decoder remains grammar authority. Short/flush failures must fail honestly. Replace
unreachable output-bound mutation with reachable container-bound weakening; report
output guard seam checks separately, never count mutation crashes as detection.
Next: complete approved stages. Cutoff remains October 6, 2026, 08:00 Eastern.
