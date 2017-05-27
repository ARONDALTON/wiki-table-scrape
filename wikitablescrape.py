"""Create CSVs from all tables on a Wikipedia article."""

import csv
import os
import platform

import bs4
import requests


class WikiPage(object):
    """Basic components of a Wikipedia page."""

    def __init__(self, url: str):
        resp = requests.get(url)
        self.soup = bs4.BeautifulSoup(resp.content, 'lxml')
        self._tables = None

    @property
    def tables(self):
        """Return parsed table data for this Wiki page."""
        if not self._tables:
            # Parse the table data from the page
            classes = {"class": ["sortable", "plainrowheaders"]}
            tags = self.soup.find_all("table", classes)
            self._tables = [WikiTable(tag) for tag in tags]
        return self._tables

    def table(self, name: str):
        """Return a table in a page by its name."""
        for table in self.tables:
            if table.name == name:
                return table


class WikiTable(object):
    """Table in a Wikipedia page."""

    def __init__(self, tag: bs4.Tag):
        self.tag = tag
        self._name = None

    def __repr__(self):
        return '<WikiTable "{}">'.format(self.name)

    @property
    def name(self):
        """Return table name parsed from caption or headline."""
        if not self._name:
            captions = self.tag.find_all('caption')
            if captions:
                self._name = strip_footnotes(captions[0])
            else:
                headline = previous_headline_element(self.tag)
                if not headline:
                    error = 'No name found for table "{}"'.format(self.tag)
                    raise ValueError(error)
                self._name = headline[0].text
        return self._name

    def to_csv(self, filepath: str):
        """Export the table to a CSV file at given filepath."""
        with open(filepath, mode='w', newline='', encoding='utf-8') as output:
            # Deal with Windows inserting an extra '\r' in line terminators
            if platform.system() == 'Windows':
                writer = csv.writer(output, lineterminator='\n')
            else:
                writer = csv.writer(output)

            write_html_table_to_csv(self.tag, writer)


def scrape(url, output_name):
    """Create CSVs from all tables in a Wikipedia article.

    ARGS:
        url (str): The full URL of the Wikipedia article to scrape tables from.
        output_name (str): The base file name (without filepath) to write to.
    """

    # Read tables from Wikipedia article into list of HTML strings
    page = WikiPage(url)

    # Create folder for output if it doesn't exist
    try:
        os.mkdir(output_name)
    except Exception:  # Generic OS Error
        pass

    for table in page.tables:
        filename = '_'.join(table.name.lower().split()) + '.csv'
        filepath = os.path.join(output_name, filename)
        table.to_csv(filepath)


def write_html_table_to_csv(table: bs4.Tag, writer):
    """Write HTML table from Wikipedia to a CSV file.

    ARGS:
        table (bs4.Tag): The bs4 Tag object being analyzed.
        writer (csv.writer): The csv Writer object creating the output.
    """

    # Hold elements that span multiple rows in a list of
    # dictionaries that track 'rows_left' and 'value'
    saved_rowspans = []
    for row in table.find_all("tr"):
        cells = row.find_all(["th", "td"])

        # If the first row, use it to define width of table
        if len(saved_rowspans) == 0:
            saved_rowspans = [None for _ in cells]
        # Insert values from cells that span into this row
        elif len(cells) != len(saved_rowspans):
            for index, rowspan_data in enumerate(saved_rowspans):
                if rowspan_data is not None:
                    # Insert the data from previous row; decrement rows left
                    value = rowspan_data['value']
                    cells.insert(index, value)

                    if saved_rowspans[index]['rows_left'] == 1:
                        saved_rowspans[index] = None
                    else:
                        saved_rowspans[index]['rows_left'] -= 1

        # If an element with rowspan, save it for future cells
        for index, cell in enumerate(cells):
            if cell.has_attr("rowspan"):
                rowspan_data = {
                    'rows_left': int(cell["rowspan"]),
                    'value': cell,
                }
                saved_rowspans[index] = rowspan_data

        if cells:
            # Clean the data of references and unusual whitespace
            cleaned = clean_data(cells)

            # Fill the row with empty columns if some are missing
            # (Some HTML tables leave final empty cells without a <td> tag)
            columns_missing = len(saved_rowspans) - len(cleaned)
            if columns_missing:
                cleaned += [None] * columns_missing

            writer.writerow(cleaned)


def clean_data(row):
    """Clean table row list from Wikipedia into a string for CSV.

    ARGS:
        row (bs4.ResultSet): The bs4 result set being cleaned for output.

    RETURNS:
        cleaned_cells (list[str]): List of cleaned text items in this row.
    """

    cleaned_cells = []

    for cell in row:
        # Strip references from the cell
        references = cell.find_all("sup", {"class": "reference"})
        if references:
            for ref in references:
                ref.extract()

        # Strip sortkeys from the cell
        sortkeys = cell.find_all("span", {"class": "sortkey"})
        if sortkeys:
            for ref in sortkeys:
                ref.extract()

        # Strip footnotes from text and join into a single string
        cleaned = (
            strip_footnotes(cell)
            .replace('\xa0', ' ')  # Replace non-breaking spaces
            .replace('\n', ' ')  # Replace newlines
            .strip()
        )

        cleaned_cells += [cleaned]

    return cleaned_cells


def strip_footnotes(tag: bs4.Tag) -> str:
    """Remove wikipedia footnotes (e.g. [14]) from text."""
    stripped = ''.join(text for text in tag.find_all(text=True)
                       if not text.startswith('['))
    return stripped


def previous_headline_element(tag: bs4.Tag) -> bs4.Tag:
    """Return first Wikipedia-style headline element before a given tag."""
    for element in tag.findPreviousSiblings():
        if not isinstance(element, bs4.Tag):
            continue
        if not element.name == 'h2':
            continue
        headline = element.find_all('span', {'class': 'mw-headline'})
        if headline:
            return headline
