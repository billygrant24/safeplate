import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score, hamming_loss
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier

from app.models import AllergenGroup

INPUT_CSV = "resources/datasets/allergens_expanded.csv"
MODEL_PATH = "resources/models/allergen_model.pkl"
VECTORIZER_PATH = "resources/models/allergen_vectorizer.pkl"

ALLERGEN_COLUMNS = AllergenGroup.to_list()


def main():
    # Load the CSV
    df = pd.read_csv(INPUT_CSV)

    # Convert the allergen columns to int
    df[ALLERGEN_COLUMNS] = df[ALLERGEN_COLUMNS].astype(int)

    # Get the X and y
    X = df["Ingredient"]
    y = df[ALLERGEN_COLUMNS]

    # Initialize the vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the data
    X_tfidf = vectorizer.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=0.2, random_state=42
    )

    # Initialize the model
    model = OneVsRestClassifier(RandomForestClassifier(random_state=42))
    model.fit(X_train, y_train)

    # Save the model
    joblib.dump(model, MODEL_PATH)
    # Save the fitted vectorizer
    joblib.dump(vectorizer, VECTORIZER_PATH)

    # Evaluate the model
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    f1 = f1_score(y_test, y_pred, average="micro")
    precision = precision_score(y_test, y_pred, average="micro")
    recall = recall_score(y_test, y_pred, average="micro")
    hamming = hamming_loss(y_test, y_pred)

    # Visualize the evaluation metrics
    metrics = {
        "F1 Score": f1,
        "Precision": precision,
        "Recall": recall,
        "Hamming Loss": hamming,
    }

    plt.bar(metrics.keys(), metrics.values())
    plt.title("Allergen Detection Model Evaluation")
    plt.xlabel("Metric")
    plt.ylabel("Score")
    plt.show()


if __name__ == "__main__":
    main()
