# webscraping_capstone
Web Scraping Capstone Code The Dream
This project scrapes current weather information from timeanddate.com using Selenium, cleans it with pandas, and saves the results to CSV files. Later stages will store the data in SQLite and show it in a Streamlit dashboard.

What it does so far

Step 1. search_city.py uses the Weather in Any City search on the site to find Cary, North Carolina. It scrapes the temperature, conditions, visibility, pressure, humidity and dew point. The output is saved to data/raw_cary.csv.

Step 2. clean_weather.py loads the raw CSV into a pandas DataFrame, removes missing and duplicate rows, converts text values to numbers (for example 52 F becomes 52.0), and splits the search query into city and state. The output is saved to data/clean_cary.csv. The script prints the data before and after cleaning.

Setup

You need Python 3.9 or newer and Google Chrome installed.

Clone the repository:
git clone https://github.com/sakthinandagopaltn/webscraping_capstone.git

Go into the project folder:
cd webscraping_capstone

Create a virtual environment:
python3 -m venv venv

Activate it. On Mac or Linux:
source venv/bin/activate

On Windows:
venv\Scripts\activate

Install the dependencies:
pip install -r requirements.txt

How to run

Run the scraper first. It writes data/raw_cary.csv:
python search_city.py

Then run the cleaning script. It writes data/clean_cary.csv:
python clean_weather.py

A Chrome window opens while the scraper runs. The ChromeDriver is downloaded automatically by webdriver-manager.

Project structure

search_city.py is the Selenium scraper.
clean_weather.py handles cleaning and transformation.
requirements.txt lists the dependencies.
data folder holds the raw and clean CSV files.

Notes on scraping

Requests are spaced out with pauses, and each page is loaded only once per run. Check the site's robots.txt file and terms of use before scraping.
