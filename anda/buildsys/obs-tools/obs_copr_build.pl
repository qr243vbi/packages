#!/usr/bin/perl
use File::ChangeNotifyd;
use RPM2;
my $RETRIES=int($ENV{'RETRIES'}) || 60;
my $TIMEOUT=int($ENV{'TIMEOUT'}) || 60;
my $outdir=$ENV{'outdir'} || `rpm --eval %{_srcrpmdir}`;

use Data::Dumper;

system('pkg_check_available', `obs_service_pkg_list`, "${RETRIES}", "${TIMEOUT}");
system('obs_pkg_install');
my $watcher =
    File::ChangeNotify->instantiate_watcher
        ( directories => [ ${outdir} ],
          filter      => qr/\.src\.rpm$/,
        );

system('obs_service_build', "-D_srcrpmdir ${outdir}", '--bs');

my @dependencies;
my @packages;

if ( my @events = $watcher->new_events ) {
   for my $path (@events){
      $path = $path->path;
      push @packages, $path;
      $path = RPM2->open_package($path);
# Get the list of dependencies
      my @requires = $path->requires();
# Print each dependency
      foreach my $dep (@requires) {
         if (!("$dep" =~ /rpmlib\(\w+\)/)) {
            push @dependencies, $dep;
         };
      };
   };
};

system('pkg_check_available', join("\n", @dependencies), "${RETRIES}", "${TIMEOUT}");

if (defined(%ENV{'BUILD_BINARY_PACKAGES'})){
    my $rpmoutdir=$ENV{'rpmoutdir'} || `rpm --eval %{_rpmdir}`;
    for my $package (@packages){
        system('rpmbuild', '--rebuild', $package, "-D_rpmdir "..$rpmoutdir);
    }
}
