import requests
import datetime
from bs4 import BeautifulSoup
import csv
import psycopg2
import json
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
    try:
        links = soup.find('table', class_='tableProc').find_all('tr')
    except:
        page_links = []
    else:
        page_links = []
        for lk in links:
            if lk.has_attr('onclick'):
                link = 'http://etzp.rzd.ru' + lk['onclick'][10:len(lk['onclick']) - 3]
                page_links.append(link)
    return page_links

def write_csv(data):
    with open('rzd_to_DB.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['code'],
                         data['subject'],
                         data['customer'],
                         data['price'],
                         data['deadline'],
                         data['link'],
                         data['document_links'],))

def write_db(data):
    conn = psycopg2.connect(dbname='tenders', user='postgres', password='1Qwerty', host='127.0.0.1', port='5432')
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.tenders_tenders WHERE code=%s", (data['code'],))
    result = cur.fetchall()
    if not result:
        cur.execute("INSERT INTO public.tenders_tenders (etp, code, subject, customer, price, deadline, link, lots, document_links) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id",
                (data['etp'], data['code'], data['subject'], data['customer'], data['price'], datetime.datetime.strptime(data['deadline'][0:10], '%d.%m.%Y').date(), data['link'], json.dumps(data['lots']), json.dumps(data['document_links'])))
        # tend_id = cur.fetchone()[0]
        # for d_l in data['document_links']:
        #     cur.execute("INSERT INTO public.tenders_tenderdocuments (doc_title, doc_link, tender_id) VALUES (%s, %s, %s)", (d_l['doc_name'], d_l['doc_link'], tend_id))
        conn.commit()
    conn.close()

    #data['code'], data['subject'], data['customer'], data['price'], data['deadline'], data['link'], data['document_links']

def get_page_data(url):
    html = get_html_get(url)
    soup = BeautifulSoup(html, 'lxml')

    try:
        spans_tender_info = soup.find('table', id='descriptionTable').find_all('span')
    except:
        spans_tender_info = soup

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
        if spans_tender_info[4].text.strip().find('НДС') != -1:
            price = spans_tender_info[4].text.strip()
        else:
            price = ''
    except:
        price = ''
    try:
        if spans_tender_info[4].text.strip().find('НДС') == -1:
            deadline = spans_tender_info[5].text.strip()
        else:
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
    try:
        lots = []
        table_lots = soup.find('table', id='listOfLots').find_all('tr', class_='tr2')
        for tl in table_lots:
            temp_dict = {}
            tds = tl.find_all('td', class_='a9')
            temp_dict['num_lot'] = tds[0].text.strip()
            temp_dict['name_lot'] = tds[1].text.strip()
            # if tds[2].text.strip().find('НДС') != -1:
            #     temp_dict['price_lot'] = tds[2].text.strip()
            # else:
            #     temp_dict['price_lot'] = tds[3].text.strip()
            temp_dict['price_lot'] = tl.find('td', class_='a9right').text.strip()
            lots.append(temp_dict)
    except:
        lots = []
    data = {
        'etp': 'РЖД',
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
    #write_csv(data)


if __name__ == '__main__':
    url = 'http://etzp.rzd.ru/freeccee/main?ACTION=searchProc'
    name_text = None
    # Срок подачи заявок "с":
    bid_deadlin_from = date.today().strftime('%d.%m.%Y')
    TYPE_SECECTS = ('OC_CKZ', 'OC_TWOSTAGE', 'OA_CKZ', 'ZK_CKZ', 'RO_CKZ')
    #TYPE_SECECTS = ('RO_CKZ',)
        # p_type_select = OC_CKZ #Открытый конкурс
    # p_type_select = OC_TWOSTAGE #Открытый двухэтапный конкурс
    # p_type_select = OA_CKZ #Открытый аукцион
    # p_type_select = ZK_CKZ%7CZK_RZDS #Запрос котировок
    # p_type_select = RO_CKZ #Запрос предложений
    # p_type_select = PQS_CKZ%7CPQS_UNLIMITED #Предварительный квалификационный отбор
    # p_type_select = QS_CKZ%7CQS_RZDS #Конкурс среди предприятий, прошедших квалификационный отбор

    all_links = []
    for p_type in TYPE_SECECTS:

        data = {
            'p_page': 0,
            'p_page_size': 200,
            'p_order': 'DATEENDSEARCH',
            'p_orderType': 'DESC',
            'p_org': 'all',
            'p_cust': 'all',
            'p_inlots': 'true',
            'p_msp': 'false',
            'p_type_select': p_type,
            'p_cust_select': 'all',
            'p_org_select': 'all',
            'p_cnumber': None,
            'name_text': name_text,
            'p_dateend_begin': bid_deadlin_from,
            'p_dateend_begin_old': None,
            'p_dateend_end': None,
            'p_dateend_end_old': None,
            'p_contest_date_oa_begin_old': None,
            'p_contest_date_oa_end_old': None,
        }
        html = get_html_post(url, data)
        soup = BeautifulSoup(html, 'lxml')
        try:
            total_pages = int(soup.find('div', class_='a8b').find_all('td', class_='pagesButtons')[-1].text.strip())
        except:
            total_pages = 1

        for i in range(total_pages):
            data['p_page'] = i
            page_links = get_all_links(url, data)
            all_links.extend(page_links)


    with Pool(20) as po:
        po.map(get_page_data, all_links)
