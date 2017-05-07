#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages


setup(
    name='rspet-server',
    version='0.4.0',
    description='Server module of the RSPET Post-Exploitation Toolset.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS'
    ],
    keywords='rspet post exploitation security reverse shell',
    url='https://github.com/panagiks/RSPET',
    author='panagiks',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    namespace_packages=['rspet'],
    package_data={
        'rspet' : [
            'server/config.json',
            'server/Plugins/Client/*'
        ]
    },
    extras_require={
        'rest' : [
            'Flask',
            'flask-cors'
        ]
    },
    install_requires=[
        'certbuilder',
        'oscrypto',
        'asn1crypto'
    ],
    entry_points={
        'console_scripts' : [
            'rspet-server=rspet.server.base:main',
            'rspet-server-rest=rspet.server.api:main'
        ]
    }
)
