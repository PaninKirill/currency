import re
import collections

import csv

PATH = './regex/nginx.log'

regex = re.compile(
    r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*\[(?P<date>.*)\.*].+\s\"(?P<method>|[A-Z]{3,9})\s(?P<path>.*?)'
    r'\s.*\"\s(?P<status_code>\d{3})\s(?P<body_bytes_sent>\d+)\s\"(?P<http_referer>.*?)\"\s\"(?P<ua>.*?)\"\s\"'
    r'(?P<host>.*?)\"\s(?P<exec_time>.*)'
)

FIELDS = (
    'ip',
    'date',
    'method',
    'path',
    'status_code',
    'body_bytes_sent',
    'http_referer',
    'ua',
    'host',
    'exec_time',
)

RESULT = []

with open(PATH) as file:
    with open('nginx_logs.csv', 'w') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for index, line in enumerate(file):
            res = regex.search(line)
            if res is not None:
                data = res.groupdict()
                w.writerow(data)
                RESULT.append((data['ip'], data['path']))

print(collections.Counter(RESULT).most_common(10))

"""
TOP 10 LOGS
(('104.168.52.10', '/'), 765), 
(('46.98.217.23', '/api/v1/rooms/housekeeping-list/'), 340), 
(('46.98.184.254', '/api/v1/rooms/housekeeping-list/?'), 164), 
(('46.98.184.254', '/api/v1/rooms/types/'), 163), 
(('46.98.184.254', '/api/v1/accounts/housekeepers/'), 160), 
(('91.243.213.4', '/api/v1/accounts/housekeepers/'), 118), 
(('89.40.73.212', '/'), 90), 
(('2.44.199.253', '/'), 83), 
(('46.98.217.23', '/api/v1/rooms/types/'), 51), 
(('188.163.44.29', '/api/v1/rooms/types/'), 48)
"""

regex = re.compile(
    r'(?P<datetime>[\d+/ :]+).*\[(?P<error_level>.+)\].*\d+\#(?P<process_id>\w*)\:\s.*'
    r'(?P<connection_id>(?<=\:\s\*)\d+)\s(?P<message>.*)\,\sclient:\s(?P<client>.*?)\,.*\:\s'
    r'(?P<server>.*?)\,.*\"(?P<method>[A-Z]{3,9})\s(?P<path>.*?)\s.*\d\"\,(?:.+upstream:\s\"'
    r'(?P<upstream>.+?)\"\,)?(?:.+host:\s\"(?P<host>.+?)\")?(?:.+referrer:\s\"(?P<referrer>.+?)\")?'
)

RESULT_ERROR = []

FIELDS_ERROR = (
    'datetime',
    'error_level',
    'process_id',
    'connection_id',
    'message',
    'client',
    'server',
    'method',
    'path',
    'upstream',
    'host',
    'referrer'
)

with open(PATH) as file:
    with open('nginx_logs_errors.csv', 'w') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS_ERROR)
        w.writeheader()
        for index, line in enumerate(file):
            res = regex.search(line)
            if res is not None:
                data = res.groupdict()
                w.writerow(data)
                RESULT_ERROR.append(data['message'])

print(collections.Counter(RESULT_ERROR).most_common(10))

"""
TOP 10 ERRORS
('user "admin": password mismatch', 344), 
('user "root" was not found in "/etc/nginx/.htpasswd"', 70), 
('user "user" was not found in "/etc/nginx/.htpasswd"', 61), 
('connect() failed (111: Connection refused) while connecting to upstream', 26), 
('open() "/etc/nginx/templates/503/1/503.html/503.html" failed (2: No such file or directory)', 26), 
('user "ktuser" was not found in "/etc/nginx/.htpasswd"', 24), 
('user "support" was not found in "/etc/nginx/.htpasswd"', 20), 
('user "(none)" was not found in "/etc/nginx/.htpasswd"', 20), 
('user "super" was not found in "/etc/nginx/.htpasswd"', 17), 
('user "(blank)" was not found in "/etc/nginx/.htpasswd"', 14)
"""
