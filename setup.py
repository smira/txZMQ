from setuptools import setup, find_packages
import sys

setup(
        name='txZMQ',
        version='0.6.2',
        packages=find_packages(),
        license='GPLv2',
        author='Andrey Smirnov',
        author_email='me@smira.ru',
        url='http://pypi.python.org/pypi/txZMQ',
        description='Twisted bindings for ZeroMQ',
        long_description=open('README.rst').read(),
        install_requires=["Twisted>=10.0", "pyzmq-ctypes>=2.1" if sys.subversion[0] == "PyPy" else "pyzmq>=2.1"],
        test_suite='txzmq.test',
        )
