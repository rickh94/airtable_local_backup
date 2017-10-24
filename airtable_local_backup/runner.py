from ruamel.yaml import YAML
import fs
from fs_s3fs import S3FS


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
        with filesystem.open(path) as configfile:
            self.config = yaml.load(configfile)
