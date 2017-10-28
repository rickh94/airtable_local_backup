from ruamel.yaml import YAML
import fs
from fs import tempfs
from fs import tarfs
from fs import zipfs
# from fs_s3fs import S3FS

from .download import DownloadTable
from . import file_io
from . import exceptions
from . import __docurl__


ERRMESS = ()


class Runner(object):
    def __init__(self, path, *, filesystem=None):
        """
        Pass in a path to get a config file. If the configuration is outside
        the local filesystem, pass in a pyfilesystem2 object to get the
        file from.
        Paths should be absolute.
        """
        yaml = YAML()
        if not filesystem:
            filesystem = fs.open_fs('/')
        with filesystem.open(path, 'r') as configfile:
            self.config = yaml.load(configfile)
        self.tmp = tempfs.TempFS()

    def _create_backup_tables(self):
        for table in self.config['Tables']:
            try:
                yield DownloadTable(
                    base_key=self.config['Airtable Base Key'],
                    table_name=table['Name'],
                    api_key=self.config['Airtable API Key'],
                    compression=self.config['Attachments']['Compress'],
                    fields=table.get('Fields', dict()),
                    discard_attach=self.config['Attachments']['Discard'],
                )
            except KeyError as err:
                raise exceptions.ConfigurationError(
                    "Options are missing in the configuration file. "
                    f"Please consult the docs at {__docurl__}.\n"
                    f"{err}")

    def _save_tables(self):
        for table in self._create_backup_tables():
            file_io.write_to_file(table, self.tmp)

    def _package(self, outfile):
        if self.config['Store As']['Type'].lower() == 'tar':
            savefs = tarfs.TarFS(outfile,
                                 write=True,
                                 compression=self.config['Store As']['Compression']
                                 )
        elif self.config['Store As']['Type'].lower() == 'zip':
            savefs = zipfs.ZipFS(outfile)
        else:
            raise exceptions.ConfigurationError(
                "Options are missing in the configuration file. "
                f"Please consult the docs at {__docurl__}.\n"
                f"Store As: Type is invalid")
        file_io.join_files(self.tmp, savefs)

    def backup(self):
        """
        Using the configuration from the file, create the backup.
        :return: None
        """
        self._save_tables()
        try:
            if self.config['Store As']['Type'] != 'files':
                outfile = self.config['Store As']['Path']
                self._package(outfile)
            else:
                outfile = None
        except KeyError as err:
            raise exceptions.ConfigurationError(
                "Options are missing in the configuration file. "
                f"Please consult the docs at {__docurl__}.\n"
                f"{err}")
        # TODO: write out backup
