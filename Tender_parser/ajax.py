from requests import Session
import requests

url = 'https://rt-ci.ru/modules/filterTable.php'
data = {
    'company': None,
    'pt': 0,
    'nmcs': None,
    'nmce': None,
    'valute': 0,
    'ds': None,
    'de': None,
    'nd': None,
    's_search': 'поставка'
}

# def get_html(url, data):
r = requests.post(url, data=data)
    # return r.text


# session = Session()
# session.head('https://rt-ci.ru/modules/filterTable.php')
#
# resp = session.post(
#     url ='https://rt-ci.ru/modules/filterTable.php',
#     # headers={
#     #     'Host': 'etp.rosseti.ru',
#     #     'Connection': 'keep-alive',
#     #     'Content-Length': '150',
#     #     'Origin': 'https://etp.rosseti.ru',
#     #     'X-Requested-With': 'XMLHttpRequest',
#     #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
#     #     'Content-Type': 'application/json',
#     #     'Accept': '*/*',
#     #     'Referer': 'https://etp.rosseti.ru/',
#     #     'Accept-Encoding': 'gzip, deflate, br',
#     #     'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
#     #     'Cookie': '_GUEST_ID=9584475; _ym_uid=1518008571464525230; _LAST_VISIT=07.02.2018+16%3A04%3A13; etpsid2=trdgf835e3mtepmpavvo33t2j3',
#     # },
#     data={
#         # "action": "Procedure",
#         # "method": "list",
#         # "data": [{"start": 0, "limit": 1000, "sort": "id", "dir":"DESC"}],
#         # "type": "rpc",
#         # "tid": 5,
#         # "token": "TtQD8za7RvzheZ09tRrfag"
#         'company': None,
#         'pt': 0,
#         'nmcs': None,
#         'nmce': None,
#         'valute': 0,
#         'ds': None,
#         'de': None,
#         'nd': None,
#         's_search': 'поставка'
#     }
# )

print(r.text)