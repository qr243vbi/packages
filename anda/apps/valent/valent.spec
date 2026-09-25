%global commit df82168bc37ad1ec700c66b0f0f5dfd7a07be485
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commit_date 20260925
%global libgnome 0a4eda0cdc2deb352bebc70ec697c42af46094e4

Name:               valent
Version:            0~%{commit_date}git.%{shortcommit}
Release:            1%{?dist}
Summary:            Connect, control and sync devices
License:            GPL-3.0-or-later
URL:                https://github.com/andyholmes/valent
Source0:            %{url}/archive/%{commit}/valent-%{commit}.tar.gz
Source1:            https://gitlab.gnome.org/GNOME/libgnome-volume-control/-/archive/%{libgnome}/libgnome-volume-control-%{libgnome}.tar.bz2

Group:          System/GUI/GNOME

BuildRequires:  meson >= 0.59.0
BuildRequires:  fdupes
BuildRequires:  vala
BuildRequires:  gcc-c++ 
BuildRequires:  cmake
BuildRequires:  sed
BuildRequires:  desktop-file-utils
BuildRequires:  pkg-config
BuildRequires:  sassc
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libdex-1)
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.76.0
BuildRequires:  pkgconfig(gtk4) >= 4.10.0
BuildRequires:  pkgconfig(gio-2.0) >= 2.76.0
BuildRequires:  pkgconfig(gnutls) >= 3.1.3
BuildRequires:  pkgconfig(json-glib-1.0) >= 1.6.0
BuildRequires:  pkgconfig(libpeas-2)
BuildRequires:  pkgconfig(tracker-sparql-3.0)
BuildRequires:  pkgconfig(sqlite3) >= 3.24.0
BuildRequires:  pkgconfig(libportal-gtk4)
BuildRequires:  pkgconfig(libebook-1.2) >= 3.34
BuildRequires:  pkgconfig(libadwaita-1) >= 1.2.0
BuildRequires:  pkgconfig(sysprof-capture-4) >= 3.38
#BuildRequires:  pkgconfig(libwalbottle-0) >= 0.3.0
BuildRequires:  pkgconfig(gstreamer-1.0)
BuildRequires:  pkgconfig(gstreamer-video-1.0)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  libpeas-devel
BuildRequires:  cmake(libphonenumber)
BuildRequires:  filesystem

Recommends: valent-lang
#BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%define soname 1-0

%if 0%{?suse_version}
%package -n typelib-1_0-libvalent-%{soname}
Summary: Typelib for valent
%description -n typelib-1_0-libvalent-%{soname}
Typelib for valent.
%define libname libvalent-%{soname}
%else
%define libname libvalent
%endif

%package -n libvalent-devel
Summary: Development library for valent
Requires: %{libname} = %{version}
%description -n libvalent-devel
Development library for valent.

%package -n %{libname}
Summary: Library for valent
%description -n %{libname}
Library for valent.

%package -n valent-lang
BuildArch: noarch
Summary: Languages for valent
%description -n valent-lang
Languages for valent.

%description
Securely connect your devices to open files and links where you need them, get notifications when you need them, stay in control of your media and more.

Features:

Sync contacts, notifications and clipboard content
Control media players and volume
Share files, links and text
Virtual touchpad and keyboard
Call and text notification
Execute custom commands

Valent is an implementation of the KDE Connect protocol, built on GNOME platform libraries.


%prep
%autosetup -n valent-%{commit}
rm -r subprojects/gvc*
tar -xf %{SOURCE1} -C subprojects
mv subprojects/libgnome-volume-control* subprojects/gvc

%build
%meson
sed 's/--pkg=libpeas-2/--pkg=Peas-2/' -i %{_vpath_builddir}/build.ninja
%meson_build

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%install
%meson_install
rm -R %{buildroot}%{_datadir}/locale/ru* || :
%fdupes %{buildroot}

%files
%doc README.md
%license LICENSE*
%{_sysconfdir}/xdg/**/*
%{_bindir}/valent
%{_datadir}/dbus-1/**/*
%{_datadir}/glib-2.0/**/*
%{_datadir}/icons/**/*
%{_datadir}/metainfo/*
%{_datadir}/applications/*
%dir %{_datadir}/applications
%dir %{_datadir}/metainfo
%dir %{_datadir}/glib-2.0
%dir %{_datadir}/dbus-1

%files -n valent-lang
%{_datadir}/locale/**/*


%files -n %{libname}
%{_libdir}/*.so.*
%if 0%{?suse_version}
%files -n typelib-1_0-libvalent-%{soname}
%endif
%{_libdir}/girepository-1.0/*

%files -n libvalent-devel
%{_includedir}/**/*
%dir %{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_datadir}/vala/**/*
%dir %{_libdir}/pkgconfig
%dir %{_datadir}/vala
%{_datadir}/gir-1.0/*
%dir %{_datadir}/gir-1.0

%changelog
