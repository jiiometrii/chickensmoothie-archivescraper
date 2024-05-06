import os
import requests
from bs4 import BeautifulSoup
import json
import threading

base_url = 'https://www.chickensmoothie.com'
tabs = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 
        'Store Pets', 'New Year', 'Lunar New Year', 'Valentine\'s Day', 'St. Patrick\'s Day', 
        'Easter', 'April Fool\'s', 'CS Birthday', 'Halloween', 'Christmas', 'Hanukkah', 'Staff Birthdays',
        'Special Releases', 'Thanksgiving', 'Kwanzaa', 'Medieval Faire', 'Beach Event', 'Chinese New Year',
        'Mardi Gras', 'Slumber Party', 'Egypt Event', 'Candy Event', 'Space Event', 'Lost City Event',
        'Jungle Event', 'Fae Mischief', 'Carnival Event', 'Cave Event', 'Internet Event', 'Camping Event']

def scrape_info(soup):
    pet_info = []
    images = soup.select('img.rarity-bar')

    for image in images:
        sibling = image.find_previous('img')
        pet_rarity = image['alt']
        pet_id = sibling['src'].split('?k=')[1].split('&amp;')[0]
        pet_info.append({'pet_id': pet_id, 'pet_rarity': pet_rarity})

    return pet_info

def scrape_with_pagination(url):
    pet_info = []
    next_page_url = url
    while next_page_url:
        page = requests.get(next_page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        pet_info += scrape_info(soup)
        next_element = soup.find('a', string='Next >')
        if next_element:
            next_page_url = base_url + next_element['href']
        else:
            next_page_url = None
    return pet_info

def scrape_year_month(year, month, collected_data):
    print(f"Checking {year}/{month}...")
    url = f"{base_url}/archive/{year}/{month}/"
    key = f"{year} - {month}"
    if key in collected_data:
        print(f"Skipping {year}/{month} as data already exists.")
        return
    try:
        page = requests.get(url, timeout=2.50, allow_redirects=False)
        if page.status_code == 302:
            print(f"Being redirected, SKIPPING {year}/{month}...")
            return
        print(f"Scraping {year}/{month}")
        pet_info = scrape_with_pagination(url)
        collected_data[key] = pet_info
    except Exception as e:
        print(f"Encountered error on {year}/{month}: {e}")

if __name__ == "__main__":
    if os.path.exists('scraped_data.json'):
        with open('scraped_data.json', 'r') as infile:
            collected_data = json.load(infile)
    else:
        collected_data = {}

    threads = []
    for year in range(2008, 2025):
        for month in tabs:
            thread = threading.Thread(target=scrape_year_month, args=(year, month, collected_data))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()

    with open('scraped_data.json', 'w') as outfile:
        json.dump(collected_data, outfile, indent=4)
