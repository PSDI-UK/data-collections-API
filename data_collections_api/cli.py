"""CLI for PSDI data-collections-api project."""

import argparse
from pathlib import Path

from . import __version__
from .metadata import dump_example, validate_metadata


def get_arg_parser() -> argparse.ArgumentParser:
    """Build argument parser for PSDI data-collection-api."""
    arg_parser = argparse.ArgumentParser(
        prog="PSDI Data",
        description="Single-utility API for data handling with remote depositories."
    )
    arg_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
    )
    arg_parser.set_defaults(func=lambda _: arg_parser.print_help())
    subparser = arg_parser.add_subparsers()

    # Validate
    sp = subparser.add_parser(
        "validate",
        help="Validate metadata",
        description="Validate a metadata file or string.",
    )
    sp.add_argument("file", help="File to validate", type=Path)
    sp.add_argument("-f", "--format", choices=["json", "yaml"], help="Parse FILE as this type.", default=None)
    sp.set_defaults(func=validate_metadata)

    # Dump
    sp = subparser.add_parser(
        "template",
        help="Dump a template file.",
        description="Dump a file template to file.",
        aliases=["dump"]
    )
    sp.add_argument("file", help="File to write", type=Path)
    sp.add_argument("-f", "--format", choices=["json", "yaml"], help="Parse FILE as this type.", default=None)
    sp.set_defaults(func=dump_example)

    return arg_parser

def main():
    """Run main entry-point for CLI."""
    ap = get_arg_parser()
    args = ap.parse_args()

    args.func(args)
