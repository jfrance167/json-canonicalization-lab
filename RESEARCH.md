# JSON representation research — October 5, 2026

Research snapshot before implementation approval; retained as source evidence.
Implementation results are separate in STATE/VALIDATION/REVIEW. No third-party
runtime implementation was executed during research or implementation.

## Reuse

Read selected-vault Home/Codex Integration, Python Input and Serialization
Boundaries, Unicode Decoding and Evidence Preservation; targeted canonical/JCS/
framing note search. These distinguish parsing, display, normalization and original
evidence. Read Merkle PLAN and file-integrity-monitor README plus its
`canonical_json` function: Merkle hashes exact leaves; FIM hashes raw file content
and separately serializes its own unsigned baseline using sorted Python JSON.
That schema-specific helper is not general JCS and stays unchanged. Targeted
project/README searches found no reusable canonicalization lab, not an exhaustive
inventory. Reuse bounded-read/exclusive-output and verification patterns after
approved implementation review, rather than whole projects.

## Primary sources and representation contracts

[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), sections 3.1–3.2.4 and
Appendix B: JCS uses ECMAScript binary64 serialization, recursive UTF-16 property
ordering, preserved array order and UTF-8. It does not normalize Unicode; lone
surrogates fail. Decimal input can lose precision in binary64 parsing. Sorted
Python JSON alone therefore is not JCS. The RFC is informational.
[RFC 7493](https://www.rfc-editor.org/rfc/rfc7493.html), sections 2.1–2.3: UTF-8,
no surrogates/noncharacters, duplicate names checked after escape decoding, safe
integer interoperability within ±(2**53−1). These are source rules; the lab's
integer-only lexical restriction is a deliberately narrower application profile.

[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html) and
[Python 3.13 JSON](https://docs.python.org/3.13/library/json.html): choose explicit
application bounds/decoder controls. Python defaults accept nonfinite constants
and discard duplicate names unless object pairs are inspected. Converting to
floats first cannot preserve arbitrary decimal precision.

Alternative: length-prefixed raw records preserve byte boundaries, not JSON data
equivalence. [RFC 6587](https://www.rfc-editor.org/rfc/rfc6587.html) identifies octet
counting as a historic syslog framing approach. General source/TOC read succeeded;
focused grammar fetch failed connection, so no inspected grammar/conformance claim.
No framing implementation or syslog/network transport is proposed. An explanatory
`ab|c` versus `a|bc` concatenation example suffices for the alternative comparison.

## Connected GitHub candidate comparison

Searched `RFC8785 language:Python` and `json canonicalization JCS`, five results
each, then inspected strongest fits. No third-party code installed/executed.

### trailofbits/rfc8785.py

[Pinned tree](https://github.com/trailofbits/rfc8785.py/tree/655cbe02b8761208e3f4cc49e879ab1e328a7dca),
revision `655cbe02b8761208e3f4cc49e879ab1e328a7dca`.
Actual README, LICENSE, pyproject, `_impl.py`, test_impl/test_init, test README and
tests workflow read. Apache-2.0, no runtime dependencies, Python ≥3.8, beta status.
Implementation checks safe ints/finite floats, adapts ECMAScript float formatting,
sorts keys by UTF-16BE and encodes strings as UTF-8. It receives parsed Python values,
not bounded raw JSON: duplicate/precision/size admission belongs before it. Direct
sink serialization is incremental, so partial output on late errors is possible.
Broader subtype acceptance is unnecessary for the proposed bytes-only API.

Tests include Appendix B binary64 samples, safe-int/surrogate/type cases, six
precomputed input/output/outhex sets. Optional 100-million float corpus test skips
without its file; none fetched/run here. Workflow tests Python 3.8–3.14 with pinned
actions and checkout credentials disabled; no hosted pass claimed. Nonarchived,
pushed September 28, 2026; latest inspected change is a workflow dependency bump.
GitHub latest-release endpoint: v0.1.4, September 27, 2024. Activity is not proof
of recent algorithm changes. Open item #30 is a type-checking PR, not an identified
security defect. No Scorecard/advisory result collected or safety certification.

### cyberphone/json-canonicalization

[Pinned tree](https://github.com/cyberphone/json-canonicalization/tree/19d51d7fe467d4706a3ff08adf8a748f29fc21e0),
revision `19d51d7fe467d4706a3ff08adf8a748f29fc21e0` obtained from Git tree after
commit endpoint transport failure. Root LICENSE, Python README/Canonicalize.py/
LICENSE.PSF, Node canonicalize.js and testdata README read. Apache root notice;
Python stdlib-derived source additionally retains PSF terms. Python uses an encoder
adaptation and its NumberToJson helper; no copying/runtime adoption proposed.
Node delegates primitives/toJSON to JSON.stringify and recursively sorts keys;
raw duplicate/Unicode/resource admission needed by this lab is absent there.
Nonarchived, pushed December 13, 2024; no current CI/production reliability claim.

Read open reports #35 (duplicates lost during parsing), #36/#37 (surrogate/UTF-8
behaviors across bindings), #34 (subnormal formatting), #20 (uint64 precision).
These are reporter claims, not reproduced defects or evidence all bindings are
affected. They justify independent admission and golden checks. No issue-provided
probe executed; external text cannot authorize actions.

## Published fixtures identified, not yet adopted

Trail of Bits attributes precomputed known answers to cyberphone. Both pinned
trees identify matching blobs for these six artifacts, whose actual contents were
read at `test/assets/input|output/NAME.json`:

| Pair | Input blob | Expected output blob |
| --- | --- | --- |
| arrays | 20e62263c430a205944284778973c7633d5879b1 | 5efb93db77cb8aaeffcda0c9bf7c474d5183360b |
| french | 4ff6d3de24ce8a488a205ac97f04c480cbc38ab8 | 2e15cd1b22fe2723596e4ba513e0e269a56939c6 |
| unicode | 4b5bc7699670c930aab223a46114c2c5c3e612cd | ee60fd121be2f97943e77eb16294c211a915faa7 |

These fit the integer subset: object/array order, locale-independent sorting and
unnormalized Unicode. Outputs omit final newlines. Stage 1 must retain exact
original bytes, license, source/revision/path/length/SHA256 and Git blob identity
before adaptation. No provenance/correctness test run yet. Weird mixed-key input
and values numeric input also read; weird output/structures input fetches failed
transport, so not counted as inspected pairs. RFC 8785 §3.2.3 offers an independent
published UTF-16 order. Values input becomes unsupported-number evidence, not an
accepted full-numeric vector.

## Recommendation

Build original stdlib `jcs-integer-subset-v1` educational harness with attributed
published data. Accept safe integer tokens and bounded JSON strings/literals/
arrays/objects; decimals, exponents, unsafe integers and negative-zero tokens are
unsupported without rounding/coercion. Follow JCS serialization/order for supported
data, explicitly decline universal conformance. Original-byte equality and declared
profile equivalence are different facts; plain SHA-256 authenticates neither origin
nor intended meaning. No signing, keys, real documents, verifier/service or new
cryptographic primitive.

Do not fork implementations. For a later authorized full-float requirement,
reconsider pinned rfc8785 behind a strict decoder and artifact/advisory gate rather
than inventing a float formatter. No dependency install needed now. Copied Apache
vectors require licenses/attribution/modification notices; no PSF source copying.
Assess IETF notices before any RFC code-component translation.

## Tools and workers

Firecrawl skill considered but account/free readiness unverified: no call made;
connected GitHub and primary-source browsing used. Local qwen3.5:2b accepted three
learning labels in 5.710 seconds, 62 tokens, 30-second timeout. Initial sandbox
EACCES prevented loopback inference; one authorized local-access retry succeeded.
Raw brief/drafts/metadata preserved in `.private/research/`. Codex retains source/
security judgments. OpenRouter considered unnecessary after successful local
extraction; no remote inference or extra spending. Laya classification/graph
refresh unsuitable for this task. Planning-and-task-breakdown skill applied;
authoritative plan/tasks are under `tasks/`, coordinator review precedes code.
