# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install
import os, sys

long_description = """
*C. elegans* models in NeuroML and neuroConstruct
==============================================

This repository contains a neuroConstruct (http://www.neuroConstruct.org) project containing a model of the *C. elegans* nervous system, see [here](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans).

The NeuroML files are available under the directories [generatedNeuroML](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans/generatedNeuroML), and [generatedNeuroML2](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans/generatedNeuroML).

This is being developed as part of the [OpenWorm project](http://www.openworm.org).

**There is also a new initiative which uses Python scripts to generate network models in NeuroML2 at multiple levels of details: [c302](https://github.com/openworm/CElegansNeuroML/tree/master/CElegans/pythonScripts/c302).** This will eventually be fully integrated with the neuroConstruct version.
"""

setup(
    name = 'CElegansNeuroML',
    install_requires=[
        'numpy', 'xlrd', 'xlwt', 'libNeuroML', 'airspeed', 'OSBModelValidation',
        'pyNeuroML'
    ],
    dependency_links = [
        'git://github.com/OpenSourceBrain/osb-model-validation.git#egg=OSBModelValidation',
        'git://github.com/purcell/airspeed.git#egg=airspeed',
        'git://github.com/NeuralEnsemble/libNeuroML.git@development#egg=libNeuroML',
        'git://github.com/NeuroML/pyNeuroML.git#egg=pyNeuroML',
    ],
    version = '0.3',
    author = 'OpenWorm.org authors and contributors',
    author_email = 'info@openworm.org',
    description = 'C. elegans models in NeuroConstruct and NeuroML',
    long_description = long_description,
    license = 'MIT',
    url='http://github.com/openworm/CElegansNeuroML',
    download_url = 'https://github.com/openworm/CElegansNeuroML/archive/master.zip',
    classifiers = [
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'
    ]
)
