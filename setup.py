from distutils.core import setup

setup(
        name='txZMQ',
        version='0.1dev',
        packages=['txZMQ','txZMQ.test'],
        license='GPLv2',
        author='Andrey Smirnov',
        author_email='me@smira.ru',
        url='http://pypi.python.org/pypi/txZMQ',
        description='Twisted binding for ZeroMQ',
        long_description=open('README').read(),
        install_requires=["Twisted>=10.0", "pyzmq>=2.1"],
        )
