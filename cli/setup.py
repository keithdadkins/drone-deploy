# -*- coding: utf-8 -*-
from setuptools import setup, setuptools, find_packages

setup(
    name='drone-deploy',
    version='0.1.0',
    license='TODO',
    url='TODO',
    packages=find_packages(
        exclude=[
            "tests"
        ]
    ),
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        drone-deploy=cli:cli
    ''',
)
