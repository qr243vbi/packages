#!/usr/bin/python3

import sys
from dataclasses import dataclass, field
from collections import deque
from functools import total_ordering
from pathlib import Path

import libdnf5.base
import libdnf5.repo
import libdnf5.rpm
from copr.v3 import Client, exceptions
import argparse
import rpm

# ================================================================
# Tree structures
# ================================================================

@dataclass
class TreeNode:
    source: str
    id: int
    parent: "TreeNode | None"
    depth: int
    type: int   # 1 = BuildRequires, 2 = Requires


@total_ordering
@dataclass(frozen=True)
class Child:
    type: int
    source: str

    def __lt__(self, other):
        if self.source != other.source:
            return self.source < other.source
        return self.type < other.type


# ================================================================
# Dependency graph
# ================================================================

class DependencyGraph:

    def __init__(self, base, repo_id):
        self.base = base
        self.repo_id = repo_id

        # source -> binary packages
        self.source_binaries = {}

        # provider source -> dependent sources
        self.build_graph = {}
        self.runtime_graph = {}


    # ============================================================
    # Queries
    # ============================================================

    def package_query(self):
        query = libdnf5.rpm.PackageQuery(self.base)

        query.filter_repo_id([self.repo_id])

        return query


    def source_query(self):
        query = self.package_query()

        query.filter_arch(["src"])

        return query


    # ============================================================
    # Collect binaries
    # ============================================================

    def collect_source_binaries(self):

        for package in self.package_query():

            if package.get_arch() == "src":
                continue

            source = package.get_source_name()

            if not source:
                continue

            self.source_binaries.setdefault(
                source, []
            ).append(package)



    # ============================================================
    # Provider lookup
    # ============================================================

    def providers_for(self, dependency):

        query = self.package_query()

        query.filter_provides(dependency)

        result = []

        for package in query:

            if package.get_arch() == "src":
                continue

            result.append(package)

        return result



    # ============================================================
    # Process dependency
    # ============================================================

    def process_dependency(
            self,
            dependent_source,
            dependency,
            graph):

        for provider in self.providers_for(dependency):

            provider_source = provider.get_source_name()

            if not provider_source:
                continue

            if provider_source not in self.source_binaries:
                continue

            if provider_source == dependent_source:
                continue


            graph.setdefault(
                provider_source,
                set()
            ).add(dependent_source)



    # ============================================================
    # BuildRequires
    # ============================================================

    def collect_build_requires(self):

        for package in self.source_query():

            source = package.get_name()

            for dependency in package.get_requires():

                self.process_dependency(
                    source,
                    dependency,
                    self.build_graph
                )



    # ============================================================
    # Runtime Requires
    # ============================================================

    def collect_runtime_requires(self):

        for source, packages in self.source_binaries.items():

            for package in packages:

                for dependency in package.get_requires():

                    self.process_dependency(
                        source,
                        dependency,
                        self.runtime_graph
                    )



    # ============================================================
    # Build
    # ============================================================

    def build(self):

        self.collect_source_binaries()

        self.collect_build_requires()

        self.collect_runtime_requires()



    # ============================================================
    # Lookup
    # ============================================================

    def has_source(self, source):

        return source in self.source_binaries



    def direct_build_dependencies(self, source):

        return self.build_graph.get(
            source,
            set()
        )



    def direct_runtime_dependencies(self, source):

        return self.runtime_graph.get(
            source,
            set()
        )



    def direct_dependencies(self, source):

        return (
            self.direct_build_dependencies(source)
            |
            self.direct_runtime_dependencies(source)
        )



    # ============================================================
    # Recursive affected
    # ============================================================

    def affected(
            self,
            source,
            include_build=True,
            include_runtime=True):

        result = set()

        queue = deque([source])


        while queue:

            current = queue.popleft()


            if include_build:

                for dep in self.build_graph.get(
                        current,
                        set()):

                    if dep not in result:
                        result.add(dep)
                        queue.append(dep)



            if include_runtime:

                for dep in self.runtime_graph.get(
                        current,
                        set()):

                    if dep not in result:
                        result.add(dep)
                        queue.append(dep)


        return result



    # ============================================================
    # Tree visitor
    # ============================================================

    def walk_tree(
            self,
            source,
            visitor,
            include_build=True,
            include_runtime=True):

        counter = 0

        visited = {source}


        root = TreeNode(
            source,
            counter,
            None,
            0,
            0
        )

        visitor(root)



        def walk(current, node, depth):

            nonlocal counter

            children = set()


            if include_build:

                for child in self.build_graph.get(
                        current,
                        set()):

                    children.add(
                        Child(1, child)
                    )


            if include_runtime:

                for child in self.runtime_graph.get(
                        current,
                        set()):

                    children.add(
                        Child(2, child)
                    )



            for child in sorted(children):

                if child.source in visited:
                    continue


                counter += 1

                visited.add(child.source)


                new_node = TreeNode(
                    child.source,
                    counter,
                    node,
                    depth + 1,
                    child.type
                )

                visitor(new_node)


                walk(
                    child.source,
                    new_node,
                    depth + 1
                )


        walk(
            source,
            root,
            0
        )



    # ============================================================
    # Get tree
    # ============================================================

    def get_tree(
            self,
            source,
            include_build=True,
            include_runtime=True):
        tree = {}
        def visitor(node):
            tree[node.id] = {
                "name": node.source,
                "type": node.type,
                "id": node.id,
                "children": []
            }
            if node.parent:

                tree[
                    node.parent.id
                ]["children"].append(
                    node.id
                )
        self.walk_tree(
            source,
            visitor,
            include_build,
            include_runtime
        )
        if 0 not in tree:
            return {}
        return tree
        
    @staticmethod
    def print_tree(tree):
        def print_node(parent_id, node_id, prefix="", last=True):
            node = tree[node_id]
            print(prefix, end="")
            if node_id != 0:
                print(
                    "└── " if last else "├── ",
                    end=""
                )
                if node["type"] == 1:
                    print("[B]", parent_id, end=" ")
                elif node["type"] == 2:
                    print("[R]", parent_id, end=" ")
            print(node_id, node["name"])
            children = node["children"]
            for i, child in enumerate(children):
                print_node(
                    node_id,
                    child,
                    prefix +
                    (
                        ""
                        if node_id == 0
                        else
                        ("    " if last else "│   ")
                    ),
                    i == len(children)-1
                )
        print_node(-1, 0)
        return tree


