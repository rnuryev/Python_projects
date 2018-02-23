import requests
from bs4 import BeautifulSoup
import csv
from datetime import date, timedelta
from multiprocessing import Pool

def get_html(url):
    r = requests.get(url)
    return r.text

def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    total_pages = int(soup.find('div', class_='cell cell-left list').find_all('li')[-2].text)
    return total_pages

def write_csv(data):
    with open('rosatom.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['code'],
                         data['subject'],
                         data['customer'],
                         data['tender_cost'],
                         data['date_end'],
                         data['status'],
                         data['link']))

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    tenders = soup.find('div', id='table-lots-list').find('table').find('tbody').find_all('tr')
    for tender in tenders:
        if 'description' not in tender['class']:
            tds = tender.find_all('td')
            try:
                code = tds[2].find_all('p')[0].text.strip()
            except:
                code = ''
            try:
                subject = tds[2].find_all('p')[1].find('a').text.strip()
            except:
                subject = ''
            try:
                link = 'http://www.zakupki.rosatom.ru' + tds[2].find_all('p')[1].find('a').get('href')
            except:
                link = ''
            try:
                tender_cost = tds[3].find_all('p')[0].text.strip()
            except:
                tender_cost = ''
            try:
                customer = tds[4].find_all('p')[0].text.strip()
            except:
                customer = ''
            try:
                date_text_list = tds[6].find_all('p')[0].text.split('\n')
                date_end = ' '.join(list(map(str.strip, date_text_list)))
            except:
                date_end = ''
            try:
                status = tds[7].find_all('p')[0].text.strip()
            except:
                status = ''

            data = {'code': code,
                    'subject': subject,
                    'customer': customer,
                    'tender_cost': tender_cost,
                    'date_end': date_end,
                    'status': status,
                    'link': link}

            write_csv(data)

def make_all(url):
    html = get_html(url)
    get_page_data(html)

def main():
    query_part = 'поставка'
    # Добавил часть с временным промежутком в 1 неделю, показывате конкурсы, обупликованные за последнюю неделю
    date_start = date.today() - timedelta(days=7)
    date_end = date.today()
    base_url = 'http://www.zakupki.rosatom.ru/Web.aspx?node=currentorders&ot='
    additional_part = '&tso=1&tsl=1&sbflag=0&ostate=P'
    date_start_part = '&pubdates='
    date_end_part = '&pubdate='
    page_part = '&pform=a&page='
    url = base_url + query_part + additional_part + date_start_part + date_start.strftime('%Y%m%d') + date_end_part + date_end.strftime('%Y%m%d') + page_part + '1'
    total_pages = get_total_pages(get_html(url))
    url_pages = []
    for i in range(1, total_pages+1):
        url_gen = base_url + query_part + additional_part + date_start_part + str(date_start) + date_end_part + str(date_end) + page_part + str(i)
        url_pages.append(url_gen)
    with Pool(20) as po:
        po.map(make_all, url_pages)

if __name__ == '__main__':
    main()