"""Test repository API functions."""

from __future__ import annotations

from pathlib import Path

import pytest

from data_collections_api.dumpers import get_loader
from data_collections_api.invenio import InvenioRepository

LOCAL_SERVER = "127.0.0.1"
LOCAL_PORT = "5000"

DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def repo():
    return InvenioRepository(url=f"http://{LOCAL_SERVER}:{LOCAL_PORT}", api_key="")


def test_create_depo(repo):
    # create an empty draft record in Invenio and retrieve its id
    draft = repo.depositions.create()
    draft_id = draft.get()["id"]

    print(draft_id)

    metadata_path = DATA_DIR / "bare_example.yml"

    # open metadata record
    loader = get_loader("yaml")
    data = loader(metadata_path)

    # add metadata to draft
    repo.depositions.draft(draft_id).update(data)

    # add files to draft
    repo.depositions.draft(draft_id).files.upload({"metadata": metadata_path})

    # bind draft to a community
    repo.depositions.draft(draft_id).bind("geoff")

    # submit draft for review
    repo.depositions.draft(draft_id).submit_review()
