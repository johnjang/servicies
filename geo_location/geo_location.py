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
    print("last_time: {}".format(last_time))
    new_line = fp.readline()
    while new_line:
        log_line = parse_line(new_line, last_time)
        if log_line:
            write_log(destination_file_location, log_line)
        new_line = fp.readline()

    write_log(destination_file_location, '---------hourly cron job over----------')

def write_log(fn, line, fn_time, time):
    with open(fn, 'a') as log:
        log.write(line)
    with open(fn_time, 'w') as time_log:
        log.write(time)

def parse_line(line, last_time):
    result = match_ok.match(line)

    if result:
        if len(result.groups()) == 3:
            if check_time(datetime.datetime.strptime(result.group(2), time_fmt), last_time):
                print("pass")
            else:
                print("no pass")
            resp = requests.get('https://ipinfo.io/{}'.format(result.group(1))).json()
            output_line = "{} - Request: {} - ip: {}\n {}, {}, {} - Org: {}\n".format(
                result.group(2), result.group(3), result.group(1), resp['country'], resp['region'], resp['city'], resp['org'])
            return output_line
        else:
            return "ERROR on line: {}".format(line)
    return None 

def check_time(curr_time, last_time):
    return True if curr_time > last_time else False

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




