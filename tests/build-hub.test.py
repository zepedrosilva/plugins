#!/usr/bin/env python3
"""Checks for scripts/build-hub.py's source parsing, which decides which repos may run a build script."""
import importlib.util
import os

spec = importlib.util.spec_from_file_location("hub", os.path.join(os.path.dirname(__file__), "..", "scripts", "build-hub.py"))
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)

cases = [
    ({"source": "git-subdir", "url": "zepedrosilva/brand-studio", "path": "plugin"}, "zepedrosilva/brand-studio"),
    ({"source": "git-subdir", "url": "https://github.com/zepedrosilva/brand-studio.git", "path": "plugin"}, "zepedrosilva/brand-studio"),
    ({"source": "github", "repo": "zepedrosilva/x"}, "zepedrosilva/x"),
    ({"source": "git-subdir", "url": "https://gitlab.com/a/b.git", "path": "p"}, None),
    ({"source": "npm", "package": "x"}, None),
    ("./local", None),
    ({"source": "github", "repo": "a/b; rm -rf /"}, None),
]
for source, want in cases:
    got = hub.repo_of(source)
    assert got == want, "%r: got %r, want %r" % (source, got, want)
assert not hub.build_site("someone-else/x", "x", "/nonexistent"), "a repo outside OWNER must not be built"
print("build-hub tests: %d passed" % (len(cases) + 1))
