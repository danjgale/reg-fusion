from setuptools import setup, find_packages
import re
import io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('regfusion/__init__.py', encoding='utf_8_sig').read()
    ).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='regfusion',
    version=__version__,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests"]),
    package_data={
        'regfusion': ['mappings/*']
    },
    include_package_data=True,
    license='MIT',
    maintainer='Dan Gale',
    maintainer_email="d.gale@queensu.ca",
    description="Python implementation of registration fustion methods",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/danjgale/reg-fusion',
    install_requires=[
        'numpy>=1.11',  
        'scipy>=0.19',
        'nibabel>=3.0.0',
        'nilearn>=0.6.2'
    ],
    tests_require=[
        'pytest-cov',
        'pytest'
    ],
    setup_requires=['pytest-runner'],
    entry_points={
        'console_scripts': [
            'regfusion=regfusion.cli:main'
            ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering'
    ]
)
