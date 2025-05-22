"""Repository data structure."""

from __future__ import annotations

from abc import ABC
from functools import cached_property
import json
from pathlib import Path
from typing import NewType

import requests

URL = NewType("URL", str)
JSONResponse = NewType("JSONResponse", dict)

import sys


def _check(request: requests.Request, proc: str) -> dict:
    """Verify that a request has succeeded.

    Parameters
    ----------
    request : requests.Request
        Job to check.
    proc : str
        Job type requested.

    Raises
    ------
    requests.HTTPError
        If request fails.
    """
    try:
        request.raise_for_status()
    except requests.HTTPError as err:
        raise requests.HTTPError(
            f"Error while {proc}, info: {request.json()['message']}",
        ) from err

    return request.json()


class _SubCommandHandler(ABC):  # noqa: B024 (abstract-base-class-without-abstract-method)
    """Abstract base for general commands.

    Parameters
    ----------
    parent
        Parent job holder.
    """

    def __init__(self, parent):
        self.parent = parent

    @property
    def url(self):
        return self.parent.url

    @property
    def api_key(self):
        return self.parent.api_key


class _File(_SubCommandHandler):
    @property
    def api_url(self) -> URL:
        return f"{self.parent.api_url}/{self.name}"

    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name

    @property
    def rec_id(self) -> str:
        """Get parent ID.

        Returns
        -------
        str
            parent ID.
        """
        return self.parent.rec_id

    @property
    def bucket_url(self):
        """Get URL for new API file bucket.

        Returns
        -------
        str
            File bucket to ``put`` files.
        """
        return self.parent.bucket_url

    def info(self, **params) -> JSONResponse:
        """Get information on a file.

        Returns
        -------
        JSONResponse
            File info.
        """
        return _check(
            requests.get(
                self.api_url,
                params={**params, "access_token": self.api_key},
            ),
            f"getting {self.name} file info from record {self.rec_id}",
        )

    def update(self, file: Path, **params) -> JSONResponse:
        """Replace a file on a record.

        Parameters
        ----------
        file
            Source file to upload.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        data = {"name": f"{file.name}"}
        header = {"Content-Type": "application/json"}
        return _check(
            requests.put(
                self.api_url,
                params={**params, "access_token": self.api_key},
                data=json.dumps(data),
                headers=header,
            ),
            f"updating {self.name} in record {self.rec_id}",
        )

    def download(self, dest: Path = Path(), **params) -> JSONResponse:
        """Download a file from a record.

        Parameters
        ----------
        dest
            Folder to write files to.

        Returns
        -------
        JSONResponse
            Status of operation.

        Raises
        ------
        OSError
            If destination exists and is not a directory.
        """
        info = self.info().json()
        link = info["links"]["download"]
        filename = info["filename"]

        request = _check(
            requests.get(link, params={**params, "access_token": self.api_key}),
            f"downloading file {self.name} from record {self.rec_id}",
        )

        dest = Path(dest)
        if dest.is_file():
            raise OSError(f"{dest} is a file which exists. Must be a directory.")

        if not dest.isdir():
            dest.mkdir(parents=True, exist_ok=True)

        with (dest / filename).open("wb") as out_file:
            out_file.write(request.content)

        return request

    def delete(self, **params) -> JSONResponse:
        """Delete this file from the record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.delete(
                f"{self.api_url}",
                params={**params, "access_token": self.api_key},
            ),
            f"deleting file {self.name} from record {self.rec_id}",
        )

    def upload(self, file: Path, **params) -> JSONResponse:
        """Upload a file to a record.

        Parameters
        ----------
        file
            Path to sourcefile to upload.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        file = Path(file)

        with file.open("rb") as in_file:
            return _check(
                requests.put(
                    f"{self.bucket_url}/{self.name}",
                    params={**params, "access_token": self.api_key},
                    data=in_file,
                ),
                f"Uploading file {self.name} to record {self.rec_id}",
            )


class _Files(_SubCommandHandler):
    """Handler for files within a record."""

    @property
    def api_url(self) -> URL:
        return f"{self.parent.api_url}/files"

    def __init__(self, parent):
        super().__init__(parent)

    @property
    def rec_id(self) -> str:
        """Get record ID.

        Returns
        -------
        str
            Record ID.
        """
        return self.parent.rec_id

    @property
    def bucket_url(self) -> str:
        """Get URL for new API file bucket.

        Returns
        -------
        str
            File bucket to ``put`` files.
        """
        return self.parent.bucket_url

    def __getitem__(self, name) -> _File:
        return _File(self, name)

    def list(self, **params) -> JSONResponse:
        """Get information about all files in record.

        Parameters
        ----------
        **params
            Extra params for requests.

        Returns
        -------
        JSONResponse
            Information about operation state.
        """
        return _check(
            requests.get(
                self.api_url,
                params={**params, "access_token": self.api_key},
            ),
            f"listing record {self.rec_id} files",
        )

    def sort(self, sorted_ids: dict[str, str], **params) -> JSONResponse:
        """Re-order files in record.

        Parameters
        ----------
        sorted_ids
            IDs of re-sorted files.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.put(
                self.api_url,
                params={**params, "access_token": self.api_key},
                data=json.dumps(sorted_ids),
                headers={"Content-Type": "application/json"},
            ),
            f"sorting files for record {self.rec_id}",
        )

    def upload(self, files: dict[str, Path], **params) -> JSONResponse:
        """Upload a set of files to a record.

        Parameters
        ----------
        files
            Dictionary where the key is the name for the repo,
            and the value is a path to the file to upload.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        request_list = []
        for name, file in files.items():
            file = Path(file)
            request_list.append(
                _check(
                requests.post(
                    self.api_url,
                    params={**params, "access_token": self.api_key},
                    data=json.dumps([{"key": name}]),
                    headers={"Content-Type": "application/json"},

                ),
                f"starting draft file upload for record {self.rec_id}",
                ),
            )

            with file.open("rb") as curr_file:
                request_list.append(
                    _check(
                        requests.put(
                            f"{self.api_url}/{name}/content",
                            params={**params, "access_token": self.api_key},
                            data=curr_file,
                            headers={"Content-Type": "application/octet-stream"},
                        ),
                        f"uploading file {name} content to record {self.rec_id}",
                    ),
                )

                request_list.append(
                    _check(
                        requests.post(
                            f"{self.api_url}/{name}/commit",
                            params={**params, "access_token": self.api_key},
                            headers={"Content-Type": "application/application/json"},
                        ),
                        f"committing file {name} to record {self.rec_id}",
                    ),
                )

        return request_list

    def download(self, dest: Path, **params) -> JSONResponse:
        """Download all files from record.

        Parameters
        ----------
        dest
            Folder in which to write downloaded files.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        request = self.list(**params).json()
        files = {file["id"]: file["filename"] for file in request}

        for file in files.values():
            self[file].download(dest, **params)


