"""Compare synthetic regular files without overwriting input or output evidence."""
import argparse
import io
from pathlib import Path
import sys
from .contract import InputError, read
from .report import compare, render


def write_checked(handle, content: str) -> None:
    if handle.write(content) != len(content):
        raise OSError("short output write")
    handle.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthetic integer-only JSON canonical comparison; no origin authentication.")
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("compare")
    command.add_argument("left", type=Path)
    command.add_argument("right", type=Path)
    command.add_argument("--output", type=Path, help="create new escaped report only")
    args = parser.parse_args(argv)
    output_is_stdout = args.output is None
    try:
        report, code = compare(read(args.left), read(args.right))
        content = render(report)
        if args.output:
            if args.output.exists():
                if any(args.output.samefile(source) for source in (args.left, args.right)):
                    raise InputError("output aliases input evidence")
            with args.output.open("x", encoding="ascii", newline="\n") as handle:
                write_checked(handle, content)
        else:
            write_checked(sys.stdout, content)
        return code
    except (InputError, OSError, UnicodeError) as error:
        # Avoid a second buffered flush failure changing the promised exit status.
        if output_is_stdout and isinstance(error, OSError):
            sys.stdout = io.StringIO()
        try:
            print("canonical-lab: " + str(error).encode("unicode_escape").decode("ascii"), file=sys.stderr)
        except OSError:
            return 2
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
