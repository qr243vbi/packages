Name:           rlottie
Version:        20260926
Release:        1%{?dist}
Summary:        A platform independent standalone library that plays Lottie Animation.

%global commit 683bbaa39dd0d366cf6b4bc300b4dfbee677ea6b
%global archive rlottie-%{commit}

License:        MIT
URL:            https://github.com/samsung/rlottie
Source0:        %{url}/archive/%{commit}.tar.gz#/%{archive}.tar.gz
 
BuildRequires: gcc-c++
BuildRequires: cmake
BuildRequires: gcc
 
%description
rlottie is a platform independent standalone c++ library for rendering
vector based animations and art in realtime.
 
Lottie loads and renders animations and vectors exported in the bodymovin
JSON format. Bodymovin JSON can be created and exported from After Effects
with bodymovin, Sketch with Lottie Sketch Export, and from Haiku.
 
For the first time, designers can create and ship beautiful animations
without an engineer painstakingly recreating it by hand. Since the animation
is backed by JSON they are extremely small in size but can be large in
complexity!
 
%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
 
%description devel
%{summary}.
 
%package image-loader
Summary: Dynamic loader plugin for %{name}
Requires: %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
 
%description image-loader
%{summary}.
 
%prep
%autosetup -p1 -n %{archive}
 
%build
# Upstream default C++ standard is c++14; gtest 1.17 requires C++17
%cmake -DCMAKE_POLICY_VERSION_MINIMUM=3.5
%cmake_build

%install
%cmake_install

%files
%doc AUTHORS README.md
%license COPYING licenses/*
%{_libdir}/lib%{name}.so.0*
 
%files devel
%{_includedir}/%{name}*.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_libdir}/cmake/%{name}/

%files image-loader
%{_libdir}/librlottie-image-loader.so
 
%changelog
%autochangelog
