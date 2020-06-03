# Generated by Django 2.2.12 on 2020-05-25 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('buy', models.DecimalField(decimal_places=2, max_digits=7)),
                ('sale', models.DecimalField(decimal_places=2, max_digits=7)),
                ('source', models.PositiveSmallIntegerField(choices=[(1, 'PrivatBank'), (2, 'MonoBank'), (3, 'PUMB'), (4, 'NBU'), (5, 'AlfaBank'), (6, 'Vkurse'), (7, 'Pivdenniy')])),
                ('currency', models.PositiveSmallIntegerField(choices=[(1, 'USD'), (2, 'EUR'), (3, 'RUR'), (4, 'BTC')])),
            ],
        ),
    ]
