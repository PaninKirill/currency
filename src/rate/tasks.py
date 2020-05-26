import bs4

from celery import shared_task

from rate import model_choices as mch
from rate.models import Rate
from rate.utils import to_decimal

import requests


@shared_task
def parse_privatbank():
    url = "https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5"
    response = requests.get(url)
    currency_type_mapper = {
        'USD': mch.CURRENCY_USD,
        'EUR': mch.CURRENCY_EUR,
        'RUR': mch.CURRENCY_RUR,
        'BTC': mch.CURRENCY_BTC,
    }
    for item in response.json():

        if item['ccy'] not in currency_type_mapper:
            continue

        currency = currency_type_mapper[item['ccy']]
        buy = to_decimal(item['buy'])
        sale = to_decimal(item['sale'])

        last = Rate.objects.filter(
            source=mch.SOURCE_PRIVATBANK,
            currency=currency,
        ).last()

        if last is None or last.buy != buy or last.sale != sale:
            Rate.objects.create(
                buy=buy,
                sale=sale,
                source=mch.SOURCE_PRIVATBANK,
                currency=currency,
            )


@shared_task
def parse_monobank():
    url = "https://api.monobank.ua/bank/currency"
    response = requests.get(url)
    currency_type_mapper = {
        # DICT KEY = currency code according to ISO 4217
        840: mch.CURRENCY_USD,
        978: mch.CURRENCY_EUR,
        643: mch.CURRENCY_RUR
    }
    for item in response.json():

        if item['currencyCodeA'] not in currency_type_mapper:
            continue
        if item['currencyCodeB'] != 980:  # 980 = UAH
            continue

        currency = currency_type_mapper[item['currencyCodeA']]
        buy = to_decimal(item['rateBuy'])
        sale = to_decimal(item['rateSell'])

        last = Rate.objects.filter(
            source=mch.SOURCE_MONOBANK,
            currency=currency,
        ).last()

        if last is None or last.buy != buy or last.sale != sale:
            Rate.objects.create(
                buy=buy,
                sale=sale,
                source=mch.SOURCE_MONOBANK,
                currency=currency,
            )


@shared_task
def parse_vkurse():
    url = "http://vkurse.dp.ua/course.json"
    response = requests.get(url)
    currency_type_mapper = {
        'Dollar': mch.CURRENCY_USD,
        'Euro': mch.CURRENCY_EUR,
        'Rub': mch.CURRENCY_RUR,
    }
    for key, value in response.json().items():
        if key not in currency_type_mapper:
            continue

        currency = currency_type_mapper[key]
        buy = to_decimal(value['buy'])
        sale = to_decimal(value['sale'])

        last = Rate.objects.filter(
            source=mch.SOURCE_VKURSE,
            currency=currency,
        ).last()

        if last is None or last.buy != buy or last.sale != sale:
            Rate.objects.create(
                buy=buy,
                sale=sale,
                source=mch.SOURCE_VKURSE,
                currency=currency,
            )


@shared_task
def parse_nbu():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    response = requests.get(url)
    currency_type_mapper = {
        # DICT KEY = currency code according to ISO 4217
        840: mch.CURRENCY_USD,
        978: mch.CURRENCY_EUR,
        643: mch.CURRENCY_RUR,
    }
    for item in response.json():

        if item['r030'] not in currency_type_mapper.keys():
            continue

        currency = currency_type_mapper[item['r030']]
        buy = to_decimal(item['rate'])
        sale = to_decimal('0.0')  # NBU HAS NO SALE RATE
        last = Rate.objects.filter(
            source=mch.SOURCE_NBU,
            currency=currency,
        ).last()

        if last is None or last.buy != buy:
            Rate.objects.create(
                buy=buy,
                sale=sale,
                source=mch.SOURCE_NBU,
                currency=currency,
            )


@shared_task
def parse_alfabank():
    url = 'https://alfabank.ua/'
    response = requests.get(url)
    currency_type_mapper = {
        'USD': mch.CURRENCY_USD,
        'EUR': mch.CURRENCY_EUR,
        'RUB': mch.CURRENCY_RUR,
    }
    soup = bs4.BeautifulSoup(response.text, 'lxml')
    data = soup.find_all('div', {'class': 'currency-block'})

    for item in data:
        if item.find(lambda span: len(span.attrs) == 2):
            currency = item.find('div', {'class': 'title'}).text.strip()
            if currency not in currency_type_mapper:
                continue

            buy = to_decimal(item.find('span', {'data-currency': f'{currency}_BUY'}).text.strip())
            sale = to_decimal(item.find('span', {'data-currency': f'{currency}_SALE'}).text.strip())

            last = Rate.objects.filter(
                source=mch.SOURCE_ALFABANK,
                currency=currency_type_mapper[currency],
            ).last()

            if last is None or last.buy != buy or last.sale != sale:
                Rate.objects.create(
                    buy=buy,
                    sale=sale,
                    source=mch.SOURCE_ALFABANK,
                    currency=currency_type_mapper[currency],
                )


@shared_task
def parse_pumb():
    url = 'https://www.pumb.ua/'
    response = requests.get(url)
    currency_type_mapper = {
        'USD': mch.CURRENCY_USD,
        'EUR': mch.CURRENCY_EUR,
        'RUB': mch.CURRENCY_RUR,
    }

    soup = bs4.BeautifulSoup(response.text, 'lxml')
    data = soup.find('div', {'class': 'exchange-rate'})
    chunk_data = data.find('table').find_all('tr')

    for item in chunk_data:
        if item.find_all('td'):
            currency = item.find_all('td')[0].text.strip()
            if currency not in currency_type_mapper:
                continue

            currency = currency_type_mapper[currency]
            buy = to_decimal(item.find_all('td')[1].text.strip())
            sale = to_decimal(item.find_all('td')[2].text.strip())

            last = Rate.objects.filter(
                source=mch.SOURCE_PUMB,
                currency=currency,
            ).last()

            if last is None or last.buy != buy or last.sale != sale:
                Rate.objects.create(
                    buy=buy,
                    sale=sale,
                    source=mch.SOURCE_PUMB,
                    currency=currency,
                )


@shared_task
def parse():
    parse_monobank.delay()
    parse_privatbank.delay()
    parse_vkurse.delay()
    parse_nbu.delay()
    parse_alfabank.delay()
    parse_pumb.delay()
