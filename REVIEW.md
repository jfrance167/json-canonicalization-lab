# ECC self-review — October 5, 2026

Implementing Codex agent used installed ecc-code-review and its pinned reviewer
checklist. Scope: actual full runtime, callers, admission/core/CLI tests, demo
generator, independently published data/provenance, output bounds/failure paths,
licenses and prepared workflows. This is self-review; native full ECC plugin
installation remains blocked, and no independent review is claimed.

No remaining actionable application defects found. Examined duplicate decoded
names before dict loss, exact byte APIs, unsupported numeric markers without
rounding, both-document validation, Unicode scalar/noncharacter rejection,
UTF-16 order, preserved strings/arrays and bool/int distinction. Digest inputs
and unauthenticated/profile-context limits are explicit. Source/callers do not
execute or interpret payload values. File/output checks preserve evidence.

Reviewed honest short-write/flush/close error handling and verified a real closed
pipe exits 2 in both normal and optimized child interpreters. Canonical/report
caps are defensive beyond tighter valid shape limits; guard seams tested without
inventing an end-to-end overflow. Reachable container weakening replaces that
mutation. Five mutants failed with assertions, not crashes, original hashes intact.

Provenance capture initially used Windows default decoding; exact blob/length
gate caught changed non-ASCII bytes before adaptation. Explicit UTF-8 capture
then verified all seven artifacts. This was a one-off capture-script correction,
not a shipped parser issue. Raw failure/source receipts retained privately.

Normal/optimized 22-test suites, exact demos, compile and Bandit pass; no suppressions.
Remaining limits: subset semantics only, reversible hex, unauthenticated hashes,
hostile filesystem races, partial new output on I/O failure, local Windows/runtime
only, no hosted/independent audit. Review grants no external publication or merge.
