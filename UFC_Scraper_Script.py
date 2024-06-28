import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import logging
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BASE_URL = "http://ufcstats.com/statistics/fighters"
OUTPUT_DIR = "ufc_data"
OUTPUT_FILE = "ufc_fighters.csv"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to make requests with rate limiting
def make_request(url, max_retries=3, delay=1):
    for _ in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            time.sleep(delay)  # Rate limiting
            return response
        except requests.RequestException as e:
            logging.warning(f"Request failed: {e}. Retrying...")
    logging.error(f"Failed to retrieve {url} after {max_retries} attempts.")
    return None

# Function to parse fighter details
def parse_fighter_details(fighter_url):
    response = make_request(fighter_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract fighter name and record
    name = soup.select_one('span.b-content__title-highlight').get_text(strip=True)
    record = soup.select_one('span.b-content__title-record').get_text(strip=True).replace('Record: ', '')

    # Extract physical stats
    info_rows = soup.select('li.b-list__box-list-item')
    info = {}
    for row in info_rows:
        text = row.get_text(strip=True)
        if ':' in text:
            key, value = text.split(':', 1)
            info[key.strip()] = value.strip()

    # Extract career stats
    career_stats = {}
    stat_rows = soup.select('li.b-list__box-list-item_type_block')
    for row in stat_rows:
        text = row.get_text(strip=True)
        if ':' in text:
            key, value = text.split(':', 1)
            career_stats[key.strip()] = value.strip()

    fighter_data = {
        'Name': name,
        'Record': f"'{record}",  # Prefixing with a single quote to prevent Excel from converting to date
        'Height': info.get('Height', ''),
        'Weight': info.get('Weight', ''),
        'Reach': info.get('Reach', ''),
        'Stance': info.get('STANCE', ''),
        'DOB': info.get('DOB', ''),
        'SLpM': career_stats.get('SLpM', ''),
        'Str. Acc.': career_stats.get('Str. Acc.', ''),
        'SApM': career_stats.get('SApM', ''),
        'Str. Def': career_stats.get('Str. Def', ''),
        'TD Avg.': career_stats.get('TD Avg.', ''),
        'TD Acc.': career_stats.get('TD Acc.', ''),
        'TD Def.': career_stats.get('TD Def.', ''),
        'Sub. Avg.': career_stats.get('Sub. Avg.', '')
    }
    return fighter_data

# Function to scrape all fighters
def scrape_fighters(test_mode=False):
    all_fighters = []
    fighter_count = 0
    for char in 'abcdefghijklmnopqrstuvwxyz':
        page = 1
        consecutive_empty_pages = 0
        while True:
            url = f"{BASE_URL}?char={char}&page={page}"
            response = make_request(url)
            if not response:
                break

            soup = BeautifulSoup(response.text, 'html.parser')
            fighters = soup.select('tr.b-statistics__table-row')[1:]  # Skip header row

            if not fighters or all(len(fighter.select('td')) < 2 for fighter in fighters):
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= 2:
                    logging.info(f"No more fighters found for letter {char.upper()}. Moving to next letter.")
                    break
            else:
                consecutive_empty_pages = 0  # Reset if we find fighters

            fighters_found = False
            for fighter in fighters:
                fighter_link = fighter.select_one('td a')
                if fighter_link:
                    fighters_found = True
                    fighter_url = urljoin(BASE_URL, fighter_link['href'])
                    logging.info(f"Scraping fighter: {fighter_url}")
                    fighter_data = parse_fighter_details(fighter_url)
                    if fighter_data:
                        all_fighters.append(fighter_data)
                        fighter_count += 1

                    if test_mode and fighter_count >= 5:
                        break

            if not fighters_found:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= 2:
                    logging.info(f"No more fighters found for letter {char.upper()}. Moving to next letter.")
                    break

            if test_mode and fighter_count >= 5:
                break

            logging.info(f"Scraped fighters data for letter {char.upper()}, page {page}")
            page += 1

        if test_mode and fighter_count >= 5:
            break

    df = pd.DataFrame(all_fighters)
    df.to_csv(os.path.join(OUTPUT_DIR, OUTPUT_FILE), index=False)
    logging.info(f"Fighters data saved to {os.path.join(OUTPUT_DIR, OUTPUT_FILE)}")

# Main execution
if __name__ == "__main__":
    logging.info("Starting UFC fighters data scraping...")
    # Uncomment the line below for test mode
    # scrape_fighters(test_mode=True)
    # Comment the line below if using test mode
    scrape_fighters()
    logging.info("UFC fighters data scraping completed.")
