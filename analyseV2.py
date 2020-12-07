import os
import re
import ipaddress
import datetime
import operator

ip_source="/tmp/ip_test"
#ip_ranges="/tmp/1.2"
#ip_source="sample_ip_list_sorted"
ip_ranges="sample_range_list_sorted"
report_file="/data/reports/ip_report_" # suffix is added from time


def main():

    now = datetime.datetime.now()
    start_time = (now.strftime("%Y-%m-%d %H:%M:%S"))

    names = dict()
    counts = dict()
    ip = []
    ip_fail = []

    # Get the ip list into list
    with open(ip_source, "r") as ips:
        lines = ips.read().split('\n')
#        lines = ips.readlines()
        for x in lines:
            if x:
                ip.append(int(x))

    total_ip = len(ip)

    with open(ip_ranges, "r") as ranges:
#        range = ranges.readlines()
        range = ranges.read().split('\n')
        for r in range:
            if ip:
                if r:
                    s = r.split(',')[0] # Range start
                    e = r.split(',')[1] # Range end


                    # For efficiency - continue until first line (of range list) is in range of first ip in list
                    if int(e) < ip[0]:
                        continue

                    # For efficiency - break after line (of range list) is larger then last ip in list
                    if int(s) > ip[-1]:
                        break

                    # Get the number of ip's matching the range by (by count of non matching)
                    count_now = len(ip)
                    count_less = 0
                    count_more = 0
                    ip_tmp = []
                    for x in ip:
                        if x < int(s):
                            count_less += 1
                            # add to fail list
                            ip_fail.append(x)
                        elif x > int(e):
                            count_more += 1
                            # add to temp list so next iteration the ip list is smaller
                            ip_tmp.append(x)
                    ip = ip_tmp

                    b = count_now - (count_less + count_more)
                    if b > 0 :
                        c = r.split(',')[2] # iso code
                        n = r.split(',')[3].strip() # full name

                        # Add count to dict
                        if not c in names:
                            names[c] = n
                            counts[c] = int(0)
                        counts[c] += int(b)

    # Sort the failed list into single elements
    if ip_fail:
        for x in ip_fail:
            ip.append(x)

    # sort the failed list
    failed = []
    if ip:
        # Count the number of each failed ip
        for x in ip:
            if not x in failed:
                c = ip.count(x)
                try:
                    ipv4 = ipaddress.ip_address(int(x))
                except:
                    ipv4 = ("NOT ipv4 " + x)
                failed.append(str(ipv4) + "," + str(c))

    matched = dict( sorted(counts.items(), key=operator.itemgetter(1),reverse=True))

    now = datetime.datetime.now()
    end_time = (now.strftime("%Y-%m-%d %H:%M:%S"))

    # Write log file
    with open(report_file + end_time.replace(' ', '_').replace(':', '.') + '.log', "w") as log:
        log.write('------ IP GEO REPORT ------\n')
        log.write('Start time {}\nFinished at {}\n====\n\n'.format(start_time, end_time))
        log.write('Processed {} IP\'s\n'.format(total_ip))
        log.write('Matched {} IP\'s\n'.format(int(total_ip) - len(ip)))
        log.write('(Failed to match {} IP\'s (listed at the end)\n\n'.format(len(ip)))
        log.write('\nCOUNTRY NAME, TOTAL COUNT\n====\n')
        for x in matched:
            log.write('{}, {}\n'.format(names[x], str(counts[x])))

        if failed:
            log.write('\n\n====\nNo results found for the following IP\'s\n====\n')
            log.write('Total failed {}\n'.format(len(ip)))
            log.write('====\nIP ADDR, COUNT\n')
            for x in failed:
                log.write('{}\n'.format(x))
        else:
            log.write('\nNo errors to report\n')

if __name__ == '__main__':
    main()
