# Research learning goals

Raw UTF-8 JSON bytes can differ in whitespace, key order and escape spelling.
A declared bounded integer-only profile can map supported parsed values to equal
canonical bytes while preserving array order and unnormalized Unicode.
Hashing either representation does not authenticate origin or intended meaning.
These three labels were extracted locally and reviewed against primary sources.

Parsing first can destroy duplicate-name or numeric-precision evidence. Admission
must preserve those boundaries before canonicalization. Python code-point sorting
differs from UTF-16 sorting for selected non-BMP/BMP keys; ordinary sorted dumps
cannot be called universal JCS. Numeric unsupported does not imply invalid JSON.
Verified implementation controls now establish these declared subset behaviors,
not full JCS or consumer semantic equivalence. Five isolated weakened guards
caused assertion failures: ordering, duplicates, normalization, integers and shape.
An unsupported left value does not hide invalid right data. Both normal/optimized
real closed-pipe checks return 2. UTF-8 capture must be explicit on Windows:
provenance caught default-decoding changes before fixture adaptation.
