import argparse
from hashlib import sha256

import requests

from app.config import SCRAPER_USER_AGENT, WEBHOOK_URL, WEBHOOK_API_KEY
from app.models import RecipeWebsite
from app.parsers import SchemaOrgParser
from app.utils import check_robots, scrape_html, crawl_sitemap

MAX_LINKS = 1000

RECIPE_SITES = [
    RecipeWebsite(
        name="NYTimes Cooking",
        host="https://cooking.nytimes.com",
        sitemap_url="https://www.nytimes.com/sitemaps/new/cooking.xml.gz",
        robots_url="https://cooking.nytimes.com/robots.txt",
        recipe_url_pattern=r"^https:\/\/cooking\.nytimes\.com\/recipes\/\d+-[a-z0-9-]+$",
        max_links=MAX_LINKS,
    ),
    RecipeWebsite(
        name="BBCFood",
        host="https://www.bbc.co.uk/food",
        sitemap_url="https://www.bbc.co.uk/food/sitemap.xml",
        robots_url="https://www.bbc.co.uk/robots.txt",
        recipe_url_pattern=r"^https:\/\/www\.bbc\.co\.uk\/food\/recipes\/[a-z0-9_]+_\d+$",
        max_links=MAX_LINKS,
    ),
    RecipeWebsite(
        name="BBCGoodFood",
        host="https://www.bbcgoodfood.com",
        sitemap_url="https://www.bbcgoodfood.com/sitemap.xml",
        robots_url="https://www.bbcgoodfood.com/robots.txt",
        recipe_url_pattern=r"^https:\/\/www\.bbcgoodfood\.com\/recipes\/[a-z0-9-]+$",
        max_links=MAX_LINKS,
    ),
    RecipeWebsite(
        name="Food",
        host="https://www.food.com",
        sitemap_url="https://www.food.com/sitemap.xml",
        robots_url="https://www.food.com/robots.txt",
        recipe_url_pattern=r"^https:\/\/www\.food\.com\/recipe\/[a-z0-9-]+-\d+$",
        max_links=MAX_LINKS,
    ),
    RecipeWebsite(
        name="BonAppetit",
        host="https://www.bonappetit.com",
        sitemap_url="https://www.bonappetit.com/sitemap.xml",
        robots_url="https://www.bonappetit.com/robots.txt",
        recipe_url_pattern=r"^https:\/\/www\.bonappetit\.com\/recipe\/[a-z0-9-]+$",
        max_links=MAX_LINKS,
    ),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "site_name",
        type=str,
        help='Name of the site to crawl. Use "all" to crawl all sites.',
    )
    args = parser.parse_args()

    sites_to_crawl = (
        RECIPE_SITES
        if args.site_name == "all"
        else [site for site in RECIPE_SITES if site.name == args.site_name]
    )

    schema_parser = SchemaOrgParser()

    for site in sites_to_crawl:
        links_scraped = 0
        failed_attempts = 0

        for url in crawl_sitemap(SCRAPER_USER_AGENT, site.sitemap_url):
            try:
                if not check_robots(SCRAPER_USER_AGENT, site.robots_url, url):
                    print(f"Skipping {url} because it is disallowed by robots.txt")
                    continue
                html_content = scrape_html(SCRAPER_USER_AGENT, url)
                recipe = schema_parser.parse(html_content)
                if not recipe:
                    continue
                recipe.site_name = site.name
                recipe.id = sha256(url.encode("utf-8")).hexdigest()
                recipe.url = url
                with requests.post(
                    WEBHOOK_URL,
                    json=recipe.model_dump(by_alias=True),
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {WEBHOOK_API_KEY}",
                    },
                ) as response:
                    pass
                links_scraped += 1
            except Exception as e:
                failed_attempts += 1
                continue
            if links_scraped == site.max_links:
                break

        total_attempts = links_scraped + failed_attempts
        failure_rate = failed_attempts / total_attempts if total_attempts > 0 else 0

        print(f"Benchmark for {site.name}:")
        print(f"Total Links Found: {links_scraped}")
        print(f"Failed Attempts: {failed_attempts}")
        print(f"Failure Rate: {failure_rate:.2f}")


if __name__ == "__main__":
    main()
