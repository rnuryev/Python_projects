import requests
import csv


def write_csv(data):
    with open('gazprom.csv', 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow((data['code_tender'],
                         data['subject_tender'],
                         data['customer'],
                         data['type_tender'],
                         data['date_end'],
                         data['prolonged_date_end'],
                         data['link']))

def get_data_from_json(url):
    resp = requests.get(url)
    tenders = resp.json()['tenders']
    for tend in tenders:
        data = {
            'customer': tend['company_customer']['name_full'],
            'date_end': tend['date_end'],
            'code_tender': tend['purchase_number'],
            'type_tender': tend['purchase_type']['header'],
            'link': 'https://etpgaz.gazprombank.ru/#com/procedure/view/procedure/' + str(tend['gpb_id'])
        }
        try:
            data['prolonged_date_end'] = tend['prolonged_date_end']
        except:
            data['prolonged_date_end'] = ''
        try:
            sls = tend['purchase_name'].split('\n')
            subject_tender = ' '.join(list(map(str.strip, sls)))
            subject_tender.replace(u'\xa0', ' ')
            subject_tender.replace('; ', '. ')
            data['subject_tender'] = subject_tender
        except:
            data['subject_tender'] = ''
        write_csv(data)

def main():
    query_string = 'разработка'
    url = 'http://www.gazprom.ru/json/site/tender.html?sEcho=6&iColumns=4&sColumns=&iDisplayStart=0&iDisplayLength=50&mDataProp_0=purchase_type&mDataProp_1=purchase_number&mDataProp_2=company_customer&mDataProp_3=company_org&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&status=active&lang=ru&limit=50&page=1&search=' + query_string + '&sort_field=date&_=1519209042167'

    get_data_from_json(url)

if __name__ == '__main__':
    main()