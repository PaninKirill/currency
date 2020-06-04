from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand

from rate import model_choices as mch
from rate.models import Rate
from rate.utils import to_decimal
import time
import requests


class Command(BaseCommand):
    help = 'Parse PrivatBank rates archives'  # noqa  help is python builtins but django command requires it.

    def handle(self, *args, **options):

        def date_generator():
            start_date = date(2019, 1, 1)
            end_date = date(2020, 5, 24)
            while start_date <= end_date:
                yield start_date.strftime("%d.%m.%Y")
                start_date += timedelta(days=1)

        for archive_date in date_generator():
            time.sleep(10)
            url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={archive_date}'
            response = requests.get(url)
            currency_type_mapper = {
                'USD': mch.CURRENCY_USD,
                'EUR': mch.CURRENCY_EUR,
                'RUB': mch.CURRENCY_RUR,
                'BTC': mch.CURRENCY_BTC,
            }

            for item in response.json()['exchangeRate']:
                if 'currency' in item:
                    if item['currency'] not in currency_type_mapper:
                        continue
                    currency = currency_type_mapper[item['currency']]
                    buy = to_decimal(item['purchaseRate'])
                    sale = to_decimal(item['saleRate'])

                    format_date = datetime.strptime(archive_date, '%d.%m.%Y').strftime('%Y-%m-%d %H:%M:%S.%f')
                    lookup_date = datetime.strptime(format_date, '%Y-%m-%d %H:%M:%S.%f')  # datetime object

                    latest_rate = Rate.objects.filter(
                        source=mch.SOURCE_PRIVATBANK,
                        currency=currency,
                        created=lookup_date,
                    ).last()
                    """
                    following compare condition helps to exclude duplicates and fill the voids in data
                    """
                    if latest_rate is None or latest_rate.buy != buy or latest_rate.sale != sale:
                        rate = Rate.objects.create(
                            created=lookup_date,
                            buy=buy,
                            sale=sale,
                            source=mch.SOURCE_PRIVATBANK,
                            currency=currency,
                        )
                        rate.created = format_date
                        rate.save(update_fields=['created'])  # avoids 'auto_now_add' restriction to pass own date
