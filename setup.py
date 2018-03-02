

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
    package_dir = {'': 'CElegans/pythonScripts'},
    packages = ['c302'],
    install_requires=[
        'numpy',
        'xlrd',
        'xlwt',
        'OSBModelValidation>=0.1.3',
        'pyNeuroML'
    ],
    dependency_links = [
        'git+https://github.com/OpenSourceBrain/osb-model-validation.git#egg=OSBModelValidation-0',
        'git+https://github.com/NeuroML/pyNeuroML.git#egg=pyNeuroML-0',
    ],
    version = '0.4',
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
