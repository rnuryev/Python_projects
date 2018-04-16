def get_tenders(self):

    data_for_post = {
        'p_page': 0,
        'p_page_size': 25,
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
        'name_text': self.query_string,
        'p_dateend_begin': self.bid_deadlin_from,
        'p_dateend_begin_old': self.bid_deadlin_from,
        'p_dateend_end': None,
        'p_dateend_end_old': None,
        'p_contest_date_oa_begin_old': None,
        'p_contest_date_oa_end_old': None,
    }

    html = requests.post(self.url, data=data_for_post).text
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find('table', class_='tableProc').find_all('tr')
    all_links = []
    for lk in links:
        if lk.has_attr('onclick'):
            link = 'http://etzp.rzd.ru' + lk['onclick'][10:len(lk['onclick']) - 3]
            all_links.append(link)


    for link in all_links:
        html = requests.get(link).text
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
        data_tender = {
            'code': code,
            'subject': subject,
            'customer': customer,
            'price': price,
            'deadline': deadline,
            'link': link,
            'document_links': document_links
        }

        new_tender = Tenders(code=data_tender['code'],
                             subject=data_tender['subject'],
                             customer=data_tender['customer'],
                             price=data_tender['price'],
                             deadline=data_tender['deadline'],
                             link=data_tender['link'])

        new_tender.rzd_tenders_request = RzdTenders.objects.get(pk=self.pk)

        for doc_l in data_tender['document_links']:
            new_tender_documents = TenderDocuments(doc_title=doc_l['doc_name'], doc_link=doc_l['doc_link'])
            new_tender_documents.tender = new_tender
