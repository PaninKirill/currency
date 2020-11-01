import hashlib

from django.core.cache import cache
from django.db import ProgrammingError

from rate import model_choices as mch
from rate.models import Rate


def rate_cache_latest(source, currency) -> str:
    return hashlib.md5(
        f'LATEST_RATES_{source}_{currency}'.encode()
    ).hexdigest()


def rate_cache_prior(source, currency) -> str:
    return hashlib.md5(
        f'PRIOR_RATES_{source}_{currency}'.encode()
    ).hexdigest()


def get_latest_rates() -> tuple:
    latest_rates = []
    prior_rates = []
    for source in mch.SOURCE_CHOICES:  # source
        source = source[0]
        for currency in mch.CURRENCY_CHOICES:  # currency
            currency = currency[0]

            key_latest = rate_cache_latest(source, currency)
            cached_latest = cache.get(key_latest)

            key_prior = rate_cache_prior(source, currency)
            cached_prior = cache.get(key_prior)

            # no rate in cache
            if cached_latest is None:
                try:
                    latest, prior = Rate.objects.filter(
                        source=source,
                        currency=currency,
                    ).order_by('-created')[:2]
                except ProgrammingError:
                    # in case no data in db, no migrations has applied
                    latest, prior = None, None
                except ValueError:
                    # in case the source doesn't have a currency that others have
                    continue
                if latest is not None:
                    cache.set(key_latest, latest, 30)
                    latest_rates.append(latest)
                    cache.set(key_prior, prior, 30)
                    prior_rates.append(prior)
            else:  # value in cache
                latest_rates.append(cached_latest)
                prior_rates.append(cached_prior)

    return latest_rates, prior_rates
