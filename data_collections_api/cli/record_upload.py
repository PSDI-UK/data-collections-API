#!/usr/bin/env python
"""Script for uploading a record to an Invenio repository."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import glob
from pathlib import Path

from data_collections_api.dumpers import Formats, get_loader
from data_collections_api.invenio import InvenioRepository
from data_collections_api.metadata import validate_metadata


def create_files_dict(all_files: Iterable[Path | str]) -> dict[str, Path]:
    """
    Save file paths into a dictionary to a format e.g.

    Parameters
    ----------
    all_files : Iterable[Path | str]
        Files to load into dict.

    Returns
    -------
    dict[str, Path]
        Dictionary of file names and file paths.

    Examples
    --------
    .. code-block:: Python

       files_dict = create_files_dict(["my_dir/*.file", "my_dir/example/*.cif"])
       # files_dict = {
       #    "name1.file": "my_dir/name1.file",
       #    "name2.file": "my_dir/name2.file",
       #    "name1.cif": "my_dir/example/name1.cif",
       # }
    """
    files_dict = {}
    for file_str in all_files:
        # expand file_str if using wildcards
        files = glob.glob(file_str)  # noqa: PTH207
        for file in files:
            file_path = Path(file)
            files_dict[file_path.name] = file_path
    return files_dict


def run_record_upload(
    api_url: str,
    api_key: str,
    metadata_path: Path,
    metadata_format: Formats,
    files: Iterable[Path | str],
    community: str,
) -> None:
    """
    Run the uploading of metadata and associated files to an Invenio repository.

    Parameters
    ----------
    api_url : str
        URL of repository.
    api_key : str
        Repository API key.
    metadata_path : Path
        Path to metadata file.
    metadata_format : Formats
        Format of metadata file (json or yaml).
    files : list[Path | str]
        Files to upload.
    community : str
        Community to which files will be uploaded.
    """
    # create repo object
    repository = InvenioRepository(url=api_url, api_key=api_key)

    # open metadata record
    loader = get_loader(metadata_format)
    data = loader(metadata_path)

    validate_metadata(data)

    # convert list of file paths to a dictionary
    files_dict = create_files_dict(files)

    # create an empty draft record in Invenio and retrieve its id
    draft = repository.depositions.create()
    draft_id = draft.get()["id"]

    # add metadata to draft
    repository.depositions.draft(draft_id).update(data)

    # add files to draft
    repository.depositions.draft(draft_id).files.upload(files_dict)

    # bind draft to a community
    repository.depositions.draft(draft_id).bind(community)

    # submit draft for review
    repository.depositions.draft(draft_id).submit_review()


def get_arg_parser(parser: argparse.ArgumentParser | None = None) -> argparse.ArgumentParser:
    """
    Return an argument parser for uploads, or configure a subparser if passed.

    Parameters
    ----------
    parser : ArgumentParser, optional
        Parser (or SubParser) to configure.

    Returns
    -------
    ArgumentParser
        Configured parser for uploading records.
    """
    if parser is None:
        parser = argparse.ArgumentParser(
            description="Upload records to Invenio repository",
        )

    parser.add_argument_group("Options")
    parser.add_argument(
        "--api-url",
        metavar="URL",
        type=str,
        required=True,
        help="URL for the API associated with the Invenio "
        "repository, e.g. https://data-collections-staging.psdi.ac.uk/api",
    )
    parser.add_argument(
        "--api-key",
        metavar="str",
        type=str,
        required=True,
        help="Your API key/token for accessing the Invenio repository instance.",
    )
    parser.add_argument(
        "--metadata-path",
        metavar="file",
        required=True,
        help="File path to the yaml file containing the metadata to upload "
        "a record to an Invenio repository, e.g. path/to/files/record.yaml",
    )
    parser.add_argument(
        "-f",
        "--metadata-format",
        choices=("json", "yaml"),
        default="yaml",
        help="Parse metadata file as this type (default: %(default)s).",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="List of file paths associated with the record to be uploaded, "
        "e.g. path/to/files/data.*",
    )
    parser.add_argument(
        "--community",
        metavar="str",
        type=str,
        help="Name of a Invenio repository community to upload the record to, "
        "e.g. biosimdb, data-to-knowledge, etc.",
    )

    return parser


def main(args: argparse.Namespace):
    """
    Upload records to Invenio repository.

    Parameters
    ----------
    args : Namespace
        Arguments to pass to :func:`run_record_upload`.
    """
    run_record_upload(
        api_url=args.api_url,
        api_key=args.api_key,
        metadata_path=args.metadata_path,
        metadata_format=args.metadata_format,
        files=args.files,
        community=args.community,
    )


def cli():
    """Run job through CLI."""
    parser = get_arg_parser()
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
