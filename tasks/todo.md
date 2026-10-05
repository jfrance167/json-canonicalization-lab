# Acceptance tasks — approved October 5, 02:01; completed locally

## 1. Provenance and admission — no dependencies
- [x] Retain three exact published input/output pairs with license/source/revision/length/Git blob/SHA256 before adaptation.
- [x] Strict bounded decoding preserves decoded names/Unicode and detects duplicates; numeric forms never silently round/coerce.
- [x] Focused admission/provenance tests distinguish invalid (2) from unsupported (3).

## 2. Supported canonical statements — depends 1
- [x] UTF-16 key order, array order, exact literals/integers and JCS string escaping follow frozen profile.
- [x] Published/RFC/hand-fixed golden bytes and exact comparisons pass, including bool versus int and Unicode normalization counterexample.
- [x] Digest inputs/profile/unsupported fields are explicit; complete in-memory checkpoint passes.

## 3. CLI and demos — depends 2
- [x] All four exit statuses, regular bounded reads, exclusive output/aliases and failure paths tested with originals unchanged.
- [x] Eight inert synthetic demos reproduce exact bytes using read-only check mode.
- [x] Final output is escaped/bounded; no partial supported verdict after admission failure.

## 4. Adversarial review — depends 3
- [x] Normal/optimized tests, compile and SAST pass; all five planned isolated mutations detected with originals unchanged.
- [x] ECC actual-code self-review fixes actionable findings and reruns affected tests.
- [x] Full receipts and precise platform/unsupported/independence limits recorded.

## 5. Portfolio/local security records — depends 4
- [x] README/security/license/attribution/AI assistance/state/learning records complete.
- [x] Prepared CI immutable pins/minimal permissions, dependency and targeted credential checks pass without hosted claims.
- [x] Clean local commit and Obsidian milestone verified; no publication/merge or unrelated edits.
