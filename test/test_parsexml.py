# /test/test_parsexml.py
#
# Tests for parsexml.
#
# See /LICENCE.md for Copyright information
"""Tests for parsexml."""

from importer import parsexml

from nose_parameterized import parameterized

from six.moves import StringIO

from testtools import (ExpectedException, TestCase)
from testtools.matchers import Is

from xml.etree import ElementTree


def wrap_document_text(text):
    """Wrap a valid XML document's txt with PubMed headers."""
    return ("<PubmedArticleSet><PubmedArticle>{}"
            "</PubmedArticle></PubmedArticleSet>").format(text)


def construct_document_from(**kwargs):
    """Create XML document from keyword arguments, recursively.

    If the value is a dictionary, recurse into that and create a
    document.
    """
    document_list = []

    for key, value in kwargs.items():
        if isinstance(value, str):
            document_list.append("<{key}>{value}</{key}>".format(key=key,
                                                                 value=value))
        elif isinstance(value, dict):
            document_list.append("<{key}>{value}</{key}>".format(
                key=key,
                value=construct_document_from(**value)
            ))

    return "\n".join(document_list)


POSSIBLE_MOCK_FIELDS = {
    "MedlineCitation": {
        "PMID": "medline_cit"
    },
    "Author": {
        "LastName": "last_name",
        "ForeName": "fore_name"
    },
    "DateCompleted": {
        "Year": "2011",
        "Month": "11",
        "Day": "11"
    },
    "DateRevised": {
        "Year": "2012",
        "Month": "11",
        "Day": "11"
    },
    "Journal": {
        "ISSN": "0"
    },
    "MedlineJournalInfo": {
        "Country": "Australia"
    }
}

CORRESPONDING_ENTRIES = {
    "Author": "Author",
    "DateCompleted": "pubDate",
    "DateRevised": "reviseDate",
    "Journal": "ISSN",
    "MedlineJournalInfo": "country"
}


class TestFileToElementTree(TestCase):
    """Test conversion of a file to an element tree."""

    def test_convert(self):
        """4.5.3.1 File can be converted to element tree."""
        stream = StringIO("<html></html>")
        parsexml.file_to_element_tree(stream)

    def test_invalid_html_file(self):
        """4.5.3.2 Throw error when parsing invalid html file."""
        stream = StringIO("<html></xml>")
        with ExpectedException(ElementTree.ParseError):
            parsexml.file_to_element_tree(stream)

    @parameterized.expand(CORRESPONDING_ENTRIES.items())
    def test_parsing_file_with_missing_optional_fields(self,
                                                       field,
                                                       entry):
        """4.5.3.3 Parse data that has missing optional fields."""
        # Construct document that has all fields but field
        fields = {
            k: v for k, v in POSSIBLE_MOCK_FIELDS.items()
            if k != field
        }
        stream = StringIO(
            wrap_document_text(construct_document_from(**fields))
        )
        result = parsexml.parse_element_tree(
            parsexml.file_to_element_tree(stream)
        )
        self.assertThat(result[entry], Is(None))

    def test_parsing_file_with_no_fields_throws(self):
        """4.5.3.4 Throw error file has no relevant fileds."""
        stream = StringIO("<PubmedArticleSet><PubmedArticle>"
                          "</PubmedArticle></PubmedArticleSet>")
        with ExpectedException(parsexml.NoFieldsError):
            parsexml.parse_element_tree(
                parsexml.file_to_element_tree(stream)
            )
