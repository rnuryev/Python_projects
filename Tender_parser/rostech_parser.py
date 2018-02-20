import requests
import csv
from bs4 import BeautifulSoup

def get_html(url, ajax_data):
    r = requests.post(url, data=ajax_data)
    return r.text

def write_csv(data):
    with open('rostech.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow((data['code_tender'],
                         data['subject_tender'],
                         data['customer'],
                         data['type_tender'],
                         data['summ_tender'],
                         data['date_end'],
                         data['status_tender'],
                         data['link']))

def filter_tender(data):
    BAD_TYPE_TENDER = 'Закупка у единственного поставщика'
    GOOD_STATUS_TENDER = ('Приём заявок',
                          'Текущая закупка',
                          'Опубликован')
    return (data['type_tender'] not in BAD_TYPE_TENDER) and (data['status_tender'] in GOOD_STATUS_TENDER)

def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')
    tenders = soup.find('table', class_='resulttable').find_all('tr')
    for tender in tenders:
        tds = tender.find_all('td')
        try:
            code_subject_tender = tds[0].text.strip()
            c_s_list = code_subject_tender.split('\n')
            code_tender = c_s_list[0].strip()
            subject_tender = c_s_list[1].strip()
        except:
            code_tender = ''
            subject_tender = ''
        try:
            customer = tds[1].text.strip()
        except:
            customer = ''
        try:
            type_tenter = tds[2].text.strip()
        except:
            type_tenter = ''
        try:
            link = tds[0].find('a').get('href')
        except:
            link = ''
        try:
            summ_rubl_tenter = tds[3].text.strip()
            sum_list =  summ_rubl_tenter.split('\n')
            summ_tenter = sum_list[0].strip()
        except:
            summ_tenter = ''
        try:
            date_end = tds[5].text.strip()
        except:
            date_end = ''
        try:
            status_tender = tds[6].text.strip()
        except:
            status_tender = ''

        data = {'code_tender': code_tender,
                'subject_tender': subject_tender,
                'customer': customer,
                'type_tender': type_tenter,
                'summ_tender': summ_tenter,
                'date_end': date_end,
                'status_tender': status_tender,
                'link': link}

        if filter_tender(data):
            write_csv(data)

def main():
    url = 'https://rt-ci.ru/modules/filterTable.php'
    query_string = 'внедрение'
    ajax_data = {
        'company': None,
        'pt': 0,
        'nmcs': None,
        'nmce': None,
        'valute': 0,
        'ds': None,
        'de': None,
        'nd': None,
        's_search': query_string
    }

    get_page_data(get_html(url, ajax_data))

if __name__ == '__main__':
    main()