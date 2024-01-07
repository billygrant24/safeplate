import math
import string

from bs4 import BeautifulSoup

from app import utils

BASE_URI = "https://www.bbc.co.uk/food/ingredients/a-z"
USER_AGENT = "SafePlate/1.0 (+https://safeplate.billgrant.dev)"
ITEMS_PER_PAGE = 4 * 6


def extract_category_urls(category_name: str) -> list[str]:
    """Find the links to the pages for a given category."""
    try:
        html = utils.scrape_html(USER_AGENT, f"{BASE_URI}/{category_name}/1")
        soup = BeautifulSoup(html, "html.parser")

        # Find the pagination summary and extract the number of items and pages
        pagination_summary = soup.find("div", class_="pagination-summary")
        num_items = int(pagination_summary.find("b").text)
        num_pages = math.ceil(num_items / ITEMS_PER_PAGE)
        return [
            f"{BASE_URI}/{category_name}/{page}" for page in range(1, num_pages + 1)
        ]
    except Exception:
        return []


def extract_ingredients(url: str) -> list[str]:
    """Extract the ingredients from a given page."""
    html = utils.scrape_html(USER_AGENT, url)
    soup = BeautifulSoup(html, "html.parser")

    ingredients = []

    # Build the list of ingredients
    for ingredient_element in soup.find_all("h3", class_="promo__title"):
        # Add the ingredient to the list
        ingredients.append(normalise_ingredient(ingredient_element.text))

    return ingredients


def normalise_ingredient(ingredient: str) -> str:
    # Remove leading and trailing whitespace and convert to lowercase
    ingredient = ingredient.strip().lower()

    # Remove non-alphabetic characters from the start and end of the string
    if ingredient[0] not in string.ascii_lowercase:
        ingredient = ingredient[1:]
    if ingredient[-1] not in string.ascii_lowercase:
        ingredient = ingredient[:-1]

    return ingredient


def extend_ingredients(ingredients: list[str]) -> list[str]:
    """Extend the ingredients by adding pluralised and accented versions."""
    # Toggle pluralisation of the ingredients and append to the original list
    pluralised_ingredients = []
    for ingredient in ingredients:
        pluralised_ingredients.append(utils.toggle_plural(ingredient))

    # Remove accents from the ingredients and append to the original list
    accented_ingredients = []
    for ingredient in ingredients:
        accented_ingredients.append(utils.remove_accents(ingredient))

    # Append the modified lists to the original list
    ingredients.extend(pluralised_ingredients)
    ingredients.extend(accented_ingredients)

    return ingredients


def main():
    categories = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
    ]

    ingredients = []

    for category in categories:
        urls = extract_category_urls(category)
        if not urls:
            continue

        for url in urls:
            if not utils.check_robots(
                USER_AGENT, "https://www.bbc.co.uk/robots.txt", url
            ):
                print(f"Skipping {url} because it is disallowed by robots.txt")
                continue

            # Add the ingredient to the list
            ingredients.extend(extract_ingredients(url))

    # Extend the ingredients by adding pluralised and accented versions
    ingredients = extend_ingredients(ingredients)

    # Remove duplicates
    ingredients = list(set(ingredients))

    # Sort the list
    ingredients.sort()

    # Output the ingredients as a CSV to stdout
    csv_string = "Ingredient\n"
    for ingredient in ingredients:
        csv_string += f"{ingredient}\n"
    print(csv_string.rstrip("\n"))


if __name__ == "__main__":
    main()
