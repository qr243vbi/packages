rpm.global("commit", gh_commit("Samsung/rlottie"));

if rpm.changed() {
  rpm.release();
  rpm.version(date());
}
