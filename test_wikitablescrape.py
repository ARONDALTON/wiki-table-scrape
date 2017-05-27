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


def test_all():
    """Create all known tables in a temporary output folder."""
    testfolder = tempfile.mkdtemp()

    wikitablescrape.scrape(
        url="https://en.wikipedia.org/wiki/List_of_volcanoes_by_elevation",
        output_name=os.path.join(testfolder, "volcanoes")
    )

    wikitablescrape.scrape(
        url="https://en.wikipedia.org/wiki/List_of_National_Basketball_Association_career_scoring_leaders",
        output_name=os.path.join(testfolder, "nba")
    )

    shutil.rmtree(testfolder)


def test_list_tables():
    """Can list available tables on a Wikipedia page."""
    table_names = [table.name for table in FILMS.tables]
    assert table_names == [
        'Highest-grossing films',
        'Highest-grossing films adjusted for inflation as of 2014',
        'High-grossing films by year of release',
        'Timeline of the highest-grossing film record'
    ]


# TODO -- Should Use parent section's header name (e.g. 8000 meters)
def test_list_tables_no_caption():
    """Can list tables by index that have no caption."""
    table_names = [table.name for table in MOUNTAINS.tables]
    assert table_names == [
        'table_0', 'table_1', 'table_2', 'table_3', 'table_4',
        'table_5', 'table_6', 'table_7', 'table_8'
    ]


def test_scrape_single_table():
    """Can scrape a single table from a page and return it in memory."""
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
