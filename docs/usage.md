# Usage


## Creating Backups

Create a simple python script, for instance `backup.py` with the contents:

```
  from airtable_local_backup import Runner

  run = Runner(path='/path/to/config/file.yaml')
  run.backup()
```

Configuration is discussed more below and you can download an [example configuration
    file](https://github.com/rickh94/airtable_local_backup/blob/master/docs/sample-config.yaml).

## Restoring from Backups

Not Implemented yet


