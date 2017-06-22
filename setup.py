#!/usr/bin/env python

import setuptools
import os

with open(os.path.join('fs', 'sshfs', '__metadata__.py')) as f:
    METADATA = {}
    for l in f:
        if not l.startswith('#'):
            key, value = l.split(' = ')
            METADATA[key] = value.strip().strip('"')

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: System :: Filesystems',
]

with open('README.rst', 'rt') as f:
    DESCRIPTION = f.read()

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

with open(os.path.join('tests', 'requirements.txt')) as f:
    TEST_REQUIREMENTS = [
        l for l in f.read().splitlines()
            if l and not l.startswith(('-r', 'http'))
    ]
    TEST_REQUIREMENTS.extend(REQUIREMENTS)


setuptools.setup(
    author=METADATA['__author__'],
    author_email=METADATA['__author_email__'],
    classifiers=CLASSIFIERS,
    description="Pyfilesystem2 implementation for SSH/SFTP using paramiko ",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license=METADATA['__license__'],
    long_description=DESCRIPTION,
    name='fs.sshfs',
    packages=['fs', 'fs.sshfs', 'fs.opener'],
    platforms=['any'],
    test_suite="tests",
    tests_require=TEST_REQUIREMENTS,
    url="https://github.com/althonos/fs.sshfs",
    version=METADATA['__version__'],
)
