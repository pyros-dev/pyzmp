from setuptools import setup

with open('pyzmp/_version.py') as vf:
    exec(vf.read())

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
            'pyzmp = pyzmp.__main__:nosemain'
        ]
    },
    # this is better than using package data ( since behavior is a bit different from distutils... )
    include_package_data=True,  # use MANIFEST.in during install.
    install_requires=[
        'tblib',  # this might not always install six (latest version does not)
        'six',
        'pyzmq'
    ],
    test_suite="nose.collector",
    tests_require=[
        'nose>=1.3.7'
    ],
    zip_safe=False,  # TODO testing...
)
