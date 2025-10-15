import json
import os
import time
from pathlib import Path
from flask import Flask, jsonify, send_file, request, make_response
from PIL import Image, UnidentifiedImageError
from main import generate_img_from_args, CLIParser
from paths import get_build_dir

app = Flask(__name__)

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_IMAGE_DIR = PROJECT_ROOT / "default_img"
SANDWICH_DIR = PROJECT_ROOT / "Sandwichlogo"
INGREDIENTS_FILE = PROJECT_ROOT / "ingredients.json"
BUILD_DIR = get_build_dir()
MEAL_LIST_FILE = PROJECT_ROOT / "mealList.json"
LAST_MENU_FILE = BUILD_DIR / "last_menu.txt"
MAIL_FILE = BUILD_DIR / "mail.txt"
DEFAULT_MAIL_FILE = DEFAULT_IMAGE_DIR / "mail.txt"
ALLOWED_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")
ALLOWED_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "Authorization, Content-Type")
ALLOWED_METHODS = os.getenv("CORS_ALLOW_METHODS", "GET, POST, OPTIONS")

# Load meal list at application startup
def load_meal_list():
    try:
        with open(MEAL_LIST_FILE, "r", encoding="utf8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            app.logger.warning(f"{MEAL_LIST_FILE} does not contain a list, using empty list")
            return []
    except FileNotFoundError:
        app.logger.warning(f"{MEAL_LIST_FILE} not found, using empty list")
        return []
    except json.JSONDecodeError:
        app.logger.warning(f"{MEAL_LIST_FILE} contains invalid JSON, using empty list")
        return []

mealList = load_meal_list()

# Helper functions
def apply_cors_headers(response):
    """Attach standard CORS headers to the outgoing response."""
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = ALLOWED_HEADERS
    response.headers["Access-Control-Allow-Methods"] = ALLOWED_METHODS
    return response


def cors_response(response):
    """Add CORS headers to response"""
    return apply_cors_headers(response)


@app.before_request
def handle_preflight():
    """Handle CORS preflight requests early."""
    if request.method == "OPTIONS":
        return apply_cors_headers(make_response("", 204))


@app.after_request
def attach_cors(response):
    """Ensure every response carries the CORS headers."""
    return apply_cors_headers(response)

def save_json_to_file(data, filepath, *, indent=None):
    """Save data as JSON to the specified file."""
    path_obj = Path(filepath)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(path_obj, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

def load_json_from_file(filepath, default=None):
    """Load JSON data from file, return default if file doesn't exist"""
    path_obj = Path(filepath)
    if path_obj.exists():
        with open(path_obj, "r", encoding="utf8") as f:
            return json.load(f)
    return default


def load_ingredients_data():
    """Load the ingredients list from disk."""
    try:
        with open(INGREDIENTS_FILE, "r", encoding="utf8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            app.logger.warning(f"{INGREDIENTS_FILE} does not contain a list, using empty list")
            return []
    except FileNotFoundError:
        app.logger.warning(f"{INGREDIENTS_FILE} not found, creating new one on first write")
        return []
    except json.JSONDecodeError:
        app.logger.error(f"{INGREDIENTS_FILE} contains invalid JSON")
        raise

def get_image_path(image_type, epoch):
    """Get the image path based on type and epoch"""
    return BUILD_DIR / f"{epoch}-{image_type}.png"


def error_response(message, status=400):
    """Return a JSON error payload with shared CORS headers."""
    return cors_response(jsonify({"message": message})), status


def normalize_image_code(raw_code):
    """Normalize supplied image codes and block path traversal attempts."""
    if not raw_code:
        return ""

    cleaned = Path(raw_code).stem.strip()
    cleaned = cleaned.replace('/', '').replace('\\', '')

    if cleaned in {"", ".", ".."}:
        return ""

    return cleaned

# Routes
@app.route('/getMealList', methods=['GET'])
def get_meal_list():
    response = jsonify(mealList)
    return cors_response(response)

@app.route('/generateImages', methods=['GET'])
def generate_images():
    args = request.args.get('menu', default="", type=str).split(" ")
    
    if args == [""]:
        return cors_response(jsonify({"error": "No arguments provided"})), 400
    
    try:
        last_menu = CLIParser().parse_arguments(args)
        filename = str(int(time.time()))
        save_json_to_file(last_menu, LAST_MENU_FILE)
        generate_img_from_args(args, filename)
        
        return cors_response(jsonify({
            "message": "Images generated successfully", 
            "vertical": filename, 
            "horizontal": filename
        }))
    except Exception as e:
        app.logger.error(f"Error generating images: {str(e)}")
        return cors_response(jsonify({"error": str(e)})), 500

@app.route('/getLastMenu', methods=['GET'])
def get_last_menu():
    last_menu = load_json_from_file(LAST_MENU_FILE)
    if last_menu is None:
        return cors_response(jsonify({"error": "No menu generated yet"})), 400
    return cors_response(jsonify(last_menu))

@app.route('/getMailingText', methods=['GET'])
def get_mailing_text():
    try:
        with open(MAIL_FILE, "r", encoding="utf8") as f:
            mailing_text = f.read()
    except FileNotFoundError:
        with open(DEFAULT_MAIL_FILE, "r", encoding="utf8") as f:
            mailing_text = f.read()
    
    return cors_response(jsonify({"text": mailing_text}))

@app.route('/verticalMenu', methods=['GET'])
def get_image1():
    return get_menu_image("vertical")

@app.route('/horizontalMenu', methods=['GET'])
def get_image2():
    return get_menu_image("horizontal")

def get_menu_image(image_type):
    """Handle image retrieval for both vertical and horizontal menus"""
    epoch = request.args.get("epoch", default="", type=str)
    file_name = get_image_path(image_type, epoch)
    
    try:
        return send_file(file_name, mimetype='image/png')
    except FileNotFoundError:
        return send_file(DEFAULT_IMAGE_DIR / f"{image_type}.png", mimetype='image/png')


@app.route('/addSandwich', methods=['POST'])
def add_sandwich():
    """Persist a new sandwich definition and optional image asset."""
    global mealList

    payload = {}
    if request.is_json:
        payload = request.get_json(silent=True) or {}
    else:
        payload = request.form.to_dict()

    name = (payload.get('name') or '').strip()
    french_description = (payload.get('frenchDescription') or '').strip()
    english_description = (payload.get('englishDescription') or '').strip()
    is_vegetarian_raw = (payload.get('isVegetarian') or '').strip().lower()
    is_vegetarian = is_vegetarian_raw in {"true", "1", "yes", "on"}

    image_code_raw = (payload.get('image') or '').strip()
    image_code = normalize_image_code(image_code_raw)

    image_file = request.files.get('imageFile') if request.files else None

    if not name:
        return error_response("Le nom du sandwich est requis", 400)

    if not image_code and image_file and image_file.filename:
        image_code = normalize_image_code(image_file.filename)

    if not image_code:
        return error_response("Un code image ou un fichier valide est requis", 400)

    english_description = english_description or french_description

    if not isinstance(mealList, list):
        mealList = []

    if any((entry.get('name') or '').strip().lower() == name.lower() for entry in mealList if isinstance(entry, dict)):
        return error_response("Ce nom de sandwich existe déjà", 409)

    if any((entry.get('image') or '').strip().lower() == image_code.lower() for entry in mealList if isinstance(entry, dict)):
        return error_response("Ce code image est déjà utilisé", 409)

    saved_image_code = image_code

    if image_file and image_file.filename:
        target_path = SANDWICH_DIR / f"{image_code}.png"
        target_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            image_file.stream.seek(0)
            image = Image.open(image_file.stream)
            image = image.convert("RGBA")
            image.save(target_path, format="PNG")
        except UnidentifiedImageError:
            return error_response("Le fichier envoyé n'est pas une image valide", 400)
        except Exception as exc:  # Catch unexpected IO issues
            app.logger.error(f"Failed to save sandwich image: {exc}")
            return error_response("Impossible d'enregistrer l'image du sandwich", 500)

    new_entry = {
        "name": name,
        "image": saved_image_code
    }

    ingredient_entry_name = name
    if is_vegetarian and "(végé/veggie)" not in ingredient_entry_name.lower():
        ingredient_entry_name = f"{ingredient_entry_name} (végé/veggie)"

    ingredient_entry = [
        ingredient_entry_name,
        french_description,
        english_description
    ]

    mealList.append(new_entry)

    try:
        save_json_to_file(mealList, MEAL_LIST_FILE, indent=4)
    except Exception as exc:
        mealList.pop()
        app.logger.error(f"Failed to write meal list: {exc}")
        return error_response("Impossible d'enregistrer le sandwich sur le serveur", 500)

    try:
        ingredients_data = load_ingredients_data()
        ingredients_data.append(ingredient_entry)
        save_json_to_file(ingredients_data, INGREDIENTS_FILE, indent=4)
    except Exception as exc:
        app.logger.error(f"Failed to append ingredient entry: {exc}")
        mealList.pop()
        try:
            save_json_to_file(mealList, MEAL_LIST_FILE, indent=4)
        except Exception as rollback_error:
            app.logger.error(f"Failed to rollback meal list after ingredient error: {rollback_error}")
        return error_response("Impossible d'enregistrer les descriptions du sandwich sur le serveur", 500)

    response_payload = {
        "message": "Sandwich ajouté avec succès",
        "item": new_entry,
        "ingredient": {
            "name": ingredient_entry_name,
            "frenchDescription": french_description,
            "englishDescription": english_description,
            "isVegetarian": is_vegetarian
        }
    }

    return cors_response(jsonify(response_payload)), 201

if __name__ == '__main__':
    # This block only runs when executing the script directly (development mode)
    # It won't run when the application is served by Gunicorn
    app.run(debug=True, host="0.0.0.0", port=5000)
