import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def prepare_comparison_dataframe(control_data, test_data):
    # Ensure the same structure/order of rows based on Recipe
    control_data = control_data.set_index("Recipe")
    test_data = test_data.set_index("Recipe")

    # We're only interested in allergen columns
    allergen_columns = control_data.columns[1:]  # Excluding the 'URL' column

    # Calculate differences
    differences = (
        control_data[allergen_columns] != test_data[allergen_columns]
    ).astype(int)

    return differences


def visualize_differences(differences):
    plt.figure(figsize=(10, len(differences) / 2))  # Adjust the size as necessary
    sns.heatmap(differences, annot=True, cmap="YlGnBu", cbar=False, yticklabels=True)
    plt.title("Differences in Allergen Data per Recipe")
    plt.xlabel("Allergens")
    plt.ylabel("Recipes")
    plt.yticks(rotation=0, fontsize=10)
    plt.xticks(rotation=45, fontsize=10)
    plt.tight_layout()
    plt.show()


control_data = pd.read_csv("resources/datasets/recipe_samples_test.csv")
test_data = pd.read_csv("resources/datasets/recipe_samples_control.csv")

differences = prepare_comparison_dataframe(control_data, test_data)
visualize_differences(differences)
