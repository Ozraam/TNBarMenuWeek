import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent
STYLE_CONFIG_FILE = PROJECT_ROOT / "style.json"

DEFAULT_STYLE_CONFIG: Dict[str, Any] = {
    "colors": {
        "background": "#FFF4EA",
        "primary": "#E6A515",
        "secondary": "#B77236",
        "text": "#FFF4EA"
    },
    "layouts": {
        "vertical": {
            "image_size": [1080, 1920],
            "title_position": [445, 30],
            "title_text": "MENU DE LA\nSEMAINE",
            "title_font_size": 90,
            "week_text_position": [719, 348],
            "week_text_anchor": "mm",
            "week_font_size": 45,
            "grid": {
                "rows": 2,
                "cols": 3,
                "cell_width": 360,
                "cell_height": 743,
                "y_start": 434
            },
            "day_font_size": 70,
            "content_font_size": 45,
            "max_text_width": 300,
            "content_spacing": 50
        },
        "horizontal": {
            "image_size": [1920, 1080],
            "title_position": [500, 80],
            "title_text": "MENU DE LA SEMAINE",
            "title_font_size": 110,
            "week_text_position": [1075, 230],
            "week_text_anchor": "mt",
            "week_font_size": 45,
            "grid": {
                "rows": 1,
                "cols": 5,
                "cell_width": 384,
                "cell_height": 682,
                "y_start": 398
            },
            "day_font_size": 70,
            "content_font_size": 40,
            "max_text_width": 390,
            "content_spacing": 30
        }
    }
}


def get_style_config_path() -> Path:
    return STYLE_CONFIG_FILE


