#! /usr/bin/python

"""
Added this to cronjob

sudo crontab -e to modify/check
It will run every hour
"""

import re
import requests
import datetime

match_ok = re.compile('^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*) -.*\] "GET (.*) .*" 200.*')

source_file_location = "/var/log/nginx/access.log"
destination_file_location = "/var/log/nginx/geo.log"
timestamp_file_location = "/var/log/nginx/geo.timestamp"
time_fmt = '%d/%b/%Y:%H:%M:%S'
default_time = "01/Jan/1999:00:00:00"

def watch_log(fn):
    fp = open(fn, 'r')
    last_time = get_time_stamp(timestamp_file_location)
    new_line = fp.readline()
    while new_line:
        log_line, log_time = parse_line(new_line, last_time)
        if log_line:
            write_log(destination_file_location, log_line, timestamp_file_location, log_time)
        new_line = fp.readline()

    write_log(destination_file_location, '---------hourly cron job over----------\n')


"""
    Write to geo.log and update geo.timestamp if necessary
"""
def write_log(fn, line, fn_time = None, time = None):
    with open(fn, 'a') as log:
        log.write(line)

    if time and fn_time:
        with open(fn_time, 'w') as time_log:
            time_log.write(time)

"""
    Parse a given line from access.log. It will parse out date, request, ip address.
    Get geolocation of the source ipaddress from ipinfo.io.
    Only returns a formatted string along with time if log is later than last get.timestamp
"""
def parse_line(line, last_time):
    result = match_ok.match(line)

    if result:
        if len(result.groups()) == 3:
            if check_time(datetime.datetime.strptime(result.group(2), time_fmt), last_time):
                resp = requests.get('https://ipinfo.io/{}'.format(result.group(1))).json()
                if not 'country' in resp or not 'org' in resp:
                    return None, None
                output_line = "{} - Request: {} - ip: {}\n {}, {}, {} - Org: {}\n\n".format(
                    result.group(2), result.group(3), result.group(1), 
                    convert_to_utf8(resp['country']), convert_to_utf8(resp['region']), convert_to_utf8(resp['city']), convert_to_utf8(resp['org']))
                return output_line, result.group(2)
            else:
                return None, None
        else:
            return "ERROR on line: {}".format(line), None
    return None, None

"""
    Compares two datetime ojbect
"""
def check_time(curr_time, last_time):
    return True if curr_time > last_time else False


def convert_to_utf8(word):
    return u''.join(word).encode('utf-8').strip()


"""
    Read from geo.timestamp and get latest time of the log data.
    Returns a datetime object containing the timestamp date
"""
def get_time_stamp(fn):
    with open(fn, 'a+') as timestamp:
        last_time = timestamp.readline()
        if last_time:
            return datetime.datetime.strptime(last_time, time_fmt)
        else:
            timestamp.write(default_time)
            return datetime.datetime.strptime(default_time, time_fmt)

def main():
    watch_log(source_file_location)


if __name__ == '__main__':
    main()