# ================================================================
# Repository loading
# ================================================================

def load_repository(base, repo_id):
    repo_sack = base.get_repo_sack()
    repo_sack.create_repos_from_system_configuration()
    repo_query = libdnf5.repo.RepoQuery(base)
    repo_query.filter_id([repo_id])
    found = False
    for repo in repo_query:
        found = True
        repo.enable()
    if not found:
        raise RuntimeError(
            f"Repository not found: {repo_id}"
        )
    repo_sack.load_repos(
        libdnf5.repo.Repo.Type_AVAILABLE
    )



# ================================================================
# Main
# ================================================================
def start(repo_id, source, print_tree=False, 
        build_requires=False, runtime_requires=False):
    base = libdnf5.base.Base()
    base.load_config()
    base.setup()
    load_repository(
        base,
        repo_id
    )
    graph = DependencyGraph(
        base,
        repo_id
    )
    graph.build()
    if not graph.has_source(source):
        if print_tree:
            print(
                f"Source package not found: {source}"
            )
        return 1
    tree = graph.get_tree(
                source,
                build_requires,
                runtime_requires
            )
    if print_tree:
            graph.print_tree(
                tree
            )
    return tree
    

def build_tree(tree, owner, project, buildid='', path = None, login = '', token = '', copr_url = 'https://copr.fedorainfracloud.org'):
    if (not login) and (not token) and (not owner):
        cli = Client.create_from_config_file()
    else:
        cli = Client({
            "username": owner,
            "token": token,
            "login": login,
            "copr_url": copr_url
        })
    if not owner:
        owner = cli.base_proxy.auth_username()
    if project:
        build_ids = {}
        if tree == 1:
            if path is not None:
                print("Creating a new build")
                bld = cli.build_proxy.create_from_file(
                    owner, 
                    project, 
                    path,
                    buildopts={"timeout": 180000}
                )
                return 0
            else:
                return 1
        else:
            if buildid.isnumeric():
                bld = {'id': int(buildid)}
            else:
                print("Submit build for", tree[0]["name"])
                if path is None:
                    bld = cli.package_proxy.build(
                        owner, 
                        project, 
                        tree[0]["name"],
                        buildopts={"timeout": 180000}
                    )
                else:
                    bld = cli.build_proxy.create_from_file(
                        owner, 
                        project, 
                        path,
                        buildopts={"timeout": 180000}
                    )
            build_ids[0] = bld['id']
            def build_package_childs(i):
                nonlocal build_ids, project, tree
                parent_id = build_ids[i]
                for u in tree[i]['children']:
                    name = tree[u]['name']
                    print("Submit build for", name) 
                    try:
                        bld = cli.package_proxy.build(
                            owner,
                            project,
                            name,
                            buildopts={"timeout": 180000, 
                                "after_build_id": parent_id}
                        )
                    except Exception as e:
                        code = 0
                        if type(e) == exceptions.CoprRequestException:
                            code = e.result.__response__.status_code
                        if code == 400:
                            try:
                                d = cli.package_proxy.get(
                                    owner,
                                    project,
                                    name
                                )
                                url = d['builds']['latest']['source_package']['url']
                                bld = cli.build_proxy.create_from_url(
                                    owner,
                                    project,
                                    url,
                                    buildopts={"timeout": 180000, 
                                        "after_build_id": parent_id}
                                )
                            except Exception as e:
                                print(type(e), e)
                                bld = {'id': parent_id}
                        else:
                            print(type(e), e)
                            bld = {'id': parent_id}
                    build_ids[u] = bld['id']
                    build_package_childs(u)
            build_package_childs(0)
            return 0

    
