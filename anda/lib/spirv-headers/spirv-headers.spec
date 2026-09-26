%if 0%{?suse_version} < 1600
%define gcc_version 13
%endif

%global commit_date 20260926
%global commit cb42dec3830d3ac67fa449ecdc0c0f73d5e74498
%global archive SPIRV-Headers-%{commit}

Name:           spirv-headers
Version:        1.6.7
Release:        1%{?dist}
Summary:        Machine-readable files from the SPIR-V registry
License:        MIT
Group:          Development/Libraries/C and C++
URL:            https://github.com/KhronosGroup/SPIRV-Headers
Source:         %{url}/archive/%{commit}.tar.gz#/%{archive}.tar.gz
BuildArch:      noarch
BuildRequires:  cmake >= 2.8
BuildRequires:  fdupes
BuildRequires:  gcc%{?gcc_version} >= 9
BuildRequires:  gcc%{?gcc_version}-c++ >= 9
BuildRequires:  pkg-config

%description
This repository contains machine-readable files from the SPIR-V
registry. This includes:

* Header files for various languages.
* JSON files describing the grammar for the SPIR-V core instruction
  set, and for the GLSL.std.450 extended instruction set.
* The XML registry file.

%prep
%autosetup -n %{archive} -p1

%build
%cmake \
	-DCMAKE_C_COMPILER="gcc%{?gcc_version:-%{gcc_version}}" \
	-DCMAKE_CXX_COMPILER="g++%{?gcc_version:-%{gcc_version}}"
%cmake_build

%install
%cmake_install
%fdupes %buildroot/%_prefix

%files
%_includedir/spirv/
%_datadir/cmake/
%_datadir/pkgconfig/*.pc
%license LICENSE

%changelog
