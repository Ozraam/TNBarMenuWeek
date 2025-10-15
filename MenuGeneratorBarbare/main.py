import json
from datetime import date, timedelta
import locale
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from unidecode import unidecode

from paths import get_build_dir
from playwright_renderer import PlaywrightRenderer
from style_config import load_style_config

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent
LOGO_PATH = PROJECT_ROOT / "Barbare.png"
FONT_PATH = PROJECT_ROOT / "OpenSans-VariableFont_wdth,wght.ttf"
SANDWICH_DIR = PROJECT_ROOT / "Sandwichlogo"
OUTPUT_DIR = get_build_dir()

class MenuGenerator:
    def __init__(self) -> None:
        self.output_dir = OUTPUT_DIR
        self.ensure_output_directory()
        locale.setlocale(locale.LC_TIME, "fr_FR.utf8")

        style_config = load_style_config()
        self.colors = style_config["colors"]
        self.layouts = self._prepare_layouts(style_config["layouts"])

    def _prepare_layouts(self, layouts: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        prepared: Dict[str, Dict[str, Any]] = {}
        for layout_name, layout in layouts.items():
            prepared[layout_name] = {
                **layout,
                "image_size": tuple(int(value) for value in layout["image_size"]),
                "title_position": tuple(int(value) for value in layout["title_position"]),
                "week_text_position": tuple(int(value) for value in layout["week_text_position"]),
                "grid": {
                    key: int(value) for key, value in layout.get("grid", {}).items()
                },
            }
        return prepared

    def ensure_output_directory(self) -> None:
        """Ensure the output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_next_week_text(self) -> str:
        """Return the date of the next Monday and Friday in French format."""
        today = date.today()
        days_ahead = 7 - today.weekday()
        monday = today + timedelta(days=days_ahead)
        friday = monday + timedelta(days=4)
        return (
            "Semaine du "
            + monday.strftime("%d")
            + " au "
            + friday.strftime("%d %B\n%Y")
        ).upper()

    def _normalize_content(
        self, content: Iterable[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        normalized: List[Dict[str, Any]] = []
        warnings: List[str] = []

        for day in content:
            day_label = str(day.get("day") or "")
            day_items: List[Dict[str, Any]] = list(day.get("content") or [])

            if len(day_items) > 2:
                warnings.append(
                    "Warning: too many content for a day, only the first two will be displayed, "
                    f"day: {day_label}"
                )
                day_items = day_items[:2]

            normalized_items = []
            for item in day_items:
                normalized_items.append(
                    {
                        "text": str(item.get("text") or ""),
                        "is_meal": bool(item.get("is_meal")),
                        "img": str(item.get("img") or ""),
                    }
                )

            normalized.append({"day": day_label, "content": normalized_items})

        return normalized, warnings

    def _build_cells(
        self,
        layout_name: str,
        headers: List[str],
        days: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        layout = self.layouts[layout_name]
        grid = layout["grid"]
        max_cells = grid["rows"] * grid["cols"]

        cells: List[Dict[str, Any]] = []
        for index in range(max_cells):
            header_label = str(headers[index]) if index < len(headers) else ""
            day_entry = days[index] if index < len(days) else None

            if not header_label and day_entry:
                header_label = day_entry.get("day") or f"Jour {index + 1}"
            elif not header_label:
                header_label = f"Jour {index + 1}"

            cell_items = day_entry.get("content") if day_entry else []

            cells.append({"label": header_label, "items": cell_items})

        return cells
    
    def transform_pascal_case(self, string):
        """Transform PascalCase to space-separated words"""
        if string == "RSAv":
            return string
            
        final = [""]
        for i in range(len(string)):
            if string[i].isupper() and i != 0:
                final.append("")
            final[-1] += string[i]
            
        return " ".join(word.strip() for word in final)
    
    def find_ingredient(self, ingredients, name):
        """Find ingredient information in the ingredients list"""
        if name.lower() == "pizza":
            return ("Pizza", "Pizza", "Pizza")
            
        for ingredient in ingredients:
            if unidecode(name.lower()) in unidecode(ingredient[0].lower()):
                return ingredient
                
        print(f"Not found: {name}")
        return (f"Not found:{name}", "", "")
    
    def flatten_meals(self, week_data):
        """Flatten the nested meal structure and remove duplicates"""
        all_meals = []
        for day in week_data["content"]:
            for content in day["content"]:
                all_meals.append(content)
                
        # Remove duplicates based on text field
        unique_meals = []
        seen_texts = set()
        for meal in all_meals:
            if meal['text'] not in seen_texts:
                unique_meals.append(meal)
                seen_texts.add(meal['text'])
                
        return unique_meals
    
    def generate_email_text(self, week_data):
        """Generate text for email with ingredient information"""
        # Load ingredients
        with open(PROJECT_ROOT / "ingredients.json", encoding="utf8") as f:
            ingredients = json.load(f)
            
        unique_meals = self.flatten_meals(week_data)
        
        # Start building the email text
        text = "👇English translation under the picture, at the end of the email👇\nBonjour à tous !\n{text-custom-french}\n\nVoici la liste des ingrédients des plats:\n"
        
        # Add French ingredients
        for meal in unique_meals:
            if meal['is_meal']:
                ingredient = self.find_ingredient(ingredients, meal['text'])
                if ingredient[0] == "Pizza":
                    continue
                text += f"\t- {ingredient[0]}: {ingredient[1]}\n"
        
        # Add English translation
        text += "\n\n\n\n\n\n{image goes here}\n\n\n\n\n\n👇English translation👇\n\nHello everyone!\n{text-custom-english}\n\nHere is the list of ingredients of the dishes:\n"
        
        # Add English ingredients
        for meal in unique_meals:
            if meal['is_meal']:
                ingredient = self.find_ingredient(ingredients, meal['text'])
                if ingredient[0] == "Pizza":
                    continue
                text += f"\t- {ingredient[0]}: {ingredient[2]}\n"
                
        text += "\n\nBar'barement vôtre,\nL'équipe Bar'bare"
        
        # Replace placeholders with custom text
        return text.replace("{text-custom-french}", week_data["text-custom-french"]).replace("{text-custom-english}", week_data["text-custom-english"])
    
    def generate_menu(self, week_data, filename):
        """Generate menu assets and return the image paths with the email text."""
        normalized_content, normalization_warnings = self._normalize_content(
            week_data.get("content", [])
        )
        normalized_week_data = dict(week_data)
        normalized_week_data["content"] = normalized_content

        week_text = self.get_next_week_text()
        horizontal_week_text = " ".join(week_text.split("\n"))

        vertical_cells = self._build_cells(
            "vertical", week_data.get("header", []), normalized_content
        )
        horizontal_cells = self._build_cells(
            "horizontal", week_data.get("header", []), normalized_content
        )

        renderer = PlaywrightRenderer(
            colors=self.colors,
            layouts=self.layouts,
            font_path=FONT_PATH,
            logo_path=LOGO_PATH,
            sandwich_dir=SANDWICH_DIR,
        )

        vertical_path = self.output_dir / f"{filename}-vertical.png"
        horizontal_path = self.output_dir / f"{filename}-horizontal.png"

        warnings: List[str] = list(normalization_warnings)

        with renderer as browser_renderer:
            warnings.extend(
                browser_renderer.render_layout(
                    "vertical",
                    week_text=week_text,
                    cells=vertical_cells,
                    output_path=vertical_path,
                )
            )
            warnings.extend(
                browser_renderer.render_layout(
                    "horizontal",
                    week_text=horizontal_week_text,
                    cells=horizontal_cells,
                    output_path=horizontal_path,
                )
            )

        email_text = self.generate_email_text(normalized_week_data)

        with open(self.output_dir / "mail.txt", "w", encoding="utf8") as file:
            file.write(email_text)

        if warnings:
            print("\n".join(warnings))

        return vertical_path, horizontal_path, email_text

class CLIParser:
    def __init__(self):
        pass
        
    def parse_string_argument(self, args, index):
        """Parse a quoted string argument"""
        string = ""
        while index < len(args) and not args[index].endswith("\""):
            string += args[index] + " "
            index += 1
            
        if index < len(args):
            string += args[index]
            
        return string[1:-1], index
    
    def parse_arguments(self, args):
        """Parse command line arguments into a structured format"""
        week_data = {
            "header": [],
            "text-custom-french": "",
            "text-custom-english": "",
            "content": []
        }
        
        i = 0
        while i < len(args):
            if args[i] == "--header":
                header = []
                i += 1
                while i < len(args) and not args[i].startswith("--"):
                    header.append(args[i])
                    i += 1
                week_data["header"] = header
                
            elif args[i] == "--custom-text-french":
                text, i = self.parse_string_argument(args, i+1)
                i += 1
                week_data["text-custom-french"] = text
                
            elif args[i] == "--custom-text-english":
                text, i = self.parse_string_argument(args, i+1)
                i += 1
                week_data["text-custom-english"] = text
                
            elif args[i] == "--content":
                day = {
                    "day": args[i+2],
                    "content": []
                }
                i += 3
                
                if args[i] == "--day-content":
                    i += 1
                else:
                    print(f"Error: --day-content is missing {args[i]}")
                    i += 1
                    continue
                    
                while i < len(args) and args[i] != "--content":
                    content = {
                        "text": "",
                        "is_meal": False
                    }
                    
                    if args[i] == "--is-meal":
                        content["is_meal"] = True
                        i += 1
                        
                    if args[i] == "--text":
                        text, i = self.parse_string_argument(args, i+1)
                        content["text"] = text
                        i += 1
                    
                    if i < len(args) and args[i] == "--img":
                        content["img"] = args[i+1]
                        i += 2
                    
                    day["content"].append(content)
                    
                week_data["content"].append(day)
            else:
                i += 1
                
        return week_data

def generate_img_from_args(args, filename="menu"):
    """Main entry point for generating images from command line arguments"""
    parser = CLIParser()
    week_data = parser.parse_arguments(args)
    
    generator = MenuGenerator()
    return generator.generate_menu(week_data, filename)

if __name__ == "__main__":
    with open(PROJECT_ROOT / "cli.txt", encoding="utf8") as f:
        args = f.read().split()
        
    parser = CLIParser()
    week_data = parser.parse_arguments(args)
    
    print(week_data)
    
    generator = MenuGenerator()
    generator.generate_menu(week_data, "menu")