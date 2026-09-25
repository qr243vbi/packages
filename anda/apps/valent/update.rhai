rpm.global("commit", gh_commit("andyholmes/valent"));
rpm.global("libgnome", gitlab_commit("gitlab.gnome.org", "1758", "master"));
if rpm.changed() {
    rpm.release();
    rpm.global("commit_date", date());
}

