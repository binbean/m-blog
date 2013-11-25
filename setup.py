#!/usr/bin/env python
# encoding: utf-8

from setuptools import find_packages, setup

setup(
    name = 'm-blog',
    version = '0.1',
    description = 'a blog',
    long_description = 'blog of markdown file',
    classifiers = [
        'Developent Status :: 5 - Production/Stable',
        'Enviroment :: Web',
        'Intended Audience :: Development',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    platforms = ['any'],
    author = 'binbean',
    autor_email = 'binbean1001@gmail.com',
    url = 'http://github.com/binbean',
    license = 'MIT',
    packages = find_packages(),
    install_requires = [
        'flask',
        'markdown',
        'pyRSSGen'
    ]
)
