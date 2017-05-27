"""Test the wikitablescrape script on four articles."""

import csv
import os
import shutil
import tempfile

import wikitablescrape


FILMS = wikitablescrape.WikiPage(
    "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
)

MOUNTAINS = wikitablescrape.WikiPage(
    "https://en.wikipedia.org/wiki/List_of_mountains_by_elevation"
)

CONGRESS = wikitablescrape.WikiPage(
    "https://en.wikipedia.org/wiki/Current_members_of_the_United_States_House_of_Representatives"
)


def test_table_names():
    """Can list available tables on a page (named by caption)."""
    table_names = [table.name for table in FILMS.tables]
    assert table_names == [
        'Highest-grossing films',
        'Highest-grossing films adjusted for inflation as of 2014',
        'High-grossing films by year of release',
        'Timeline of the highest-grossing film record'
    ]


def test_table_names_no_caption():
    """Can list tables that have no caption by section headline."""
    table_names = [table.name for table in MOUNTAINS.tables]
    assert table_names == [
        '8,000 metres',
        '7,000 metres',
        '6,000 metres',
        '5,000 metres',
        '4,000 metres',
        '3,000 metres',
        '2,000 metres',
        '1,000 metres',
        'Under 1,000 metres'
    ]


def test_scrape_single_table():
    """Can scrape a single table from a page and write it to a CSV."""
    # Create the CSV in a test directory
    testdir = tempfile.mkdtemp()
    output = os.path.join(testdir, 'testfile.csv')
    table = FILMS.table('Highest-grossing films')
    table.to_csv(output)
    # Assert the CSV is as expected, then delete it
    with open(output, 'r') as stream:
        reader = csv.reader(stream)
        headers = next(reader)
        row_one = next(reader)
    assert headers == ['Rank', 'Peak', 'Title', 'Worldwide gross', 'Year', 'Reference(s)']
    assert row_one == ['1', '1', 'Avatar', '$2,787,965,087', '2009', '']
    shutil.rmtree(testdir)


# TODO -- Build this test that rowspan tables are read properly
def test_rowspan_table():
    """Can properly parse an HTML table with many rowspans."""
    pass
