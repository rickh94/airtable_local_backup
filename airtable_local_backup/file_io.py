import os
import boto3
import json
from pathlib import Path
import hashlib
import tempfile


def make_file_name(tablename, prefix, suffix):
    return prefix + tablename + suffix + '.json'


def write_to_file(downloadtable, directory=None, prefix='', suffix=''):
    """
    Write out the table data to a file.
    Arguments:
        downloadtable: A DownloadTable object for the table to be saved
        directory: the directory in which to save the file
        prefix: A prefix for a the file name
        suffix: the suffix to append to the file name
    """
    data = list(dowloadtable)
    filename = make_file_name(downloadtable.table_name, prefix, suffix)
    if directory:
        os.makedirs(directory, exist_ok=True)
        path = Path(directory, filename)
    else:
        path = Path(filename)

    with open(path, 'w') as outfile:
        json.dump(data, outfile)


def put_to_s3(tabledata, bucket, prefix='', suffix='', encryption='AES256',
              storage_class='STANDARD-IA'):
    """
    Upload the tabledata as an object to s3.
    Arguments:
        downloadtable: A DownloadTable object for the the table to be uploaded
        bucket: the s3 bucket to upload to
        prefix: the prefix to add to the object. include / for "folders"
        suffix: the suffix to append to the filename
    """
    data = list(downloadtable)
    key = make_file_name(downloadtable.table_name, prefix, suffix)
    s3 = boto3.client('s3')
    extra_args = {
        'StorageClass': storage_class,
        'ServerSideEncryption': encryption
    }
    with tempfile.TemporaryFile() as f:
        json.dump(data, f)
        f.seek(0)
        s3.upload_fileobj(f, bucket, key, ExtraArgs=extra_args)
