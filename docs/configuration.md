# Configuration


## Getting Started


A great starting point is the [example configuration
    file](https://github.com/rickh94/airtable_local_backup/blob/master/docs/sample-config.yaml).


## What You'll Need
 * Your Airtable base key (If you go to the api documentation for your base,
   it's in the url ``https://api.airtable.com/v0/YOUR_BASE_KEY``. It is usually
   app then an alphanumeric string)
 * Your Airtable API key (This would be on your account page after enabling
   api access. (It is preferable to store this in the environment variable
   ``AIRTABLE_API_KEY`` rather than in the config file if possible). You may want to
   read more about the [Airtable API](https://airtable.com/api).
 * Somewhere to put the backups. This can be a local directory, S3 or S3
   compatible service, or [any builtin in filesystem of
   pyfilesystem2](https://docs.pyfilesystem.org/en/latest/builtin.html). If
   pyfilesystem2 has an extension for the filesystem you want to use, it
   should work but you will need to install the extension separately.

## Configuration File
There are several configuration options available:

* ``Base Name:`` This is just a reference name for the database, something you'll recognize.
* ``Airtable Base Key:`` *Required* (see above). This begins 'app' and then a bunch of numbers and letters.
* ``Airtable API Key:`` *Required* This will be stored in plain text, so it is better to save it in an environment
  variable ($AIRTABLE_API_KEY) and leave this ``null``.
* ``Store As:`` *Required* This is the configuration for storing the downloaded data.
    * ``Type:`` *Required* Store the files as a ``tar`` archive, ``zip`` file, or just as ``files``
    * ``Compression:`` This is available only with tar. Choose your favorite of ``xz``, ``bz2`` , or ``gz``.
    * ``Path:`` Where to put files on the system temporarily before writing out to the ``Backing Store``.
* ``Backing Store:`` Where to put the backups. See 
[sample config](https://github.com/rickh94/airtable_local_backup/blob/master/docs/sample-config.yaml) for more details.
    * ``Prefix:`` Something to prepend to the backup files
    * ``Date:`` (boolean) Whether to include the date on backup files
* ``Tables:`` This is the most important part of the config. Because of the nature of the Airtable API, you must
specify each table you want to back up and keep this up-to-date. 
    * ``- Name:`` Each table requires at minimum the name to be specified (precisely, case sensitive)
    * ``  Fields:`` You can specify the fields here for easier recovery (once implemented)
* ``Attachments:`` Currently attachments are downloaded, base64 encoded, and embedded into the json backup files. Other
solutions may be possible in the future
   * ``Discard:`` Set this to true to remove the attachments from the backups.
   * ``Compress:`` Whether to compress the attachments. Compression somewhat slows down backups, but can save quite
   a bit of disk space.