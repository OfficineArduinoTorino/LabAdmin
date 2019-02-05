#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.5.1'

setup(
    name='labadmin',
    version=version,
    description="""A django app to manage your Fablab""",
    author='Officine Torino',
    author_email='d.gomba@officine.cc',
    url='https://github.com/OfficineArduinoTorino/labadmin.git',
    packages=[
        'labadmin',
    ],
    include_package_data=True,
    install_requires=[
       'django<1.11,>=1.8',
       'djangorestframework>3,<3.7',
       'django-cors-middleware==1.3.1',
       'django-oauth-toolkit==0.10.0',
       'django-registration>=2.2,<2.3',
       'django-versatileimagefield>=1.7.0,<2',
       'paho-mqtt>1,<2',
       'Pillow<4.1',
    ],
    zip_safe=False,
    keywords='Fablab, lab, admin',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
