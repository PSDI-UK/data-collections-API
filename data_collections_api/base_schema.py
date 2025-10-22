"""Parsing schema for metadata."""

from __future__ import annotations

from datetime import date
from urllib.parse import urlparse, urlunparse
from uuid import UUID

from schema import And, Optional, Or, Regex, Schema, Use

ORCID_ID_RE = r"(\d{4}-){3}\d{4}"

id_schema = Or(
    {
        "scheme": "orcid",
        "identifier": Regex(ORCID_ID_RE),
    },
    {
        "identifier": And(Use(urlparse), lambda x: x.scheme and x.netloc, Use(urlunparse)),
        Optional("scheme", default="doi"): "doi",
    },
)

creator_schema = Schema(
    {
        Optional("affiliations"): [
            {
                "name": str,
            },
        ],
        "person_or_org": {
            Or("name", "family_name"): And(str, len),
            Optional("given_name"): And(str, len),
            Optional("identifiers"): [id_schema],
            "type": Or("personal"),
        },
    },
    ignore_extra_keys=True,
)

metadata_schema = Schema(
    {
        "title": And(str, len),
        "description": And(str, len),
        "creators": [creator_schema],
        "rights": [
            {
                "id": Or("cc-by-4.0"),
            },
        ],
        "resource_type": {
            "id": Or("model"),
        },
        Optional("subjects", default=[]): [{"subject": str}],
        "version": Regex(r"^v\d+(\.\d+)*"),
        Optional("publisher"): str,
        Optional("publication_date"): Or(date.fromisoformat, date.fromtimestamp),
        Optional("identifiers"): [id_schema],
    },
)

base_schema = Schema(
    {
        Optional("access", default={"files": "public", "record": "public"}): {
            Optional("embargo"): {
                "active": bool,
                "reason": Or(str, None),
            },
            Optional("files", default="public"): Or("public", "private"),
            Optional("record", default="public"): Or("public", "private"),
            Optional("status"): Or("open", "closed"),
        },
        Optional("files"): {"enabled": bool},
        "custom_fields": {"dsmd": [dict]},
        "metadata": metadata_schema,
        Optional("community"): UUID,
    },
)
