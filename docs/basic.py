from airtable_local_backup import Runner
from os import path

HERE = path.dirname(path.abspath(__file__))
config = path.join(HERE, "config.yml")

runner = Runner(str(config))
runner.backup()
