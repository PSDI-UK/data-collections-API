CLI Usage
=========

``data_collections_api`` provides a few command-line tools for simplifying the process of uploading
or verifying data and metadata.

data_collections
----------------

.. program:: data_collections
.. describe:: data_collections

   .. option:: operation {validate,template,dump,upload}

      .. option:: validate

         Validate metadata

      .. option:: template
      .. option:: dump

         Dump a template file.

      .. option:: `upload`

         Upload a dataset to an invenio repository.

   .. option:: -V, --version

      Show program's version number and exit.

``data_collections`` is the general top-level interface to the tools. These tools are implemented as
sub-parsers within the main module.

.. admonition:: Running ``data_collections``

   By default, if the ``data_collections_api`` package is installed, ``data_collections`` is
   installed as an executable script on your main ``PATH``. In general, this is the main entry
   point.

   If that is not desired, it is possible to run ``data_collections`` through the python module
   system::

     python -m data_collections_api

   where the ``data_collections_api`` **module** (folder) is on the current ``sys.path`` (by being
   installed, in the current ``PYTHONPATH`` or being in the current working directory.)::

     PYTHONPATH=/path/containing/data_collections_api python -m data_collections_api

   Throughout the rest of this page, we will assume ``data_collections`` is used as the main
   entrypoint.


.. _upload:

upload
******

.. program:: data_collections upload
.. describe:: data_collections upload

   .. option:: --api-url URL

      URL for the API associated with the Invenio repository, e.g.
      https://data-collections-staging.psdi.ac.uk/api

   .. option:: --api-key str

      Your API key/token for accessing the Invenio repository instance.

   .. option:: --metadata-path file

      File path to the yaml file containing the metadata to upload a record to an Invenio
      repository, e.g.  path/to/files/record.yaml

   .. option:: -f {json,yaml}, --metadata-format {json,yaml}

      Parse metadata file as this type (default: yaml).

   .. option:: --files FILES [FILES ...]

      List of file paths associated with the record to be uploaded, e.g. path/to/files/data.*

   .. option:: --community str

      Name of a Invenio repository community to upload the record to, e.g. biosimdb,
      data-to-knowledge, etc.


``data_collections_api`` can take your data and metadata and automatically upload it to the Invenio
repository. To do so, you need to have some information at hand:

- The URL of the repository you wish to upload the data to. In the case of PSDI data, this will
  often be https://data-collections.psdi.ac.uk.
- Your API key (also called a Personal Access Token or PAT) for the repository to give permissions
  to write and upload data.
- A metadata file detailing the data relating to the files (see :doc:`schemas/index`).
- The files ready to upload.

With all this prepared, uploading the data is as simple as:

.. code-block:: console

   data_collections upload --api-url https://data-collections.psdi.ac.uk --api-key 1234567890abcdef --metadata-path /path/to/metata_file.yaml --files FILE1 FILE2 --community my_community

.. note::

   Since this is a common operation it is also available as the standalone :option:`upload_record`

.. _validate:

validate
********

.. program:: data_collections validate

.. describe:: data_collections validate

   .. option:: FILE

      File to validate.

   .. option:: -f {json,yaml}, --format {json,yaml}

      Parse :option:`FILE` as this type (default: determine from suffix).

   .. option:: -S SCHEMA, --schema SCHEMA

      Validate against the given schema (default: :doc:`base`)

Validate the metadata file for a dataset before uploading.

``data_collections_api`` can validate your metadata file against the schema to verify the contents
of the file match what is required to make a valid upload.

.. note::

   The validator does not verify most data itself, you must ensure that all entries are spelled and
   written correctly.

To validate a data file simply run:

.. code-block:: console

   data_collections validate [file]

e.g.

.. code-block:: console

   data_collections validate examples/biosim_record.yaml

The file can be either in ``json`` or ``yaml`` formats (see: :doc:`schema`). :option:`data_collections validate` will attempt to determine the
appropriate format from the file extension, but this can be specified explicitly with the ``-f``
flag.

.. code-block:: console

   data_collections validate -f json examples/biosim_record.yaml

.. note::

   The above will raise an error since the file is not in ``json`` format.

dump
****

.. program:: data_collections template
.. describe:: data_collections template
.. describe:: data_collections dump

   .. option:: FILE

      File to dump.

   .. option:: -f {json,yaml}, --format {json,yaml}

      Dump :option:`FILE` as this type (default: determine from suffix).

``data_collections_api`` provides a method to quick-start building metadata, ``template`` will dump
an example metadata file for a particular community and data-type (though currently only a basic
example is available).  To do so, simply run

.. code-block:: console

   data_collections dump my_metadata.yaml

You can then edit and modify this template to fill in the data needed.


upload_record
-------------

.. program:: upload_record
.. describe:: upload_record

   .. option:: --api-url URL

      URL for the API associated with the Invenio repository, e.g.
      https://data-collections-staging.psdi.ac.uk/api

   .. option:: --api-key str

      Your API key/token for accessing the Invenio repository instance.

   .. option:: --metadata-path file

      File path to the yaml file containing the metadata to upload a record to an Invenio
      repository, e.g.  path/to/files/record.yaml

   .. option:: -f {json,yaml}, --metadata-format {json,yaml}

      Parse metadata file as this type (default: yaml).

   .. option:: --files FILES [FILES ...]

      List of file paths associated with the record to be uploaded, e.g. ``path/to/files/data.*``

   .. option:: --community str

      Name of a Invenio repository community to upload the record to, e.g. biosimdb,
      data-to-knowledge, etc.


One-stop tool to upload a record to the repository, see `upload`_.

.. _pat_guide: ...
