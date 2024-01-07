import json
from enum import StrEnum, auto
from re import Pattern
from typing import Annotated, Optional

from pydantic import BeforeValidator, BaseModel, Field
from starlette.requests import Request

PyObjectId = Annotated[str, BeforeValidator(str)]


class RecipeWebsite(BaseModel):
    name: str = Field(...)
    host: str = Field(...)
    sitemap_url: str = Field(...)
    robots_url: Optional[str] = Field(default=None)
    recipe_url_pattern: Pattern[str] = Field(...)
    max_links: int = Field(default=100)


class RecipeFilters(BaseModel):
    site_name: list[str] = Field(default_factory=list)
    allergen: list[str] = Field(default_factory=list)
    cuisine: list[str] = Field(default_factory=list)
    diet: list[str] = Field(default_factory=list)
    cook_time: list[str] = Field(default_factory=list)

    @staticmethod
    def from_request(request: Request) -> "RecipeFilters":
        """Create a RecipeFilters object from a request."""
        filters = RecipeFilters()
        filters.site_name = request.query_params.getlist("site_name")
        filters.allergen = request.query_params.getlist("allergen")
        filters.cuisine = request.query_params.getlist("cuisine")
        filters.diet = request.query_params.getlist("diet")
        filters.cook_time = request.query_params.getlist("cook_time")
        return filters


class Recipe(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    site_name: str = Field(...)
    url: str = Field(...)
    image_url: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    cook_time: str = Field(...)
    cuisine: list[str] = Field(...)
    diet: list[str] = Field(...)
    ingredients: list[str] = Field(...)
    allergens: list[str] = Field(...)

    def to_json(self) -> str:
        return json.dumps(self.model_dump(by_alias=True))


class AllergenGroup(StrEnum):
    GLUTEN = auto()
    CRUSTACEANS = auto()
    EGGS = auto()
    FISH = auto()
    PEANUTS = auto()
    SOYBEANS = auto()
    MILK = auto()
    NUTS = auto()
    CELERY = auto()
    MUSTARD = auto()
    SESAME = auto()
    SULPHITES = auto()
    LUPIN = auto()
    MOLLUSCS = auto()

    def __str__(self) -> str:
        return self.name.title()

    @staticmethod
    def to_list() -> list[str]:
        return [f"{allergen}" for allergen in AllergenGroup]
