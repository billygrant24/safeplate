from app.models import AllergenGroup


class AllergenDetector:
    def __init__(self, model, vectorizer):
        self.model = model
        self.vectorizer = vectorizer

    def detect(self, ingredients: list[str]) -> list[str]:
        """Detect allergens in a recipe."""
        if not ingredients:
            return []

        # Transform the ingredients into a TF-IDF vector
        input_tfidf = self.vectorizer.transform(ingredients)
        predictions = self.model.predict(input_tfidf)

        # Get the allergen columns from the model
        allergen_columns = AllergenGroup.to_list()

        # Get the allergens from the predictions
        unique_allergens = set()
        for prediction in predictions:
            allergens = [
                allergen_columns[i]
                for i in range(len(allergen_columns))
                if prediction[i] == 1
            ]
            unique_allergens.update(allergens)

        # Convert the set to a list
        allergens = list(unique_allergens)

        # Sort the allergens alphabetically
        allergens.sort()

        return allergens
