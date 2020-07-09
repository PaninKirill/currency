from bs4 import BeautifulSoup

from fake_useragent import UserAgent

import requests

from utils import create_db, save_into_db, save_into_json

BASE_URL = 'https://www.work.ua'
PARSE_URL = 'https://www.work.ua/ru/jobs/'

ua = UserAgent()


def main():
    db_fields = (
        'vacancy_id',
        'vacancy_link',
        'vacancy_name',
        'company',
        'address',
        'description',
        'salary',
    )
    create_db(db_fields)
    page = 0

    while True:
        page += 1
        print(f'start to parse page: {page}')  # NOQA helps to follow and observe parsing process

        headers = {'User-Agent': ua.random}

        response = requests.get(PARSE_URL, params={'page': page}, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        res = soup.find('div', {'id': 'pjax-job-list'})

        if res is None:
            break

        res = res.find_all('h2')
        for elem in res:
            href = elem.find('a').attrs['href']
            vacancy_name = elem.find('a').text.strip()

            # vacancy description (gain extra params from vacancy)
            details = requests.get(BASE_URL + href, headers=headers)
            vacancy_text = details.text.strip()
            vacancy_link = BASE_URL + href
            vacancy_id = ''.join(i for i in href if i.isdigit())
            vacancy_card = BeautifulSoup(vacancy_text, 'lxml')
            company = vacancy_card.find('span', {'class': 'glyphicon-company'}).findNext('a').find('b').text.strip()
            address = vacancy_card.find('span', {'class': 'glyphicon-map-marker'}).findParent('p').contents[2].strip()
            address = address.replace('\n', '').replace('\\', '').replace("/", '')
            description = vacancy_card.find('div', {'id': 'job-description'}).text.strip()
            description = description.replace('\n', '').replace('\\', '').replace("/", '')
            try:
                salary = vacancy_card.find(
                    'span', {'class': 'glyphicon-hryvnia'}
                ).findNext(
                    'b', {'class': 'text-black'}
                ).text.strip()
                salary = salary.replace('\u202f', '')
                salary = salary.replace('\u2009', '')
            except AttributeError:
                salary = 'NULL'
            # end vacancy description

            save_into_db(
                vacancy_id,
                vacancy_link,
                vacancy_name,
                company,
                address,
                description,
                salary,
            )
    save_into_json()


if __name__ == "__main__":
    main()
