#!/bin/perl
use RPM2;
use File::Temp qw(tempdir);
use HTTP::Request;
use Cwd;
use LWP::UserAgent;
use MIME::Base64;

my $old_directory = Cwd::getcwd();
my $project = $ENV{OBS_PROJECT} // die "Set OBS_PROJECT";
my $user = $ENV{OBS_USER} // die "Set OBS_USER";
my $pass = $ENV{OBS_PASSWORD} // die "Set OBS_PASSWORD";

for my $file (@ARGV) {

my $pkg = RPM2->open_package($file);

my $package = $pkg->tag("name");

sub extract_rpm {
  my $rpm = shift or die "Usage: $0 file.rpm [outdir]\n";
  my $out = shift // 'out';

  mkdir $out unless -d $out;
  chdir $out or die "chdir $out failed: $!\n";
  print("\nOutdir: $out\n");

# Start cpio in the output directory and write rpm2cpio output into it
  open(my $cpio_fh, "|-", "cpio", "-idmuv") or die "Cannot start cpio: $!\n";
# Make cpio run inside $out
# Easiest: chdir before starting rpm2cpio -> cpio still writes absolute/relative paths.
  open(my $rpm2cpio_fh, "-|", "rpm2cpio", $rpm) or die "Cannot run rpm2cpio: $!\n";

  while (read($rpm2cpio_fh, my $buf, 1024)) {
    print {$cpio_fh} $buf or die "Write to cpio failed: $!\n";
  }
  close $rpm2cpio_fh or die "rpm2cpio failed: $!\n";
  close $cpio_fh      or die "cpio failed: $!\n";
}

print($pkg->filename);


my $tmpdir = tempdir(CLEANUP => 1);
extract_rpm($pkg->filename, $tmpdir);

chdir($tmpdir);


my $base = "https://api.opensuse.org/source/$project/$package";

my $ua = LWP::UserAgent->new(
    agent => "perl-script/1.0",
    timeout => 30,
    ssl_opts => { verify_hostname => 1 },
);

# Basic auth header
my $req = HTTP::Request->new('GET', $base);
$req->authorization_basic($user, $pass);

ret_loop:
# GET list

my $res = $ua->request( $req );

my $res_code = $res->code;

if ($res_code == 404){
  my $uri = URI->new("https://api.opensuse.org/source/$project/$package");
  $uri->query_form(
    cmd       => 'copy',
    oproject  => "$project",
    opackage  => 'simple-package',
  );
  my $req = HTTP::Request->new('POST', $uri->as_string);
  $req->authorization_basic($user, $pass);

  my $res = $ua->request( $req );
  if ($res->code == 200){
    goto ret_loop;
  } else {
    goto end_loop;
  }
} elsif ($res_code == 401) {
  goto end_loop;
}

my $body = $res->decoded_content;

# Extract names from <entry ... name="...">
my @names = ($body =~ m/<entry[^>]*\sname="([^"]+)"/g);

for my $name (@names) {
    my $url = "$base/$name";
    my $req = HTTP::Request->new('DELETE', $url);
    $req->authorization_basic($user, $pass);

    my $r = $ua->request($req);
    if ($r->code == 200) {
        print "Deleted $project/$package/$name\n";
    } else {
        warn "Failed to delete $name from $project/$package: " . $r->status_line . "\n";
    }
}

my $ua = LWP::UserAgent->new;

opendir(my $dh, '.') or die "Can't opendir .: $!\n";
my @files = grep { -f $_ } readdir($dh);
closedir($dh);

for my $file (@files) {
    open my $fh, '<', $file or die "Can't open $file: $!\n";
    binmode($fh);

    local $/;
    my $data = <$fh>;
    close $fh;

    my $url = "https://api.opensuse.org/source/$project/$package/$file";

    my $req = HTTP::Request->new('PUT', $url);
    $req->authorization_basic($user, $pass);
    $req->content($data);

    my $res = $ua->request($req);
    if ($res->is_success) {
        print "Added: $project/$package/$file (" . $res->status_line . ")\n";
    } else {
        warn "FAIL: $project/$package/$file  (" . $res->status_line . ")\n";
    }
}



end_loop:

}
