rpm.global("commit", gh_commit("tdlib/td"));
if rpm.changed() {
  rpm.release();
  rpm.global("commit_date", date());
}
