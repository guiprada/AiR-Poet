#!/usr/bin/env python3
"""
looking_glass — AiR-Poet project navigator.

    ./air_vm looking_glass/looking_glass.air [root=./] [port=8000]

Scans the given root directory for AiR-Poet components (.meta / .air / .py)
and serves a hypertext interface identical to docs_server.py, but rooted at
the supplied path instead of the script's own directory.
"""
import html as _html
import json
import re
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# ── CLI args ───────────────────────────────────────────────────────────────────
# sys.argv is set by air_vm: [looking_glass.py, root?, port?]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).parent.parent
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8000


# ── .meta parsing ──────────────────────────────────────────────────────────────

def parse_meta(text: str) -> dict:
    r = {}
    for key in ('name', 'type'):
        m = re.search(rf'^{key}:\s*"([^"]*)"', text, re.MULTILINE)
        if m:
            r[key] = m.group(1)
    m = re.search(r'about:\s*"\n(.*?)\n"', text, re.DOTALL)
    if not m:
        m = re.search(r'about:\s*"([^"]*)"', text)
    if m:
        r['about'] = m.group(1).strip()
    return r


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


# ── Project scan ───────────────────────────────────────────────────────────────

def _make_component(cid: str, path: Path, top=False) -> dict:
    files = {}
    if path.exists():
        for f in sorted(path.iterdir()):
            if f.is_file() and not f.name.startswith(('.', '_')):
                files[f.name] = f
    meta_f = path / f'{cid}.meta'
    meta = parse_meta(meta_f.read_text('utf-8', errors='replace')) if meta_f.exists() else {}
    return {'id': cid, 'path': path, 'files': files, 'meta': meta, 'top': top}


def scan_components() -> list:
    air = ROOT / 'air'
    result = []

    if air.exists():
        top_files = {f.name: f for f in sorted(air.iterdir())
                     if f.is_file() and not f.name.startswith(('.', '_'))}
        meta = (parse_meta((air / 'air.meta').read_text('utf-8', errors='replace'))
                if (air / 'air.meta').exists() else {})
        result.append({'id': 'air', 'path': air, 'files': top_files, 'meta': meta, 'top': True})
        for sub in sorted(air.iterdir()):
            if sub.is_dir() and not sub.name.startswith(('.', '_')):
                result.append(_make_component(sub.name, sub))

    for name in ('air_meta', 'looking_glass'):
        d = ROOT / name
        if d.exists() and d.is_dir():
            result.append(_make_component(name, d))

    return result


def scan_docs() -> list:
    docs = []
    for name in ('air_poet.meta', 'ARCHITECTURE.md', 'TODO.md',
                 'CODEBASE_ANALYSIS.md', 'bootstrap_meta.meta'):
        f = ROOT / name
        if f.exists():
            docs.append(f)
    for d in (ROOT / 'docs', ROOT / 'lost_and_found', ROOT / 'test_programs'):
        if d.exists():
            for f in sorted(d.rglob('*')):
                if f.is_file() and not f.name.startswith('.'):
                    docs.append(f)
    return docs


# ── CSS ────────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --bg: #f5f5f7; --card: #fff; --border: #e0e0e0;
  --sidebar: #1e1e2e; --sidebar-fg: #cdd6f4; --sidebar-hi: #89b4fa;
  --accent: #4f8ef7; --code-bg: #1e1e2e; --code-fg: #cdd6f4;
  --text: #1a1a2e; --muted: #666;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui,-apple-system,sans-serif; background: var(--bg);
       color: var(--text); display: flex; min-height: 100vh; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
#sb { width: 210px; min-width: 210px; background: var(--sidebar);
      color: var(--sidebar-fg); display: flex; flex-direction: column;
      position: sticky; top: 0; height: 100vh; overflow-y: auto; padding-bottom: 1rem; }
#sb h1 { font-size: 1.05rem; padding: 1.2rem 1.2rem 1rem; color: #fff;
          border-bottom: 1px solid #333; white-space: nowrap; }
