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
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
    long_description=io.open('README.rst', encoding='utf-8').read(),
    install_requires=["Twisted>=10.0", "pyzmq>=13"],
)
