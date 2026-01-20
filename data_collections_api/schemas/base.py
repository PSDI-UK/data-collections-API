"""Parsing schema for metadata."""

from __future__ import annotations

from datetime import date
from urllib.parse import urlparse, urlunparse

from schema import And, Literal, Optional, Or, Regex, Schema, Use

ORCID_ID_RE = r"(\d{4}-){3}\d{4}"
UUID_RE = r"\d{8}-(\d{4}-){3}\d{12}"

id_schema = Or(
    {
        Literal("scheme", description="ID scheme."): "orcid",
        Literal("identifier", description="An [ORCID](https://orcid.org)."): Regex(ORCID_ID_RE),
    },
    {
        Optional(Literal("scheme", description="ID scheme."), default="doi"): "doi",
        Literal("identifier", description="A [DOI](https://www.doi.org)"): And(
            Use(urlparse), lambda x: x.scheme and x.netloc, Use(urlunparse)
        ),
    },
)

creator_schema = Schema(
    {
        Optional(Literal("affiliations", description="Member affiliations.")): [
            {
                Literal("name", description="Name of institution."): str,
            },
        ],
        Literal("person_or_org", description="Person or organisation."): {
            Or(
                Literal("name", description="Full set of given names."),
                Literal("family_name", description="Family name(s)."),
            ): And(str, len),
            Optional(Literal("given_name", description="Given name(s).")): And(str, len),
            Optional(Literal("identifiers", description="ORCIDs or other IDs")): [id_schema],
            Literal("type", description="Personal or organisation."): Or("personal"),
        },
    },
    ignore_extra_keys=True,
)

metadata_schema = Schema(
    {
        Literal("title", description="Title of resource."): And(str, len),
        Literal("description", description="Summary of resource."): And(str, len),
        Literal("creators", description="List of creators."): [creator_schema],
        Literal("rights", description="Rights or license."): [
            {
                Literal("id", description="ID of rights or license."): Or("cc-by-4.0"),
            },
        ],
        Literal("resource_type", description="Type of resource."): {
            Literal("id", description="Resource class."): Or("model"),
        },
        Optional(
            Literal("subjects", description="List of keywords defining subjects resource covers."),
            default=[],
        ): [{Literal("subject", description="Subject keyword."): str}],
        Literal("version", description="Current version of resource."): Regex(r"^v\d+(\.\d+)*"),
        Optional(Literal("publisher", description="Publisher of resource.")): str,
        Optional(Literal("publication_date", description="Date of publication of resource.")): Or(
            date.fromisoformat, date.fromtimestamp
        ),
        Optional(
            Literal("identifiers", description="Resource identifiers such as ORCID or DOI.")
        ): [id_schema],
    },
)

base_schema = Schema(
    {
        Optional(
            Literal("access", description="Accessibility of data outside of owners."),
            default={"files": "public", "record": "public"},
        ): {
            Optional(Literal("embargo", description="Details of resource embargo.")): {
                Literal("active", description="Whether resource is under embargo."): bool,
                Literal("reason", description="Cause for embargo."): Or(str, None),
            },
            Optional(
                Literal("files", description="Accessibility to individual files."), default="public"
            ): Or("public", "private"),
            Optional(
                Literal("record", description="Accessibility to record as a whole."),
                default="public",
            ): Or("public", "private"),
            Optional(Literal("status", description="Current status or resource.")): Or(
                "open", "closed"
            ),
        },
        Optional(Literal("files", description="Details of files.")): {
            Literal("enabled", description="Whether file is enabled."): bool
        },
        Literal("custom_fields", description="Block for custom data."): {
            Literal("dsmd", description="Domain specific metadata (dsmd)."): [dict]
        },
        Literal("metadata", description="Resource metadata."): metadata_schema,
        Optional(
            Literal("community", description="UUID of community associated with resource.")
        ): Regex(UUID_RE),
    },
    description="Base schema from which community specific schemas are built.",
    name="base",
)
