from distutils.core import setup
import sys

setup(
        name='txZMQ',
        version='0.5.2',
        packages=['txzmq','txzmq.test'],
        license='GPLv2',
        author='Andrey Smirnov',
        author_email='me@smira.ru',
        url='http://pypi.python.org/pypi/txZMQ',
        description='Twisted bindings for ZeroMQ',
        long_description=open('README.rst').read(),
        install_requires=["Twisted>=10.0", "pyzmq-ctypes>=2.1" if sys.subversion[0] == "PyPy" else "pyzmq>=2.1" ],
        )
