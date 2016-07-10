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
