%define __builder ninja
%define _lto_cflags %{nil}

%global commit 9826d0e27894a575a63d4b15b2acf8e749e3da67
%global commit_date 250926
%global archive tg_owt-%{commit}

Name:           tg-owt
Version:        0.0.1~git.%commit_date
Release:        0
Summary:        WebRTC library for the Telegram messenger
License:        BSD-3-Clause
URL:            https://github.com/desktop-app/tg_owt
Source0:        %{url}/archive/%commit.tar.gz#/%archive.tar.gz
Patch0:         https://patch-diff.githubusercontent.com/raw/desktop-app/tg_owt/pull/180.patch
BuildRequires:  cmake
BuildRequires:  fdupes
%if 0%{?sle_version} == 150400
BuildRequires:  gcc10-c++
%else
BuildRequires:  gcc-c++
%endif
BuildRequires:  (ninja or ninja-build)
BuildRequires:  pkgconfig
BuildRequires:  yasm-devel
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(openh264)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libavcodec) 
BuildRequires:  pkgconfig(libavformat) 
BuildRequires:  pkgconfig(libavutil) 
BuildRequires:  pkgconfig(libswresample) 
BuildRequires:  pkgconfig(libswscale) 
BuildRequires:  pkgconfig(openssl) >= 3.0
BuildRequires:  pkgconfig(opus)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(xtst)
BuildRequires:  pkgconfig(protobuf)
BuildRequires:  pkgconfig(vpx)
BuildRequires:  pkgconfig(libsrtp2)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(epoxy)
BuildRequires:  pkgconfig(absl_algorithm_container)
BuildRequires:  pkgconfig(absl_bind_front)
BuildRequires:  pkgconfig(absl_config)
BuildRequires:  pkgconfig(absl_core_headers)
BuildRequires:  pkgconfig(absl_flags)
BuildRequires:  pkgconfig(absl_flags_parse)
BuildRequires:  pkgconfig(absl_flags_usage)
BuildRequires:  pkgconfig(absl_flat_hash_map)
BuildRequires:  pkgconfig(absl_inlined_vector)
BuildRequires:  pkgconfig(absl_memory)
BuildRequires:  pkgconfig(absl_optional)
BuildRequires:  pkgconfig(absl_strings)
BuildRequires:  pkgconfig(absl_synchronization)
BuildRequires:  pkgconfig(absl_type_traits)
BuildRequires:  pkgconfig(absl_variant)
BuildRequires:  cmake(Microsoft.GSL)
BuildRequires:  pkgconfig(libyuv)
BuildRequires:  pkgconfig(rnnoise)

%description
%{summary}.

%package devel
Summary:        Development files for %{name}
Provides:       %{name}-static = %{version}
Requires:       pkgconfig(alsa)
Requires:       pkgconfig(epoxy)
Requires:       pkgconfig(gbm)
Requires:       pkgconfig(libavcodec)
Requires:       pkgconfig(libavformat)
Requires:       pkgconfig(libavutil)
Requires:       pkgconfig(libswresample)
Requires:       pkgconfig(libswscale)
Requires:       pkgconfig(libdrm) 
Requires:       pkgconfig(libjpeg)
Requires:       pkgconfig(libpipewire-0.3)
Requires:       pkgconfig(libpulse)
Requires:       pkgconfig(openssl)
Requires:       pkgconfig(opus)
Requires:       pkgconfig(vpx)
Requires:       pkgconfig(x11)
Requires:       pkgconfig(xcomposite)
Requires:       pkgconfig(xdamage)
Requires:       pkgconfig(xext)
Requires:       pkgconfig(xfixes)
Requires:       pkgconfig(xrandr)
Requires:       pkgconfig(xrender)
Requires:       pkgconfig(xtst)
Requires:       pkgconfig(libyuv)
Requires:       pkgconfig(rnnoise)

%description devel
%{summary}.

%prep
%autosetup -p1 -n %archive

%build
%if 0%{?sle_version} == 150400
export LDFLAGS="%{optflags} -std=gnu++17"
export CC=gcc-10
export CXX=g++-10
%endif
%cmake \
 -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON \
 -DBUILD_SHARED_LIBS:BOOL=OFF \
 -DTG_OWT_USE_PROTOBUF:BOOL=OFF \
 -DTG_OWT_USE_X11:BOOL=ON \
%if 0%{?sle_version} == 150400
 -DCMAKE_CXX_STANDARD=17 \
%endif
 -DTG_OWT_PACKAGED_BUILD:BOOL=ON
%cmake_build

%install
%cmake_install
%fdupes %{buildroot}/%{_prefix}

%files devel
%license LICENSE
%{_includedir}/tg_owt
%{_libdir}/libtg_owt.a
%{_libdir}/cmake/tg_owt

%changelog
