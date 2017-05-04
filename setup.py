#! /usr/bin/env python

from setuptools import setup

setup(
    name='sco-datastore',
    version='0.5.0',
    description='Library to manipulate objects in the Standard Cortical Observer Data Store',
    keywords='neuroscience vision cortex ',
    author='Heiko Mueller',
    author_email='heiko.muller@gmail.com',
    url='https://github.com/heikomuller/sco-datastore',
    license='GPLv3',
    packages=['scodata'],
    package_data={'': ['LICENSE']},
    install_requires=['pymongo']
)