class _Draft(_SubCommandHandler):
    """Draft handler."""

    @property
    def api_url(self) -> URL:
        return f"{self.parent.url}/records/{self.rec_id}/draft"

    def __init__(self, parent, rec_id):
        super().__init__(parent)
        self.rec_id = rec_id

    @property
    def files(self) -> _Files:
        """Get files container for this record.

        Returns
        -------
        _Files
            File handler.
        """
        return _Files(self)

    @cached_property
    def bucket_url(self):
        """Get URL for new API file bucket.

        Returns
        -------
        str
            File bucket to ``put`` files.
        """
        return self.get()

    def get(self, **params) -> JSONResponse:
        """Get information about draft record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        request = _check(
            requests.get(
                f"{self.parent.url}/records/{self.rec_id}/draft",
                params={**params, "access_token": self.api_key},
            ),
            f"getting record {self.rec_id}",
        )
        self.bucket_url = request
        return request

    def update(self, data: object, **params) -> JSONResponse:
        """Update draft record information.

        Parameters
        ----------
        data
            Data to be json dumped.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.put(
                f"{self.parent.url}/records/{self.rec_id}/draft",
                params={**params, "access_token": self.api_key},
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            ),
            f"updating record {self.rec_id}",
        )

    def delete(self, **params) -> JSONResponse:
        """Delete draft record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.delete(
                f"{self.parent.url}/records/{self.rec_id}/draft",
                params={**params, "access_token": self.api_key},
            ),
            f"deleting record {self.rec_id}",
        )
    
    
    def bind(self, community_slug: str, **params) -> JSONResponse:
        """Bind a draft record to a community

        Parameters
        ----------
        community_slug
            Name of the community to bind the draft record to.

        Returns
        -------
        JSONResponse
            Status of operation.
        """

        response = _check(
            requests.get(
                f"{self.url}/communities/{community_slug}"
                ),
                f"getting the ID for {community_slug} community",
            )
        community_id = response["id"]

        return _check(
            requests.put(
                f"{self.url}/records/{self.rec_id}/draft/review",
                params={**params, "access_token": self.api_key},
                json={
                    "receiver": {
                        "community": f"{community_id}"
                    },
                    "type": "community-submission"
                },
            ),
            f"binding draft record {self.rec_id} to community {community_slug} with ID {community_id}",
            ),

    def publish(self, **params) -> JSONResponse:
        """Publish draft record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                f"{self.parent.url}/records/{self.rec_id}/draft/actions/publish",
                params={**params, "access_token": self.api_key},
            ),
            f"publishing record {self.rec_id}",
        )


