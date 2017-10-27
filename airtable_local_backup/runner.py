from ruamel.yaml import YAML
import fs
from fs import tempfs
from fs_s3fs import S3FS

from .download import DownloadTable
from . import file_io
from . import exceptions
from . import __docurl__


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
            except KeyError:
                raise exceptions.ConfigurationError(
                    "Options are missing in the configuration file. "
                    f"Please consult the docs at {__docurl__}"
                )

    def _save_tables(self):
        for table in self._create_backup_tables():
            file_io._write_to_file(table, self.tmp)