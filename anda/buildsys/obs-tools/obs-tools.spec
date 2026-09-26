Name: obs-tools
Version: 46
Release: 1.75
License: GPLv3
Summary: %{name}
Source0: obs_service_run.sh
Source1: obs_service_list.sh
Source2: obs_copr_build.pl
Source3: obs_dnf_install.sh
Source4: obs_git_build.sh
Source5: obs_service_build.sh
Source6: obs_local_run.sh
Source7: pkg_check_available.sh
Source8: obs_service_pkg_list.sh
Source9: obs_repos_list.sh
Source10: obs_pkg_list.sh
Source11: obs_remote_run.sh
Source12: obs_mockbuild.sh
Source13: obs_edit.sh
Source14: obs_tools.cpp
Source15: CMakeLists.txt
Source16: obs_edit.h
Source17: obs_tools.h
Source18: obs_edit.qml
Source19: obs_edit.qrc
Source20: obs_edit.cpp

Requires: cpio

%global __perl_requires %{_rpmconfigdir}/perl.req
BuildRequires: (rpm-build-perl or perl-generators)
BuildRequires: sed
BuildRequires: sudo
BuildRequires: cmake(Qt6)
BuildRequires: cmake(Qt6Xml)
BuildRequires: cmake(Qt6Qml)
BuildRequires: cmake(Qt6Gui)
BuildRequires: gcc-c++
BuildRequires: cmake

%description
%{summary}.

%build
cp %{SOURCE13} ./
cp %{SOURCE14} ./
cp %{SOURCE15} ./
cp %{SOURCE16} ./
cp %{SOURCE17} ./
cp %{SOURCE18} ./
cp %{SOURCE19} ./
cp %{SOURCE20} ./
%cmake
%cmake_build
 
%install
%cmake_install

install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/obs_service_run
install -Dm755 %{SOURCE1} %{buildroot}%{_bindir}/obs_service_list
install -Dm755 %{SOURCE13} %{buildroot}%{_bindir}/obs_edit
install -Dm755 %{SOURCE8} %{buildroot}%{_bindir}/obs_service_pkg_list
install -Dm755 %{SOURCE9} %{buildroot}%{_bindir}/obs_repos_list
install -Dm755 %{SOURCE10} %{buildroot}%{_bindir}/obs_pkg_list
install -Dm755 %{SOURCE2} %{buildroot}%{_bindir}/obs_copr_build
install -Dm755 %{SOURCE11} %{buildroot}%{_bindir}/obs_remote_run
install -Dm755 %{SOURCE12} %{buildroot}%{_bindir}/obs_mockbuild
mkdir -pv %{buildroot}%{_sysconfdir}/sudoers.d
cat << EOF > %{buildroot}%{_sysconfdir}/sudoers.d/mockbuild
mockbuild ALL=(ALL) NOPASSWD: ALL
EOF

%{lua:

exclude_package_managers = {}
only_package_managers = {}
exclude_all = false

if rpm.isdefined("EXCLUDE_PACKAGE_MANAGERS")
then
for word in rpm.expand("%{EXCLUDE_PACKAGE_MANAGERS}"):gmatch("%S+")
do
    exclude_package_managers[word] = true
end
end

if rpm.isdefined("ONLY_PACKAGE_MANAGERS")
then
for word in rpm.expand("%{ONLY_PACKAGE_MANAGERS}"):gmatch("%S+")
do
    only_package_managers[word] = true
    exclude_all = true
end
end

allowed_package_manager = function(word)
  if exclude_all
  then
     return not not only_package_managers[word]
  else
     return not exclude_package_managers[word]
  end
end

package_manager_string = '/'

for key, value in pairs({ dnf = '--refresh provides', dnf5 = '--refresh provides', zypper = 'search --provides --match-exact', microdnf = 'provides' })
do
if allowed_package_manager(key)
then
rpm.define('pkg_manager_name '..key)
rpm.define('pkg_manager_provides '..key..' '..value)
print( rpm.expand( [[
  cat %{SOURCE3} | sed "s/dnf/%{pkg_manager_name}/g;" > %{buildroot}%{_bindir}/obs_"%{pkg_manager_name}"_install
  chmod 755 %{buildroot}%{_bindir}/obs_"%{pkg_manager_name}"_install

  cat %{SOURCE7} | sed "s/dnf provides/%{pkg_manager_provides}/g;" > %{buildroot}%{_bindir}/"%{pkg_manager_name}_check_available"
  chmod 755 %{buildroot}%{_bindir}/"%{pkg_manager_name}_check_available"
]] ))

package_manager_string = package_manager_string .. '/' .. key .. '/'

end
end

rpm.define('INCLUDE_PACKAGE_MANAGERS '.. package_manager_string)
}
install -Dm755 %{SOURCE4} %{buildroot}%{_bindir}/obs_git_build
install -Dm755 %{SOURCE5} %{buildroot}%{_bindir}/obs_service_build
install -Dm755 %{SOURCE6} %{buildroot}%{_bindir}/obs_local_run

