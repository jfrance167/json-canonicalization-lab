# JSON canonicalization lab

Compare original UTF-8 JSON bytes and their representations under the explicitly
restricted **jcs-integer-subset-v1** profile. Offline, synthetic educational data
only; Python 3.13+, standard library at runtime.

```powershell
python -m canonical_lab compare tests/vectors/original/input/arrays.json tests/vectors/original/output/arrays.json
python -m unittest discover -v
python -O -m unittest discover -v
python scripts/demo_reports.py --check
```

The first command exits 0: original bytes differ, canonical bytes agree. Optional
`--output NEW.json` creates a new report exclusively; existing files/input aliases
are rejected. Same-file left/right comparison is valid. Inputs remain unchanged.
Reports are escaped ASCII JSON with canonical bytes as hex, exact SHA-256 inputs,
separate equality facts and `origin_authenticated: false`.

**Hex is reversible, not redaction.** Use only invented documents. A digest binds
the bytes hashed under hash assumptions; it authenticates neither sender nor
intended meaning, and does not bind the separately reported profile/context.

| Exit | Meaning |
| --- | --- |
| 0 | Supported canonical representations equal |
| 1 | Supported canonical representations differ |
| 2 | Invalid encoding/JSON/Unicode/duplicates/resources, I/O or output failure |
| 3 | Valid bounded JSON with numeric forms outside the declared subset |

Both documents are validated before any verdict; unsupported left input cannot
hide invalid right input. Unsupported output can still report raw-byte equality,
but claims no canonical equality. Syntax authority is the strict decoder; preflight
only imposes bounds. Any JSON top-level value is accepted if supported/bounded;
object names are payload data, not ignored configuration fields.

## Representation contract

Accept null, booleans, strings, arrays, objects and integer-form tokens within
±9007199254740991. Decimals/exponents, unsafe integers and `-0` are unsupported,
without float conversion or coercion. This deliberately excludes JSON forms that
full JCS can serialize. Strings remain unnormalized; arrays preserve order;
objects sort recursively by unsigned UTF-16 code units. Booleans and integers
remain different even where Python equality would equate `True` and `1`.

Strict UTF-8, no BOM/replacement decoding/nonfinite constants. Duplicate names
are detected after escape decoding, at every depth. Lone/reversed surrogates and
Unicode noncharacters fail; valid escaped pairs match literal scalar UTF-8.
String escape/ordering rules follow [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html)
for accepted data, with [I-JSON constraints](https://www.rfc-editor.org/rfc/rfc7493.html).
Ordinary `json.dumps(sort_keys=True)` is not universal JCS. No general conformance
or downstream schema/business meaning is asserted.

Limits per document: 16 KiB input; eight nested containers; 256 total nodes
(including property keys); 64 members/elements per container; 1024 scalar
characters per string/key and 4096 aggregate; 64-character numeric lexemes;
32 KiB defensive canonical cap. Report cap 256 KiB. Exact-byte APIs carry these
same admission limits, excluding arbitrary Python objects/custom serialization.

```text
bounded original bytes → strict parser → shape/Unicode validation
                      → restricted UTF-16 ordered serializer
                      → exact byte comparisons + SHA-256 → escaped report
```

`canonical_lab.canonical.canonicalize(bytes)` returns a frozen `Canonical` holding
raw bytes, canonical bytes (or None) and fixed unsupported reason codes.
`canonical_lab.report.compare(left_bytes, right_bytes)` returns report/exit code;
invalid admission raises `InputError`. Exact built-in bytes required. SHA-256 inputs
are exactly the corresponding original or canonical byte sequence, with no added
newline, BOM or profile prefix. Detailed frozen fields are in [tasks/plan.md](tasks/plan.md).

## Demonstration and learning

[Eight case results](samples/demo-report.json) and [fixed synthetic input hex](samples/demo-cases.json)
cover format/order and astral-escape equality, UTF-16 ordering, composed/decomposed
Unicode difference, bool/int difference, array order, unsupported numbers and
duplicate-name errors. `scripts/demo_reports.py` is the reusable generator:
no user paths, fixed inputs/expected exits, write mode replaces only these two
sample artifacts; `--check` compares exact bytes without writing. Invalid cases
have teaching error records, never fabricated successful comparison reports.

Length-prefix framing is an alternative for preserving record boundaries, not
JSON equivalence: `ab`+`c` and `a`+`bc` concatenate alike unless boundaries survive.
This lab implements neither framing transport nor a log/signature service.

[VALIDATION.md](VALIDATION.md) records 22 normal/optimized tests, three published
golden pairs, provenance, five guard mutations and SAST. [REVIEW.md](REVIEW.md)
is ECC self-review by the implementing agent, not independent review. No hosted
CI/CodeQL, Linux execution or production audit claimed. Prepared immutable-pinned
CI and version-pinned development tooling are local artifacts only.

Original harness MIT; RFC-derived components retain IETF Revised BSD notice;
Apache published vectors retain exact originals, license and source/hash manifest.
See [NOTICE.md](NOTICE.md), [RESEARCH.md](RESEARCH.md), [SECURITY.md](SECURITY.md).
No third-party runtime implementation copied/executed or package installed.
AI assistance: Codex implementation/source verification/security judgments/ECC
self-review; local qwen3.5:2b extracted three reviewed learning labels. No remote
worker inference or additional spending.

Optional exercise: why can formatting change the raw hash while leaving the
canonical hash unchanged, and why does neither establish who supplied the data?

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
