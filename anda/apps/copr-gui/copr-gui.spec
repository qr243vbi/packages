Name:           copr-gui
%define pypi_name copr_gui
Version:        0.1.7.1
Release:        1%{?dist}
Summary:        GUI for managing COPR instances

License:        GPL-3.0-or-later
URL:            https://github.com/qr243vbi/%{pypi_name}
Source0:        %{url}/archive/refs/tags/%{version}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  pyproject-rpm-macros
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  python3-pyqt6
BuildRequires:  python3-copr

Requires:       qt6-qtdeclarative
Requires:       python3-pyqt6
Requires:       python3-copr

%description
A Qt-based graphical user interface for managing COPR instances.

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
install -Dm644 favicon.ico %{buildroot}%{_iconsdir}/hicolor/256x256/apps/copr.png
install -Dm644 copr-gui.desktop %{buildroot}%{_datadir}/applications/copr-gui.desktop
%pyproject_install
%pyproject_save_files copr_gui copr_gui_source_types


%check
%pyproject_check_import

%files -f %{pyproject_files}
%license LICENSE
%{_bindir}/copr-gui
%{_iconsdir}/hicolor/256x256/apps/copr.png
%{_datadir}/applications/copr-gui.desktop

%changelog
* Wed Sep 23 2026 qr243vbi <qr243vbi@atomicmail.io> - 0.1.6-1
- Increase default timeout, make projetcs undeletable

* Sun Sep 20 2026 qr243vbi <qr243vbi@atomicmail.io> - 0.1.3-1
- Added ability to look for build chroots

* Fri Sep 18 2026 qr243vbi <qr243vbi@atomicmail.io> - 0.1.1-1
- Bugfixes and improvements

* Fri Sep 18 2026 qr243vbi <qr243vbi@atomicmail.io> - 0.1.0-1
- Initial package
