Name:             python-txzmq
Version:          0.3.1
Release:          1%{?dist}
Summary:          Twisted bindings for ZeroMQ

Group:            Development/Languages
License:          GPLv2
URL:              http://pypi.python.org/pypi/txZMQ
Source0:          http://pypi.python.org/packages/source/t/txZMQ/txZMQ-0.3.1.tar.gz

BuildArch:        noarch


BuildRequires:    python-devel
BuildRequires:    python-setuptools
BuildRequires:    python-zmq
BuildRequires:    python-twisted

Requires:         python-zmq
Requires:         python-twisted

%description
txZMQ allows to integrate easily `ZeroMQ <http://zeromq.org>`_ sockets into
Twisted event loop (reactor).

%prep
%setup -q -n txZMQ-%{version}

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc README.rst LICENSE.txt

%{python_sitelib}/*

%changelog
* Thu Apr 05 2012 Ralph Bean <rbean@redhat.com> 0.3.1-1
- initial package for Fedora
