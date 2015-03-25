# -*- coding: utf-8 -*-

import re
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


REQUIREMENTS = [
    'six',
]
TEST_REQUIREMENTS = [
    'pytest',
    'pytest-cov',
    'pytest-django',
    'pytest-pythonpath',
    'peewee',
    'pony',
    'Django',
    'SQLAlchemy',
]


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--cov', 'guardrail', 'tests',
            '--cov-report', 'term-missing',
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version('guardrail/__init__.py')


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='guardrail',
    version=__version__,
    description=(
        'An extensible library for managing object-level permissions with '
        'support for SQLAlchemy, Peewee, Pony, and Django.'
    ),
    long_description=read('README.rst'),
    author='Joshua Carp',
    author_email='jm.carp@gmail.com',
    url='https://github.com/jmcarp/guardrail',
    packages=find_packages(exclude=('test*', 'examples')),
    package_dir={'guardrail': 'guardrail'},
    install_requires=REQUIREMENTS,
    license=read('LICENSE'),
    ip_safe=False,
    keywords=(
        'guardrail', 'authorization', 'sql',
        'sqlalchemy', 'peewee', 'pony', 'django',
    ),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
    cmdclass={'test': PyTest},
)
