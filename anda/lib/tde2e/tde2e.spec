%define __builder ninja
%global _lto_cflags %{?_lto_cflags} -ffat-lto-objects

%global commit 42e6a5259551178d1dab54a22ad96d14bd906e20
%global commit_date 250926
%global archive td-%{commit}

Name:           tde2e
Version:        1.8.0
Release:        0
Summary:        Cross-platform library for building Telegram clients
License:        BSL-1.0
URL:            https://github.com/tdlib/td
Source0:        %{url}/archive/%commit.tar.gz#/%archive.tar.gz

BuildRequires:  abseil-cpp-devel
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gperf
BuildRequires:  (ninja or ninja-build)

%description
TDE2E is a cross-platform library for building Telegram clients.

%package devel
Summary:        Development files for TDE2E
Provides:       %{name}-static = %{version}-%{release}
Conflicts:      tdlib-devel
Conflicts:      tdlib-static

%description devel
TDE2E is a cross-platform library for building Telegram clients.
Contains development files and static libraries.

%prep
%autosetup -p1 -n %{archive}

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_LIBDIR=%{_lib} \
  -DBUILD_TESTING:BOOL=OFF \
  -DTD_ENABLE_JNI:BOOL=OFF \
  -DTD_ENABLE_DOTNET:BOOL=OFF \
  -DTD_WITH_ABSEIL:BOOL=ON \
  -DTD_E2E_ONLY:BOOL=ON \
  -DTDE2E_ENABLE_INSTALL:BOOL=ON \
  -DTDE2E_INSTALL_INCLUDES:BOOL=ON
%cmake_build

%install
%cmake_install

%check

%files devel
%license LICENSE_1_0.txt
%doc README.md
%{_includedir}/td/
%{_libdir}/cmake/%{name}/
%{_libdir}/pkgconfig/td*.pc
%{_libdir}/libtd*.a

%changelog
