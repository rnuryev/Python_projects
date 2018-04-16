import requests
from bs4 import BeautifulSoup
import csv
from datetime import date
from multiprocessing import Pool

def get_html_post(url, data):
    r = requests.post(url, data=data)
    return r.text

def get_html_get(url):
    r = requests.get(url)
    return r.text

def get_all_links(url, data):
    html = get_html_post(url, data)
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find('table', class_='tableProc').find_all('tr')
    all_links = []
    for lk in links:
        if lk.has_attr('onclick'):
            link = 'http://etzp.rzd.ru' + lk['onclick'][10:len(lk['onclick']) - 3]
            all_links.append(link)
    return all_links

def write_csv(data):
    with open('rzd_new.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['code'],
                         data['subject'],
                         data['customer'],
                         data['price'],
                         data['deadline'],
                         data['link'],
                         data['document_links'],))

def get_page_data(url):
    html = get_html_get(url)
    soup = BeautifulSoup(html, 'lxml')

    spans_tender_info = soup.find('table', id='descriptionTable').find_all('span')

    try:
        code = spans_tender_info[0].text.strip()
    except:
        code = ''
    try:
        subject = spans_tender_info[1].text.strip()
    except:
        subject = ''
    try:
        customer = spans_tender_info[2].text.strip()
    except:
        customer = ''
    try:
        price = spans_tender_info[4].text.strip()
    except:
        price = ''
    try:
        deadline = spans_tender_info[6].text.strip()
    except:
        deadline = ''
    try:
        link = url
    except:
        link = ''
    try:
        document_links = []
        trs_a = soup.find('div', id='attachmentsDiv').find('table').find_all('a')
        for tr in trs_a:
            dl = {}
            dl['doc_name'] = tr.text.strip()
            dl['doc_link'] = 'http://etzp.rzd.ru' + tr.get('href')
            document_links.append(dl)
    except:
        document_links = []
    data = {
        'code': code,
        'subject': subject,
        'customer': customer,
        'price': price,
        'deadline': deadline,
        'link': link,
        'document_links': document_links
    }

    write_csv(data)


if __name__ == '__main__':
    url = 'http://etzp.rzd.ru/freeccee/main?ACTION=searchProc'
    name_text = 'поставка'
    # Срок подачи заявок "с":
    bid_deadlin_from = date.today().strftime('%d.%m.%Y')
    data = {
        'p_page': 0,
        'p_page_size': 200,
        'p_order': 'DATEENDSEARCH',
        'p_orderType': 'DESC',
        'p_org': 'all',
        'p_cust': 'all',
        'p_inlots': 'true',
        'p_msp': 'false',
        'p_type_select': None,
        'p_cust_select': 'all',
        'p_org_select': 'all',
        'p_cnumber': None,
        'name_text': name_text,
        'p_dateend_begin': None,
        'p_dateend_begin_old': None,
        'p_dateend_end': None,
        'p_dateend_end_old': None,
        'p_contest_date_oa_begin_old': None,
        'p_contest_date_oa_end_old': None,
    }

    all_links = get_all_links(url, data)

    with Pool(20) as po:
        po.map(get_page_data, all_links)