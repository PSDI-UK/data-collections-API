"""Dumper/loader functions."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
import json
from pathlib import Path
from typing import Any, Literal, NamedTuple, TextIO

_YAML_TYPE = None

with suppress(ImportError):
    import yaml

    _YAML_TYPE = "pyyaml"

with suppress(ImportError):
    from ruamel import yaml as ruamel

    _YAML_TYPE = "ruamel"

#: Dumping function protocol.
Dumper = Callable[[Any, TextIO], None]
#: Loading function protocol.
Loader = Callable[[Path | str], dict[str, Any]]
#: String loading function protocol.
StrLoader = Callable[[str], dict[str, Any]]


class Format(NamedTuple):
    """Set of operations for a given loader format."""

    #: Dumper for format.
    dumper: Dumper
    #: Loader for format.
    loader: Loader
    #: String loader for format.
    str_loader: StrLoader


def _json_dumper(data: Any, file: TextIO):
    """
    JSON format dumper.

    Parameters
    ----------
    data : Any
        Data to dump.
    file : TextIO
        File to dump to.
    """
    json.dump(data, file, indent=2)


def _ruamel_dumper(data: Any, file: TextIO):
    """
    YAML (ruamel.yaml) format dumper.

    Parameters
    ----------
    data : Any
        Data to dump.
    file : TextIO
        File to dump to.
    """
    yaml_eng = ruamel.YAML(typ="safe")
    yaml_eng.dump(data, file)


def _pyyaml_dumper(data: Any, file: TextIO):
    """
    YAML (pyyaml) format dumper.

    Parameters
    ----------
    data : Any
        Data to dump.
    file : TextIO
        File to dump to.
    """
    yaml.dump(data, file)


def _json_loader(path: Path | str) -> dict[str, Any]:
    """
    JSON format loader.

    Parameters
    ----------
    path : Path | str
        File to load.

    Returns
    -------
    dict[str, Any]
        Parsed file.
    """
    path = Path(path)

    with path.open("r", encoding="utf8") as file:
        return json.load(file)


def _ruamel_loader(path: Path | str) -> dict[str, Any]:
    """
    YAML (ruamel.yaml) format loader.

    Parameters
    ----------
    path : Path | str
        File to load.

    Returns
    -------
    dict[str, Any]
        Parsed file.
    """
    yaml_eng = ruamel.YAML(typ="safe")
    path = Path(path)

    with path.open("r", encoding="utf8") as file:
        return yaml_eng.load(file)


def _pyyaml_loader(path: Path | str) -> dict[str, Any]:
    """
    PYYAML format loader.

    Parameters
    ----------
    path : Path | str
        Path to load.

    Returns
    -------
    dict[str, Any]
        Parsed data.
    """
    path = Path(path)

    with path.open("r", encoding="utf8") as file:
        return yaml.safe_load(file)


def _json_str_loader(data: str) -> dict[str, Any]:
    """
    JSON format string loader.

    Parameters
    ----------
    data : str
        Data to parse.

    Returns
    -------
    dict[str, Any]
        Parsed data.
    """
    return json.loads(data)


def _pyyaml_str_loader(data: str) -> dict[str, Any]:
    """
    YAML (pyyaml) format string loader.

    Parameters
    ----------
    data : str
        Data to parse.

    Returns
    -------
    dict[str, Any]
        Parsed data.
    """
    return yaml.safe_load(data)


def _ruamel_str_loader(data: str) -> dict[str, Any]:
    """
    YAML (ruamel.yaml) format string loader.

    Parameters
    ----------
    data : str
        Data to parse.

    Returns
    -------
    dict[str, Any]
        Parsed data.
    """
    yaml_eng = ruamel.YAML(typ="safe")
    return yaml_eng.load(data)


def get_load_dump(
    fmt: Formats, *, loader: bool, string: bool = False
) -> Dumper | Loader | StrLoader:
    """
    Get appropriate loader/dumper for unified interface.

    Parameters
    ----------
    fmt : str
        Format to handle.
    loader : bool
        Whether to load loader.
    string : bool, optional
        Whether for string or file.

    Returns
    -------
    Dumper or Loader or StrLoader
        Dumping/Loading function.

    Raises
    ------
    ValueError
        Invalid `fmt` provided.
    ImportError
        No valid YAML dumper and `yaml` requested.
    NotImplementedError
        String dumper requested.

    See Also
    --------
    SUPPORTED_FORMATS
        Acceptable values for `fmt`.
    """
    if string and not loader:
        raise NotImplementedError("Dumping to string not implemented")

    if fmt == "yaml":
        if _YAML_TYPE is None:
            raise ImportError(
                "Couldn't find valid yaml dumper (ruamel.yaml / yaml)please install and try again.",
            )
        fmt = _YAML_TYPE

    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Cannot output in {fmt} format. Valid keys are: {', '.join(SUPPORTED_FORMATS.keys())}",
        )

    return SUPPORTED_FORMATS[fmt][loader + string]


def get_dumper(fmt: Formats):
    """
    Get appropriate dumper for unified interface.

    Parameters
    ----------
    fmt : Formats
        Format to handle.

    Returns
    -------
    Dumper
        Dumping function.

    See Also
    --------
    SUPPORTED_FORMATS
        Acceptable values for `fmt`.
    """
    return get_load_dump(fmt, loader=False)


def get_loader(fmt: Formats):
    """
    Get appropriate loader for unified interface.

    Parameters
    ----------
    fmt : Formats
        Format to handle.

    Returns
    -------
    Loader
        Loading function.

    See Also
    --------
    SUPPORTED_FORMATS
        Acceptable values for `fmt`.
    """
    return get_load_dump(fmt, loader=True)


def get_str_loader(fmt: Formats):
    """
    Get appropriate loader for unified interface.

    Parameters
    ----------
    fmt : Formats
        Format to handle.

    Returns
    -------
    StrLoader
        String loading function.

    See Also
    --------
    SUPPORTED_FORMATS
        Acceptable values for `fmt`.
    """
    return get_load_dump(fmt, loader=True, string=True)


def guess_format(path: Path, *, raise_on_invalid: bool = True) -> Formats | None:
    """
    Guess format from path suffix.

    Parameters
    ----------
    path : Path
        Path to guess format of.
    raise_on_invalid : bool
        Whether to raise on unrecognised or return ``None``.

    Returns
    -------
    Formats or None
        Expected format.

    Raises
    ------
    NotImplementedError
        Unknown format found.

    Examples
    --------
    >>> from pathlib import Path
    >>> guess_format(Path("my_file.json"))
    'json'
    >>> guess_format(Path("my_file.yml"))
    'yaml'
    """
    match path.suffix:
        case ".json":
            return "json"
        case ".yaml" | ".yml":
            return "yaml"
        case _ if raise_on_invalid:
            raise NotImplementedError(f"Cannot infer type of file {path.suffix!r}")
        case _:
            return None


#: Currently supported dumpers.
SUPPORTED_FORMATS: dict[str, Format] = {
    "json": Format(_json_dumper, _json_loader, _json_str_loader),
    "ruamel": Format(_ruamel_dumper, _ruamel_loader, _ruamel_str_loader),
    "pyyaml": Format(_pyyaml_dumper, _pyyaml_loader, _pyyaml_str_loader),
}
#: Valid formats.
Formats = Literal["json", "yaml", "ruamel", "pyyaml"]
