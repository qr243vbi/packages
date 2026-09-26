%global commit re
%global commit_date da
%global archive dds-ktx-%{commit}

Name:           dds-ktx-header
Version:        %{commit_date}.%{commit}
Release:        0
Summary:        Single header "no-allocation" KTX/DDS file reader
License:        BSD-2-Clause
URL:            https://github.com/septag/dds-ktx
Source0:        %{url}/archive/%{commit}.tar.gz#/%{archive}.tar.gz

%description
dds-ktx: Portable single header DDS/KTX reader for C/C++

%prep
%autosetup -p1 -n %{archive}

%build


%install
install -Dm644 dds-ktx.h %{buildroot}%{_includedir}/dds-ktx.h

%files
%license LICENSE
%doc README.md
%{_includedir}/dds-ktx.h

