import io

from distutils.core import setup

setup(
    name='txZMQ',
    version=io.open('VERSION', encoding='utf-8').read().strip(),
    packages=['txzmq', 'txzmq.test'],
    license='GPLv2',
    author='Andrey Smirnov',
    author_email='me@smira.ru',
    url='https://github.com/smira/txZMQ',
    description='Twisted bindings for ZeroMQ',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    install_requires=["Twisted>=10.0", "pyzmq>=13"],
)
