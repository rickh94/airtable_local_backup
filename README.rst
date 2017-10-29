Airtable Local Backup - IN PROGRESS
===================================
.. image:: https://travis-ci.org/rickh94/airtable_local_backup.svg?branch=master
    :target: https://travis-ci.org/rickh94/airtable_local_backup


.. image:: https://codecov.io/gh/rickh94/airtable_local_backup/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/rickh94/airtable_local_backup


The goal of this project is to provide an easy way to backup data from
Airtable without too much user intervention. (The current recommended
solution is download individual csv files and attachments and correlate them
manually. yuck.)

Goals
=====

With a simple yaml configuration file and this library, it should be possible to
download all table data (including attachments) and restore them to a new
airtable database.

A cli frontend is also possible once the library/api is complete.

Internals
=========

Airtable does not offer an quick offline backup solution, but they do offer
and decent REST API so that is what is used to download the table data.
Listing tables is not supported so they will need to be specified in a config
(yaml) file. Attachment files are downloaded, their data compressed
(optional), and base64 encoded and stored with their filename and a hash fo
the original data. The whole table is then serialized to json and dumped to a
file. *incomplete*

The json can be read and uploaded to a new database by the restore functions.
Airtable requires a public endpoint for files so temporary storage is
required. Currently s3 buckets are supported (NOTE: the bucket need not and should not be
public. A presigned url will be generated for airtable to download the file.)
I hope to also support digitalocean spaces. If no backing store is provided,
attachment data will be discarded (though still available in the backup).

Once json files are created for each table, they will be combined to a
zipfile or tar archive for storage. (If this is not desired, scripts can be
written to access other parts of the api.)

TODO
====

- Finish core API: mainly files. Download and upload are mostly working.
- Implement configuration file for database schema.
- Help restore database schema in some way, possbily blank-ish csvs with data
  type guesses based on downloaded data.


Long-Term Goals
===============

- Linked Records: Record linking will be tricky because restored bases will
  have different unique ids assigned to the records. It will require
  something like creating the whole database and then doing a second pass to
  create the links based on searches. Will probably be pretty hack-y.
- Data migration: Because the data is being serialzed to json, it shouldn't be too
  hard to go from that to loading it into another document database (tinydb,
  mongodb, dynamodb, etc.) or maybe even a SQL database (not sure.)

Contributing
============

If you are interested in using this, feel free to open an issue or a PR or
grab something off the todo and hack on it a little, or write a test for
existing code that isn't covered (please use pytest).
