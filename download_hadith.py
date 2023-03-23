""" 
Downloads hadith by scraping sunnah.com and saves each book/chapter as .json files

some code inspired by SunnahGPT: https://github.com/hazemabdelkawy/SunnahGPT
"""

import json
import os, sys
import requests
from bs4 import BeautifulSoup

book = sys.argv[1]
base_url = f'https://sunnah.com/{book}'
data_dir = 'hadith/'+book+'/'
os.makedirs(data_dir, exist_ok=True)
page = requests.get(base_url)
soup = BeautifulSoup(page.content, 'html.parser')

books_containers = soup.find_all(class_='book_title')
books_data = []
for container in books_containers:
    book_number = container.find(class_='title_number').get_text(strip=True)
    book_link = f"{base_url}/{book_number}"
    book_en_name = container.find(class_='english_book_name').get_text(strip=True)
    book_ar_name = container.find(class_='arabic_book_name').get_text(strip=True)
    books_data.append({
        'book_link': book_link,
        'book_number': book_number,
        'english_name': book_en_name,
        # 'arabic_name': book_ar_name
    })
for book_data in books_data:
    page = requests.get(book_data['book_link'])
    soup = BeautifulSoup(page.content, 'html.parser')
    hadith_containers = soup.find_all(class_='actualHadithContainer')
    hadiths_data = []
    for idx, container in enumerate(hadith_containers):
        hadith_en_text = container.find(class_='english_hadith_full').get_text(strip=True)
        hadith_ar_text = container.find(class_='arabic_hadith_full').get_text(strip=True)
        hadith_ref = container.find(class_='hadith_reference').get_text(strip=True)
        ref_parts = hadith_ref.split('In-book reference:')
        reference = ref_parts[0].strip().replace('Reference:', '')
        book_reference = None
        hadith_number = None
        if len(ref_parts) > 1:
            book_ref_parts = ref_parts[1].strip().split(',')
            book_reference = book_ref_parts[0].strip()
            hadith_number = book_ref_parts[1].strip().split('USC-MSA')[0].strip()
        hadiths_data.append({
            'english': hadith_en_text,
            # 'arabic': hadith_ar_text,
            'reference': reference,
            'book_reference': book_reference,
            'hadith_number': hadith_number
        })
    book_data['hadith_data'] = hadiths_data

    filename = f"{book_data['book_number'].zfill(2)}_{book_data['english_name']}.json"
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(book_data, f)