%files
%attr(755, root, root) %{_bindir}/obs_tools
%attr(755, root, root) %{_bindir}/obs_service_run
%attr(755, root, root) %{_bindir}/obs_remote_run
%attr(755, root, root) %{_bindir}/obs_service_list
%attr(755, root, root) %{_bindir}/obs_local_run
%attr(755, root, root) %{_bindir}/obs_pkg_list
%attr(755, root, root) %{_bindir}/obs_service_pkg_list
%attr(755, root, root) %{_bindir}/obs_repos_list
%if %{defined NO_COPR_TOOLS}
%exclude %{_bindir}/obs_copr_build
%else
%package copr
Summary: %{name}
Requires: perl
BuildArch: noarch
Requires: %{name}-pkg
Requires: %{name}-build
Requires: (%{_bindir}/rpmbuild or rpm-build or rpmbuild)

%description copr
%{summary}.

%files copr
%attr(755, root, root) %{_bindir}/obs_copr_build
%endif

%{lua:
for p in rpm.expand("%{INCLUDE_PACKAGE_MANAGERS}"):gmatch("[^/]+")
do
rpm.define("pkg_manager_name "..p)
print(rpm.expand([[

%%package %{pkg_manager_name}-pkg
Provides: %{name}-pkg
BuildArch: noarch
Summary: %{name}
Requires: %{name}
Requires: (%{pkg_manager_name} or %{_bindir}/%{pkg_manager_name})
Requires: (%{_bindir}/bash or bash)
Requires(post): update-alternatives
Requires(postun): update-alternatives

%%description %{pkg_manager_name}-pkg
%{summary}.

%%post %{pkg_manager_name}-pkg
update-alternatives --install '%{_bindir}/obs_pkg_install' obs_pkg_install '%{_bindir}/obs_%{pkg_manager_name}_install' 25

%%postun %{pkg_manager_name}-pkg
update-alternatives --remove obs_pkg_install '%{_bindir}/obs_%{pkg_manager_name}_install' || :

%%files %{pkg_manager_name}-pkg
%%attr(755, root, root) %{_bindir}/obs_%{pkg_manager_name}_install


%%package %{pkg_manager_name}-pkg-checkaval
Provides: %{name}-pkg-checkaval
BuildArch: noarch
Summary: %{name}
Requires: (%{pkg_manager_name} or %{_bindir}/%{pkg_manager_name})
Requires: (%{_bindir}/bash or bash)
Requires(post): update-alternatives
Requires(postun): update-alternatives

%%description %{pkg_manager_name}-pkg-checkaval
%{summary}.

%%post %{pkg_manager_name}-pkg-checkaval
update-alternatives --install '%{_bindir}/pkg_check_available' pkg_check_available '%{_bindir}/%{pkg_manager_name}_check_available' 25

%%postun %{pkg_manager_name}-pkg-checkaval
update-alternatives --remove pkg_check_available '%{_bindir}/%{pkg_manager_name}_check_available' || :

%%files %{pkg_manager_name}-pkg-checkaval
%%attr(755, root, root) %{_bindir}/%{pkg_manager_name}_check_available

]]))
end
}

%package git
BuildArch: noarch
Summary: %{name}
Requires: %{name}-pkg
Requires: (%{_bindir}/git or git)
Requires: (%{_bindir}/bash or bash)

%description git
%{summary}.

%files git
%attr(755, root, root) %{_bindir}/obs_git_build

%package build
BuildArch: noarch
Requires: (%{_bindir}/bash or bash)
Summary: %{name}
Requires: %{name}
Requires: rpm-build

%description build
%{summary}.

%files build
%attr(755, root, root) %{_bindir}/obs_service_build


%package edit
Summary: %{name}
Requires: %{name}
Requires: (%{_bindir}/bash or bash)

%description edit
%{summary}.

%files edit
%attr(755, root, root) %{_bindir}/obs_edit
%attr(755, root, root) %{_libdir}/libobs_edit.so

%package mockbuild
Summary: obs tools mockbuild
Requires: obs-tools-pkg-checkaval
Requires: obs-tools-pkg
Requires: obs-tools
Requires: obs-tools-build
Requires: pam
Requires: rpm-build
Requires: sudo
Requires: bash
BuildArch: noarch


%description mockbuild
used to leverage mockbuild sudo

%files mockbuild
%attr(644, root, root) %{_sysconfdir}/sudoers.d/mockbuild
%attr(755, root, root) %{_bindir}/obs_mockbuild
