import json
import unittest

from app.services import AllergenDetector


class TestAllergenDetector(unittest.TestCase):
    def setUp(self):
        self.detector = AllergenDetector(
            "./resources/models/allergen_model.pkl",
            "./resources/models/allergen_vectorizer.pkl",
        )

    def test_detector(self):
        with open("resources/datasets/recipe_samples.json") as f:
            recipes = json.load(f)

            for recipe in recipes:
                ingredients = recipe["ingredients"]
                detected_allergens = self.detector.detect(ingredients)
                self.assertListEqual(recipe["allergens"], detected_allergens)
