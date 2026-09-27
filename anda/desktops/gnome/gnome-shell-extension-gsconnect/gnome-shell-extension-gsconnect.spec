# Firefox doesn't provide arch-independent web extension directory, although
# GSConnect web extension is arch-independent
%global debug_package %{nil}

%global app_id org.gnome.Shell.Extensions.GSConnect

Name:           gnome-shell-extension-gsconnect
Version:        73
Release:        1%{?dist}
Summary:        KDE Connect implementation for GNOME Shell

License:        GPL-2.0-or-later
URL:            https://github.com/GSConnect/%{name}
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        nautilus-gsconnect.metainfo.xml
Source2:        nemo-gsconnect.metainfo.xml
Patch1:         gnome-shell-extension-gsconnect-42-firewalld.patch

BuildRequires:  desktop-file-utils
BuildRequires:  firewalld-filesystem
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  gtk4
BuildRequires:  libappstream-glib
BuildRequires:  meson
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(glib-2.0)
Requires:       firewalld-filesystem
Requires:       gnome-shell
# Needed for ssh-keygen
Requires:       openssh
# Needed for ssh-add
Requires:       openssh-clients
Requires:       openssl
Requires:       /usr/bin/ffmpeg
Requires(post): firewalld-filesystem
Recommends:     evolution-data-server
Recommends:     (gsound or libcanberra-gtk3)
Suggests:       (nautilus-gsconnect = %{version}-%{release} if nautilus)
Suggests:       (nemo-gsconnect = %{version}-%{release} if nemo)
Suggests:       webextension-gsconnect = %{version}-%{release}

%description
The KDE Connect project allows devices to securely share content such as
notifications and files as well as interactive features such as SMS messaging
and remote input. The KDE Connect team maintains cross-desktop, Android and
Sailfish applications as well as an interface for KDE Plasma.

GSConnect is a complete implementation of KDE Connect especially for GNOME Shell
with Nautilus, Chrome and Firefox integration. It is does not rely on the KDE
Connect desktop application and will not work with it installed.


%package -n nautilus-gsconnect
Summary:        Nautilus extension for GSConnect
Requires:       gobject-introspection
Requires:       nautilus-extensions
Requires:       nautilus-python
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description -n nautilus-gsconnect
The nautilus-gsconnect package provides a Nautilus context menu for sending
files to devices that are online, paired and have the "Share and receive" plugin
enabled.


%package -n nemo-gsconnect
Summary:        Nemo extension for GSConnect
Requires:       gobject-introspection
Requires:       nemo-extensions
Requires:       nemo-python
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description -n nemo-gsconnect
The nemo-gsconnect package provides a Nemo context menu for sending files to
devices that are online, paired and have the "Share and receive" plugin enabled.


%package -n webextension-gsconnect
Summary:        Web browser integration for GSConnect
Requires:       mozilla-filesystem
Requires:       %{name} = %{version}-%{release}

%description -n webextension-gsconnect
The webextension-gsconnect package allows Google Chrome/Chromium, Firefox,
Vivaldi, Opera (and other Browser Extension, Chrome Extension or WebExtensions
capable browsers) to interact with GSConnect, using the Share plugin to open
links in device browsers and the Telephony plugin to share links with contacts
by SMS.


%prep
%autosetup -p0


%build
%meson \
    -Dfirewalld=true \
    -Dinstalled_tests=false \
    -Dnemo=true
%meson_build


%install
%meson_install

# Install AppData files
install -Dpm 0644 %{SOURCE1} %{SOURCE2} -t $RPM_BUILD_ROOT%{_metainfodir}/

%find_lang %{app_id}


%check
desktop-file-validate \
    $RPM_BUILD_ROOT%{_datadir}/applications/%{app_id}.desktop \
    $RPM_BUILD_ROOT%{_datadir}/applications/%{app_id}.Preferences.desktop
appstream-util validate-relax --nonet \
    $RPM_BUILD_ROOT%{_metainfodir}/nautilus-gsconnect.metainfo.xml \
    $RPM_BUILD_ROOT%{_metainfodir}/nemo-gsconnect.metainfo.xml \
    $RPM_BUILD_ROOT%{_metainfodir}/%{app_id}.metainfo.xml


%post
%firewalld_reload


%files -f %{app_id}.lang
%doc CONTRIBUTING.md README.md
%license LICENSES/GPL-2.0-or-later.txt
%{_datadir}/gnome-shell/extensions/gsconnect@andyholmes.github.io/
%{_datadir}/applications/%{app_id}.desktop
%{_datadir}/applications/%{app_id}.Preferences.desktop
%{_datadir}/dbus-1/services/%{app_id}.service
%{_datadir}/glib-2.0/schemas/%{app_id}.gschema.xml
%{_datadir}/icons/hicolor/scalable/apps/*.svg
%{_prefix}/lib/firewalld/services/*.xml
%{_metainfodir}/%{app_id}.metainfo.xml


%files -n nautilus-gsconnect
%{_datadir}/nautilus-python/extensions/nautilus-gsconnect.py
%{_metainfodir}/nautilus-gsconnect.metainfo.xml


%files -n nemo-gsconnect
%{_datadir}/nemo-python/extensions/nemo-gsconnect.py
%{_metainfodir}/nemo-gsconnect.metainfo.xml


%files -n webextension-gsconnect
%{_libdir}/mozilla/native-messaging-hosts/
%{_sysconfdir}/chromium/
%{_sysconfdir}/opt/chrome/


%changelog