def get_srpm_name(path):

    ts = rpm.TransactionSet()

    with open(path, "rb") as f:
        hdr = ts.hdrFromFdno(f.fileno())

    name = hdr[rpm.RPMTAG_NAME]
    version = hdr[rpm.RPMTAG_VERSION]
    release = hdr[rpm.RPMTAG_RELEASE]

    return f"{name}-{version}-{release}.src.rpm"

def main():
    parser = argparse.ArgumentParser(
        description="Dependency tree generator"
    )

    parser.add_argument(
        "repo",
        help="Repository ID"
    )

    parser.add_argument(
        "source",
        help="Source package"
    )
    
    parser.add_argument(
        "--build",
        action="store_true",
        default=False,
        help="Build package"
    )
    
    parser.add_argument(
        "--owner",
        default="",
        help="COPR owner"
    )

    parser.add_argument(
        "--project",
        default="",
        help="COPR project"
    )
    
    parser.add_argument(
        "--id",
        default="",
        help="Id of build"
    )

    parser.add_argument(
        "--tree",
        action="store_true",
        default=True,
        help="Show dependency tree"
    )

    parser.add_argument(
        "--buildrequires",
        action="store_true",
        help="Include build requirements"
    )

    parser.add_argument(
        "--requires",
        dest="requires",
        action="store_true",
        help="Include runtime requirements"
    )
    
    parser.add_argument(
        "--login",
        dest="login",
        help="Login COPR secret"
    )
    
    parser.add_argument(
        "--copr-url",
        dest="copr_url",
        default="https://copr.fedorainfracloud.org",
        help="COPR URL"
    )
    
    parser.add_argument(
        "--token",
        dest="token",
        help="Token COPR secret"
    )

    args = parser.parse_args()
    buildid = args.id
    buildrequires = args.buildrequires
    runtime_requires = args.requires
    source = args.source
    
    path = Path(source).expanduser()
    if path.exists() and path.is_file() and path.suffix == ".src.rpm":
        source = get_srpm_name(path)
    else:
        path = None

    # Default: both enabled
    if not buildrequires and not runtime_requires:
        buildrequires = True
        runtime_requires = True

    tree = start(
        args.repo,
        args.source,
        args.tree,
        buildrequires,
        runtime_requires
    )
    if args.build:
        return build_tree(tree, args.owner, args.project, args.id, path, args.login, args.token)
    
    return 1 if tree == 1 else 0


if __name__ == "__main__":
    sys.exit(main())
