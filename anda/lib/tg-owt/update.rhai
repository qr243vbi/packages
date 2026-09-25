rpm.global("commit", gh_commit("desktop-app/tg_owt"));
if rpm.changed() {
  rpm.release();
  rpm.global("commit_date", date());
}
