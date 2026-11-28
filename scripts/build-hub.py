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


# Styled after zepedro.com (its fonts, colours and label rail), so the hub reads as part of that site.
LOGO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 196 129"><title>José Silva (aka Zé Pedro)</title><path d="m178.19779,7.34586c11.74545,8.47277 17.22578,19.59523 16.96791,33.68493c-0.17626,9.63098 0.02482,19.26824 -0.04573,28.90194c-0.1556,21.2457 -16.96249,37.90384 -38.25067,37.95775c-9.96648,0.02526 -19.9331,0.00431 -30.14097,0.00431c0,-11.08596 0,-21.76598 0,-33.10015c8.6505,0 17.25562,0.02821 25.86046,-0.00836c7.76451,-0.03298 9.20987,-1.49272 9.23266,-9.22422c0.02171,-7.36726 0.01625,-14.73468 0.00157,-22.10199c-0.01603,-8.04105 -1.20263,-9.26498 -9.0309,-9.28592c-7.36727,-0.01971 -14.73468,-0.01404 -22.102,-0.0016c-7.97681,0.01345 -9.25943,1.21535 -9.26985,9.13786c-0.03453,26.2579 -0.01313,52.51589 -0.01317,78.77384c0,1.86166 0.00002,3.72331 0.00002,5.90378c-11.20032,0 -22.01803,0 -33.30587,0c0,-3.36497 0,-6.53223 0,-9.6995c0,-26.25795 -0.02503,-52.51593 0.00779,-78.77383c0.02707,-21.65775 16.73724,-38.39935 38.31187,-38.44163c9.82308,-0.01926 19.65066,0.17868 29.46795,-0.06022c8.01418,-0.19501 15.27066,1.8251 22.30894,6.33301l-0.00001,0z"/><path d="m40.46205,107.83222c-6.61008,0 -12.65315,0.013 -18.69614,-0.00309c-8.78196,-0.02334 -11.55495,-3.59903 -9.07658,-12.1633c3.66209,-12.6547 7.53865,-25.24729 11.32042,-37.86737c2.31094,-7.71181 4.61543,-15.42555 7.09032,-23.69836c-10.41015,0 -20.13983,0 -30.10007,0c0,-11.08964 0,-21.76683 0,-33.08348c3.9333,0 7.82307,-0.00001 11.71284,0c16.24065,0.00007 32.4815,-0.04859 48.72185,0.02027c8.43457,0.03575 11.02863,3.29134 8.66284,11.43788c-5.66792,19.51747 -11.59359,38.96007 -17.41024,58.43438c-0.31371,1.05025 -0.58167,2.11418 -1.01897,3.71313c10.51451,0 20.60529,0 31.01543,0c0,11.13585 0,21.81463 0,33.20993c-13.88708,0 -27.77087,0 -42.22171,0l0.00001,0.00001z"/></svg>'

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plugins · José Silva</title>
<meta name="description" content="{desc}">
<link rel="icon" href="https://zepedro.com/favicon.ico" type="image/x-icon">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Instrument+Serif&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  :root {{ --paper: #ffffff; --ink: #0a0a0a; --ink-2: #1a1a1a; --mute: #a1a1a1; --mute-2: #6f6f6f; --line: #e8e8e8; --accent: #2563eb;
    --mono: 'JetBrains Mono', ui-monospace, monospace; --sans: 'Inter', system-ui, sans-serif; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--paper); color: var(--ink); font: 15px/1.58 var(--sans); -webkit-font-smoothing: antialiased; }}
  a {{ color: inherit; text-decoration: none; }}
  .page {{ max-width: 1200px; margin: 0 auto; padding: 48px 48px 72px; }}
  .header {{ display: flex; align-items: center; justify-content: space-between; }}
  .logo svg {{ height: 28px; fill: var(--ink); display: block; }}
  .nav {{ display: flex; gap: 24px; font: 11.5px var(--mono); letter-spacing: .14em; text-transform: uppercase; color: var(--mute-2); }}
  .nav a:hover {{ color: var(--ink); }}
  h1 {{ font: 400 76px/0.95 'Instrument Serif', Georgia, serif; letter-spacing: -0.04em; margin: 56px 0 0; }}
  .tagline {{ font-size: 24px; font-weight: 500; line-height: 1.3; letter-spacing: -0.02em; margin: 20px 0 0; max-width: 46rem; }}
  .tagline .muted {{ color: var(--mute); font-weight: 400; }}
  .section {{ margin-top: 56px; padding-top: 28px; border-top: 1px solid var(--line); display: grid; grid-template-columns: 140px 1fr; gap: 32px; }}
  .label {{ font: 11.5px var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--mute-2); padding-top: 6px; }}
  pre {{ margin: 0; background: #fafafa; border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; overflow-x: auto; font: 13.5px/1.55 var(--mono); }}
  .plugin {{ padding: 20px 0; border-bottom: 1px solid var(--line); }}
  .plugin:first-child {{ padding-top: 0; }}
  .plugin:last-child {{ border-bottom: none; }}
  .plugin h2 {{ font-size: 22px; font-weight: 600; letter-spacing: -0.02em; margin: 0 0 6px; }}
  .plugin p {{ margin: 0 0 12px; color: var(--ink-2); max-width: 44rem; }}
  .links {{ display: flex; gap: 22px; margin-top: 12px; font: 13px var(--mono); letter-spacing: .06em; text-transform: uppercase; color: var(--mute-2); }}
  .links a:hover {{ color: var(--accent); }}
  .footer {{ margin-top: 56px; padding-top: 24px; border-top: 1px solid var(--line); display: flex; gap: 14px; align-items: center;
    font: 11.5px var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--mute-2); }}
  .footer .logo svg {{ height: 16px; }}
  .footer a:hover {{ color: var(--ink); }}
  .section > div {{ min-width: 0; }}
  .footer {{ flex-wrap: wrap; row-gap: 6px; }}
  @media (max-width: 900px) {{ .section {{ grid-template-columns: 1fr; gap: 12px; }} h1 {{ font-size: 58px; }} }}
  @media (max-width: 640px) {{ .page {{ padding: 32px 24px 56px; }} .tagline {{ font-size: 20px; }} }}
</style>
</head>
<body>
<main class="page">
  <header class="header">
    <a href="https://zepedro.com/" class="logo" aria-label="José Silva, home">{logo}</a>
    <nav class="nav" aria-label="Primary">
      <a href="https://zepedro.com/">Home</a>
      <a href="https://blog.zepedro.com/">Writing</a>
      <a href="https://github.com/{owner}/plugins">Source</a>
    </nav>
  </header>
  <h1>Plugins</h1>
  <p class="tagline">{desc} <span class="muted">Each one lives in its own repository.</span></p>
  <section class="section">
    <span class="label">Add the catalog</span>
    <div><pre>/plugin marketplace add {owner}/plugins</pre></div>
  </section>
  <section class="section">
    <span class="label">Plugins</span>
    <div>
{items}
    </div>
  </section>
  <footer class="footer">
    <a href="https://zepedro.com/" class="logo" aria-label="José Silva, home">{logo}</a>
    <span>© José Silva</span><span>·</span><a href="https://zepedro.com/">zepedro.com</a>
  </footer>
</main>
</body>
</html>
"""

ITEM = """      <article class="plugin">
        <h2>{title}</h2>
        <p>{desc}</p>
        <pre>/plugin install {name}@{market}</pre>
        <div class="links">{links}</div>
      </article>"""


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
            links.append('<a href="%s/">Website ↗</a>' % e(name))
        if repo:
            links.append('<a href="https://github.com/%s">Source ↗</a>' % e(repo))
        items.append(ITEM.format(title=e(p.get("displayName") or name), desc=e(p.get("description", "")),
                                 name=e(name), market=e(market["name"]), links=" ".join(links)))
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(PAGE.format(desc=html.escape(market.get("description", "")), owner=OWNER, logo=LOGO, items="\n".join(items)))
    open(os.path.join(out, ".nojekyll"), "w").close()
    print("build-hub: wrote %s with %d plugins" % (out, len(items)))


if __name__ == "__main__":
    main()
