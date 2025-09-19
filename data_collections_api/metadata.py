"""Metadata validation and parsing."""

from __future__ import annotations

import argparse
from functools import singledispatch
from pathlib import Path

from data_collections_api.dumpers import Formats, get_dumper, get_loader, get_str_loader
from data_collections_api.schema import schema

EXAMPLES_FOLDER = Path(__file__).parent / "examples"


@singledispatch
def dump_example(out_file: Path, fmt: Formats | None = None):
    """Dump an example schema.

    Parameters
    ----------
    out_file : Path
        File to write to.
    fmt : Formats
        Format to dump as.
    """
    if fmt is None:
        match out_file.suffix:
            case ".json":
                fmt = "json"
            case ".yaml" | ".yml":
                fmt = "yaml"
            case _:
                raise NotImplementedError(f"Cannot infer type of file {out_file.suffix!r}")

    test = validate_metadata(EXAMPLES_FOLDER / "bare_example.yml")
    with out_file.open("w", encoding="utf8") as file:
        get_dumper(fmt)(test, file)


@dump_example.register(argparse.Namespace)
def _(args: argparse.Namespace):
    dump_example(args.file, args.format)


@singledispatch
def validate_metadata(_val, fmt: Formats | None = None):
    """Verify and process project metadata.

    Parameters
    ----------
    path : Path | str
        Path to data to validate.
    fmt : Formats, optional
        Format to process.
    """
    raise NotImplementedError(f"Cannot validate data as {type(_val).__name__}")


@validate_metadata.register(dict)
def _(data: dict) -> dict:
    return schema.validate(data)


@validate_metadata.register(str)
def _(data: Path | str, fmt: Formats) -> dict:
    try:
        data = get_str_loader(fmt)(data)
    except Exception:
        data = Path(data)
        return validate_metadata(data)
    else:
        return schema.validate(data)


@validate_metadata.register(Path)
def _(path: Path, fmt: Formats | None = None) -> dict:
    if fmt is None:
        match path.suffix:
            case ".json":
                fmt = "json"
            case ".yaml" | ".yml":
                fmt = "yaml"
            case _:
                raise NotImplementedError(f"Cannot infer type of file {path.suffix!r}")

    data = get_loader(fmt)(path)
    return schema.validate(data)


@validate_metadata.register(argparse.Namespace)
def _(inp: argparse.Namespace) -> dict:
    return validate_metadata(inp.file, inp.format)

def validate_cli(inp: argparse.Namespace) -> dict:
    """Validate metadata and print success to screen.

    Parameters
    ----------
    inp : argparse.Namespace
        Input arguments from CLI.

    Returns
    -------
    dict
        Validated schema from file.

    """
    out = validate_metadata(inp)
    if out:
        print(f"{inp.file} valid.")
    return out
