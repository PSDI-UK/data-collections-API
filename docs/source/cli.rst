CLI Usage
=========

``data_collections_api`` provides a few commandline tools for
simplifying the process of uploading or verifying data.

data_collections
----------------

.. code-block:: text

   usage: data_collections [-h] [-V] {validate,template,dump,upload} ...

   Single-utility API for data handling with remote depositories.

   positional arguments:
     {validate,template,dump,upload}
       validate            Validate metadata
       template (dump)     Dump a template file.
       upload              Upload a dataset to an invenio repository.

   options:
     -h, --help            show this help message and exit
     -V, --version         show program's version number and exit

``data_collections`` is the general top-level interface to the
tools. These tools are implemented as sub-parsers within the main
module.


upload
******

Construct a set of data and upload a set of files along with the metadata to an
Invenio repository. This is an alias for ``upload_record``.

validate
********

.. code-block:: text

   usage: data_collections validate [-h] [-f {json,yaml}] file

   Validate a metadata file or string.

   positional arguments:
     file                  File to validate

   options:
     -h, --help            show this help message and exit
     -f, --format {json,yaml}
                           Parse FILE as this type (default: determine from
                           suffix).

Validate the metadata file for a dataset complies with the schema before uploading. See `schema`__ for details on a valid metadata file.

dump
****

.. code-block:: text

   usage: data_collections template [-h] [-f {json,yaml}] file

   Dump a file template to file.

   positional arguments:
     file                  File to write

   options:
     -h, --help            show this help message and exit
     -f, --format {json,yaml}
                           Parse FILE as this type (default: determine from
                           suffix).


Dump a template metadata file ready for modification to upload.


upload_record
-------------

.. code-block:: text

   usage: upload_record [-h] --api-url URL --api-key str --metadata-path file
                        [-f {json,yaml}] [--files FILES [FILES ...]] [--community str]

   Upload records to Invenio repository

   options:
     -h, --help            show this help message and exit
     --api-url URL         URL for the API associated with the Invenio repository, e.g.
                           https://data-collections-staging.psdi.ac.uk/api
     --api-key str         Your API key/token for accessing the Invenio repository
                           instance.
     --metadata-path file  File path to the yaml file containing the metadata to upload
                           a record to an Invenio repository, e.g.
                           path/to/files/record.yaml
     -f {json,yaml}, --metadata-format {json,yaml}
                           Parse metadata file as this type (default: yaml).
     --files FILES [FILES ...]
                           List of file paths associated with the record to be
                           uploaded, e.g. path/to/files/data.*
     --community str       Name of a Invenio repository community to upload the record
                           to, e.g. biosimdb, data-to-knowledge, etc.


One-stop tool to upload a record to the repository. This requries that you have already defined your metadata file (see ``dump`` and ``validate``) and got an API key (see: PSDI Invenio docs on how to get this)
