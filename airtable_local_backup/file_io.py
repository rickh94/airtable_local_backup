import os
import boto3
import json
import re
from pathlib import Path
import hashlib
import tempfile
from fs.copy import copy_fs
from fs.errors import ResourceNotFound


def _normalize(name):
    """Clean up the names."""
    if name is None:
        return None
    clean = re.sub(r'[-_\s]+', '_', name.strip())
    return clean.lower()


def _make_file_name(tablename, prefix, suffix):
    return prefix + _normalize(tablename) + suffix + '.json'


def _write_to_file(downloadtable, tmpfs, prefix='', suffix=''):
    """
    Write out the table data to a file.
    Arguments:
        downloadtable: A DownloadTable object for the table to be saved
        filesystem: the temporary filesystem (from pyfilesystem2) to write the
            file to.
        prefix: A prefix for a the file name. include a / for directories
        suffix: the suffix to append to the file name
    """
    data = list(downloadtable.download_table())
    filename = _make_file_name(downloadtable.table_name, prefix, suffix)
    if '/' in prefix:
        tmpfs.makedir(prefix)
    tagged_data = {
        'table_name': downloadtable.table_name,
        'data': data
    }
    with tmpfs.open(filename, 'w') as outfile:
        json.dump(tagged_data, outfile, indent=2)


def _join_files(tmpfs, outfs):
    """
    Join the files into a single file (tarball, zip).
    Arguments:
        tmpfs: the temporary fs where the backup is stored.
        outfs: the filesystem to copy to (should be tarfs or zipfs). things
            like compression and encoding should be specified at instanciation.
    """
    copy_fs(tmpfs, outfs)


def _write_out_backup(backing_store_fs, *, filepath=None, filesystem=None,
                      prefix=''):
    """
    Write the backup data to its final backing store
    Arguments:
        backing_store_fs: a pyfilesystem2 object to be the final storage
            location of the backup. should be OSFS, S3FS, FTPFS, etc.
            can be a single object or list of filesystem objects for copying to
            multiple backing stores.
        filepath: path to the zip or tar file containing the backup data (if
            desired). Can be a path object or str
        filesystem: the tmpfs containing the backup data.
        prefix: a parent directory for the files to be saved under.
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
