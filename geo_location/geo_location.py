#! /usr/bin/python

import time
import re
import requests

match_ok = re.compile('^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(\d{2}\/\w{3}\/\d{4}):.*\] "GET (.*) .*" 200.*')

source_file_location = "/var/log/nginx/access.log"
destination_file_location = "/var/log/nginx/geo.log"

def watch_log(fn):
    fp = open(fn, 'r')
    while True:
        new_line = fp.readline()
        if new_line:
            parse_line(new_line)
            #write_log(destination_file_location, parse_line(new_line))
            pass
        else:
            time.sleep(10)


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

            print(output_line)
            return output_line

        else:
            print("error")
            return "ERROR on line: {}".format(line)


    return None 
 


def main():
    print("starting...\n")
    watch_log(source_file_location)


if __name__ == '__main__':
    main()




