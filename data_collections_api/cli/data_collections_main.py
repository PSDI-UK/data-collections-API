"""CLI for PSDI data-collections-api project."""

from __future__ import annotations

import argparse
from pathlib import Path

from data_collections_api import __version__
from data_collections_api.cli.record_upload import get_arg_parser as get_upload_parser
from data_collections_api.cli.record_upload import main as upload_main
from data_collections_api.metadata import dump_example, validate_cli
from data_collections_api.schemas import SCHEMAS


def get_arg_parser() -> argparse.ArgumentParser:
    """
    Build argument parser for PSDI data-collection-api.

    Returns
    -------
    ArgumentParser
        Configured parser for CLI.
    """
    arg_parser = argparse.ArgumentParser(
        prog="data_collections",
        description="Single-utility API for data handling with remote depositories.",
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
    sp.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml"],
        help="Parse FILE as this type (default: determine from suffix).",
        default=None,
    )
    sp.add_argument(
        "-S",
        "--schema",
        choices=SCHEMAS.keys(),
        help="Validate against given schema (default: default).",
        default="default",
    )
    sp.set_defaults(func=validate_cli)

    # Dump
    sp = subparser.add_parser(
        "template",
        help="Dump a template file.",
        description="Dump a file template to file.",
        aliases=["dump"],
    )
    sp.add_argument("file", help="File to write", type=Path)
    sp.add_argument(
        "-f",
        "--format",
        choices=("json", "yaml"),
        help="Dump FILE as this type (default: determine from suffix).",
        default=None,
    )
    sp.set_defaults(func=dump_example)

    # Upload
    sp = subparser.add_parser(
        "upload",
        help="Upload a dataset to an invenio repository.",
        description="Tool for uploading dataset to invenio repository.",
    )
    sp = get_upload_parser(sp)
    sp.set_defaults(func=upload_main)

    return arg_parser


def main():
    """Run main entry-point for CLI."""
    ap = get_arg_parser()
    args = ap.parse_args()

    args.func(args)
