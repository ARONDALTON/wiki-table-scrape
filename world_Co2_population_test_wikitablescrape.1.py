"""Test the wikitablescrape script on four articles."""

import os
import shutil

import wikitablescrape

# Delete previous output folder if it exists, then create a new one
try:
    shutil.rmtree('output')
except FileNotFoundError:
    pass

wikitablescrape.scrape(
    url="https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population",
    output_name="world_population_by_contry"
)

wikitablescrape.scrape(
    url="https://en.wikipedia.org/wiki/List_of_countries_by_carbon_dioxide_emissions",
    output_name="carbon_dioxide_by_contry"
)

# wikitablescrape.scrape(
#     url="https://en.wikipedia.org/wiki/List_of_National_Basketball_Association_career_scoring_leaders",
#     output_name="nba"
# )

# wikitablescrape.scrape(
#     url="https://en.wikipedia.org/wiki/List_of_highest-grossing_films",
#     output_name="films"
# )

# Move all CSV folders into a single 'output' folder
os.makedirs('output')
# shutil.move('./insulation', './output')
# shutil.move('./rebates', './output')
# shutil.move('./nba', './output')
# shutil.move('./films', './output')
