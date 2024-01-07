import unittest

from app.utils import (
    remove_accents,
    strip_html,
    toggle_plural,
    iso_duration_to_text,
)


class TestRemoveAccents(unittest.TestCase):
    def test_remove_accents(self):
        self.assertEqual(remove_accents("néñó"), "neno")
        self.assertEqual(remove_accents("Déjà vu déjà vu"), "Deja vu deja vu")
        self.assertEqual(remove_accents("Café Zaré"), "Cafe Zare")
        self.assertEqual(remove_accents("Zürich"), "Zurich")
        self.assertEqual(remove_accents("Århus"), "Arhus")


class TestStripHTML(unittest.TestCase):
    def test_strip_html(self):
        html_content = "<h1>Hello World!</h1>"
        stripped_content = strip_html(html_content)
        self.assertEqual(stripped_content, "Hello World!")

        html_content = "<div><p>Hello</p><p>World</p></div>"
        stripped_content = strip_html(html_content)
        self.assertEqual(stripped_content, "HelloWorld")

        html_content = "<strong>Lorem ipsum</strong> dolor sit amet"
        stripped_content = strip_html(html_content)
        self.assertEqual(stripped_content, "Lorem ipsum dolor sit amet")


class TestTogglePlural(unittest.TestCase):
    def setUp(self):
        self.word_singular = "dog"
        self.word_plural = "dogs"

    def test_toggle_plural_from_singular(self):
        """Test the toggle_plural when given a singular word."""
        self.assertEqual(toggle_plural(self.word_singular), self.word_plural)

    def test_toggle_plural_from_plural(self):
        """Test the toggle_plural when given a plural word."""
        self.assertEqual(toggle_plural(self.word_plural), self.word_singular)


class TestIsoDurationToText(unittest.TestCase):
    def test_conversion(self):
        """Test that the conversion works correctly."""
        self.assertEqual(iso_duration_to_text("PT1H"), "Over 1 hour")
        self.assertEqual(iso_duration_to_text("PT10M"), "Over 10 minutes")
        self.assertEqual(iso_duration_to_text("PT30S"), "Under 10 minutes")
        self.assertEqual(iso_duration_to_text("PT2H10M30S"), "Over 2 hours")
        self.assertEqual(iso_duration_to_text("P1DT1H"), "Over 1 day")

    def test_space_removal(self):
        """Test that spaces are removed from the beginning and end of the string."""
        self.assertEqual(iso_duration_to_text(" PT1H"), "Over 1 hour")
        self.assertEqual(iso_duration_to_text("PT1H "), "Over 1 hour")
