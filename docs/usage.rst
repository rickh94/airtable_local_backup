=======================
Configuration and Usage
=======================

A great starting point is the `example configuration
file <https://github.com/rickh94/airtable_local_backup/sample-config.yaml>`_.

You will also need:
 * Your Airtable base key (If you go to the api documentation for your base,
   it's in the url https://api.airtable.com/v0/YOUR_BASE_KEY. It is usually
   app then an alphanumeric string)
 * Your Airtable api key (This would be on your account page after enabling
   api access. (It is preferable to store this in the environment variable
   AIRTABLE_API_KEY rather than in the config file if possible)
 * Somewhere to put the backups. This can be a local directory, S3 or S3
   compatible service, or `any builtin in filesystem of
   pyfilesystem2 <https://docs.pyfilesystem.org/en/latest/builtin.html>`_. If
   pyfilesystem2 has an extension for the filesystem you want to use, it
   should work but you will need to install the extension separately.
