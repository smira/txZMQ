from distutils.core import setup

setup(
    name='txZMQ',
    version=open('VERSION').read().strip(),
    packages=['txzmq', 'txzmq.test'],
    license='GPLv2',
    author='Andrey Smirnov',
    author_email='me@smira.ru',
    url='https://github.com/smira/txZMQ',
    description='Twisted bindings for ZeroMQ',
    long_description=open('README.rst').read(),
    install_requires=["Twisted>=10.0", "pyzmq>=13"],
)
