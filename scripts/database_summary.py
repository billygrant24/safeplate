from pymongo import MongoClient
from prettytable import PrettyTable

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017/")
db = client.safeplate
recipes_collection = db.recipes

# Queries
unique_recipes_count = recipes_collection.estimated_document_count()
unique_allergens_count = len(recipes_collection.distinct("allergens"))
unique_cuisines_count = len(recipes_collection.distinct("cuisine"))
unique_diets_count = len(recipes_collection.distinct("diet"))

# Create and populate the table
table = PrettyTable()
table.field_names = ["Metric", "Count"]
table.add_row(["Unique Recipes", unique_recipes_count])
table.add_row(["Unique Allergens", unique_allergens_count])
table.add_row(["Unique Cuisines", unique_cuisines_count])
table.add_row(["Unique Diets", unique_diets_count])

# Print the table
print(table)
