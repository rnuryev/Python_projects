import requests
from bs4 import BeautifulSoup
import csv
# from urllib.parse import quote

def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('div', class_='padB10').find_all('a')[-1].get('href')
    total_pages = int(pages[-1])
    return total_pages

def write_csv(data):
    with open('rzd.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['date'],
                         data['code'],
                         data['subject'],
                         data['link']))

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    tenders = soup.find('table', class_='table').find_all('tr')
    for tender in tenders:
        tds = tender.find_all('td')
        try:
            date = tds[1].text.strip()
        except:
            date = ''
        try:
            code = tds[2].text.strip()
        except:
            code = ''
        try:
            sls = tds[5].find('a').text.split('\n')
            subject = ' '.join(list(map(str.strip, sls)))
        except:
            subject = ''
        try:
            link = 'http://tender.rzd.ru' + tds[5].find('a').get('href')
        except:
            link = ''
        data = {'date': date,
                'code': code,
                'subject': subject,
                'link': link}

        write_csv(data)

def main():
    base_url = 'http://tender.rzd.ru/tender/public/ru?cod=&deal_type=&property_type_id=&organaizer_id=&city_id=&status_type=&name='
    query_part = 'создание'
    additional_part = '&date_from=&date_to=&action=filtr&STRUCTURE_ID=4078&layer_id=&x=31&y=12'
    page_part = '&page4893_1465='
    url = base_url + query_part + additional_part + page_part + '1'
    total_pages = get_total_pages(get_html(url))
    for i in range(1, total_pages+1):
        url_gen = base_url + query_part + additional_part + page_part + str(i)
        get_page_data(get_html(url_gen))

if __name__ == '__main__':
    main()