"""Playwright-backed renderer used to build weekly menu images."""

from __future__ import annotations

import base64
import html
import mimetypes
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from playwright.sync_api import sync_playwright


def _to_data_uri(path: Path) -> str:
    """Return the file content as a data URI."""
    if not path.exists():
        raise FileNotFoundError(path)

    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type:
        mime_type = "application/octet-stream"

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


class PlaywrightRenderer:
    """Render menu layouts to images using Playwright."""

    def __init__(
        self,
        *,
        colors: Dict[str, str],
        layouts: Dict[str, Dict[str, Any]],
        font_path: Path,
        logo_path: Path,
        sandwich_dir: Path,
        meal_image_width: int = 250,
    ) -> None:
        self.colors = colors
        self.layouts = layouts
        self._font_data_uri = _to_data_uri(Path(font_path))
        self._logo_data_uri = _to_data_uri(Path(logo_path))
        self._sandwich_dir = Path(sandwich_dir)
        self._meal_image_width = meal_image_width

        self._playwright = None
        self._browser = None

    def __enter__(self) -> "PlaywrightRenderer":
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)
        return self

    def __exit__(self, *_exc: object) -> None:
        if self._browser is not None:
            self._browser.close()
            self._browser = None
        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def render_layout(
        self,
        layout_name: str,
        *,
        week_text: str,
        cells: List[Dict[str, Any]],
        output_path: Path,
    ) -> List[str]:
        layout = self.layouts[layout_name]
        width, height = layout["image_size"]
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self._browser is None:
            raise RuntimeError("PlaywrightRenderer must be entered as a context manager before rendering")

        page = self._browser.new_page()
        page.set_viewport_size({"width": width, "height": height})

        markup, warnings = self._build_html(layout_name, layout, week_text, cells)
        page.set_content(markup, wait_until="networkidle")
        page.wait_for_timeout(100)
        page.screenshot(path=str(output_path), full_page=False)
        page.close()

        return warnings

    def _build_html(
        self,
        layout_name: str,
        layout: Dict[str, Any],
        week_text: str,
        cells: List[Dict[str, Any]],
    ) -> Tuple[str, List[str]]:
        width, height = layout["image_size"]
        grid = layout["grid"]
        content_spacing = int(layout.get("content_spacing", 30))
        header_gap = 0
        header_inner_gap = 0
        cell_padding_y = 6
        items_gap = 0
        text_margin_bottom = 0
        grid_width = int(grid["cell_width"]) * int(grid["cols"])
        grid_top_margin = int(grid.get("y_start", 0))
        image_width = self._meal_image_width
        image_title_gap = 0
        cell_padding_bottom = 0
        cell_padding_x = 0

        if layout_name.lower() == "horizontal":
            header_gap = max(10, content_spacing // 3)
            header_inner_gap = max(8, header_gap // 2)
            image_width = min(
                self._meal_image_width,
                max(140, int(int(grid["cell_width"]) * 0.55)),
            )
            items_gap = max(8, content_spacing // 3)
            text_margin_bottom = max(6, content_spacing // 4)
            cell_padding_y = max(8, header_gap // 3)
            image_title_gap = 2
            cell_padding_bottom = cell_padding_y + 12
            cell_padding_x = max(16, int(grid["cell_width"]) // 12)

        cell_markup, warnings = self._render_cells(cells, grid, layout)

        week_anchor_style = self._anchor_style(
            layout.get("week_text_position", (0, 0)),
            layout.get("week_text_anchor", "lt"),
        )

        title_text = html.escape(layout.get("title_text", "")).replace("\n", "<br>")
        week_text_html = html.escape(week_text).replace("\n", "<br>")

        css = f"""
            <style>
            @font-face {{
                font-family: 'MenuFont';
                src: url('{self._font_data_uri}') format('truetype');
                font-display: swap;
            }}

            html, body {{
                margin: 0;
                padding: 0;
                width: {width}px;
                height: {height}px;
                background: {self.colors['background']};
            }}

            body {{
                font-family: 'MenuFont', 'Open Sans', sans-serif;
                color: {self.colors['text']};
            }}

            .container {{
                position: relative;
                width: {width}px;
                height: {height}px;
                background: {self.colors['background']};
                overflow: hidden;
            }}

            .logo {{
                position: absolute;
                left: 10px;
                top: 10px;
                width: 360px;
                height: auto;
            }}

            .title {{
                position: absolute;
                left: {layout['title_position'][0]}px;
                top: {layout['title_position'][1]}px;
                font-size: {layout['title_font_size']}px;
                font-weight: 700;
                line-height: 1.05;
                text-align: center;
                color: {self.colors['secondary']};
                white-space: pre-line;
            }}

            .week {{
                width: max-content;
                position: absolute;
                {week_anchor_style}
                font-size: {layout['week_font_size']}px;
                font-weight: 600;
                color: {self.colors['primary']};
                text-transform: uppercase;
                line-height: 1.1;
                text-align: center;
                white-space: pre-line;
            }}

            .grid {{
                position: relative;
                margin: {grid_top_margin}px auto 0;
                width: {grid_width}px;
                display: grid;
                grid-template-columns: repeat({grid['cols']}, {grid['cell_width']}px);
                grid-auto-rows: {grid['cell_height']}px;
                justify-content: center;
            }}

            .cell {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                padding: {cell_padding_y}px {cell_padding_x}px {cell_padding_bottom}px;
                box-sizing: border-box;
                gap: {header_gap}px;
                font-size: {layout['content_font_size']}px;
                color: {self.colors['text']};
            }}

            .day-header {{
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: {header_inner_gap}px;
            }}

            .day-header .separator {{
                width: calc(100% - 20px);
                height: 5px;
                background: {self.colors['background']};
                border-radius: 3px;
            }}

            .day-header .label {{
                text-align: center;
                font-size: {layout['day_font_size']}px;
                font-weight: 800;
                letter-spacing: 1px;
            }}

            .items {{
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: {items_gap}px;
            }}

            .item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: {image_title_gap}px;
                text-align: center;
                width: 100%;
            }}

            .item-text {{
                white-space: pre-line;
                line-height: 1.2;
                font-weight: 600;
                margin: 0 auto {text_margin_bottom}px;
            }}

            .item.meal img {{
                width: {image_width}px;
                height: auto;
                border-radius: 12px;
                object-fit: contain;
            }}

            .item.note .item-text {{
                font-style: italic;
            }}

            .missing-image-note {{
                font-size: 14px;
                color: {self.colors['background']};
                background: rgba(0, 0, 0, 0.35);
                padding: 2px 8px;
                border-radius: 4px;
            }}
            </style>
        """

        markup = f"""<!DOCTYPE html>
<html lang=\"fr\">
<head>
<meta charset=\"utf-8\" />
{css}
</head>
<body>
<div class=\"container\">
    <img class=\"logo\" src=\"{self._logo_data_uri}\" alt=\"Logo\" />
    <div class=\"title\">{title_text}</div>
    <div class=\"week\">{week_text_html}</div>
    <div class=\"grid\">
        {cell_markup}
    </div>
</div>
</body>
</html>
"""
        return markup, warnings

    def _render_cells(
        self,
        cells: List[Dict[str, Any]],
        grid: Dict[str, Any],
        layout: Dict[str, Any],
    ) -> Tuple[str, List[str]]:
        chunks: List[str] = []
        warnings: List[str] = []
        cols = grid["cols"]

        for index, cell in enumerate(cells):
            row = index // cols
            col = index % cols
            background = (
                self.colors["primary"]
                if (row + col) % 2 == 0
                else self.colors["secondary"]
            )

            label_raw = cell.get("label") or f"Jour {index + 1}"
            label_html = html.escape(label_raw).upper()

            items_html, item_warnings = self._render_items(
                cell.get("items", []),
                day_label=label_raw,
            )
            warnings.extend(item_warnings)

            cell_html = f"""
            <div class=\"cell\" style=\"background: {background};\">
                <div class=\"day-header\">
                    <div class=\"separator\"></div>
                    <div class=\"label\">{label_html}</div>
                    <div class=\"separator\"></div>
                </div>
                <div class=\"items\">
                    {items_html}
                </div>
            </div>
            """
            chunks.append(cell_html)

        return "\n".join(chunks), warnings

    def _render_items(
        self,
        items: Iterable[Dict[str, Any]],
        *,
        day_label: str,
    ) -> Tuple[str, List[str]]:
        parts: List[str] = []
        warnings: List[str] = []

        for item in items:
            text_raw = (item.get("text") or "").strip()
            text_html = html.escape(text_raw).replace("\n", "<br>")

            if item.get("is_meal"):
                image_code = (item.get("img") or "").strip()
                image_data_uri = None
                missing_reason = ""

                if image_code:
                    image_path = self._sandwich_dir / f"{image_code}.png"
                    if image_path.exists():
                        image_data_uri = _to_data_uri(image_path)
                    else:
                        missing_reason = f"Image {image_code}.png manquante"
                        warnings.append(
                            f"Warning: image '{image_code}.png' introuvable pour '{text_raw}' ({day_label})"
                        )
                else:
                    missing_reason = "Image non renseignée"
                    warnings.append(
                        f"Warning: aucun code image fourni pour '{text_raw}' ({day_label})"
                    )

                placeholder = (
                    f"<span class=\"missing-image-note\">{html.escape(missing_reason)}</span>"
                    if missing_reason
                    else ""
                )
                image_tag = (
                    f"<img src=\"{image_data_uri}\" alt=\"{html.escape(image_code)}\" />"
                    if image_data_uri
                    else ""
                )

                block = f"""
                <div class=\"item meal\">
                    {image_tag}
                    {placeholder}
                    <div class=\"item-text\">{text_html}</div>
                </div>
                """
            else:
                block = f"""
                <div class=\"item note\">
                    <div class=\"item-text\">{text_html}</div>
                </div>
                """

            parts.append(block)

        return "\n".join(parts), warnings

    @staticmethod
    def _anchor_style(position: Tuple[int, int], anchor: str) -> str:
        x, y = position
        anchor = anchor or "lt"

        transforms: List[str] = []
        horizontal = anchor[0] if len(anchor) > 0 else "l"
        vertical = anchor[1] if len(anchor) > 1 else "t"

        if horizontal == "m":
            transforms.append("translateX(-50%)")
        elif horizontal == "r":
            transforms.append("translateX(-100%)")

        if vertical == "m":
            transforms.append("translateY(-50%)")
        elif vertical == "b":
            transforms.append("translateY(-100%)")

        transform_style = (
            f"transform: {' '.join(transforms)};"
            if transforms
            else ""
        )

        return f"left: {x}px; top: {y}px; {transform_style}"
