import os
import json
import re
from fs.copy import copy_fs
from fs.errors import ResourceNotFound


def _normalize(name):
    """Clean up the names."""
    if name is None:
        return None
    clean = re.sub(r'[-_/\s]+', '_', name.strip())
    return clean.lower()


def _make_file_name(tablename, prefix, suffix):
    return prefix + _normalize(tablename) + suffix + '.json'


def write_to_file(downloadtable, tmpfs, prefix='', suffix='', fields=dict()):
    """
    Write out the table data to a file.

    :param downloadtable: A `download.DownloadTable` object for the table to be saved
    :param tmpfs: the temporary filesystem (from pyfilesystem2) to write the
            file to.
    :param prefix: A prefix for a the file name. include a / for directories
    :param suffix: A suffix to append to the file name
    :param fields: a dict of the fields and type of data in the field for easier restoring.
    """
    data = list(downloadtable.download())
    filename = _make_file_name(downloadtable.table_name, prefix, suffix)
    if '/' in prefix:
        tmpfs.makedir(prefix)
    tagged_data = {
        'table_name': downloadtable.table_name,
        'fields': fields,
        'data': data
    }
    with tmpfs.open(filename, 'w') as outfile:
        json.dump(tagged_data, outfile, indent=2)


def join_files(tmpfs, outfs):
    """
    Join the backup json files into a single package (tarball, zip).

    :param tmpfs: the temporary fs where the backup is stored.
    :param outfs: the filesystem to copy to (should be `TarFS` or `ZipFS`). things
            like compression and encoding should be specified at instantiation.
    """
    copy_fs(tmpfs, outfs)
    outfs.close()


def write_out_backup(backing_store_fs, *, filepath=None, filesystem=None,
                     prefix=''):
    """
    Write the backup data to its final location. A backing store is required
    and either a filepath to the packaged backup or the tmp filesystem is required.

    :param required backing_store_fs: a pyfilesystem2 object to be the final storage
            location of the backup. (should be `OSFS`, `S3FS`, `FTPFS`, etc.)
            Can be a single object or list of filesystem objects for copying to
            multiple backing stores.

    :param filepath: path to the zip or tar file containing the backup data (if
            desired). Can be a path object or str.

    :param filesystem: the `TmpFS` containing the backup data.
    :param prefix: a parent directory for the files to be saved under.
            This is can be a good place to encode some information about the
            backup. A slash will be appended to the prefix to create
            a directory or pseudo-directory structure.
    """
    if prefix and not prefix[-1] == '/':
        prefix = prefix + '/'
    if not isinstance(backing_store_fs, list):
        backing_store_fs = [backing_store_fs]
    if filepath:
        name = os.path.basename(filepath)
        for backing_fs in backing_store_fs:
            # read outfile directly from infile
            with backing_fs.open(prefix + name, 'w') as outfile:
                with open(filepath, 'r') as infile:
                    outfile.write(infile.read())
    elif filesystem:
        for backing_fs in backing_store_fs:
            if prefix:
                try:
                    backing_fs.opendir(prefix)
                except ResourceNotFound:
                    backing_fs.makedir(prefix)
                copy_fs(filesystem, backing_fs.opendir(prefix))
            else:
                copy_fs(filesystem, backing_fs)
    else:
        raise AttributeError("filepath or filesystem is required.")
