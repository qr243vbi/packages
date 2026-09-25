%ifarch aarch64
    %global _lto_cflags %nil
%endif

# Telegram Desktop's constants...
%global appname ayugram

# Reducing debuginfo verbosity...
%global optflags %(echo %{optflags} | sed 's/-g /-g1 /')

Name: ayugram-desktop
Version: 7.0.9
Release: 0%{?dist}

# Application and 3rd-party modules licensing:
# * Telegram Desktop - GPL-3.0-or-later with OpenSSL exception -- main tarball;
# * tg_owt - BSD-3-Clause AND BSD-2-Clause AND Apache-2.0 AND MIT AND LicenseRef-Fedora-Public-Domain -- static dependency;
# * rlottie - LGPL-2.1-or-later AND AND FTL AND BSD-3-Clause -- static dependency;
# * cld3  - Apache-2.0 -- static dependency;
# * qt_functions.cpp - LGPL-3.0-only -- build-time dependency;
# * open-sans-fonts  - Apache-2.0 -- bundled font;
# * vazirmatn-fonts - OFL-1.1 -- bundled font.
License: GPL-3.0-or-later

URL:      https://github.com/ayugram/ayugramdesktop
%define archive AyuGramDesktop-%{version}-full

Summary:  Unofficial Telegram Desktop client
Source0:  https://github.com/AyuGram/AyuGramDesktop/releases/download/v%{version}/%{archive}.tar.gz


BuildRequires: cmake(Microsoft.GSL)
BuildRequires: cmake(OpenAL)
BuildRequires: cmake(Qt6Concurrent)
BuildRequires: cmake(Qt6Core)
BuildRequires: cmake(Qt6Core5Compat)
BuildRequires: cmake(Qt6DBus)
BuildRequires: cmake(Qt6Gui)
BuildRequires: cmake(Qt6Network)
BuildRequires: cmake(Qt6OpenGL)
BuildRequires: cmake(Qt6OpenGLWidgets)
BuildRequires: cmake(Qt6Svg)
BuildRequires: cmake(Qt6WaylandClient)
BuildRequires: cmake(Qt6Widgets)
BuildRequires: cmake(fmt)
BuildRequires: cmake(range-v3)
BuildRequires: cmake(tg_owt)
BuildRequires: cmake(tl-expected)
BuildRequires: cmake(ada)
BuildRequires: pkg-config

BuildRequires: pkgconfig(libsrtp2)
BuildRequires: pkgconfig(alsa)
BuildRequires: pkgconfig(gio-2.0)
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(glibmm-2.68) >= 2.76.0
BuildRequires: pkgconfig(gobject-2.0)
BuildRequires: pkgconfig(gobject-introspection-1.0)
BuildRequires: pkgconfig(hunspell)
BuildRequires: pkgconfig(jemalloc)
BuildRequires: pkgconfig(libcrypto)
BuildRequires: pkgconfig(liblz4)
BuildRequires: pkgconfig(liblzma)
BuildRequires: pkgconfig(libpulse)
BuildRequires: pkgconfig(libswresample)
BuildRequires: pkgconfig(libswscale)
BuildRequires: pkgconfig(libxxhash)
%if 0%{?fedora} < 41
BuildRequires: pkgconfig(openssl)
%endif
BuildRequires: pkgconfig(opus)
BuildRequires: pkgconfig(protobuf)
BuildRequires: pkgconfig(protobuf-lite)
BuildRequires: pkgconfig(rnnoise)
BuildRequires: pkgconfig(vpx)
BuildRequires: pkgconfig(wayland-client)
BuildRequires: pkgconfig(webkitgtk-6.0)
BuildRequires: pkgconfig(xcb)
BuildRequires: pkgconfig(xcb-keysyms)
BuildRequires: pkgconfig(xcb-record)
BuildRequires: pkgconfig(xcb-screensaver)
BuildRequires: cmake(absl)
BuildRequires: pkgconfig(tde2e)

BuildRequires: boost-devel
%if 0%{?suse_version} > 0
BuildRequires: libboost_regex-devel
%endif
BuildRequires: cmake
BuildRequires: desktop-file-utils

%if 0%{?suse_version}
BuildRequires:  ffmpeg-7-libavcodec-devel
BuildRequires:  ffmpeg-7-libavformat-devel
BuildRequires:  ffmpeg-7-libavutil-devel
BuildRequires:  ffmpeg-7-libswresample-devel
BuildRequires:  ffmpeg-7-libswscale-devel
BuildRequires:  ffmpeg-7-libavdevice-devel
%else
BuildRequires:  ffmpeg-free-devel
%endif

BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libpulse)

BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: (libappstream-glib or appstream-glib)
BuildRequires: (libatomic or libatomic_ops-devel)
%ifarch x86_64 %x86_64 aarch64 %arm64 ppc64le %power64
BuildRequires: libdispatch-devel
%endif
BuildRequires: (libqrcodegencpp-devel or QR-Code-generator-devel)
BuildRequires: libstdc++-devel
BuildRequires: (minizip-compat-devel or minizip-devel)
BuildRequires: (ninja or ninja-build)
BuildRequires: python3
BuildRequires: (qt6-qtbase-private-devel or qt6-base-private-devel)
BuildRequires: (qt6-qtbase-static or qt6-base-devel)
BuildRequires: pkgconfig(openh264)
BuildRequires: rpm_macro(_metainfodir)
BuildRequires: (qt6-shadertools or qt6-qtshadertools)

Requires: hicolor-icon-theme
Requires: (qt6-imageformats%{?_isa} or qt6-qtimageformats%{?_isa})

# Short alias for the main package...
Provides: telegram = %{?epoch:%{epoch}:}%{version}-%{release}
Provides: telegram%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}


%description
Telegram is a messaging app with a focus on speed and security, it’s super
fast, simple and free. You can use Telegram on all your devices at the same
time — your messages sync seamlessly across any number of your phones,
tablets or computers.

With Telegram, you can send messages, photos, videos and files of any type
(doc, zip, mp3, etc), as well as create groups for up to 50,000 people or
channels for broadcasting to unlimited audiences. You can write to your
phone contacts and find people by their usernames. As a result, Telegram is
like SMS and email combined — and can take care of all your personal or
business messaging needs.

%prep
# Unpacking Telegram Desktop source archive...
%autosetup -n %{archive} -p1

%build
# Building Telegram Desktop using cmake...
%cmake \
    -DTDESKTOP_API_ID=611335 \
    -DTDESKTOP_API_HASH=d524b414d21f4d37f08684c1df41ac9c \
    -DTDESKTOP_DISABLE_AUTOUPDATE:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED:BOOL=ON \
    -DDESKTOP_APP_USE_PACKAGED_RLOTTIE:BOOL=OFF \
    -DDESKTOP_APP_USE_PACKAGED_FONTS:BOOL=ON \
    -DDESKTOP_APP_DISABLE_WAYLAND_INTEGRATION:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_X11_INTEGRATION:BOOL=OFF \
    -DDESKTOP_APP_DISABLE_CRASH_REPORTS:BOOL=ON
cat << EOF > third_libyuv.h
#include <libyuv.h>
EOF
install -Dm644 third_libyuv.h third_party/libyuv/include/libyuv.h
install -Dm644 third_libyuv.h Telegram/ThirdParty/tgcalls/tgcalls/third_party/libyuv/include/libyuv.h
%cmake_build

%install
%cmake_install

%files
%doc README.md changelog.txt
%license LICENSE LEGAL
%{_bindir}/*
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/*/apps/*.*
%{_datadir}/dbus-1/services/*.service
%{_metainfodir}/*.metainfo.xml

%changelog
