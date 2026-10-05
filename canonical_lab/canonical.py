# RFC 8785 string/order code components: Copyright (c) 2020 IETF Trust
# and identified authors. Revised BSD notice: LICENSES/IETF-BSD-3-Clause.txt.
"""Restricted serializer; never interpret unsupported numbers or normalize text."""
from dataclasses import dataclass
from .contract import InputError, parse

PROFILE = "jcs-integer-subset-v1"
MAX_CANONICAL = 32 * 1024
SHORT = {8: "\\b", 9: "\\t", 10: "\\n", 12: "\\f", 13: "\\r"}


@dataclass(frozen=True)
class Canonical:
    raw: bytes
    canonical: bytes | None
    reasons: tuple[str, ...]


def _string(value: str) -> str:
    # Admission has already excluded surrogates/noncharacters and bounded strings.
    pieces = ['"']
    for char in value:
        point = ord(char)
        if char in ('"', "\\"):
            pieces.append("\\" + char)
        elif point < 32:
            pieces.append(SHORT.get(point, f"\\u{point:04x}"))
        else:
            pieces.append(char)
    return "".join(pieces) + '"'


def _serialize(value: object) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if type(value) is str:
        return _string(value)
    if type(value) is list:
        return "[" + ",".join(_serialize(child) for child in value) + "]"
    if type(value) is dict:
        keys = sorted(value, key=lambda key: key.encode("utf-16be"))
        return "{" + ",".join(_string(key) + ":" + _serialize(value[key]) for key in keys) + "}"
    raise InputError("unsupported internal serializer type")


def canonicalize(data: bytes) -> Canonical:
    """Return complete canonical bytes, or None/reasons after full validation."""
    parsed = parse(data)
    if parsed.reasons:
        return Canonical(data, None, parsed.reasons)
    encoded = _serialize(parsed.value).encode("utf-8")
    if len(encoded) > MAX_CANONICAL:
        raise InputError("canonical byte limit exceeded")
    return Canonical(data, encoded, ())
