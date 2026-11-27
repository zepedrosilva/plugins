#!/usr/bin/env python3
"""Build the plugins hub: an index page from .claude-plugin/marketplace.json, plus each plugin's own site.

For every entry whose source is a GitHub repo owned by OWNER, the repo is cloned and, if it has
scripts/build-site.sh, that script writes the plugin's site to <out>/<plugin name>/.
Usage: python3 scripts/build-hub.py <out-dir>
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile

OWNER = "zepedrosilva"  # only these repos may run a build script in this workflow


def repo_of(source):
    """Return 'owner/repo' for a github or git-subdir source on github.com, else None."""
    if not isinstance(source, dict):
        return None
    ref = source.get("repo") if source.get("source") == "github" else source.get("url") if source.get("source") == "git-subdir" else None
    m = re.fullmatch(r"(?:https://github\.com/)?([\w.-]+/[\w.-]+?)(?:\.git)?", ref or "")
    return m.group(1) if m else None


def build_site(repo, name, out):
    """Clone repo and run its scripts/build-site.sh into out/name. Returns True when a site was written."""
    if repo.split("/")[0] != OWNER:
        print("build-hub: skip %s (%s is not owned by %s)" % (name, repo, OWNER))
        return False
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "clone", "--quiet", "--depth", "1", "https://github.com/%s.git" % repo, tmp], check=True)
        script = os.path.join(tmp, "scripts", "build-site.sh")
        if not os.path.isfile(script):
            print("build-hub: %s has no scripts/build-site.sh; listed without a site" % name)
            return False
        subprocess.run(["sh", script, os.path.abspath(os.path.join(out, name))], check=True)
    return True


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plugins for Claude Code</title>
<meta name="description" content="{desc}">
<style>
  :root {{ --bg: #FAFAF9; --text: #1C1917; --muted: #57534E; --line: #E7E5E4; --card: #FFFFFF; --link: #B4231A; color-scheme: light; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg: #1C1917; --text: #FAFAF9; --muted: #A8A29E; --line: #3A3532; --card: #262220; --link: #FE7A6B; color-scheme: dark; }} }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--text); font: 17px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }}
  main {{ max-width: 48rem; margin: 0 auto; padding: 3rem 1.25rem 4rem; }}
  h1 {{ font-size: clamp(1.8rem, 5vw, 2.4rem); margin: 0 0 .5rem; }}
  a {{ color: var(--link); }}
  .muted {{ color: var(--muted); }}
  pre, code {{ font: 15px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }}
  pre {{ background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: .9rem 1.1rem; overflow-x: auto; }}
  .plugin {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 1.25rem 1.4rem; margin: 1.25rem 0; }}
  .plugin h2 {{ margin: 0 0 .4rem; font-size: 1.3rem; }}
  .plugin p {{ margin: .4rem 0; }}
  .links a {{ margin-right: 1.1rem; }}
  footer {{ margin-top: 3rem; font-size: .95rem; }}
</style>
</head>
<body>
<main>
  <h1>Plugins for Claude Code</h1>
  <p class="muted">{desc}</p>
  <p>Add the catalog once, then install any plugin from it:</p>
  <pre>/plugin marketplace add {owner}/plugins</pre>
{items}
  <footer class="muted">Source: <a href="https://github.com/{owner}/plugins">github.com/{owner}/plugins</a></footer>
</main>
</body>
</html>
"""

ITEM = """  <section class="plugin">
    <h2>{title}</h2>
    <p>{desc}</p>
    <pre>/plugin install {name}@{market}</pre>
    <p class="links">{links}</p>
  </section>"""


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build-hub.py <out-dir>")
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "..", ".claude-plugin", "marketplace.json")) as f:
        market = json.load(f)
    items = []
    for p in market["plugins"]:
        name, e = p["name"], html.escape
        repo = repo_of(p.get("source"))
        links = []
        if repo and build_site(repo, name, out):
            links.append('<a href="%s/">Website</a>' % e(name))
        if repo:
            links.append('<a href="https://github.com/%s">Source</a>' % e(repo))
        items.append(ITEM.format(title=e(p.get("displayName") or name), desc=e(p.get("description", "")),
                                 name=e(name), market=e(market["name"]), links=" ".join(links)))
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(PAGE.format(desc=html.escape(market.get("description", "")), owner=OWNER, items="\n".join(items)))
    open(os.path.join(out, ".nojekyll"), "w").close()
    print("build-hub: wrote %s with %d plugins" % (out, len(items)))


if __name__ == "__main__":
    main()
