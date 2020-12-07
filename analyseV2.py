import os
import re
import ipaddress
import time
import datetime
import operator
import urllib.request
import json

now = datetime.datetime.now()
start_time = (now.strftime("%Y-%m-%d %H:%M:%S"))

print("start " + start_time) # testing

#ip_source="/tmp/ip_test"
#ip_ranges="/tmp/1.2"
ip_source="sample_ip_list"
ip_ranges="sample_range_list_sorted"
report_file="/data/reports/ip_report_" # suffix is added from time

def ip_reduce(l, m):
    for i in range(0, len(l), m):
        yield l[i : i + m]

def main():


    names = dict()
    counts = dict()
    ip = []
    ip_fail = []
    ip_skip_private = 0
    ip_skip_invalid = 0
    line_skip = 0
    max = 3000 # max per ip list,
    """ max = explained;
    Results from my tests of large lists (> 500k) showed 3000 is the sweetest spot.
    on lists of ~100k ip's it seems 1000 might be best.
    Time results of > 550k ip's split into 3000 seemed the sweetest spot (total time ~44 seconds).
    (Test of 1 chunk of 557k ip's took 3660 seconds)
    """

    # Get the ip list into list
    with open(ip_source, "r") as ips:
        lines = ips.read().split('\n')
#        lines = ips.readlines()
        for x in lines:
            if x:
                if x.startswith(('127.', '10.', '0.')):
                    ip_skip_private += 1
                    continue
                try:
                    ip.append(int(ipaddress.IPv4Address(str(x.strip()))))
                except:
                    ip_skip_invalid += 1
                    continue

    now = datetime.datetime.now() #testing
    print("end convert ip list " + now.strftime("%H:%M:%S")) # testing

    ip = sorted(ip)
    total_ip = len(ip)

    for ip_part in ip_reduce(ip, max):
        with open(ip_ranges, "r") as ranges:
#            range = ranges.readlines()
            range = ranges.read().split('\n')
            for r in range:
                if ip_part:
                    if r:
                    #     s = r.split(',')[0] # Range start
                    #     e = r.split(',')[1] # Range end
                        try:
                            s = r.split(',')[0] # Range start
                            e = r.split(',')[1] # Range end
                            c = r.split(',')[2] # iso code
                            n = r.split(',')[3].strip() # full name
                        except:
                            line_skip += 1
                            continue
                        # For efficiency - continue until first line (of range list) is in range of first ip in list
                        if int(e) < ip_part[0]:
                            continue

                        # For efficiency - break after line (of range list) is larger then last ip in list
                        if int(s) > ip_part[-1]:
                            for x in ip_part:
                                if x:
                                    ip_fail.append(x)
                            break

                        # Get the number of ip's matching the range by (by count of non matching)
                        count_now = len(ip_part)
                        count_less = 0
                        count_more = 0
                        ip_tmp = []
                        for x in ip_part:
                            if x < int(s):
                                count_less += 1
                                # add to fail list
                                ip_fail.append(x)
                            elif x > int(e):
                                count_more += 1
                                # add to temp list so next iteration the ip list is smaller
                                ip_tmp.append(x)
                        ip_part = ip_tmp

                        b = count_now - (count_less + count_more)
                        if b > 0 :
                            # c = r.split(',')[2] # iso code
                            # n = r.split(',')[3].strip() # full name

                            # Add count to dict
                            if not c in names:
                                names[c] = n
                                counts[c] = int(0)
                            counts[c] += int(b)

    now = datetime.datetime.now() # testing
    print("going to failed " + now.strftime("%H:%M:%S")) # testing

    # sort the failed list
    failed = []
    if ip_fail:
        # Count the number of each failed ip
        req = 0 # whoisip requests count
        suc = 0 # whoisip success count
        ignore = []
        for x in ip_fail:
            if not x in ignore: # only process each unique ip once
                ignore.append(x)
                c = ip.count(x)
                comment = ''
                add_to = 0

                tmp = ipaddress.IPv4Address(int(x))
                conv_ip = str(tmp)

                # see if we can get a result from whoisip
                time.sleep(0.5) # keep the api requests slow in a free account
                req += 1
                response = urllib.request.urlopen("https://ipwhois.app/json/" + conv_ip + "?objects=country_code,country")
                data = json.load(response)

                if data:
                    code = data["country_code"]
                    name = data["country"]

                    if code:
                        suc += 1
                        if not code in names:
                            names[code] = name
                            counts[code] = int(0)
                        counts[code] += int(c)
                        add_to = 1

                if add_to == 0:
                    failed.append(str(conv_ip) + "," + str(c) + comment)

    matched = dict( sorted(counts.items(), key=operator.itemgetter(1),reverse=True))

    now = datetime.datetime.now()
    end_time = (now.strftime("%Y-%m-%d %H:%M:%S"))

    log_error = 0

    # Write log file
    with open(report_file + end_time.replace(' ', '_').replace(':', '.') + '.log', "w") as log:
        log.write('------ IP GEO REPORT ------\n')
        log.write('Start time {}\nFinished at {}\n====\n\n'.format(start_time, end_time))
        log.write('Processed {} IP\'s\n'.format(total_ip))
        log.write('Matched {} IP\'s\n'.format(int(total_ip) - len(failed)))
        if req > 0:
            log.write('Made {} requests to whoisip, got {} successful results\n'.format(str(req), str(suc)))
        if ip_skip_invalid > 0:
            log.write('{} lines were skipped from ip list as invalid\n'.format(str(ip_skip_invalid)))
        if ip_skip_private > 0:
            log.write('{} lines were skipped from ip list as they seem to be reserved (private) IP\'s\n'.format(str(ip_skip_private)))
        if line_skip > 0:
            log.write('{} lines were skipped from the range list as invalid\n'.format(str(ip_skip_invalid)))
        if failed:
            log.write('(Failed to match {} IP\'s (listed at the end)\n'.format(len(failed)))
        log.write('\n\nCOUNTRY NAME, TOTAL COUNT\n====\n')
        for x in matched:
            log.write('{}, {}\n'.format(names[x], str(counts[x])))

        if failed:
            log.write('\n\n====\nNo results found for the following IP\'s\n====\n')
            log.write('Total failed {}\n'.format(len(ip_fail)))
            log.write('====\nIP ADDR, COUNT\n')
            for x in failed:
                log.write('{}\n'.format(x))
        else:
            log.write('\n====\nNo errors to report\n====\n')

    now = datetime.datetime.now() #testing
    print("all done " + now.strftime("%H:%M:%S")) # testing

if __name__ == '__main__':
    main()
