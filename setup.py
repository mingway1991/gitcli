#!env/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='gitcli',
    version='0.1',
    description='git命令行封装',
    author='Mingway',
    author_email='mingwei.shi@hotmail.com',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['gitcli'],
    install_requires=[
        'Click','pyyaml'
    ],
    entry_points='''
        [console_scripts]
        gitcli=gitcli:gitcli
    ''',
    scripts=['gitcli.py'],
)