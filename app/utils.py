import gzip
import time
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import inflect
import isodate
import requests
from bs4 import BeautifulSoup

# Initialize the inflector as a singleton. We do this because
# initializing the inflector is a relatively expensive operation.
_INFLECTOR = inflect.engine()


def strip_html(html_content: str) -> str:
    """
    Function to strip HTML tags from the given HTML content.

    This is important for avoiding injecting HTML tags into the
    database or into the user's browser.

    :param html_content: The HTML content from which to strip the tags.
    :return: The stripped text without the HTML tags.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text()


def toggle_plural(word: str) -> str:
    """
    Toggle the plural form of a word.

    This is useful for when we want to toggle the plural form of a word
    to its singular form, and vice versa.

    :param word: The word to toggle the plural form of.
    :return: The toggled plural form of the word.
    """
    if word == _INFLECTOR.plural(word):
        singular = _INFLECTOR.singular_noun(word)
        if word == singular:
            return word
        else:
            return f"{singular}"
    else:
        return _INFLECTOR.plural(word)


def remove_accents(input_str: str) -> str:
    """
    Remove accents from a given string.

    This is used to remove accents from a string so that it can be
    compared to other strings without accents.

    :param input_str: The input string from which accents will be removed.
    :return: The input string with accents removed.
    """
    import unicodedata

    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_ascii = nfkd_form.encode("ASCII", "ignore")
    return only_ascii.decode("ASCII")


def iso_duration_to_text(duration: str | None) -> str:
    """
    Convert an ISO 8601 duration string to a human-readable string.

    :param duration: The ISO 8601 duration string.
    :type duration: str
    :return: The human-readable string.
    :rtype: str
    """
    if not duration:
        return ""

    parsed_duration = isodate.parse_duration(duration.strip())
    total_seconds = parsed_duration.total_seconds()

    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    if days > 1:
        return "Over 1 day"
    if hours > 4:
        return "Over 4 hours"
    if hours > 2:
        return "Over 2 hours"
    if hours > 1:
        return "Over 1 hour"
    if minutes > 30:
        return "Over 30 minutes"
    if minutes > 10:
        return "Over 10 minutes"

    return "Under 10 minutes"


def check_robots(user_agent: str, robots_url: str, subject_url: str) -> bool:
    """Check if the robots.txt file disallows the user agent."""
    import urllib.robotparser

    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, subject_url)


def scrape_html(user_agent: str, url: str) -> str:
    """Scrape the HTML content of a URL."""
    import requests

    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": user_agent})
        if response.status_code != 200:
            raise Exception(f"Failed to fetch {url}")
        return response.text
    except requests.ReadTimeout:
        time.sleep(5)
        return scrape_html(user_agent, url)


def modify_query_parameter(url, param_name, param_value):
    """Update a query parameter in a URL."""
    # Parse the URL
    parsed_url = urlparse(url)

    # Extract the query parameters
    query_params = parse_qs(parsed_url.query)

    # Add or replace the specified query parameter
    query_params[param_name] = param_value

    # Rebuild the query string
    new_query_string = urlencode(query_params, doseq=True)

    # Rebuild the full URL
    new_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query_string,
            parsed_url.fragment,
        )
    )

    return new_url


def crawl_sitemap(user_agent: str, url: str) -> Optional[str]:
    """Recursively crawl a sitemap and yield URLs."""
    with requests.Session() as session:
        response = session.get(
            url,
            headers={"User-Agent": user_agent},
            timeout=10,
        )

        if response.status_code == 200:
            xml = response.text

            # If the sitemap is gzipped, decompress it
            if response.headers.get("content-type") == "application/x-gzip":
                xml = gzip.decompress(response.content)

            # Parse the sitemap
            soup = BeautifulSoup(xml, features="xml")

            # Look for sitemap elements
            for sitemap in soup.find_all("sitemap"):
                yield from crawl_sitemap(user_agent, sitemap.find("loc").text)

            # Look for urlset elements
            for urlset in soup.find_all("urlset"):
                for url in urlset.find_all("url"):
                    yield url.find("loc").text
