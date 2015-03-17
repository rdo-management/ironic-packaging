%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global	release_name juno
%global	full_release ironic-%{version}


Name:		openstack-ironic
Summary:	OpenStack Baremetal Hypervisor API (ironic)
Version: XXX
Release: XXX{?dist}
License:	ASL 2.0
Group:		System Environment/Base
URL:		http://www.openstack.org
Source0:	https://launchpad.net/ironic/%{release_name}/%{version}/+download/ironic-%{version}.tar.gz
#Source0:	https://launchpad.net/ironic/juno/2014.2/+download/ironic-2014.2.tar.gz

Source1:	openstack-ironic-api.service
Source2:	openstack-ironic-conductor.service
Source3:	ironic-rootwrap-sudoers

Patch0001:	0001-ironic-Remove-runtime-dependency-on-python-pbr.patch

BuildArch:	noarch
BuildRequires:	python-setuptools
BuildRequires:	python2-devel
BuildRequires:	python-pbr
BuildRequires:	openssl-devel
BuildRequires:	libxml2-devel
BuildRequires:	libxslt-devel
BuildRequires:	gmp-devel
BuildRequires:	python-sphinx
BuildRequires:	systemd


%prep
%setup -q -n ironic-%{upstream_version}
rm requirements.txt test-requirements.txt

%patch0001 -p1

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}


# install systemd scripts
mkdir -p %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}

# install sudoers file
mkdir -p %{buildroot}%{_sysconfdir}/sudoers.d
install -p -D -m 440 %{SOURCE3} %{buildroot}%{_sysconfdir}/sudoers.d/ironic

mkdir -p %{buildroot}%{_sharedstatedir}/ironic/
mkdir -p %{buildroot}%{_sysconfdir}/ironic/rootwrap.d

