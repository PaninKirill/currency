import re
import collections

PATH = './regex/apache.log'

regex = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*\[(?P<date>.*)\]')
RESULT = []

with open(PATH) as file:
    for index, line in enumerate(file):
        res = regex.search(line).groupdict()
        ip = res['ip']
        date = res['date']

        RESULT.append(ip)

print(collections.Counter(RESULT).most_common(10))