class _Record(_SubCommandHandler):
    """Record handler."""

    @property
    def api_url(self) -> URL:
        return f"{self.parent.api_url}/{self.rec_id}"

    def __init__(self, parent, rec_id):
        super().__init__(parent)
        self.rec_id = rec_id

    @property
    def files(self) -> _Files:
        """Get files container for this record.

        Returns
        -------
        _Files
            File handler.
        """
        return _Files(self)

    @cached_property
    def bucket_url(self):
        """Get URL for new API file bucket.

        Returns
        -------
        str
            File bucket to ``put`` files.
        """
        return self.get()["links"]["self"] #["bucket"]

    def get(self, **params) -> JSONResponse:
        """Get information about record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        request = _check(
            requests.get(
                self.api_url,
                params={**params, "access_token": self.api_key},
            ),
            f"getting record {self.rec_id}",
        )
        self.bucket_url = request["links"]["self"] #["bucket"]
        return request

    def update(self, data: object, **params) -> JSONResponse:
        """Update record information.

        Parameters
        ----------
        data
            Data to be json dumped.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.put(
                self.api_url,
                params={**params, "access_token": self.api_key},
                data=json.dumps(data),
                headers={"Content-Type": "application/json"},
            ),
            f"updating record {self.rec_id}",
        )

    def delete(self, **params) -> JSONResponse:
        """Delete record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.delete(
                self.api_url,
                params={**params, "access_token": self.api_key},
            ),
            f"deleting record {self.rec_id}",
        )

    def publish(self, **params) -> JSONResponse:
        """Publish record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                f"{self.api_url}/actions/publish",
                params={**params, "access_token": self.api_key},
            ),
            f"publishing record {self.rec_id}",
        )

    def edit(self, **params) -> JSONResponse:
        """Edit record details.
        Edit a published record (Create a draft record from a published record)

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                f"{self.parent.url}/records/{self.rec_id}/draft",
                params={**params, "access_token": self.api_key},
            ),
            f"editing record {self.rec_id}",
        )

    def discard(self, **params) -> JSONResponse:
        """Discard record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                f"{self.api_url}/actions/discard",
                params={**params, "access_token": self.api_key},
            ),
            f"discarding record {self.rec_id}",
        )

    def new_version(self, **params) -> JSONResponse:
        """Push new version of record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                f"{self.api_url}/actions/newversion",
                params={**params, "access_token": self.api_key},
            ),
            f"setting new version for record {self.rec_id}",
        )


class _AllRecords(_SubCommandHandler):
    @property
    def api_url(self):
        return f"{self.url}/records"

    def __getitem__(self, rec_id) -> _Record:
        return _Record(self, rec_id)

    def get(self, rec_id, **params) -> JSONResponse:
        """Get information about specific record on depository.

        Parameters
        ----------
        rec_id
            ID of record to look up.
        **params
            Extra params for requests.

        Returns
        -------
        JSONResponse
            Information about operation state.
        """
        return _check(
            requests.get(
                f"{self.api_url}/{rec_id}",
                params={**params, "access_token": self.api_key},
            ),
            f"getting record {rec_id}",
        )
    
    def draft(self, rec_id, **params) -> _Draft:
        """Get information about specific record on depository.

        Parameters
        ----------
        rec_id
            ID of record to look up.
        **params
            Extra params for requests.

        Returns
        -------
        JSONResponse
            Information about operation state.
        """
        response =  _check(
            requests.get(
                f"{self.api_url}/{rec_id}/draft",
                params={**params, "access_token": self.api_key},
            ),
            f"getting record {rec_id}",
        )
        return _Draft(self, response["id"])

    def create(self, **params) -> _Draft:
        """Create new empty record.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        response = _check(
            requests.post(
                f"{self.url}/records",
                params={**params, "access_token": self.api_key},
                json={},
                headers={"Content-Type": "application/json"},
            ),
            "creating record",
        )
        return _Draft(self, response["id"])

    def list(self, **params) -> JSONResponse:
        """Get information about all records on depository.

        Parameters
        ----------
        **params
            Extra params for requests.

        Returns
        -------
        JSONResponse
            Information about operation state.
        """
        return _check(
            requests.get(
                self.api_url,
                params={**params, "access_token": self.api_key},
            ),
            "listing records",
        )


