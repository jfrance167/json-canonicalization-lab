"""Bounded raw JSON admission; decoder owns grammar, no float conversion."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import stat

MAX_INPUT = 16 * 1024
MAX_DEPTH = 8
MAX_NODES = 256
MAX_CONTAINER = 64
MAX_STRING = 1024
MAX_TOTAL_STRING = 4096
MAX_NUMERIC = 64
MAX_INTEGER = 2**53 - 1
REASONS = ("fraction-or-exponent", "unsafe-integer", "negative-zero")


class InputError(ValueError):
    """Invalid encoding, JSON, shape or resource contract (exit 2)."""


@dataclass(frozen=True)
class _Unsupported:
    reason: str


@dataclass(frozen=True)
class Parsed:
    value: object
    reasons: tuple[str, ...]


def _numeric(text: str, fractional: bool = False):
    if len(text) > MAX_NUMERIC:
        raise InputError("numeric lexeme limit exceeded")
    if fractional:
        return _Unsupported("fraction-or-exponent")
    if text == "-0":
        return _Unsupported("negative-zero")
    value = int(text)
    if abs(value) > MAX_INTEGER:
        return _Unsupported("unsafe-integer")
    return value


def _constant(_text: str):
    raise InputError("nonfinite constants are not JSON")


def _pairs(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise InputError("duplicate decoded property name")
        result[key] = value
    return result


def _preflight(text: str) -> None:
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise InputError("container depth limit exceeded")
        elif char in "}]":
            depth -= 1


def _validate(value: object) -> tuple[str, ...]:
    nodes = total = 0
    reasons = set()

    def walk(item: object) -> None:
        nonlocal nodes, total
        nodes += 1
        if nodes > MAX_NODES:
            raise InputError("total node limit exceeded")
        kind = type(item)
        if kind is str:
            if len(item) > MAX_STRING:
                raise InputError("string length limit exceeded")
            total += len(item)
            if total > MAX_TOTAL_STRING:
                raise InputError("aggregate string limit exceeded")
            for char in item:
                point = ord(char)
                if 0xD800 <= point <= 0xDFFF or 0xFDD0 <= point <= 0xFDEF or point & 0xFFFF in (0xFFFE, 0xFFFF):
                    raise InputError("surrogate or noncharacter is forbidden")
        elif kind in (dict, list):
            if len(item) > MAX_CONTAINER:
                raise InputError("container element limit exceeded")
            if kind is dict:
                for key, child in item.items():
                    walk(key)
                    walk(child)
            else:
                for child in item:
                    walk(child)
        elif kind is _Unsupported:
            reasons.add(item.reason)
        elif kind not in (int, bool, type(None)):
            raise InputError("unexpected decoded type")
    walk(value)
    return tuple(reason for reason in REASONS if reason in reasons)


def parse(data: bytes) -> Parsed:
    """Validate a complete exact-bytes document, retaining numeric limitations."""
    if type(data) is not bytes or len(data) > MAX_INPUT:
        raise InputError("expected bytes within 16 KiB")
    try:
        text = data.decode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            raise InputError("BOM not supported")
        _preflight(text)
        value = json.loads(text, object_pairs_hook=_pairs, parse_int=_numeric,
                           parse_float=lambda token: _numeric(token, True), parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise InputError("invalid UTF-8 JSON") from error
    return Parsed(value, _validate(value))


def read(path: Path) -> bytes:
    """Read regular files only; bound the read even if size changes after stat."""
    if not stat.S_ISREG(path.stat().st_mode):
        raise InputError("input must be a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(path, flags), "rb") as handle:
        info = os.fstat(handle.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_INPUT:
            raise InputError("nonregular or oversized input")
        result = handle.read(MAX_INPUT + 1)
        if len(result) > MAX_INPUT:
            raise InputError("input grew beyond byte limit")
        return result