#sb h1 em { color: var(--sidebar-hi); font-style: normal; }
.ns { padding: 0.8rem 1.2rem 0.3rem; font-size: 0.68rem; text-transform: uppercase;
      letter-spacing: .1em; color: #555; }
.nl { display: block; padding: .3rem 1.2rem; font-size: .84rem;
      color: var(--sidebar-fg); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nl:hover, .nl.active { color: var(--sidebar-hi); background: rgba(137,180,250,.12);
                         text-decoration: none; }
#main { flex: 1; padding: 2rem 2.5rem; overflow-x: hidden; max-width: 980px; }
h2 { font-size: 1.5rem; margin-bottom: .4rem; }
h3 { font-size: 1rem; margin: 1.4rem 0 .5rem; color: #444; }
.sub { color: var(--muted); font-size: .9rem; margin-bottom: 1.8rem; }
.bc { font-size: .82rem; color: var(--muted); margin-bottom: 1.4rem; }
.bc a { color: var(--accent); }
.grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(240px,1fr));
        gap: .9rem; margin-bottom: 2rem; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
        padding: 1rem 1.1rem; transition: box-shadow .15s; display: block;
        color: inherit; text-decoration: none !important; }
.card:hover { box-shadow: 0 3px 12px rgba(0,0,0,.1); }
.card-title { font-weight: 600; font-size: .96rem; margin-bottom: .3rem; }
.card-about { font-size: .8rem; color: var(--muted); line-height: 1.4; }
.tag { display: inline-block; font-size: .66rem; padding: .15em .5em; border-radius: 3px;
       font-weight: 700; vertical-align: middle; }
.t-module { background: #d8f5d8; color: #217a21; }
.t-system { background: #d0f0f8; color: #1a6a7a; }
.t-meta   { background: #ede0ff; color: #6030a0; }
.t-test   { background: #ffe0e0; color: #900000; }
.t-other  { background: #eee;    color: #555;    }
.file-group { margin-bottom: 1.8rem; }
.file-header { display: flex; align-items: center; gap: .6rem;
               font-size: .78rem; color: var(--muted); margin-bottom: .4rem; font-family: monospace; }
.file-header a { color: var(--accent); }
.about-block { background: var(--card); border: 1px solid var(--border); border-radius: 6px;
               padding: .9rem 1.1rem; margin-bottom: 1.4rem;
               font-size: .88rem; line-height: 1.65; white-space: pre-wrap; color: #333; }
pre { background: var(--code-bg); color: var(--code-fg); padding: 1rem 1.1rem;
      border-radius: 6px; overflow-x: auto; max-height: 480px;
      font-size: .78rem; line-height: 1.5; tab-size: 4; }
.editor-wrap { position: relative; margin-bottom: 1rem; }
textarea.editor { width: 100%; background: var(--code-bg); color: var(--code-fg);
  padding: 1rem 1.1rem; border-radius: 6px; border: none; outline: none;
  font-family: 'JetBrains Mono','Fira Code','Consolas',monospace; font-size: .78rem;
  line-height: 1.5; tab-size: 4; resize: vertical; min-height: 260px; }
textarea.editor:focus { box-shadow: 0 0 0 2px var(--accent); }
.save-bar { display: flex; align-items: center; gap: .8rem; margin-bottom: 1.4rem; }
.btn { padding: .35rem .9rem; border-radius: 4px; font-size: .82rem; cursor: pointer;
       border: 1px solid var(--accent); background: var(--accent); color: #fff; font-weight: 500; }
.btn:hover { opacity: .85; }
#status { font-size: .82rem; transition: opacity .4s; opacity: 0; }
.doc-list { list-style: none; }
.doc-list li { padding: .28rem 0; border-bottom: 1px solid var(--border); font-size: .88rem; }
"""

_SAVE_JS = """<script>
async function _saveFile(path, taId, statusId) {
  const content = document.getElementById(taId).value;
  const s = document.getElementById(statusId);
  try {
    const r = await fetch('/save?p=' + encodeURIComponent(path), {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'content=' + encodeURIComponent(content)
    });
    const j = await r.json();
    s.textContent = j.ok ? 'Saved' : 'Error: ' + j.error;
    s.style.color = j.ok ? '#a6e3a1' : '#f38ba8';
  } catch(e) { s.textContent = 'Network error'; s.style.color = '#f38ba8'; }
  s.style.opacity = '1';
  setTimeout(() => s.style.opacity = '0', 2500);
}
</script>"""


def h(s) -> str:
    return _html.escape(str(s))


def type_tag(t: str) -> str:
    if not t:
        return ''
    cls = {'module': 't-module', 'system': 't-system', 'meta': 't-meta',
           'test': 't-test'}.get(t, 't-other')
    return f'<span class="tag {cls}">{h(t)}</span>'


def _sidebar(active='') -> str:
    comps = scan_components()
    docs  = scan_docs()
    comp_links = ''.join(
        f'<a class="nl{" active" if c["id"] == active else ""}" href="/component/{c["id"]}">'
        f'{h(c["meta"].get("name", c["id"]))}</a>'
        for c in comps
    )
    doc_links = ''.join(
        f'<a class="nl" href="/file?p={rel(f)}">{h(f.name)}</a>'
        for f in docs[:10]
    )
    return f"""<nav id="sb">
  <h1>AiR-<em>Poet</em></h1>
  <span class="ns">Components</span>
  {comp_links}
  <span class="ns">Docs</span>
  {doc_links}
</nav>"""


def page(title: str, body: str, active='') -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{h(title)} — Looking Glass</title>
  <style>{CSS}</style>
</head>
<body>
{_sidebar(active)}
<main id="main">
{body}
</main>
{_SAVE_JS}
</body>
</html>"""


_ROLE_ORDER = {'.meta': 0, '.air': 1, '.py': 2, '.md': 3, '.txt': 4}

def _file_role_key(name: str) -> tuple:
    p = Path(name)
    base, ext = p.stem, p.suffix
    return (int(base.startswith('plan_')) + int(base.startswith('test')) * 2,
            _ROLE_ORDER.get(ext, 9), name)


# ── Page generators ────────────────────────────────────────────────────────────

def index_page() -> str:
    comps = scan_components()
    docs  = scan_docs()
    cards = ''.join(
        f'<a class="card" href="/component/{c["id"]}">'
        f'<div class="card-title">{h(c["meta"].get("name", c["id"]))} '
        f'{type_tag(c["meta"].get("type",""))}</div>'
        f'<div class="card-about">{h((c["meta"].get("about","") or "")[:220])}</div>'
        f'</a>'
        for c in comps
    )
    doc_items = ''.join(
        f'<li><a href="/file?p={rel(f)}">{h(rel(f))}</a></li>'
        for f in docs
    )
    return page('Home', f"""
<h2>Looking Glass</h2>
<p class="sub">Scanning: {h(str(ROOT))}</p>
<div class="grid">{cards}</div>
<h3>Documentation</h3>
<ul class="doc-list">{doc_items}</ul>
""")


def component_page(cid: str) -> str:
    comps = scan_components()
    c = next((x for x in comps if x['id'] == cid), None)
    if not c:
        return page('Not found', '<p>Component not found. <a href="/">Home</a></p>')

    name  = c['meta'].get('name', cid)
    about = c['meta'].get('about', '')
    about_html = f'<div class="about-block">{h(about)}</div>' if about else ''

    files_html = ''
    for i, fname in enumerate(sorted(c['files'], key=_file_role_key)):
        fpath = c['files'][fname]
        try:
            content = fpath.read_text('utf-8', errors='replace')
        except Exception as e:
            content = f'(error: {e})'
        frel  = rel(fpath)
        ta_id = f'ed-{cid}-{i}'
        st_id = f'st-{cid}-{i}'
        nlines = max(6, content.count('\n') + 2)
        files_html += (
            f'<div class="file-group">'
            f'<div class="file-header"><a href="/file?p={frel}">{h(fname)}</a>'
            f'  <button class="btn" style="padding:.1rem .5rem;font-size:.7rem"'
            f'   onclick="_saveFile({json.dumps(frel)},{json.dumps(ta_id)},{json.dumps(st_id)})">'
            f'Save</button>'
            f'  <span id="{st_id}" style="font-size:.75rem;transition:opacity .4s;opacity:0"></span>'
            f'</div>'
            f'<textarea id="{ta_id}" class="editor" spellcheck="false" rows="{nlines}">{h(content)}</textarea>'
            f'</div>'
        )

    return page(name, f"""
<div class="bc"><a href="/">Home</a> › {h(name)}</div>
<h2>{h(name)} {type_tag(c["meta"].get("type",""))}</h2>
{about_html}
{files_html}
""", active=cid)


def _safe_path(path_str: str):
    try:
        p = (ROOT / path_str).resolve()
        p.relative_to(ROOT.resolve())
        return p
    except Exception:
        return None


def file_page(path_str: str) -> str:
    p = _safe_path(path_str)
    if not p or not p.exists() or not p.is_file():
        return page('Not found', '<p>File not found. <a href="/">Home</a></p>')
    try:
        content = p.read_text('utf-8', errors='replace')
    except Exception as e:
        content = f'Error: {e}'

    parts = path_str.split('/')
    bc = '<a href="/">Home</a>' + ''.join(f' › {h(pt)}' for pt in parts)

    extra = ''
    if p.suffix == '.meta':
        meta = parse_meta(content)
        if meta.get('about'):
            extra = f'<div class="about-block">{h(meta["about"])}</div>'

    path_json = json.dumps(path_str)
    nlines    = max(10, content.count('\n') + 2)
    ctrlS_js  = (f'<script>document.addEventListener("keydown",e=>{{'
                 f'if((e.ctrlKey||e.metaKey)&&e.key==="s"){{'
                 f'e.preventDefault();_saveFile({path_json},"editor","status");}}}});</script>')

    return page(p.name, f"""
<div class="bc">{bc}</div>
<h2>{h(p.name)}</h2>
{extra}
<div class="save-bar">
  <button class="btn" onclick="_saveFile({path_json},'editor','status')">Save</button>
  <span id="status"></span>
</div>
<div class="editor-wrap">
  <textarea id="editor" class="editor" spellcheck="false" rows="{nlines}">{h(content)}</textarea>
</div>
{ctrlS_js}
""")


# ── HTTP handler ───────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def _send(self, body: str, mime='text/html; charset=utf-8', status=200):
        data = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs     = parse_qs(parsed.query)
        match parsed.path:
            case '/':
                self._send(index_page())
            case p if p.startswith('/component/'):
                self._send(component_page(p[len('/component/'):]))
            case '/file':
                self._send(file_page(qs.get('p', [''])[0]))
            case _:
                self._send(page('Not found', '<p>Not found. <a href="/">Home</a></p>'), status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        qs     = parse_qs(parsed.query)
        length = int(self.headers.get('Content-Length', 0))
        params = parse_qs(self.rfile.read(length).decode('utf-8'))

        if parsed.path == '/save':
            path_str = qs.get('p', [''])[0]
            content  = params.get('content', [''])[0]
            p = _safe_path(path_str)
            if not p:
                self._send(json.dumps({'ok': False, 'error': 'invalid path'}),
                           'application/json', 403)
                return
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding='utf-8')
                print(f'  saved  {path_str}')
                self._send(json.dumps({'ok': True}), 'application/json')
            except Exception as e:
                self._send(json.dumps({'ok': False, 'error': str(e)}),
                           'application/json', 500)
        else:
            self._send(json.dumps({'ok': False, 'error': 'not found'}),
                       'application/json', 404)

    def log_message(self, fmt, *args):
        print(f'  {args[1]}  {args[0]}')


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    server = HTTPServer(('', PORT), Handler)
    print(f'Looking Glass  →  http://localhost:{PORT}')
    print(f'  root: {ROOT}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