#Populate the conf dir
install -p -D -m 640 etc/ironic/ironic.conf.sample %{buildroot}/%{_sysconfdir}/ironic/ironic.conf
install -p -D -m 640 etc/ironic/policy.json %{buildroot}/%{_sysconfdir}/ironic/policy.json
install -p -D -m 640 etc/ironic/rootwrap.conf %{buildroot}/%{_sysconfdir}/ironic/rootwrap.conf
install -p -D -m 640 etc/ironic/rootwrap.d/* %{buildroot}/%{_sysconfdir}/ironic/rootwrap.d/


%description
Ironic provides an API for management and provisioning of physical machines

%package common
Summary: Ironic common
Group: System Environment/Base

Requires:	ipmitool
Requires:	python-eventlet
Requires:	python-greenlet
Requires:	python-iso8601
Requires:	python-posix_ipc
Requires:	python-jsonpatch
Requires:	python-keystonemiddleware
Requires:	python-kombu
Requires:	python-anyjson
Requires:	python-lockfile
Requires:	python-lxml
Requires:	python-migrate
Requires:	python-mock
Requires:	python-netaddr
Requires:	python-oslo-concurrency
Requires:	python-oslo-config
Requires:	python-oslo-context
Requires:	python-oslo-db
Requires:	python-oslo-i18n
Requires:	python-oslo-policy
Requires:	python-oslo-rootwrap
Requires:	python-oslo-serialization
Requires:	python-oslo-utils
Requires:	python-paramiko
Requires:	python-pecan
Requires:	python-retrying
Requires:	python-six
Requires:	python-stevedore
Requires:	python-webob
Requires:	python-websockify
Requires:	python-wsme
Requires:	pycrypto
Requires:	python-sqlalchemy
Requires:	python-neutronclient
Requires:	python-glanceclient
Requires:	python-keystoneclient
Requires:	python-swiftclient
Requires:	python-jinja2
Requires:	python-pyghmi
Requires:	python-alembic
Requires:	pysendfile
Requires:	python-pbr

Requires(pre):	shadow-utils

%description common
Components common to all OpenStack Ironic services


%files common
%doc README.rst LICENSE
%{_bindir}/ironic-dbsync
%{_bindir}/ironic-rootwrap
%{_bindir}/ironic-nova-bm-migrate
%{python_sitelib}/ironic*
%{_sysconfdir}/sudoers.d/ironic
%config(noreplace) %attr(-,root,ironic) %{_sysconfdir}/ironic
%attr(-,ironic,ironic) %{_sharedstatedir}/ironic

%pre common
getent group ironic >/dev/null || groupadd -r ironic
getent passwd ironic >/dev/null || \
    useradd -r -g ironic -d %{_sharedstatedir}/ironic -s /sbin/nologin \
-c "OpenStack Ironic Daemons" ironic
exit 0

%package api
Summary: The Ironic API
Group: System Environment/Base

Requires: %{name}-common = %{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api
Ironic API for management and provisioning of physical machines


%files api
%doc LICENSE
%{_bindir}/ironic-api
%{_unitdir}/openstack-ironic-api.service

%post api
%systemd_post openstack-ironic-api.service

%preun api
%systemd_preun openstack-ironic-api.service

%postun api
%systemd_postun_with_restart openstack-ironic-api.service

%package conductor
Summary: The Ironic Conductor
Group: System Environment/Base

Requires: %{name}-common = %{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description conductor
Ironic Conductor for management and provisioning of physical machines


%files conductor
%doc LICENSE
%{_bindir}/ironic-conductor
%{_unitdir}/openstack-ironic-conductor.service

%post conductor
%systemd_post openstack-ironic-conductor.service

%preun conductor
%systemd_preun openstack-ironic-conductor.service

%postun conductor
%systemd_postun_with_restart openstack-ironic-conductor.service



%changelog
* Thu Oct 23 2014 Angus Thomas <athomas@redhat.com> - 2014.2-2
- Rebased to 2014.2 GA release

* Fri Oct 17 2014 Angus Thomas <athomas@redhat.com> - 2014.2-1
- Rebased to 2014.2 GA release

* Tue Oct 14 2014 Angus Thomas <athomas@redhat.com> - 2014.2-0.3.rc2
- Added requirement for ipmitool

* Mon Oct 13 2014 Angus Thomas <athomas@redhat.com> - 2014.2.rc2-1
- Rebased to 2014.2.rc2

* Thu Oct 9 2014 Angus Thomas <athomas@redhat.com> - 2014.2.rc1-2
- Added sudoers file for rootwrap (bz #1149189)
- Removed the autodiscovery patch

* Mon Oct 6 2014 Angus Thomas <athomas@redhat.com> - 2014.2.rc1-1
- Updated Requires
- Added autodiscovery patch

* Thu Apr 17 2014 Angus Thomas <athomas@redhat.com> - 2014.1-rc2.1
- License file in each package

* Wed Apr 9 2014 Angus Thomas <athomas@redhat.com> - 2014.1-rc1.2
- License file in each package

* Mon Apr 7 2014 Angus Thomas <athomas@redhat.com> - 2014.1-rc1.1
- Rebuilt with -rc1 tarball
- Rebased patches
- Added dependency on python-alembic

* Thu Mar 27 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.5
- Split into multiple packages

* Fri Feb 28 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.4
- Restored BuildRequires: python-pbr 

* Thu Feb 27 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.3
- Added dependency on python-pyghmi
- Patch to remove pbr build dependency
- Fixed python2-devel build dependency
- Added noreplace to config files
- Added  unitdir macro for systemd service file installation
- Added scripts to manage systemd services
- Removed unnecessary Requires & BuildRequires


* Mon Feb 24 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.2
- Removed /var/log/ironic from package
- Replaced hardcoded file paths with macros
- Added LICENSE and README.rst docs

* Fri Feb 21 2014 Angus Thomas <athomas@redhat.com> - 2014.1-b2.1
- Initial package build

