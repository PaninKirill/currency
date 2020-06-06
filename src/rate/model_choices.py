SOURCE_PRIVATBANK = 1
SOURCE_MONOBANK = 2
SOURCE_PUMB = 3
SOURCE_NBU = 4
SOURCE_ALFABANK = 5
SOURCE_VKURSE = 6
SOURCE_PIVDENNIY = 7

SOURCE_CHOICES = (
    (SOURCE_PRIVATBANK, 'PrivatBank'),
    (SOURCE_MONOBANK, 'MonoBank'),
    (SOURCE_PUMB, 'PUMB'),
    (SOURCE_NBU, 'NBU'),
    (SOURCE_ALFABANK, 'AlfaBank'),
    (SOURCE_VKURSE, 'Vkurse'),
    (SOURCE_PIVDENNIY, 'Pivdenniy'),
)

CURRENCY_USD = 1
CURRENCY_EUR = 2
CURRENCY_RUR = 3
CURRENCY_BTC = 4
CURRENCY_CHOICES = (
    (CURRENCY_USD, 'USD'),
    (CURRENCY_EUR, 'EUR'),
    (CURRENCY_RUR, 'RUR'),
    (CURRENCY_BTC, 'BTC'),
)
