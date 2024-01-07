import unittest

from app.parsers import SchemaOrgParser


class TestSchemaOrgParser(unittest.TestCase):
    def test_parse_success(self):
        content = """
        <html>
            <script type="application/ld+json">{
                "@type": "Recipe",
                "name": "test",
                "description": "description",
                "recipeCategory": "category",
                "recipeIngredient": ["ingredient1", "ingredient2"]
            }</script>
        </html>"""

        parser = SchemaOrgParser()
        recipe = parser.parse(content)
        self.assertEqual(recipe.name, "test")
        self.assertEqual(recipe.description, "description")
        self.assertEqual(recipe.category, "category")
        self.assertEqual(recipe.ingredients, ["ingredient1", "ingredient2"])

    def test_parse_no_recipe(self):
        content = "<html></html>"
        parser = SchemaOrgParser()
        recipe = parser.parse(content)
        self.assertIsNone(recipe)

    def test_parse_no_data(self):
        content = """
        <html>
            <script type="application/ld+json"></script>
        </html>"""
        parser = SchemaOrgParser()
        recipe = parser.parse(content)
        self.assertIsNone(recipe)

    def test_parse_invalid_data(self):
        content = """
        <html>
            <script type="application/ld+json">invalid json</script>
        </html>"""
        parser = SchemaOrgParser()
        recipe = parser.parse(content)
        self.assertIsNone(recipe)
