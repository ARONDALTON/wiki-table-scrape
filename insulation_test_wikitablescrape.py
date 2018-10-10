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
    url="https://www.bchydro.com/powersmart/residential/savings-and-rebates/current-rebates-buy-backs/home-renovation-rebates/eligibility.html",
    output_name="rebates"
)

wikitablescrape.scrape(
    url="https://en.wikipedia.org/wiki/R-value_(insulation)",
    output_name="insulation"
)

wikitablescrape.scrape(
    url="https://en.wikipedia.org/wiki/List_of_National_Basketball_Association_career_scoring_leaders",
    output_name="nba"
)

wikitablescrape.scrape(
    url="https://en.wikipedia.org/wiki/List_of_highest-grossing_films",
    output_name="films"
)

# Move all CSV folders into a single 'output' folder
os.makedirs('output')
shutil.move('./insulation', './output')
shutil.move('./rebates', './output')
shutil.move('./nba', './output')
shutil.move('./films', './output')
