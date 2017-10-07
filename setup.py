from os import path
from setuptools import setup, find_packages
import subprocess

HERE = path.abspath(path.dirname(__file__))
out = subprocess.run(['git', 'show-ref'], stdout=subprocess.PIPE)
VERS = out.stdout.decode('utf-8')[0:7]
DESC = 'Script to create local backups from airtable databases'

with open(path.join(HERE, 'README.rst'), 'r') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='airtable_local_backup',
    version=VERS,

    description=DESC,
    long_description=LONG_DESCRIPTION,

    url='https://github.com/rickh94/airtable_local_backup',
    author='Rick Henry',
    author_email='fredericmhenry@gmail.com',

    license='MIT',
    python_requires='>=3',

    packages=find_packages(),

    install_requires=[
        'requests',
        'airtable_python_wrapper',
        'boto3',
    ],

)
