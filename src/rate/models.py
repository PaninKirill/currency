import datetime

from django.db import models
from django.utils import timezone

from rate import model_choices as mch
from rate.utils import to_decimal


class Rate(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    buy = models.DecimalField(max_digits=6, decimal_places=2)
    sale = models.DecimalField(max_digits=6, decimal_places=2)
    source = models.PositiveSmallIntegerField(choices=mch.SOURCE_CHOICES)  # get_{field}_display()
    currency = models.PositiveSmallIntegerField(choices=mch.CURRENCY_CHOICES)

    def save(self, *args, **kwargs):
        self.buy = to_decimal(self.buy)
        self.sale = to_decimal(self.sale)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.id},\t ' \
               f'{self.created}, ' \
               f'{self.get_source_display()}, ' \
               f'CCY: {self.get_currency_display()}, ' \
               f'buy: {self.buy}, ' \
               f'sell: {self.sale}'

    def was_changed_recently(self):
        """
        USAGE:
        obj = Rate.objects.all().last()
        obj.was_changed_recently()
        :return:
        True
        If obj was changed recently <= 15 min (considering current time)
        """
        return self.created >= (timezone.now() - datetime.timedelta(minutes=15))
