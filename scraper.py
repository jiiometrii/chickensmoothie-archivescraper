import requests
from bs4 import BeautifulSoup
import json

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
    collected_pet_info = []
    next_page_url = url
    while next_page_url:
        page = requests.get(next_page_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        pet_info = scrape_info(soup)
        collected_pet_info += pet_info
        next_element = soup.find('a', string='Next >')
        if next_element:
            next_page_url = base_url + next_element['href']
            print(f"Next page found: {next_page_url}")
        else:
            next_page_url = None
    return collected_pet_info

if __name__ == "__main__":
    collected_pet_info = []

    for year in range(2008, 2025):
        for month in tabs:
            url = f"{base_url}/archive/{year}/{month}/"
            try:
                page = requests.get(url, timeout=2.50, allow_redirects=False)
                if page.status_code == 302:
                    print(f"Redirected to {page.headers['Location']}")
                    print(f'Skipping {year}/{month}...')
                    continue
                print(f"Scraping {year}/{month}")
                collected_pet_info += scrape_with_pagination(url)
            except Exception as e:
                # print('Encountered error:', e)
                print(f"Encountered error on {year}/{month}")
                continue
                
    with open('scraped_data.json', 'w') as outfile:
        json.dump(collected_pet_info, outfile, indent=4)
