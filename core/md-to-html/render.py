from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Iterable

try:
    import markdown
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency 'Markdown'. Install it with:\n"
        "  python -m pip install Markdown"
    ) from exc


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #ffffff;
      --surface: #fbfbfd;
      --text: #1f2328;
      --muted: #5b6472;
      --border: #d8dee8;
      --brand: #6f42ff;
      --code-bg: #f3f5f8;
      --quote: #eef2ff;
      --max-width: 1280px;
      --shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 32px 20px 64px;
      font: 16px/1.7 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, Arial, sans-serif;
      color: var(--text);
      background: var(--bg);
    }}
    main {{
      max-width: var(--max-width);
      margin: 0 auto;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      box-shadow: var(--shadow);
      padding: 28px 32px;
    }}
    .meta {{
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
      color: var(--muted);
      font-size: 14px;
    }}
    h1, h2, h3, h4 {{
      line-height: 1.3;
      margin-top: 1.6em;
      margin-bottom: 0.6em;
    }}
    h1 {{ margin-top: 0; font-size: 2rem; }}
    h2 {{ font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.2em; }}
    h3 {{ font-size: 1.2rem; }}
    p, ul, ol, blockquote, table, pre {{ margin: 0 0 1em; }}
    a {{ color: var(--brand); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      background: var(--code-bg);
      padding: 0.12em 0.35em;
      border-radius: 6px;
      font-size: 0.92em;
    }}
    pre {{
      background: var(--code-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      overflow-x: auto;
    }}
    pre code {{
      background: transparent;
      padding: 0;
      border-radius: 0;
    }}
    blockquote {{
      border-left: 4px solid var(--brand);
      margin-left: 0;
      padding: 12px 16px;
      background: var(--quote);
      border-radius: 0 10px 10px 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      border: 1px solid var(--border);
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    th {{ background: var(--code-bg); }}
    img {{ max-width: 100%; height: auto; }}
    hr {{
      border: 0;
      border-top: 1px solid var(--border);
      margin: 2em 0;
    }}
    .index-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .index-list li {{
      padding: 10px 0;
      border-bottom: 1px solid var(--border);
    }}
    ul, ol {{
      padding-left: 28px;
      margin: 14px 0;
    }}
    li {{
      margin-bottom: 8px;
      line-height: 1.6;
    }}
    .mermaid {{
      background: #ffffff;
      padding: 20px;
      border-radius: 8px;
      border: 1px solid #e0e0e0;
      margin: 20px auto;
      box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      overflow-x: auto;
      text-align: center;
    }}
    .mermaid svg {{
      max-width: 100%;
      height: auto;
      display: inline-block;
      margin: 0 auto;
    }}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'loose',
      flowchart: {{
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis',
        nodeSpacing: 35,
        rankSpacing: 40,
        padding: 12
      }},
      gantt: {{
        useMaxWidth: false,
        leftPadding: 220,
        rightPadding: 30,
        barHeight: 26,
        barGap: 8,
        fontSize: 12.5,
        sectionFontSize: 13.5,
        axisFormat: '%m-%d'
      }},
      themeVariables: {{
        fontSize: '13px',
        lineHeight: '1.4'
      }}
    }});
  </script>
</head>
<body>
  <main>
    <div class="meta">Source: <code>{source}</code></div>
    {body}
  </main>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render explicitly selected Markdown files to readable HTML."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Markdown files or directories to render.",
    )
    parser.add_argument(
        "--output",
        default="docs/html",
        help="Output directory for generated HTML. Default: docs/html",
    )
    return parser.parse_args()


def workspace_root() -> Path:
    return Path.cwd()


def collect_markdown_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
            continue
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
    deduped = sorted({file.resolve() for file in files})
    return deduped


def common_base(files: list[Path]) -> Path:
    if not files:
        raise SystemExit("No Markdown files found.")
    base = Path(files[0]).parent
    for file in files[1:]:
        while not str(file).startswith(str(base)):
            base = base.parent
    return base


def render_markdown(source: Path, text: str) -> str:
    body = markdown.markdown(
        text,
        extensions=[
            "extra",
            "toc",
            "sane_lists",
            "nl2br",
        ],
        output_format="html5",
    )
    return convert_mermaid_blocks(body)


def convert_mermaid_blocks(body: str) -> str:
    """Turn Python-Markdown's ``<pre><code class="language-mermaid">`` output
    into ``<pre class="mermaid">`` so Mermaid 11's ``startOnLoad`` picks it up."""
    pattern = re.compile(
        r'<pre><code class="language-mermaid">(.*?)</code></pre>',
        re.DOTALL,
    )

    def repl(match: re.Match) -> str:
        code = html.unescape(match.group(1))
        return f'<pre class="mermaid">{code.strip()}</pre>'

    return pattern.sub(repl, body)


def extract_title(source: Path, text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return source.stem.replace("_", " ").replace("-", " ").strip() or "Document"


def write_html(source: Path, output_path: Path, body_html: str, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        rel_source = source.relative_to(workspace_root()).as_posix()
    except ValueError:
        rel_source = source.as_posix()
    full_html = HTML_TEMPLATE.format(
        title=html.escape(title),
        source=html.escape(rel_source),
        body=body_html,
    )
    output_path.write_text(full_html, encoding="utf-8")


def write_index(output_root: Path, generated: list[tuple[Path, Path, str]]) -> Path:
    items = []
    for source, output_path, title in generated:
        rel = output_path.relative_to(output_root).as_posix()
        items.append(
            f'<li><a href="{html.escape(rel)}">{html.escape(title)}</a>'
            f"<br><small><code>{html.escape(str(source))}</code></small></li>"
        )
    body = (
        "<h1>Document Index</h1>\n"
        "<p>Generated HTML documents for this workspace.</p>\n"
        f'<ul class="index-list">{"".join(items)}</ul>'
    )
    index_path = output_root / "index.html"
    write_html(Path("generated index"), index_path, body, "Document Index")
    return index_path


def main() -> None:
    args = parse_args()
    root = workspace_root()
    input_paths = [root / arg for arg in args.inputs]
    files = collect_markdown_files(input_paths)
    base = common_base(files)
    output_root = (root / args.output).resolve()

    generated: list[tuple[Path, Path, str]] = []
    for source in files:
        text = source.read_text(encoding="utf-8")
        title = extract_title(source, text)
        body_html = render_markdown(source, text)
        relative = source.relative_to(base).with_suffix(".html")
        output_path = output_root / relative
        write_html(source, output_path, body_html, title)
        generated.append((source, output_path, title))
        print(f"Rendered {source} -> {output_path}")

    index_path = output_root / "index.html"
    if len(generated) >= 3:
        index_path = write_index(output_root, generated)
        print(f"Index: {index_path}")
    elif index_path.exists():
        index_path.unlink()
        print(f"Removed stale index: {index_path}")


if __name__ == "__main__":
    main()
