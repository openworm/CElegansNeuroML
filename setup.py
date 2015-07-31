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
        'pyNeuroML', 'PySide'
    ],
    dependency_links = [
        'git://github.com/OpenSourceBrain/osb-model-validation.git#egg=OSBModelValidation',
        'git://github.com/purcell/airspeed.git#egg=airspeed',
        #grab a specific tag from the 'development' branch to avoid downstream breaking changes
        'git://github.com/NeuralEnsemble/libNeuroML.git@b02b6467146d52aecbbaa1c4cda9c08a5e971e3f#egg=libNeuroML',
        #grab a specific tag from the 'master' branch to avoid downstream breaking changes
        'git://github.com/NeuroML/pyNeuroML.git@c64eabc8bc397a1acada15433eb4444db295f391#egg=pyNeuroML',
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
