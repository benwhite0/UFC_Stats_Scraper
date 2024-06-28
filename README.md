# UFC Fighter Scraper

This script scrapes fighter data from [ufcstats.com](http://ufcstats.com) and saves it into a CSV file.

## Requirements

- Python 3
- Required Python libraries:
  - `requests`
  - `beautifulsoup4`
  - `pandas`

## Installation

Install the required libraries using pip:


'pip install requests beautifulsoup4 pandas'

## Usage
Run the script to scrape fighter data and save it to a CSV file:

'python ufc_fighter_scraper.py'

## Test Mode
To run the script in test mode (scraping only the first 5 fighters), uncomment the following line in the script:

'# scrape_fighters(test_mode=True)'

and comment out the line:

'scrape_fighters()'

## Output
The scraped data will be saved to ufc_data/ufc_fighters.csv.

## Notes
The script includes error handling and retries for failed requests.
A single quote is prefixed to the Record field to prevent Excel from converting it to a date.
The script detects consecutive empty pages and moves to the next letter if no fighters are found.
The script scrapes various stats including the fighter's name, record, height, weight, reach, stance, date of birth (DOB), significant strikes landed per minute (SLpM), significant striking accuracy (Str. Acc.), significant strikes absorbed per minute (SApM), significant strike defense (Str. Def), average takedowns landed per 15 minutes (TD Avg.), takedown accuracy (TD Acc.), takedown defense (TD Def.), and average submissions attempted per 15 minutes (Sub. Avg.).

## Logging
The script uses logging to provide detailed progress and error information.
