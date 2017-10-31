.. Airtable Local Backup documentation master file, created by
   sphinx-quickstart on Sat Oct 28 22:49:56 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=====================
Airtable Local Backup
=====================

Introduction
============

Airtable Local Backup provides a (somewhat) user friendly way to backup data
from `Airtable <http://airtable.com>`_ locally. There are a number of useful
functions to generate your own custom backup scripts or you can use the
provided ``Runner`` class and a yaml-style configuration file **ADD EXAMPLE**
to orchestrate the backup.


Installation
============
For now, clone the repo and ``python setup.py install``
**COMING**
``$ pip install airtable_local_backup``


Basic Usage
===========

Creating Backups
----------------

.. code::

  from airtable_local_backup import Runner

  run = Runner(path='/path/to/config/file.yaml')
  run.backup()


Configuration is discussed more below and you can download an `example config
file <https://github.com/rickh94/airtable_local_backup/sample-config.yaml>`_.

Restoring from Backups
----------------------

Not Implemented yet


-----------------
Table Of Contents
-----------------

.. toctree::
   :maxdepth: 2

   usage
   apidoc



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
