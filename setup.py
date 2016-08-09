import os
import sys
from setuptools import setup

with open('pyzmp/_version.py') as vf:
    exec(vf.read())

if sys.argv[-1] == 'publish':

    os.system("python setup.py sdist")
    os.system("python setup.py bdist_wheel")
    # OLD way:
    #os.system("python setup.py sdist bdist_wheel upload")
    # NEW way:
    # Ref: https://packaging.python.org/distributing/
    os.system("twine upload dist/*")
    print("You probably want to also tag the version now:")
    print("  python setup.py tag")
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a {0} -m 'version {0}'".format(__version__))
    os.system("git push --tags")
    sys.exit()

setup(name='pyzmp',
    version=__version__,
    description='ZeroMq based multiprocessing framework.',
    url='http://github.com/asmodehn/pyzmp',
    author='AlexV',
    author_email='asmodehn@gmail.com',
    license='BSD',
    packages=[
        'pyzmp',
        'pyzmp.tests'
    ],
    entry_points={
        'console_scripts': [
            'pyzmp = pyzmp.__main__:main'
        ]
    },
    # this is better than using package data ( since behavior is a bit different from distutils... )
    include_package_data=True,  # use MANIFEST.in during install.
    install_requires=[
        'tblib',  # this might not always install six (latest version does not)
        'six',
        'pyzmq',
        'pytest-timeout',
        # Careful : upon install plugins can be resolved instead of core pytest package
        # => pytest should be listed last here...
        'pytest>=2.9.1',  # since tests are embedded in package
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest>=2.9.1'],
    zip_safe=False,  # TODO testing...
)
