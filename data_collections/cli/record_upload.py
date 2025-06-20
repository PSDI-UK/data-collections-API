#!/usr/bin/env python
"""Script for uploading a record to an Invenio repository."""

from __future__ import annotations

import argparse
import glob
import logging
from pathlib import Path
import sys

import yaml

from data_collections.invenio import InvenioRepository


def create_files_dict(all_files: list):
    """
    Save file paths into a dictionary to a format e.g.

    files_dict = {
        "name1.file": "path/to/name1.file",
        "name2.file": "path/to/name2.file",
    }

    Returns
    -------
    dict
        Dictionary of file names and file paths.

    """
    files_dict = {}
    for file_str in all_files:
        # expand file_str if using wildcards
        files = glob.glob(file_str)
        for file in files:
            file_path = Path(file)
            files_dict[file_path.name] = file_path
    return files_dict


def run_record_upload(
    api_url="api_url",
    api_key="api_key",
    metadata_path="metadata_path",
    files="files",
    community="community",
):
    """Run the uploading of metadata and associated files to an Invenio repository."""
    # create repo object
    repository = InvenioRepository(url=api_url, api_key=api_key)

    # open metadata record
    with Path.open(metadata_path) as f:
        data = yaml.safe_load(f)

    # TO-DO: validate metadata here

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


def main():
    """Upload records to Invenio repository."""
    try:
        usage = "upload_record [-h]"
        parser = argparse.ArgumentParser(
            description="Upload records to Invenio repository",
            usage=usage,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        parser.add_argument_group("Options")
        parser.add_argument(
            "--api_url",
            metavar="str",
            default=None,
            required=True,
            help="url for the API associated with the Invenio repository",
        )
        parser.add_argument(
            "--api_key",
            metavar="str",
            default=None,
            required=True,
            help="key for accessing the Invenio repository",
        )
        parser.add_argument(
            "--metadata_path",
            metavar="file",
            default=None,
            required=True,
            help="file path for Invenio metadata yaml file",
        )
        parser.add_argument(
            "--files",
            nargs="+",
            help="list of file paths associated with the record to be uploaded",
        )
        parser.add_argument(
            "--community",
            metavar="str",
            default=None,
            help="name of community to upload record to, e.g. biosimdb",
        )
        op = parser.parse_args()
    except argparse.ArgumentError:
        logging.error(
            "Command line arguments are ill-defined, please check the arguments.",
        )
        raise
        sys.exit(1)

    run_record_upload(
        api_url=op.api_url,
        api_key=op.api_key,
        metadata_path=op.metadata_path,
        files=op.files,
        community=op.community,
    )


if __name__ == "__main__":
    main()
