"""Module defining different schemas available for use."""

from __future__ import annotations

from functools import singledispatch

from schema import Schema as Schema

from .base import base_schema

SCHEMAS = {
    "base": base_schema,
    "default": base_schema,
}


@singledispatch
def get_schema(schema) -> Schema:
    """
    Get schema.

    Parameters
    ----------
    schema : Schema | str
        Schema to get.

    Returns
    -------
    Schema
        Desired schema.

    Raises
    ------
    NotImplementedError
        Passed an invalid type.

    Examples
    --------
    >>> get_schema(base_schema)
    >>> get_schema("default")
    """
    raise NotImplementedError(f"Cannot find schema with {type(schema).__name__}")


@get_schema.register
def _(schema: Schema) -> Schema:
    return schema


@get_schema.register
def _(schema: str) -> Schema:
    return SCHEMAS[schema]
