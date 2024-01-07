import pandas as pd


def extract_domain_from_url(url: str) -> str:
    """
    Extract the domain from a URL in the format [http(s)://](subdomain.)domain.com[/path]
    """
    from urllib.parse import urlparse

    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.hostname}"


def url_with_protocol(url: str) -> str:
    """
    Add the protocol to a URL if it is missing
    """
    if "://" not in url:
        return f"https://{url}"
    return url


def html_contains_recipe_microformat(html: str) -> bool:
    """
    Check if the HTML contains recipe microformat data
    """
    import json
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    schema_recipe = soup.find("script", type="application/ld+json")
    if schema_recipe:
        try:
            recipe_data = json.loads(schema_recipe.string)
            return recipe_data.get("@type") == "Recipe"
        except json.JSONDecodeError:
            pass
        except TypeError:
            pass
    return False


def url_is_healthy(url: str) -> bool:
    """
    Check if the URL is healthy by making sure it returns a 200 status code and is a
    HTML document which includes recipe microformat data.
    """
    import requests

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        return (
            response.status_code == 200
            and "text/html" in response.headers["Content-Type"]
            and html_contains_recipe_microformat(response.text)
        )
    except:
        return False


def main():
    import json

    # Load the CSV
    df = pd.read_csv("resources/datasets/recipe1m.csv")
    # Cleanup the links to ensure they are valid URLs
    df["link"] = df["link"].apply(url_with_protocol)
    # Augment the dataframe with the domain
    df["domain"] = df["link"].apply(extract_domain_from_url)
    # Count the number of recipes per domain
    domain_counts = df["domain"].value_counts()
    max_domains = 100
    link_sample_size = 5
    # Create a dataframe of the top domains, the counts and
    # the number of healthy links from a sampling of links
    top_domains = pd.DataFrame(
        {
            "domain": domain_counts.head(max_domains).index,
            "count": domain_counts.head(max_domains).values,
            "healthy_count": [
                sum(
                    [
                        url_is_healthy(link)
                        for link in df[df["domain"] == domain]["link"].sample(
                            link_sample_size
                        )
                    ]
                )
                for domain in domain_counts.head(max_domains).index
            ],
        }
    )
    # Save the top domains to a file
    top_domains.to_csv("resources/datasets/recipe1m_top_domains.csv", index=False)
    # Save the healthy domains to a file
    top_domains[top_domains["healthy_count"] == link_sample_size]["domain"].to_csv(
        "resources/datasets/recipe1m_healthy_domains.csv", index=False
    )
    # Save a filtered CSV of the recipes belonging where the domain is found in the healthy domains.
    # Take only 1000 recipes from each domain.
    df[
        df["domain"].isin(
            top_domains[top_domains["healthy_count"] == link_sample_size]["domain"]
        )
    ].groupby("domain").head(1000)[["link", "domain"]].to_csv(
        "resources/datasets/recipe1m_filtered.csv", index=False
    )
    # Create a unique list of all lower-cased ingredients, sorted alphabetically,
    # first having parsed the JSON value into a list of ingredients. We use
    # only the records belonging to the top domains.
    ingredients = sorted(
        list(
            set(
                [
                    ingredient.lower()
                    for ingredients in df[df["domain"].isin(top_domains["domain"])][
                        "NER"
                    ].apply(json.loads)
                    for ingredient in ingredients
                ]
            )
        )
    )
    # Save the ingredients to a file
    with open("resources/datasets/recipe1m_ingredients.txt", "w") as f:
        f.write("\n".join(ingredients))


if __name__ == "__main__":
    main()
