"""Metadata validation and parsing."""

from __future__ import annotations

from functools import singledispatch
from pathlib import Path

from .dumpers import Formats, get_dumper, get_loader, get_str_loader
from .schema import schema

EXAMPLES_FOLDER = Path(__file__).parent.parent / "examples"

def dump_example(out_file: Path, fmt: Formats):
    """Dump an example schema.

    Parameters
    ----------
    out_file : Path
        File to write to.
    fmt : Formats
        Format to dump as.

    Examples
    --------
    FIXME: Add docs.
    """
    test = validate_metadata(EXAMPLES_FOLDER / "bare_example.yaml")
    get_dumper(fmt)(test, out_file)


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
def _(data: dict):
    return schema.validate(data)

@validate_metadata.register(str)
def _(data: str, fmt: Formats):
    try:
        data = get_str_loader(fmt)(data)
    except Exception:
        data = Path(data)
        return validate_metadata(data)
    else:
        return schema.validate(data)

@validate_metadata.register(Path)
def _(path: Path, fmt: Formats | None = None):
    if fmt is None:
        match path.suffix:
            case ".json":
                fmt = "json"
            case ".yaml" | ".yml":
                fmt = "yaml"

    data = get_loader(fmt)(path)
    return schema.validate(data)


if __name__ == "__main__":
    from pprint import pprint
    test = validate_metadata(EXAMPLES_FOLDER / "biosim_record.yaml")
    pprint(schema.validate(test))
    test = validate_metadata(EXAMPLES_FOLDER / "bare_example.yaml")
    pprint(schema.validate(test))
