"""
A setuptools based setup module.

Adopted from:
https://github.com/pypa/sampleproject

"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='probart',
    version='0.1.0',
    description='Tiny library for probabilistic line drawing',
    long_description=long_description,
    url='https://github.com/a5kin/probart',
    author='Andrey Zamaraev',
    author_email='a5kin@github.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Artistic Software',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='probabilistic drawing tools utils utility',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pycairo', 'numpy'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
