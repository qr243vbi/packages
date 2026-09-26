let grammar = gh_rawfile("KhronosGroup/SPIRV-Headers", "main", "include/spirv/unified1/spirv.core.grammar.json");

let data = json(grammar);

let version = `${data.major_version}.${data.minor_version}.${data.revision}`;

rpm.version(version);

rpm.global("commit", gh_commit("KhronosGroup/SPIRV-Headers"));

if rpm.changed() {
    rpm.release();
    rpm.global("commit_date", date());
}

