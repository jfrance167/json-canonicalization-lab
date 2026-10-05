"""Exact representation comparisons; hashes bind bytes, not origin/profile."""
import hashlib
import json
from .canonical import PROFILE, Canonical, canonicalize
from .contract import InputError

MAX_OUTPUT = 256 * 1024
LIMITATION = ("Synthetic educational data only. Canonical hex is reversible, not redaction. "
              "Equality applies only to the declared integer profile, not intended consumer meaning. "
              "SHA-256 inputs are exactly raw or canonical bytes; digests do not authenticate origin "
              "or bind the separately reported profile/context. No full JCS conformance claim.")


def _side(value: Canonical) -> dict:
    encoded = value.canonical
    return dict(raw_length=len(value.raw), raw_sha256=hashlib.sha256(value.raw).hexdigest(),
                canonical_length=None if encoded is None else len(encoded),
                canonical_hex=None if encoded is None else encoded.hex(),
                canonical_sha256=None if encoded is None else hashlib.sha256(encoded).hexdigest(),
                unsupported_reasons=list(value.reasons))


def compare(left: bytes, right: bytes) -> tuple[dict, int]:
    """Validate BOTH complete documents before unsupported or supported verdicts."""
    first, second = canonicalize(left), canonicalize(right)
    if first.reasons or second.reasons:
        relation, status, code = "unsupported", "unsupported", 3
    elif first.canonical == second.canonical:
        relation, status, code = "equal", "supported-equal", 0
    else:
        relation, status, code = "different", "supported-different", 1
    return dict(report_version=1, profile=PROFILE, hash_algorithm="sha256", status=status,
                raw_bytes_equal=left == right, canonical_relation=relation,
                left=_side(first), right=_side(second), origin_authenticated=False,
                limitation=LIMITATION), code


def render(report: dict) -> str:
    """Render inert ASCII JSON and enforce the defensive output guard."""
    result = json.dumps(report, ensure_ascii=True, indent=2, allow_nan=False) + "\n"
    if len(result.encode("ascii")) > MAX_OUTPUT:
        raise InputError("report byte limit exceeded")
    return result
