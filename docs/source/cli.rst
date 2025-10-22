CLI Usage
=========

``data_collections_api`` provides a few command-line tools for simplifying the process of uploading
or verifying data and metadata.

data_collections
----------------

``data_collections`` is the general top-level interface to the tools. These tools are implemented as
sub-parsers within the main module.

.. admonition:: Running ``data_collections``

   By default, if the ``data_collections_api`` package is installed, ``data_collections`` is
   installed as an executable script on your main ``PATH``. In general, this is the main entry
   point.

   If that is not desired, it is possible to run ``data_collections`` through the python module
   system::

     python -m data_collections_api

   where the ``data_collections_api`` **module** (folder) is on the current ``sys.path`` (by being installed, in
   the current ``PYTHONPATH`` or being in the current working directory.)::

     PYTHONPATH=/path/containing/data_collections_api python -m data_collections_api

   Throughout the rest of this page, we will assume ``data_collections`` is used as the main entrypoint.

upload
******

  Construct a set of data and upload a set of files along with the metadata to an Invenio repository.

``data_collections_api`` can take your data and metadata and automatically upload it to the Invenio
repository. To do so, you need to have some information at hand:

- The URL of the repository you wish to upload the data to. In the case of PSDI data, this will
  often be https://data-collections.psdi.ac.uk.
- Your API key (also called a Personal Access Token or PAT, see `pat_guide`_ for how to create
  this.) for the repository to give permissions to write and upload data.
- A metadata file detailing the data relating to the files (see `template`_).
- The files ready to upload.

With all this prepared, uploading the data is as simple as:

::

   data_collections upload --api-url https://data-collections.psdi.ac.uk --api-key 1234567890abcdef --metadata-path /path/to/metata_file.yaml --files FILE1 FILE2 --community my_community

.. note::

   Since this is a common operation it is also available as the standalone ``upload_record``

validate
********

  Validate the metadata file for a dataset before uploading.

``data_collections_api`` can validate your metadata file against the schema to verify the contents
of the file match what is required to make a valid upload.

.. note::

   The validator does not verify most data itself, you must ensure that all entries are spelled and
   written correctly.

To validate a data file simply run:

::

   data_collections validate [file]

e.g.

::

   data_collections validate examples/biosim_record.yaml

The file can be either in ``JSON`` or ``YAML`` formats. ``validate`` will attempt to determine the
appropriate format from the file extension, but this can be specified explicitly with the ``-f``
flag.

::

   data_collections validate -f json examples/biosim_record.yaml

.. note::

   The above will raise an error since the file is not in ``json`` format.

template
********

  Dump a template metadata file ready for modification to upload.

``data_collections_api`` provides a method to quick-start building metadata, ``template`` will dump
an example metadata file for a particular community and data-type (though currently only a basic
example is available).  To do so, simply run::

   data_collections dump my_metadata

You can then edit and modify this template to fill in the data needed.

.. _pat_guide: ...
