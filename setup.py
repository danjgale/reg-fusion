from setuptools import setup, find_packages
import re
import io

__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('regfusion/__init__.py', encoding='utf_8_sig').read()
    ).group(1)

test_deps = ['pytest-cov',
             'pytest']

extras = {
    'test': test_deps,
}

setup(
    name='regfusion',
    version=__version__,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*",
                                    "tests"]),
    package_data={'regfusion': ['mappings/*.txt']},
    license='MIT',
    author='Dan Gale',
    long_description=open('README.md').read(),
    url='https://github.com/danjgale/reg-fusion',
    install_requires=[
        'numpy',
        'scipy',
        'nibabel',
        'nilearn'
    ],
    tests_require=test_deps,
    extras_require=extras,
    setup_requires=['pytest-runner'],
    entry_points={
        'console_scripts': [
            'regfusion=regfusion.cli:main'
            ]
        }
)
