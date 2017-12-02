#! /usr/bin/python

"""
Added this to cronjob

sudo crontab -e to modify/check
It will run every hour
"""

import re
import requests

match_ok = re.compile('^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*) -.*\] "GET (.*) .*" 200.*')

source_file_location = "/var/log/nginx/access.log"
destination_file_location = "/var/log/nginx/geo.log"

def watch_log(fn):
    fp = open(fn, 'r')
    new_line = fp.readline()
    while new_line:
        log_line = parse_line(new_line)
        if log_line:
            write_log(destination_file_location, log_line)
        new_line = fp.readline()

    write_log(destination_file_location, '---------houly cron job over----------')

def write_log(fn, line):
    with open(fn, 'a') as log:
        log.write(line)

def parse_line(line):
    result = match_ok.match(line)

    if result:
        if len(result.groups()) == 3:
            resp = requests.get('https://ipinfo.io/{}'.format(result.group(1))).json()
            output_line = "{} - Request: {} - ip: {}\n {}, {}, {} - Org: {}\n".format(
                result.group(2), result.group(3), result.group(1), resp['country'], resp['region'], resp['city'], resp['org'])
            return output_line
        else:
            return "ERROR on line: {}".format(line)
    return None 

def main():
    watch_log(source_file_location)

if __name__ == '__main__':
    main()