class _Repository(_AllRecords):
    @property
    def api_url(self):
        return f"{self.parent.url}/deposit/depositions"


class _Licenses(_SubCommandHandler):
    @property
    def api_url(self):
        return f"{self.url}/licenses"

    def get(self, lic_id, **params) -> JSONResponse:
        """Get information about specific license on depository.

        Parameters
        ----------
        lic_id
            ID of license to look up.
        **params
            Extra params for requests.

        Returns
        -------
        JSONResponse
            Information about operation state.
        """
        return _check(
            requests.get(
                f"{self.api_url}/{lic_id}",
                params={**params, "access_token": self.api_key},
            ),
            f"getting license {lic_id}",
        )

    def list(self, **params) -> JSONResponse:
        """Get information about all licenses on depository.

        Parameters
        ----------
        **params
            Extra params for requests.

        Returns
        -------
        JSONResponse
            Information about operation state.
        """
        return _check(
            requests.get(
                self.api_url,
                params={**params, "access_token": self.api_key},
            ),
            "listing licenses",
        )


class InvenioRepository:
    """Handler for Invenio-like repositories.

    Handles pushing info to e.g. Zenodo

    Parameters
    ----------
    url
        Repository URL.
    api_key : str
        API key with appropriate permissions.
    is_zenodo : bool
        Whether to use `deposition` interface or `records` interface.

    Examples
    --------
    .. code-block::

        my_repo = InvenioRepository(url="companyname.website", api_key="abc123")
        my_repo.depositions["my_repo"].files["file"].upload(my_file)
        my_repo.records.get()
        my_repo.licenses.list()
    """

    def __init__(self, url: str, api_key: str, *, is_zenodo: bool = False):
        self.url = url.strip("/").removesuffix("/api") + "/api"
        self.api_key = api_key

        self.depositions = _Repository(self) if is_zenodo else _AllRecords(self)
        self.licenses = _Licenses(self)
