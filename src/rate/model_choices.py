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

# Charts.js
BACKGROUND_COLOR_MAPPER = {
        1: 'rgba(102, 153, 0, 0.1)',
        2: 'rgba(0, 162, 235, 0.1)',
        3: 'rgba(0, 206, 86, 0.1)',
        4: 'rgba(0, 192, 192, 0.1)',
        5: 'rgba(0, 102, 255, 0.1)',
        6: 'rgba(0, 159, 64, 0.1)',
        7: 'rgba(165, 255, 64, 0.1)',
    }
