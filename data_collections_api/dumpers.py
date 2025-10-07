"""Dumper/loader functions."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from functools import partial
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


class DumpLoad(NamedTuple):
    """Holder for dumpers and loaders."""

    dumper: Dumper
    loader: Loader
    str_loader: StrLoader


def json_dumper(data: Any, file: TextIO):
    """
    JSON format dumper.

    Parameters
    ----------
    data
        Data to dump.
    file
        File to dump to.
    """
    json.dump(data, file, indent=2)


def ruamel_dumper(data: Any, file: TextIO):
    """
    YAML (ruamel.yaml) format dumper.

    Parameters
    ----------
    data
        Data to dump.
    file
        File to dump to.
    """
    yaml_eng = ruamel.YAML(typ="safe")
    yaml_eng.dump(data, file)


def pyyaml_dumper(data: Any, file: TextIO):
    """
    YAML (pyyaml) format dumper.

    Parameters
    ----------
    data
        Data to dump.
    file
        File to dump to.
    """
    yaml.dump(data, file)


def json_loader(path: Path | str) -> dict[str, Any]:
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


def ruamel_loader(path: Path | str) -> dict[str, Any]:
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


def pyyaml_loader(path: Path | str) -> dict[str, Any]:
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


def json_str_loader(data: str) -> dict[str, Any]:
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


def pyyaml_str_loader(data: str) -> dict[str, Any]:
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


def ruamel_str_loader(data: str) -> dict[str, Any]:
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


def get_load_dump(fmt: str, *, loader: bool, string: bool = False) -> Dumper | Loader | StrLoader:
    """
    Get appropriate loader/dumper for unified interface.

    Parameters
    ----------
    fmt
        Format to handle.
    loader
        Whether to load loader.
    string
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


get_dumper = partial(get_load_dump, loader=False)
get_dumper.__doc__ = get_load_dump.__doc__.replace("loader/dumper", "dumper")
get_loader = partial(get_load_dump, loader=True)
get_loader.__doc__ = get_load_dump.__doc__.replace("loader/dumper", "loader")
get_str_loader = partial(get_load_dump, loader=True, string=True)
get_str_loader.__doc__ = get_load_dump.__doc__.replace("loader/dumper", "string loader")

#: Currently supported dumpers.
SUPPORTED_FORMATS: dict[str, DumpLoad] = {
    "json": DumpLoad(json_dumper, json_loader, json_str_loader),
    "ruamel": DumpLoad(ruamel_dumper, ruamel_loader, ruamel_str_loader),
    "pyyaml": DumpLoad(pyyaml_dumper, pyyaml_loader, pyyaml_str_loader),
}
#: Valid formats
Formats = Literal["json", "yaml", "ruamel", "pyyaml"]
