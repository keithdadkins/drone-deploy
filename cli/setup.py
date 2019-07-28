# -*- coding: utf-8 -*-
from setuptools import setup, setuptools, find_packages

version = {}
with open("./version.py") as ver:
    exec(ver.read(), version)

setup(
    name='drone-deploy',
    description='Build, provision, and deploy DroneCI EC2 instances on AWS.',
    version=version['__version__'],
    author='Keith D. Adkins',
    author_email='keithdadkins@me.com',
    license='MIT',
    url='https://github.com/keithdadkins/drone-deploy',
    classifiers=[
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Utilities',
        'Development Status :: Alpha',
        'Environment :: Console'
    ],
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
