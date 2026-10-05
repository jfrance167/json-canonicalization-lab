# Security model

Synthetic educational documents only. Canonical hex is reversible and can disclose
every supported value; it is not redaction. No real documents/credentials are
needed. No network, signature/key, deserialization, expression evaluation, custom
object hook or third-party runtime dependency.

Untrusted bytes undergo strict UTF-8/JSON admission, pre-parse byte/depth/numeric
bounds, decoded duplicate detection and aggregate/node/Unicode checks. Unsupported
numbers are opaque reason markers without float conversion. Both documents must
validate before any report, including an unsupported result. Declared equivalence
deliberately erases formatting/escape spelling/member order while preserving scalar
strings, types and array order. No downstream application schema/meaning asserted.

Files are regular-only, checked before and after open, with bounded reads including
post-stat growth. CLI output is rendered/bounded before exclusive creation; no
overwrite or input aliases. Short writes, flush/close errors and closed stdout fail
with exit 2. Output is not transactional: stdout can be partial, and disk failure
can leave a partial newly created file. Hostile concurrent path replacement,
power-loss durability and a strict OS memory/time sandbox are outside scope.

Plain SHA-256 does not authenticate origin, timestamps or a separately reported
profile/context. Canonical equality does not authenticate meaning or truth.
Restricted integer subset is not full JCS or a production integrity protocol.
Consequential reliance requires Jake's manual review and appropriate independent
validation. Prepared CI/CodeQL and targeted signature scanning do not establish
absence of vulnerabilities or secrets. No deployment/publication/merge authorized.
