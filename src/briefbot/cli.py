"""BriefBot command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Sequence

from .input import load_brief
from .models import BriefError
from .output import write_output
from .planning import build_brief
from .report import format_brief


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an ISO date: YYYY-MM-DD") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="briefbot",
        description="Generate deterministic project briefs from local JSON notes",
    )
    parser.add_argument("--version", action="version", version="briefbot 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser(
        "validate",
        help="validate source notes without rendering a brief",
    )
    validate.add_argument("input", type=Path)
    validate.add_argument("--json", action="store_true", dest="as_json")

    render = commands.add_parser(
        "render",
        help="render validated source notes as Markdown or JSON",
    )
    render.add_argument("input", type=Path)
    render.add_argument("--as-of", type=_date, default=date.today())
    render.add_argument("--json", action="store_true", dest="as_json")
    render.add_argument("--output", type=Path)
    return parser


def _validation_summary(source, *, as_json: bool) -> str:
    payload = {
        "valid": True,
        "context_items": len(source.context),
        "decisions": len(source.decisions),
        "risks": len(source.risks),
        "actions": len(source.actions),
    }
    if as_json:
        return json.dumps(payload, indent=2, sort_keys=True)
    return (
        "Brief input is valid\n"
        f"Context items: {payload['context_items']}\n"
        f"Decisions: {payload['decisions']}\n"
        f"Risks: {payload['risks']}\n"
        f"Actions: {payload['actions']}"
    )


def run(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        source = load_brief(args.input)
        if args.command == "validate":
            print(_validation_summary(source, as_json=args.as_json))
            return 0

        brief = build_brief(source, as_of=args.as_of)
        content = format_brief(brief, as_json=args.as_json)
        if args.output is None:
            print(content, end="" if content.endswith("\n") else "\n")
        else:
            destination = write_output(args.output, content)
            print(f"Wrote {destination.name}")
        return 0
    except BriefError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
