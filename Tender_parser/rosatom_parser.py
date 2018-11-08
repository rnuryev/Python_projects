import requests
import datetime
import psycopg2
from bs4 import BeautifulSoup
import json
from datetime import date
from multiprocessing import Pool

def get_html(url):
    r = requests.get(url)
    return r.text

def write_db(data):
    with psycopg2.connect(dbname='tenders', user='postgres', password='1Qwerty', host='127.0.0.1', port='5432') as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM public.tenders_tenders WHERE code=%s", (data['code'],))
            result = cur.fetchall()
            if not result:
                cur.execute("INSERT INTO public.tenders_tenders (etp, code, subject, customer, price, deadline, link, lots, document_links) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (data['etp'], data['code'], data['subject'], data['customer'], data['price'], datetime.datetime.strptime(data['deadline'][0:10], '%d.%m.%Y').date(), data['link'], json.dumps(data['lots']), json.dumps(data['document_links'])))

# def get_total_pages(html):
#     soup = BeautifulSoup(html, 'lxml')
#     total_pages = int(soup.find('div', class_='cell cell-left list').find_all('li')[-2].text)
#     return total_pages

def get_total_pages():
    url = 'http://www.zakupki.rosatom.ru/Web.aspx?node=currentorders&tso=1&tsl=1&sbflag=0&ostate=P&findates=' + date.today().strftime('%Y%m%d2359') + '&pform=a&page=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    total_pages = soup.find('div', class_='tbl pages-list').find_all('li')[-2].text.strip()

    return int(total_pages)

def get_lots(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    lots = []
    lots_trs = soup.find('div', id='table_07').find('tbody').find_all('tr')
    for index, tr in enumerate(lots_trs):
        temp_dict = {}
        tds = tr.find_all('td')
        temp_dict['num_lot'] = index + 1
        temp_dict['name_lot'] = tds[1].find('p').text.strip()
        temp_dict['price_lot'] = tds[2].find('p').text.strip()
        lots.append(temp_dict)
    return lots

def get_doc_links(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    document_links = []
    doc_trs = soup.find('div', id='table_04').find('tbody').find_all('tr')
    for tr in doc_trs:
        temp_dict = {}
        td = tr.find('td', class_='ms-formlabel')
        temp_dict['doc_name'] = td.find_all('a')[1].text.strip()
        temp_dict['doc_link'] = 'http://www.zakupki.rosatom.ru' + td.find_all('a')[1].get('href')
        document_links.append(temp_dict)
    return document_links

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        tenders = soup.find('div', id='table-lots-list').find('tbody').find_all('tr')
    except:
        tenders = []
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
                price = tds[3].find_all('p')[0].text.strip()
            except:
                price = ''
            try:
                customer = tds[4].find_all('p')[0].text.strip()
            except:
                customer = ''
            try:
                date_text_list = tds[6].find_all('p')[0].text.split('\n')
                date_end = ' '.join(list(map(str.strip, date_text_list)))
                deadline = date_end.split('/')[0].strip().split(' ')[-1]
                for ch in deadline:
                    if ch not in '1234567890.,':
                        deadline = '01.01.1900'
                        break
            except:
                deadline = '01.01.1900'
            try:
                document_links = get_doc_links(link)
            except:
                document_links = []
            try:
                lots = get_lots(link)
            except:
                lots = []

            data = {
                'etp': 'Росатом',
                'code': code,
                'subject': subject,
                'customer': customer,
                'price': price,
                'deadline': deadline,
                'link': link,
                'document_links': document_links,
                'lots': lots
            }

            write_db(data)


def do_all(url):
    html = get_html(url)
    get_page_data(html)

if __name__ == '__main__':
    url_basis = 'http://www.zakupki.rosatom.ru/Web.aspx?node=currentorders&tso=1&tsl=1&sbflag=0&ostate=P&findates=' + date.today().strftime(
        '%Y%m%d2359') + '&pform=a&page='
    url = 'http://www.zakupki.rosatom.ru/Web.aspx?node=currentorders&tso=1&tsl=1&sbflag=0&ostate=P&findates=' + date.today().strftime(
        '%Y%m%d2359') + '&pform=a&page=1'
    pages = get_total_pages()
    all_pages = []
    for i in range(1, pages + 1):
        ur = url_basis + str(i)
        all_pages.append(ur)


    with Pool(20) as po:
        po.map(do_all, all_pages)