Name:           teakra
%global commit e
%global archive %{name}-%{commit}

Version:        0
Release:        0
Summary:        DSi/3DS DSP emulator, disassembler, assembler, and tester
License:        MIT
URL:            https://github.com/wwylele/teakra
Source0:        %{url}/archive/%{commit}.tar.gz#/%{archive}.tar.gz
BuildRequires:  cmake 
BuildRequires:  (c_compiler or gcc) 
BuildRequires:  (c++_compiler or gcc-c++)

%description
Emulator, (dis-)assembler, tools and documentation for XpertTeak, the DSP used by DSi/3DS.

Many thanks to Martin Korth and many other contributers for their help and their excellent GBATEK doc!

%prep
%autosetup -p1

%build
%cmake
%cmake_build

%install
%cmake_install
rm -rf %{buildroot}/usr/lib/debug
rm %{buildroot}%{_libdir}/cmake/teakra/teakraConfig-relwithdebinfo.cmake

%if 0%{?suse_version}
%package -n lib%{name}0
Summary: Runtime library for %{name}

%description  -n lib%{name}0
%{summary}
%define libname lib%{name}0
%else
%define libname %{name}
%endif

%package devel
Requires: %{libname} = %{version}
Summary: Development library for %{name}

%description devel
%{summary}

%files -n %{libname}
%{_libdir}/libteakra.so.0
%{_libdir}/libteakra_c.so.0

%files devel
%{_includedir}/teakra/disassembler.h
%{_includedir}/teakra/disassembler_c.h
%{_includedir}/teakra/impl/register.h
%dir %{_includedir}/teakra/impl
%{_includedir}/teakra/teakra.h
%{_includedir}/teakra/teakra_c.h
%dir %{_includedir}/teakra
%{_libdir}/cmake/teakra/teakraConfig.cmake
%{_libdir}/libteakra.so
%{_libdir}/libteakra_c.so
%dir %{_libdir}/cmake/teakra


%changelog
