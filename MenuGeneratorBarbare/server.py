import json
import time
from pathlib import Path
from flask import Flask, jsonify, send_file, request
from main import generate_img_from_args, CLIParser
from paths import get_build_dir

app = Flask(__name__)

# Constants
PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_IMAGE_DIR = PROJECT_ROOT / "default_img"
BUILD_DIR = get_build_dir()
MEAL_LIST_FILE = PROJECT_ROOT / "mealList.json"
LAST_MENU_FILE = BUILD_DIR / "last_menu.txt"
MAIL_FILE = BUILD_DIR / "mail.txt"
DEFAULT_MAIL_FILE = DEFAULT_IMAGE_DIR / "mail.txt"

# Load meal list at application startup
def load_meal_list():
    try:
        with open(MEAL_LIST_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    except FileNotFoundError:
        app.logger.warning(f"{MEAL_LIST_FILE} not found, using empty dictionary")
        return {}
    except json.JSONDecodeError:
        app.logger.warning(f"{MEAL_LIST_FILE} contains invalid JSON, using empty dictionary")
        return {}

mealList = load_meal_list()

# Helper functions
def cors_response(response):
    """Add CORS headers to response"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def save_json_to_file(data, filepath):
    """Save data as JSON to the specified file"""
    path_obj = Path(filepath)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with open(path_obj, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_json_from_file(filepath, default=None):
    """Load JSON data from file, return default if file doesn't exist"""
    path_obj = Path(filepath)
    if path_obj.exists():
        with open(path_obj, "r", encoding="utf8") as f:
            return json.load(f)
    return default

def get_image_path(image_type, epoch):
    """Get the image path based on type and epoch"""
    return BUILD_DIR / f"{epoch}-{image_type}.png"

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

if __name__ == '__main__':
    # This block only runs when executing the script directly (development mode)
    # It won't run when the application is served by Gunicorn
    app.run(debug=True, host="0.0.0.0", port=5000)
