CLI Usage
=========

``data_collections_api`` provides a few commandline tools for
simplifying the process of uploading or verifying data.

data_collections
----------------

``data_collections`` is the general top-level interface to the
tools. These tools are implemented as sub-parsers within the main
module.

upload
******

Construct a set of data and upload a set of files along with the metadata to an
Invenio repository.

validate
********

Validate the metadata file for a dataset before uploading.

dump
****

Dump a template metadata file ready for modification to upload.


upload_record
-------------
