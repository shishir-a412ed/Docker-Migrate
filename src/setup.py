#!/usr/bin/env python
"""
setup.py for docker-migrate.
"""

# Author: Shishir Mahajan <shishir.mahajan@redhat.com>

from setuptools import setup

setup(name="docker-migrate", scripts=["docker-migrate"],
      version='1.0',
      description="Tool for migrating docker from one backend storage to another",
      author="Shishir Mahajan", author_email="shishir.mahajan@redhat.com",
      packages=["dockermigrate"])
