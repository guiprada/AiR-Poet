#!/usr/bin/env python3
"""
AiR-Poet docs server — hypertext project navigation + AI index generation.

    python docs_server.py [port=8000]
    open http://localhost:8000

AI endpoints (no extra deps, pure stdlib):
    /llms.txt    — LLM-friendly index (llmstxt.org format)
    /index.json  — Full structured JSON
    /context.md  — Flat markdown dump for pasting into AI context
"""
import html as _html
import json
import re
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote_plus

ROOT = Path(__file__).parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


# ── .meta parsing ─────────────────────────────────────────────────────────────

def parse_meta(text: str) -> dict:
    """Extract name / type / about from a .meta file."""
    r = {}
    for key in ('name', 'type'):
        m = re.search(rf'^{key}:\s*"([^"]*)"', text, re.MULTILINE)
        if m:
            r[key] = m.group(1)
    # about: " ... "  (quoted, possibly multiline)
    m = re.search(r'about:\s*"\n(.*?)\n"', text, re.DOTALL)
    if not m:
        m = re.search(r'about:\s*"([^"]*)"', text)
    if m:
        r['about'] = m.group(1).strip()
    return r


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


# ── Project scan ──────────────────────────────────────────────────────────────

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

    # Top-level air spec (air.meta, air.air, README.md …)
    top_files = {f.name: f for f in sorted(air.iterdir())
                 if f.is_file() and not f.name.startswith(('.', '_'))}
    meta = (parse_meta((air / 'air.meta').read_text('utf-8', errors='replace'))
            if (air / 'air.meta').exists() else {})
    result.append({'id': 'air', 'path': air, 'files': top_files, 'meta': meta, 'top': True})

    # Subdirectory components
    for sub in sorted(air.iterdir()):
        if sub.is_dir() and not sub.name.startswith(('.', '_')):
            result.append(_make_component(sub.name, sub))

    # Extra top-level modules
    for name in ('air_meta', 'air_vm'):
        d = ROOT / name
        if d.exists():
            result.append(_make_component(name, d))

    return result


def scan_docs() -> list:
    docs = []
    for name in ('air_poet.meta', 'ARCHITECTURE.md', 'TODO.md', 'CODEBASE_ANALYSIS.md', 'bootstrap_meta.meta'):
        f = ROOT / name
        if f.exists():
            docs.append(f)
    for d in (ROOT / 'docs', ROOT / 'lost_and_found', ROOT / 'test_programs'):
        if d.exists():
            for f in sorted(d.rglob('*')):
                if f.is_file() and not f.name.startswith('.'):
                    docs.append(f)
    return docs


# ── CSS ───────────────────────────────────────────────────────────────────────

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

