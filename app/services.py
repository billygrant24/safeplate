from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from app.models import RecipeFilters, Recipe


class PagedResults:
    def __init__(
        self,
        results: list,
        total: int,
        page: int,
        next_page: Optional[int],
        prev_page: Optional[int],
    ):
        self.results = results
        self.total = total
        self.page = page
        self.next_page = next_page
        self.prev_page = prev_page


class RecipeService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db

    async def find_all(
        self, filters: RecipeFilters, page: int, limit: int
    ) -> PagedResults:
        matchers = {}
        if filters.allergen:
            matchers["allergens"] = {"$nin": filters.allergen}
        if filters.site_name:
            matchers["site_name"] = {"$in": filters.site_name}
        if filters.cuisine:
            matchers["cuisine"] = {"$in": filters.cuisine}
        if filters.diet:
            matchers["diet"] = {"$in": filters.diet}
        if filters.cook_time:
            matchers["cook_time"] = {"$in": filters.cook_time}

        # Get the total count of matching documents
        total_count = await self.db["recipes"].count_documents(matchers)

        # Initialize pagination variables
        limit = limit or 10
        next_page = page + 1 if page * limit < total_count else None
        prev_page = page - 1 if page > 1 else None

        # Get the paged recipes and also the total number of results before pagination
        recipes = (
            await self.db["recipes"]
            .aggregate(
                [
                    {"$match": matchers},
                    {"$skip": (page - 1) * limit},
                    {"$limit": limit},
                    {"$sort": {"_id": -1}},
                ]
            )
            .to_list(length=limit)
        )

        return PagedResults(recipes, total_count, page, next_page, prev_page)

    async def upsert(self, recipe: Recipe) -> Recipe:
        """Upsert a recipe into the database."""
        await self.db["recipes"].update_one(
            {"_id": recipe.id},
            {"$set": recipe.model_dump(by_alias=True, exclude=set("id"))},
            upsert=True,
        )

        return recipe

    async def find_available_filters(self) -> dict:
        """Get the available filters for the recipes."""
        pipeline = [
            # Unwind the arrays with preservation of null and empty arrays
            {"$unwind": {"path": "$cuisine", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$diet", "preserveNullAndEmptyArrays": True}},
            # Group and get unique values
            {
                "$group": {
                    "_id": None,
                    "site_names": {"$addToSet": "$site_name"},
                    "cuisines": {"$addToSet": "$cuisine"},
                    "cook_times": {"$addToSet": "$cook_time"},
                    "diets": {"$addToSet": "$diet"},
                }
            },
        ]

        result = await self.db["recipes"].aggregate(pipeline).to_list(length=1)

        return result[0]
