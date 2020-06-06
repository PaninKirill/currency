import hashlib

from django.core.cache import cache

from rate import model_choices as mch
from rate.models import Rate


def rate_cache_key(source, currency) -> str:
    return hashlib.md5(
        f'LATEST_RATES_{source}_{currency}'.encode()
    ).hexdigest()


def get_latest_rates() -> list:
    object_list = []
    for source in mch.SOURCE_CHOICES:  # source
        source = source[0]
        for currency in mch.CURRENCY_CHOICES:  # currency
            currency = currency[0]

            key = rate_cache_key(source, currency)
            cached_rate = cache.get(key)

            # no rate in cache
            if cached_rate is None:
                rate = Rate.objects.filter(
                    source=source,
                    currency=currency,
                ).order_by('created').last()
                if rate is not None:
                    cache.set(key, rate, 30)
                    object_list.append(rate)
            else:  # value in cache
                object_list.append(cached_rate)

    return object_list