def _deep_merge(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _ensure_numeric_pair(value: Any, fallback: List[int]) -> List[int]:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        first, second = value
        if isinstance(first, (int, float)) and isinstance(second, (int, float)):
            return [int(first), int(second)]
    return fallback


def _ensure_positive_int(value: Any, fallback: int) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    return fallback


def _ensure_string(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return fallback


def _normalize_layout(name: str, layout: Dict[str, Any]) -> Dict[str, Any]:
    default_layout = DEFAULT_STYLE_CONFIG["layouts"][name]
    normalized = {
        "image_size": _ensure_numeric_pair(layout.get("image_size"), default_layout["image_size"]),
        "title_position": _ensure_numeric_pair(layout.get("title_position"), default_layout["title_position"]),
        "title_text": _ensure_string(layout.get("title_text"), default_layout["title_text"]),
        "title_font_size": _ensure_positive_int(layout.get("title_font_size"), default_layout["title_font_size"]),
        "week_text_position": _ensure_numeric_pair(layout.get("week_text_position"), default_layout["week_text_position"]),
        "week_text_anchor": _ensure_string(layout.get("week_text_anchor"), default_layout["week_text_anchor"]),
        "week_font_size": _ensure_positive_int(layout.get("week_font_size"), default_layout["week_font_size"]),
        "grid": {
            "rows": _ensure_positive_int(layout.get("grid", {}).get("rows"), default_layout["grid"]["rows"]),
            "cols": _ensure_positive_int(layout.get("grid", {}).get("cols"), default_layout["grid"]["cols"]),
            "cell_width": _ensure_positive_int(layout.get("grid", {}).get("cell_width"), default_layout["grid"]["cell_width"]),
            "cell_height": _ensure_positive_int(layout.get("grid", {}).get("cell_height"), default_layout["grid"]["cell_height"]),
            "y_start": _ensure_positive_int(layout.get("grid", {}).get("y_start"), default_layout["grid"]["y_start"]),
        },
        "day_font_size": _ensure_positive_int(layout.get("day_font_size"), default_layout["day_font_size"]),
        "content_font_size": _ensure_positive_int(layout.get("content_font_size"), default_layout["content_font_size"]),
        "max_text_width": _ensure_positive_int(layout.get("max_text_width"), default_layout["max_text_width"]),
        "content_spacing": _ensure_positive_int(layout.get("content_spacing"), default_layout["content_spacing"]),
    }
    return normalized


def normalize_style_config(config: Dict[str, Any]) -> Dict[str, Any]:
    merged = _deep_merge(DEFAULT_STYLE_CONFIG, config)

    normalized_colors = {}
    for key, default_value in DEFAULT_STYLE_CONFIG["colors"].items():
        normalized_colors[key] = _ensure_string(merged.get("colors", {}).get(key), default_value)

    normalized_layouts: Dict[str, Dict[str, Any]] = {}
    for layout_name in DEFAULT_STYLE_CONFIG["layouts"].keys():
        layout_data = merged.get("layouts", {}).get(layout_name, {})
        normalized_layouts[layout_name] = _normalize_layout(layout_name, layout_data)

    return {
        "colors": normalized_colors,
        "layouts": normalized_layouts,
    }


def load_style_config() -> Dict[str, Any]:
    if not STYLE_CONFIG_FILE.exists():
        return deepcopy(DEFAULT_STYLE_CONFIG)

    try:
        with open(STYLE_CONFIG_FILE, "r", encoding="utf8") as file:
            raw_config = json.load(file)
            if not isinstance(raw_config, dict):
                return deepcopy(DEFAULT_STYLE_CONFIG)
            return normalize_style_config(raw_config)
    except json.JSONDecodeError:
        return deepcopy(DEFAULT_STYLE_CONFIG)


def save_style_config(config: Dict[str, Any]) -> Dict[str, Any]:
    normalized = normalize_style_config(config)
    STYLE_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STYLE_CONFIG_FILE, "w", encoding="utf8") as file:
        json.dump(normalized, file, ensure_ascii=False, indent=4)
    return normalized


def validate_style_config(config: Any) -> List[str]:
    errors: List[str] = []

    if not isinstance(config, dict):
        return ["Configuration payload must be a JSON object"]

    colors = config.get("colors")
    if not isinstance(colors, dict):
        errors.append("'colors' must be an object")
    else:
        for color_key in DEFAULT_STYLE_CONFIG["colors"].keys():
            value = colors.get(color_key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"'colors.{color_key}' must be a non-empty string")

    layouts = config.get("layouts")
    if not isinstance(layouts, dict):
        errors.append("'layouts' must be an object")
    else:
        for layout_name, default_layout in DEFAULT_STYLE_CONFIG["layouts"].items():
            layout = layouts.get(layout_name)
            if not isinstance(layout, dict):
                errors.append(f"'layouts.{layout_name}' must be an object")
                continue

            for pair_key in ("image_size", "title_position", "week_text_position"):
                value = layout.get(pair_key)
                if not (isinstance(value, (list, tuple)) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value)):
                    errors.append(
                        f"'layouts.{layout_name}.{pair_key}' must be an array of two numbers"
                    )

            for str_key in ("title_text", "week_text_anchor"):
                value = layout.get(str_key)
                if not isinstance(value, str) or not value:
                    errors.append(f"'layouts.{layout_name}.{str_key}' must be a string")

            for int_key in (
                "title_font_size",
                "week_font_size",
                "day_font_size",
                "content_font_size",
                "max_text_width",
                "content_spacing",
            ):
                value = layout.get(int_key)
                if not isinstance(value, (int, float)):
                    errors.append(f"'layouts.{layout_name}.{int_key}' must be a number")

            grid = layout.get("grid")
            if not isinstance(grid, dict):
                errors.append(f"'layouts.{layout_name}.grid' must be an object")
            else:
                for grid_key in ("rows", "cols", "cell_width", "cell_height", "y_start"):
                    grid_value = grid.get(grid_key)
                    if not isinstance(grid_value, (int, float)):
                        errors.append(
                            f"'layouts.{layout_name}.grid.{grid_key}' must be a number"
                        )

    return errors
