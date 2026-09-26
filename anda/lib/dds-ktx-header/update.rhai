rpm.global("commit", gh_commit("septag/dds-ktx"));
if rpm.changed() {
  rpm.release();
  rpm.global("commit_date", date());
}
