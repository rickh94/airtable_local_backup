import datetime
import os

from ruamel.yaml import YAML
import fs
from fs import tempfs
from fs import tarfs
from fs import zipfs
from fs.errors import CreateFailed
from fs_s3fs import S3FS

from .download import DownloadTable
from . import file_io
from . import exceptions
from . import __docurl__


class Runner(object):
    """
    This class handles orchestration of downloading and storing the backup.
    Options are set in a yaml configuration file. There is an
    :download:`example <./sample-config.yaml>` you can use as a
    starting point.

    :param path: (required) absolute path to the file on the system or relative to
        the FS object supplied in the filesystem parameter
    :param filesystem: (keyword only) a pyfilesystem2 FS object where the yaml config
        file is located.
    """
    def __init__(self, path, *, filesystem=None):
        yaml = YAML()
        if not filesystem:
            filesystem = fs.open_fs('/')
        with filesystem.open(str(path), 'r') as configfile:
            self.config = yaml.load(configfile)
        self.tmp = tempfs.TempFS()

    def _create_backup_tables(self):
        for table in self.config['Tables']:
            try:
                base = _get_from_env(self.config['Airtable Base Key'])
                api_key = _get_from_env(self.config['Airtable API Key'])
                yield DownloadTable(
                    base_key=base,
                    table_name=table['Name'],
                    api_key=api_key,
                    compression=self.config['Attachments']['Compress'],
                    fields=table.get('Fields', dict()),
                    discard_attach=self.config['Attachments']['Discard'],
                )
            except KeyError as err:
                _config_error(err)

    def _save_tables(self):
        for table in self._create_backup_tables():
            file_io.write_to_file(table, self.tmp)

    def _package(self, outfile):
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        if self.config['Store As']['Type'].lower() == 'tar':
            savefs = tarfs.TarFS(
                outfile, write=True,
                compression=self.config['Store As']['Compression']
            )
        elif self.config['Store As']['Type'].lower() == 'zip':
            savefs = zipfs.ZipFS(outfile)
        else:
            _config_error("Store AS: Type is invalid")
        file_io.join_files(self.tmp, savefs)

    def backup(self):
        """
        Using the configuration from the file, create the backup.
        :return: None
        """
        self._save_tables()
        outfile = None
        try:
            if self.config['Store As']['Type'] != 'files':
                outfile = self.config['Store As']['Path']
                self._package(outfile)
        except KeyError as err:
            _config_error(err)
        try:
            outfs = self._configure_backing_store()
            prefix = self.config['Backing Store'].get('Prefix', '')
            if self.config['Backing Store'].get('Date', False):
                date = datetime.datetime.today().isoformat()
                if prefix:
                    prefix = date + '-' + prefix
                else:
                    prefix = date
        except KeyError as err:
            _config_error(err)
        if outfile:
            file_io.write_out_backup(
                backing_store_fs=outfs,
                filepath=outfile,
                prefix=prefix,
            )
        else:
            file_io.write_out_backup(
                backing_store_fs=outfs,
                filesystem=self.tmp,
                prefix=prefix
            )

    def _configure_backing_store(self):
        try:
            bs = self.config['Backing Store']
            if 'Type' in bs:
                for key, item in bs.items():
                    bs[key] = _get_from_env(item)
                if bs['Type'].lower() == 's3':
                    return S3FS(
                        bs['Bucket'],
                        strict=False,
                        aws_access_key_id=bs.get('Key ID', None),
                        aws_secret_access_key=bs.get('Secret Key', None),
                        endpoint_url=bs.get('Endpoint URL', None)
                    )
            else:
                return fs.open_fs(bs['URI'], create=True)
        except (KeyError, OSError, CreateFailed) as err:
            _config_error(err)


def _config_error(err=''):
    raise exceptions.ConfigurationError(
        "Options are missing in the configuration file. "
        f"Please consult the docs at {__docurl__}.\n"
        f"{err}")


def _get_from_env(item):
    if item is None:
        return None
    try:
        if item[0] == '$':
            return os.environ[item[1:]]
    except TypeError:
        pass
    return item
