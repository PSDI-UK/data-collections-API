"""Generate schema documentation."""

from __future__ import annotations

import argparse
from pathlib import Path
from shutil import rmtree
from textwrap import indent
from typing import TYPE_CHECKING

import jsonschema_markdown

from data_collections_api.schemas import SCHEMAS, Schema, get_schema

if TYPE_CHECKING:
    from collections.abc import Sequence

__author__ = "Jacob Wilkins"
__version__ = "0.1"

INDEX_MD = """\
{filename}
{underline}

This page documents the available schemas.

.. toctree::
   :maxdepth: 1
   :caption: Schemas:

{schemas}

"""


def get_arg_parser() -> argparse.ArgumentParser:
    """Get parser for CLI.

    Returns
    -------
    argparse.ArgumentParser
        Arg parser.
    """
    parser = argparse.ArgumentParser(
        description="Convert a schema to a markdown document.",
    )

    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s v{__version__}")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print while generating schemas",
    )
    parser.add_argument(
        "-F",
        "--force",
        action="store_true",
        help="Force removal of output directory (if not CWD). (default: %(default)s)",
    )
    parser.add_argument(
        "schemas",
        nargs="*",
        choices=SCHEMAS.keys() | {"all"},
        help="Schemas to convert or 'all' if all are to be done. (default: %(default)r)",
        default="all",
    )

    parser.add_argument(
        "--clear",
        action=argparse.BooleanOptionalAction,
        help="Clear folder before writing. (default: %(default)s)",
        default=True,
    )
    parser.add_argument(
        "--index",
        action=argparse.BooleanOptionalAction,
        help="Write index file with toctree to folder. (default: %(default)s)",
        default=True,
    )

    parser.add_argument(
        "--header",
        help="Title of index file. (default: %(default)r)",
        default="Schemas",
    )

    parser.add_argument(
        "-O",
        "--out-name",
        help=(
            "Format to use for naming output, "
            "substituting '%%s' for schema key. (default: %(default)r)"
        ),
        default="%s.md",
    )
    parser.add_argument(
        "-o",
        "--out-folder",
        help="Folder to write formatted docs in. (default: %(default)r)",
        default="schemas",
        type=Path,
    )

    return parser


def process_schema(
    schema_key: Schema | str,
    *,
    name: str | None = None,
) -> str:
    """Process a schema into markdown.

    Parameters
    ----------
    schema_key : Schema or str
        Key for schemas.
    name : str, optional
        Override for name (mandatory if passing :class:`schema` directly).

    Returns
    -------
    str
        Markdown rendered documentation.

    Raises
    ------
    ValueError
        Name not passed with Schema.
    """
    match (schema_key, name):
        case (_, str() as inp):
            name = inp
        case (str() as inp, _):
            name = inp
        case _:
            raise ValueError(f"Cannot reliably determine name from {type(schema_key).__name__}")

    schema = get_schema(schema_key)
    json_schema = schema.json_schema(name)

    return jsonschema_markdown.generate(
        json_schema,
        title=name,
        footer=False,
        hide_empty_columns=True,
    )


def get_filename(fmt: str, key: str) -> str:
    """Format filename from CLI.

    Parameters
    ----------
    fmt : str
        CLI format.
    key : str
        Schema key.

    Returns
    -------
    str
        Formatted filename.

    Examples
    --------
    >>> get_filename("%s.md", "base")
    'base.md'
    """
    return fmt % key


def main(args_in: Sequence[str] | None = None, /) -> None:
    """Parse schemas and dump to file.

    Parameters
    ----------
    args_in : Sequence[str], optional
        Pass CLI params directly.
    """
    parser = get_arg_parser()
    args = parser.parse_args(args_in)

    # Get unique (by schema), but ordered keys matching reqs
    schemas = {
        schema: key
        for key, schema in reversed(SCHEMAS.items())
        if "all" in args.schemas or key in args.schemas
    }
    out_names = [get_filename(args.out_name, key) for key in schemas.values()]

    if args.verbose:
        print(f"Generating schemas for keys {', '.join(map(repr, schemas.values()))}...")

    if args.clear and args.out_folder.exists() and not args.out_folder.samefile(Path.cwd()):
        if (
            not args.force
            and input(
                f"Running this will clear {args.out_folder},"
                " are you sure you want to continue? [y/N] "
            )
            .strip()
            .lower()
            != "y"
        ):
            print("Cancelling.")
            return

        if args.verbose:
            print(f"Deleting {args.out_folder}...")

        rmtree(args.out_folder, ignore_errors=True)
        args.out_folder.mkdir()

    for key, out_name in zip(schemas.values(), out_names, strict=True):
        out_path = args.out_folder / out_name

        if args.verbose:
            print(f"Generating schema for {key!r} to {out_path}...")

        markdown = process_schema(key)

        with out_path.open("w", encoding="utf-8") as out:
            out.write(markdown)

    if args.index:
        if args.verbose:
            print(f"Writing index to {args.out_folder / 'index.rst'}...")

        with (args.out_folder / "index.rst").open("w", encoding="utf-8") as out:
            out.write(
                INDEX_MD.format(
                    filename=args.header,
                    underline="=" * len(args.header),
                    schemas=indent("\n".join(Path(key).stem for key in out_names), " " * 3),
                )
            )

    if args.verbose:
        print("Done with schemas")


if __name__ == "__main__":
    main()
