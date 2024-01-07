import html
import json
from typing import Optional

from bs4 import BeautifulSoup

from app import utils
from app.models import Recipe


class SchemaOrgParser:
    def parse(self, content: str) -> Optional[Recipe]:
        """
        Parse the content and retrieve recipe data.
        """
        soup = BeautifulSoup(content, "html.parser")
        schema_recipe = soup.find("script", type="application/ld+json")
        if schema_recipe:
            try:
                recipe_data = json.loads(schema_recipe.string)
                if recipe_data.get("@type") == "Recipe":
                    recipe = Recipe(
                        site_name="",
                        url="",
                        image_url="",
                        name=utils.strip_html(
                            html.unescape(recipe_data.get("name").strip())
                        ).title(),
                        description=utils.strip_html(
                            html.unescape(recipe_data.get("description").strip())
                        ),
                        category=recipe_data.get("recipeCategory") or "",
                        cook_time=utils.iso_duration_to_text(
                            recipe_data.get("cookTime")
                        ),
                        cuisine=[],
                        diet=[],
                        ingredients=[
                            utils.strip_html(ingredient.strip())
                            for ingredient in recipe_data.get("recipeIngredient")
                        ],
                        allergens=[],
                    )

                    # Parse image
                    found_images = recipe_data.get("image")
                    if found_images:
                        if isinstance(found_images, list):
                            recipe.image_url = found_images[0]
                        elif isinstance(found_images, dict):
                            recipe.image_url = found_images.get("url")
                        else:
                            recipe.image_url = found_images

                    # Parse recipeCuisine
                    found_cuisines = recipe_data.get("recipeCuisine")
                    if found_cuisines:
                        # If there are multiple cuisines, they are separated by commas
                        recipe.cuisine = [
                            cuisine.strip().title()
                            for cuisine in found_cuisines.split(",")
                        ]
                        # Sort alphabetically
                        recipe.cuisine.sort()

                    # Parse suitableForDiet
                    found_diets = recipe_data.get("suitableForDiet")
                    if found_diets:
                        if isinstance(found_diets, str):
                            found_diets = [found_diets]
                        recipe.diet = [
                            self._parse_restricted_diet(diet.strip())
                            for diet in found_diets
                        ]
                        # Remove any None values
                        recipe.diet = [diet for diet in recipe.diet if diet is not None]
                        # Sort alphabetically
                        recipe.diet.sort()

                    return recipe
            except json.JSONDecodeError:
                pass
            except TypeError:
                pass
        return None

    def _parse_restricted_diet(self, restricted_diet: str) -> Optional[str]:
        if restricted_diet == "https://schema.org/LowCalorieDiet":
            return "Low Calorie"
        elif restricted_diet == "https://schema.org/LowFatDiet":
            return "Low Fat"
        elif restricted_diet == "https://schema.org/LowLactoseDiet":
            return "Low Lactose"
        elif restricted_diet == "https://schema.org/LowSaltDiet":
            return "Low Salt"
        elif restricted_diet == "https://schema.org/DiabeticDiet":
            return "Diabetic"
        elif restricted_diet == "https://schema.org/GlutenFreeDiet":
            return "Gluten Free"
        elif restricted_diet == "https://schema.org/HalalDiet":
            return "Halal"
        elif restricted_diet == "https://schema.org/HinduDiet":
            return "Hindu"
        elif restricted_diet == "https://schema.org/KosherDiet":
            return "Kosher"
        return None
