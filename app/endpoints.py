from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates

from app.config import WEBHOOK_API_KEY
from app.ml import AllergenDetector
from app.models import Recipe, AllergenGroup, RecipeFilters
from app.services import RecipeService
from app.utils import modify_query_parameter


class Endpoints:
    def __init__(
        self,
        recipe_service: RecipeService,
        allergen_detector: AllergenDetector,
        templates: Jinja2Templates,
    ):
        self.recipe_service = recipe_service
        self.allergen_detector = allergen_detector
        self.templates = templates

    async def index(self, request: Request):
        available_filters = await self.recipe_service.find_available_filters()

        recipes = await self.recipe_service.find_all(
            RecipeFilters.from_request(request),
            page=int(request.query_params.get("page", 1)),
            limit=int(request.query_params.get("limit", 30)),
        )

        url = f"{request.url}"
        next_url = None
        prev_url = None
        if recipes.prev_page:
            prev_url = modify_query_parameter(url, "page", recipes.prev_page)
        if recipes.next_page:
            next_url = modify_query_parameter(url, "page", recipes.next_page)

        return self.templates.TemplateResponse(
            request,
            "index.jinja",
            {
                "recipes": recipes,
                "allergens": AllergenGroup.to_list(),
                "available_filters": available_filters,
                "filters": {
                    "allergen": request.query_params.getlist("allergen"),
                    "cuisine": request.query_params.getlist("cuisine"),
                    "site_name": request.query_params.getlist("site_name"),
                    "diet": request.query_params.getlist("diet"),
                    "cook_time": request.query_params.getlist("cook_time"),
                },
                "next_url": next_url,
                "prev_url": prev_url,
            },
        )

    async def sync_recipe(self, request: Request):
        # Check if the request is authorized via Bearer token
        if request.headers.get("Authorization") != f"Bearer {WEBHOOK_API_KEY}":
            return JSONResponse({"error": "Unauthorized"}, 401)

        try:
            # Parse the recipe from the request body
            json = await request.json()
            recipe = Recipe(**json)

            # Detect allergens in the recipe
            recipe.allergens = self.allergen_detector.detect(recipe.ingredients)

            # Save the recipe
            await self.recipe_service.upsert(recipe)

            return JSONResponse(recipe.model_dump(by_alias=True))
        except Exception as e:
            print("Error updating document: ", e)
            JSONResponse({"error": "Error updating recipe"}, 500)
