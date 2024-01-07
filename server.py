import logging

import joblib
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app.config import DATABASE_URI, DATABASE_NAME, LOG_LEVEL, DEBUG
from app.endpoints import Endpoints
from app.factories import get_db_connection
from app.ml import AllergenDetector
from app.services import RecipeService

# Configure logging
logging.basicConfig()
logging.getLogger().setLevel(LOG_LEVEL)

# Initialize database connection
db = get_db_connection(DATABASE_URI, DATABASE_NAME)

# Initialize the recipe service
recipe_service = RecipeService(db)

# Load the model and vectorizer
model = joblib.load("resources/models/allergen_model.pkl")
vectorizer = joblib.load("resources/models/allergen_vectorizer.pkl")
if not model or not vectorizer:
    raise Exception("Failed to load model or vectorizer")

# Initialize the allergen detector
allergen_detector = AllergenDetector(model, vectorizer)

# Initialize the Jinja2 templates
templates = Jinja2Templates(directory="app/views")

# Initialize HTTP endpoints
endpoints = Endpoints(recipe_service, allergen_detector, templates)

# Initialize the Starlette application
app = Starlette(
    debug=DEBUG,
    routes=[
        Route(path="/", endpoint=endpoints.index, methods=["GET"]),
        Route(path="/api/recipes", endpoint=endpoints.sync_recipe, methods=["POST"]),
        Mount(path="/static", app=StaticFiles(directory="app/static")),
    ],
)