/* sidebar */
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
.ai-nav { margin-top: auto; padding: .8rem 1.2rem 0; border-top: 1px solid #333; }
.ai-nav a { display: block; font-size: .78rem; color: #666; padding: .2rem 0; }
.ai-nav a:hover { color: var(--sidebar-hi); }

/* main */
#main { flex: 1; padding: 2rem 2.5rem; overflow-x: hidden; max-width: 980px; }
h2 { font-size: 1.5rem; margin-bottom: .4rem; }
h3 { font-size: 1rem; margin: 1.4rem 0 .5rem; color: #444; }
.sub { color: var(--muted); font-size: .9rem; margin-bottom: 1.8rem; }
.bc { font-size: .82rem; color: var(--muted); margin-bottom: 1.4rem; }
.bc a { color: var(--accent); }

/* cards */
.grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(240px,1fr));
        gap: .9rem; margin-bottom: 2rem; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
        padding: 1rem 1.1rem; transition: box-shadow .15s; display: block;
        color: inherit; text-decoration: none !important; }
.card:hover { box-shadow: 0 3px 12px rgba(0,0,0,.1); }
.card-title { font-weight: 600; font-size: .96rem; margin-bottom: .3rem;
              display: flex; align-items: center; gap: .4rem; }
.card-about { font-size: .8rem; color: var(--muted); line-height: 1.4;
              display: -webkit-box; -webkit-line-clamp: 3;
              -webkit-box-orient: vertical; overflow: hidden; }

/* type tags */
.tag { display: inline-block; font-size: .66rem; padding: .15em .5em; border-radius: 3px;
       font-weight: 700; vertical-align: middle; }
.t-module { background: #d8f5d8; color: #217a21; }
.t-system { background: #d0f0f8; color: #1a6a7a; }
.t-meta   { background: #ede0ff; color: #6030a0; }
.t-data   { background: #fff0e0; color: #904800; }
.t-test   { background: #ffe0e0; color: #900000; }
.t-other  { background: #eee;    color: #555;    }

/* files */
.file-group { margin-bottom: 1.8rem; }
.file-header { display: flex; align-items: center; gap: .6rem;
               font-size: .78rem; color: var(--muted); margin-bottom: .4rem; font-family: monospace; }
.file-header a { color: var(--accent); }
.about-block { background: var(--card); border: 1px solid var(--border); border-radius: 6px;
               padding: .9rem 1.1rem; margin-bottom: 1.4rem;
               font-size: .88rem; line-height: 1.65; white-space: pre-wrap; color: #333; }
pre { background: var(--code-bg); color: var(--code-fg); padding: 1rem 1.1rem;
      border-radius: 6px; overflow-x: auto; overflow-y: auto; max-height: 480px;
      font-size: .78rem; line-height: 1.5; tab-size: 4; }

/* editor */
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
.btn-ghost { background: transparent; color: var(--accent); }
#status { font-size: .82rem; transition: opacity .4s; opacity: 0; }

/* doc list */
.doc-list { list-style: none; }
.doc-list li { padding: .28rem 0; border-bottom: 1px solid var(--border); font-size: .88rem; }

/* AI box */
.ai-box { background: var(--card); border: 1px solid var(--border); border-radius: 8px;
          padding: 1rem 1.2rem; margin-top: 1.8rem; }
.ai-box h3 { margin-top: 0; }
.ai-links { display: flex; gap: .8rem; flex-wrap: wrap; margin-top: .6rem; }
.ai-btn { display: inline-block; padding: .35rem .9rem; border: 1px solid var(--accent);
          border-radius: 4px; font-size: .82rem; color: var(--accent); }
.ai-btn:hover { background: var(--accent); color: #fff; text-decoration: none; }
"""


# ── HTML helpers ──────────────────────────────────────────────────────────────

def h(s) -> str:
    return _html.escape(str(s))


def type_tag(t: str) -> str:
    if not t:
        return ''
    cls = {'module': 't-module', 'system': 't-system', 'meta': 't-meta',
           'data': 't-data', 'test': 't-test'}.get(t, 't-other')
    return f'<span class="tag {cls}">{h(t)}</span>'


def _sidebar(active='') -> str:
    comps = scan_components()
    docs = scan_docs()
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
  <div class="ai-nav">
    <a href="/llms.txt">llms.txt</a>
    <a href="/index.json">index.json</a>
    <a href="/context.md">context.md</a>
  </div>
</nav>"""


def page(title: str, body: str, active='') -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{h(title)} — AiR-Poet</title>
  <style>{CSS}</style>
</head>
<body>
{_sidebar(active)}
<main id="main">
{body}
</main>
</body>
</html>"""


# ── File categorisation ───────────────────────────────────────────────────────

_ROLE_ORDER = {
    '.meta': 0, '.air': 1, '.py': 2, '.md': 3, '.txt': 4,
}

def _file_role_key(name: str) -> tuple:
    p = Path(name)
    base = p.stem
    ext = p.suffix
    # plan files after main files
    is_plan = base.startswith('plan_')
    is_test = base.startswith('test')
    order = _ROLE_ORDER.get(ext, 9)
    return (int(is_plan) + int(is_test) * 2, order, name)


# ── Page generators ───────────────────────────────────────────────────────────

def index_page() -> str:
    comps = scan_components()
    docs = scan_docs()

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
    top_meta = ROOT / 'air_poet.meta'
    top_about = ''
    if top_meta.exists():
        tm = parse_meta(top_meta.read_text('utf-8', errors='replace'))
        if tm.get('about'):
            top_about = (f'<div class="about-block" style="margin-bottom:1.8rem">'
                         f'<div style="display:flex;justify-content:space-between;align-items:center;'
                         f'margin-bottom:.5rem"><strong>air_poet.meta</strong>'
                         f'<a href="/file?p=air_poet.meta" style="font-size:.8rem">edit</a></div>'
                         f'{h(tm["about"])}</div>')

    return page('Home', f"""
<h2>AiR-Poet</h2>
<p class="sub">Intermediary Representation Language — table-based Lisp for deterministic AI code generation</p>
{top_about}
<div class="grid">{cards}</div>
<h3>Documentation &amp; Notes</h3>
<ul class="doc-list">{doc_items}</ul>
<div class="ai-box">
  <h3>AI Index</h3>
  <p style="font-size:.84rem;color:var(--muted);margin:.3rem 0 0">
    Machine-readable indexes for LLM tooling and context loading.</p>
  <div class="ai-links">
    <a class="ai-btn" href="/llms.txt">llms.txt</a>
    <a class="ai-btn" href="/index.json">index.json</a>
    <a class="ai-btn" href="/context.md">context.md</a>
  </div>
</div>
""")


def component_page(cid: str) -> str:
    comps = scan_components()
    c = next((x for x in comps if x['id'] == cid), None)
    if not c:
        return page('Not found', '<p>Component not found. <a href="/">Home</a></p>')

    name = c['meta'].get('name', cid)
    about = c['meta'].get('about', '')

    about_html = (f'<div class="about-block">{h(about)}</div>' if about else '')

    files_html = ''
    for fname in sorted(c['files'], key=_file_role_key):
        fpath = c['files'][fname]
        try:
            content = fpath.read_text('utf-8', errors='replace')
        except Exception as e:
            content = f'(error: {e})'
        frel = rel(fpath)
        raw_link = f'<a href="/file?p={frel}">{h(fname)}</a>'
        edit_link = f'<a href="/file?p={frel}" style="font-size:.72rem;color:var(--muted)">edit</a>'
        files_html += (
            f'<div class="file-group">'
            f'<div class="file-header">{raw_link} {edit_link}</div>'
            f'<pre>{h(content)}</pre>'
            f'</div>'
        )

    return page(name, f"""
<div class="bc"><a href="/">Home</a> › {h(name)}</div>
<h2>{h(name)} {type_tag(c["meta"].get("type",""))}</h2>
{about_html}
{files_html}
""", active=cid)


def _safe_path(path_str: str):
    """Return resolved Path if within ROOT, else None."""
    try:
        p = (ROOT / path_str).resolve()
        p.relative_to(ROOT.resolve())  # raises if outside
        return p
    except (ValueError, Exception):
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
    bc = '<a href="/">Home</a>'
    for part in parts[:-1]:
        bc += f' › {h(part)}'
    bc += f' › {h(parts[-1])}'

    extra = ''
    if p.suffix == '.meta':
        meta = parse_meta(content)
        if meta.get('about'):
            extra = f'<div class="about-block">{h(meta["about"])}</div>'

    path_json = json.dumps(path_str)
    editor_js = f"""
<script>
const _PATH = {path_json};
function _status(msg, ok) {{
  const el = document.getElementById('status');
  el.textContent = msg;
  el.style.color = ok ? '#a6e3a1' : '#f38ba8';
  el.style.opacity = '1';
  setTimeout(() => el.style.opacity = '0', 2500);
}}
async function _save() {{
  const content = document.getElementById('editor').value;
  try {{
    const r = await fetch('/save?p=' + encodeURIComponent(_PATH), {{
      method: 'POST',
      headers: {{'Content-Type': 'application/x-www-form-urlencoded'}},
      body: 'content=' + encodeURIComponent(content)
    }});
    const j = await r.json();
    _status(j.ok ? 'Saved' : 'Error: ' + j.error, j.ok);
  }} catch(e) {{ _status('Network error', false); }}
}}
document.addEventListener('keydown', e => {{
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {{ e.preventDefault(); _save(); }}
}});
</script>"""

    return page(p.name, f"""
<div class="bc">{bc}</div>
<h2>{h(p.name)}</h2>
{extra}
<div class="save-bar">
  <button class="btn" onclick="_save()">Save</button>
  <span id="status"></span>
  <span style="margin-left:auto;font-size:.76rem;color:var(--muted)">Ctrl+S to save</span>
</div>
<div class="editor-wrap">
  <textarea id="editor" class="editor" spellcheck="false">{h(content)}</textarea>
</div>
{editor_js}
""")


# ── AI index generators ───────────────────────────────────────────────────────

def gen_llms_txt(base: str) -> str:
    comps = scan_components()
    docs = scan_docs()

    lines = [
        '# AiR-Poet',
        '',
        '> AiR is an intermediary representation language for deterministic AI code generation.',
        '> Implemented as a table-based Lisp with lazy evaluation, mixed indexing, and scope inheritance.',
        '',
        'Each component has a `.meta` specification, an `.air` language definition,',
        'a `.py` Python implementation, and optional `plan_*.md` design notes.',
        '',
        '## Components',
        '',
    ]
    for c in comps:
        name = c['meta'].get('name', c['id'])
        ctype = c['meta'].get('type', '')
        about = (c['meta'].get('about', '') or '').split('\n')[0].strip()
        tag = f' [{ctype}]' if ctype else ''
        desc = f': {about}' if about else ''
        lines.append(f'- [{name}]({base}/component/{c["id"]}){tag}{desc}')

    lines += ['', '## Specifications', '']
    for c in comps:
        for fname, fpath in sorted(c['files'].items()):
            if fpath.suffix == '.meta':
                lines.append(f'- [{rel(fpath)}]({base}/file?p={rel(fpath)})')

    lines += ['', '## Language Definitions', '']
    for c in comps:
        for fname, fpath in sorted(c['files'].items()):
            if fpath.suffix == '.air':
                lines.append(f'- [{rel(fpath)}]({base}/file?p={rel(fpath)})')

    lines += ['', '## Design Plans', '']
    for c in comps:
        for fname, fpath in sorted(c['files'].items()):
            if fname.startswith('plan_') and fpath.suffix == '.md':
                lines.append(f'- [{rel(fpath)}]({base}/file?p={rel(fpath)})')

    lines += ['', '## Documentation', '']
    for f in docs:
        lines.append(f'- [{rel(f)}]({base}/file?p={rel(f)})')

    lines += [
        '',
        '## AI Indexes',
        '',
        f'- [index.json]({base}/index.json): Full structured JSON index',
        f'- [context.md]({base}/context.md): Flat markdown for AI context window',
        '',
    ]
    return '\n'.join(lines)


def gen_index_json() -> dict:
    comps = scan_components()
    docs = scan_docs()
    return {
        'project': 'AiR-Poet',
        'description': 'AiR language runtime — table-based Lisp with lazy evaluation',
        'components': [
            {
                'id': c['id'],
                'name': c['meta'].get('name', c['id']),
                'type': c['meta'].get('type', ''),
                'about': c['meta'].get('about', ''),
                'path': rel(c['path']),
                'files': {
                    ext.lstrip('.'): [rel(fp) for fn, fp in sorted(c['files'].items())
                                      if fp.suffix == ext]
                    for ext in {fp.suffix for fp in c['files'].values()}
                },
            }
            for c in comps
        ],
        'docs': [rel(f) for f in docs],
    }


def gen_context_md() -> str:
    """Full flat markdown dump of all specs and plans — paste into AI context."""
    comps = scan_components()
    docs = scan_docs()
    parts = [
        '# AiR-Poet — Project Context',
        '',
        '> Auto-generated by docs_server.py. Contains all .meta specs, .air definitions, and design plans.',
        '',
    ]
    for c in comps:
        name = c['meta'].get('name', c['id'])
        parts.append(f'\n---\n\n## Component: {name}\n')
        if c['meta'].get('about'):
            parts.append(c['meta']['about'] + '\n')
        for fname in sorted(c['files'], key=_file_role_key):
            fpath = c['files'][fname]
            if fpath.suffix in ('.meta', '.air') or fname.startswith('plan_'):
                try:
                    content = fpath.read_text('utf-8', errors='replace')
                    lang = fpath.suffix.lstrip('.')
                    parts.append(f'\n### `{rel(fpath)}`\n\n```{lang}\n{content}\n```\n')
                except Exception:
                    pass

    parts.append('\n---\n\n## Documentation\n')
    for f in docs:
        try:
            content = f.read_text('utf-8', errors='replace')
            parts.append(f'\n### `{rel(f)}`\n\n{content}\n')
        except Exception:
            pass

    return '\n'.join(parts)


# ── HTTP handler ──────────────────────────────────────────────────────────────

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
        qs = parse_qs(parsed.query)
        host = self.headers.get('Host', f'localhost:{PORT}')
        base = f'http://{host}'

        match parsed.path:
            case '/':
                self._send(index_page())
            case p if p.startswith('/component/'):
                self._send(component_page(p[len('/component/'):]))
            case '/file':
                self._send(file_page(qs.get('p', [''])[0]))
            case '/index.json':
                self._send(json.dumps(gen_index_json(), indent=2, ensure_ascii=False),
                           'application/json; charset=utf-8')
            case '/llms.txt':
                self._send(gen_llms_txt(base), 'text/plain; charset=utf-8')
            case '/context.md':
                self._send(gen_context_md(), 'text/markdown; charset=utf-8')
            case _:
                self._send(page('Not found', '<p>Not found. <a href="/">Home</a></p>'), status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length).decode('utf-8')
        params = parse_qs(raw)

        if parsed.path == '/save':
            path_str = qs.get('p', [''])[0]
            content = unquote_plus(params.get('content', [''])[0])
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


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    server = HTTPServer(('', PORT), Handler)
    print(f'AiR-Poet docs  →  http://localhost:{PORT}')
    print(f'  llms.txt     →  http://localhost:{PORT}/llms.txt')
    print(f'  index.json   →  http://localhost:{PORT}/index.json')
    print(f'  context.md   →  http://localhost:{PORT}/context.md')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
