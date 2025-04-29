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
    def loc_id(self) -> str:
        """Get parent ID.

        Returns
        -------
        str
            parent ID.
        """
        return self.parent.loc_id

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
            f"getting {self.name} file info from deposition {self.loc_id}",
        )

    def update(self, file: Path, **params) -> JSONResponse:
        """Replace a file on a deposition.

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
            f"updating {self.name} in deposition {self.loc_id}",
        )

    def download(self, dest: Path = Path(), **params) -> JSONResponse:
        """Download a file from a deposition.

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
            f"downloading file {self.name} from deposition {self.loc_id}",
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
        """Delete this file from the deposition.

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
            f"deleting file {self.name} from deposition {self.loc_id}",
        )

    def upload(self, file: Path, **params) -> JSONResponse:
        """Upload a file to a deposition.

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
                f"Uploading file {self.name} to deposition {self.loc_id}",
            )


class _Files(_SubCommandHandler):
    """Handler for files within a deposition."""

    @property
    def api_url(self) -> URL:
        return f"{self.parent.api_url}/files"

    def __init__(self, parent):
        super().__init__(parent)

    @property
    def loc_id(self) -> str:
        """Get deposition ID.

        Returns
        -------
        str
            Deposition ID.
        """
        return self.parent.loc_id

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
        """Get information about all files in deposition.

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
            f"listing deposition {self.loc_id} files",
        )

    def sort(self, sorted_ids: dict[str, str], **params) -> JSONResponse:
        """Re-order files in deposition.

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
            f"sorting files for deposition {self.loc_id}",
        )

    def upload(self, files: dict[str, Path], **params) -> JSONResponse:
        """Upload a set of files to a deposition.

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

            with file.open("rb") as curr_file:
                request_list.append(
                    _check(
                        requests.put(
                            f"{self.bucket_url}/{name}",
                            params={**params, "access_token": self.api_key},
                            data=curr_file,
                        ),
                        f"Uploading file {self.name} to deposition {self.loc_id}",
                    ),
                )

        return request_list

    def download(self, dest: Path, **params) -> JSONResponse:
        """Download all files from deposition.

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


class _Deposition(_SubCommandHandler):
    """Deposition handler."""

    @property
    def api_url(self) -> URL:
        return f"{self.parent.api_url}/{self.loc_id}"

    def __init__(self, parent, loc_id):
        super().__init__(parent)
        self.loc_id = loc_id

    @property
    def files(self) -> _Files:
        """Get files container for this deposition.

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
        return self.get().json()["links"]["bucket"]

    def get(self, **params) -> JSONResponse:
        """Get information about deposition.

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
            f"getting deposition {self.loc_id}",
        )
        self.bucket_url = request.json()["links"]["bucket"]
        return request

    def create(self, **params) -> JSONResponse:
        """Create new empty deposition.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                self.parent.api_url,
                params={**params, "access_token": self.api_key},
                json={},
                headers={"Content-Type": "application/json"},
            ),
            "creating deposition",
        )

    def update(self, data: object, **params) -> JSONResponse:
        """Update deposition information.

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
            f"updating deposition {self.loc_id}",
        )

    def delete(self, **params) -> JSONResponse:
        """Delete deposition.

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
            f"deleting deposition {self.loc_id}",
        )

    def publish(self, **params) -> JSONResponse:
        """Publish deposition.

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
            f"publishing deposition {self.loc_id}",
        )

    def edit(self, **params) -> JSONResponse:
        """Edit deposition details.

        Returns
        -------
        JSONResponse
            Status of operation.
        """
        return _check(
            requests.post(
                f"{self.api_url}/actions/edit",
                params={**params, "access_token": self.api_key},
            ),
            f"editing deposition {self.loc_id}",
        )

    def discard(self, **params) -> JSONResponse:
        """Discard deposition.

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
            f"discarding deposition {self.loc_id}",
        )

    def new_version(self, **params) -> JSONResponse:
        """Push new version of deposition.

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
            f"setting new version for deposition {self.loc_id}",
        )


class _Repository(_SubCommandHandler):
    @property
    def api_url(self):
        return f"{self.url}/deposit/depositions"

    def __getitem__(self, loc_id: str) -> _Deposition:
        """Get specific deposition in repository (by id).

        Parameters
        ----------
        loc_id
            Depository ID.

        Returns
        -------
        _Deposition
            Deposition for further processing.
        """
        return _Deposition(self, loc_id)

    def list(self, **params) -> JSONResponse:
        """Get information about all depositions on depository.

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
            "listing depositions",
        )

class _AllRecords(_SubCommandHandler):
    @property
    def api_url(self):
        return f"{self.url}/records/"

    def __getitem__(self, rec_id) -> _Deposition:
        return _Deposition(self, rec_id)

    def get(self, rec_id, **params) -> JSONResponse:
        """Get information about specific record on depository.

        Parameters
        ----------
        rec_id
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
                f"{self.api_url}/{rec_id}",
                params={**params, "access_token": self.api_key},
            ),
            f"getting record {rec_id}",
        )

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
        self.url = url
        self.api_key = api_key

        self.depositions = _Repository(self) if is_zenodo else _AllRecords(self)
        self.licenses = _Licenses(self)
