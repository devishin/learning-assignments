"""PDF generation with WeasyPrint and Jinja2."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from platform_utils import ensure_gtk_on_path_windows


def list_templates(templates_dir: Path) -> list[Path]:
    return sorted(templates_dir.glob("*.html"))


def resolve_font_uri(project_dir: Path) -> str:
    candidates = [
        project_dir / "fonts" / "DejaVuSans.ttf",
        project_dir / "fonts" / "Roboto-Regular.ttf",
        Path("/Library/Fonts/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve().as_uri()
    raise FileNotFoundError(
        "Не найден шрифт с кириллицей. Положите DejaVuSans.ttf в папку fonts/."
    )


def _inject_font(html: str, font_uri: str) -> str:
    font_css = (
        "<style>"
        '@font-face { font-family: "InvoiceFont"; src: url("'
        + font_uri
        + '") format("truetype"); }'
        "body, * { font-family: \"InvoiceFont\", sans-serif; }"
        "</style>"
    )
    if "</head>" in html:
        return html.replace("</head>", font_css + "</head>", 1)
    return font_css + html


def render_invoice_html(template_path: Path, invoice: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_path.name)
    return template.render(**invoice)


def html_to_pdf(
    html: str,
    template_path: Path,
    output_path: Path,
    project_dir: Path,
) -> None:
    font_uri = resolve_font_uri(project_dir)
    html = _inject_font(html, font_uri)
    html = re.sub(r'@font-face\s*\{[^}]+\}', "", html, flags=re.IGNORECASE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ensure_gtk_on_path_windows()
    try:
        from weasyprint import HTML
    except OSError as exc:
        raise RuntimeError(
            "WeasyPrint не может загрузить системные библиотеки. "
            "Windows: установите GTK3 Runtime (см. README). "
            "macOS: brew install pango libffi."
        ) from exc
    HTML(string=html, base_url=str(template_path.parent.resolve())).write_pdf(str(output_path))
