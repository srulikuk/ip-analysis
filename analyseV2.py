import os
import re
import ipaddress
import datetime
import operator

#ip_source="/tmp/1.1"
#ip_ranges="/tmp/1.2"
ip_source="sample_ip_list_sorted"
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
        for x in lines:
            if x:
                ip.append(int(x))

    total_ip = len(ip)

    first_m = 0
    with open(ip_ranges, "r") as ranges:
#        range = ranges.readlines()
        range = ranges.read().split('\n')
        for r in range:
            if r:
                s = r.split(',')[0] # Range start
                e = r.split(',')[1] # Range end

                # For efficiency - continue until first line (of range list) is in range of first ip in list
                if first_m == 0:
                    if int(e) < int(ip[0]):
                        continue
                    else:
                        first_m = 1

                # For efficiency - break after line (of range list) is larger then last ip in list
                if int(s) > int(ip[-1]):
                    break

                # Get the number of ip's matching the range
                b = sum(int(s) < x < int(e) for x in ip) # is there a more efficient way?
                if b > 0 :

                    c = r.split(',')[2] # iso code
                    n = r.split(',')[3].strip() # full name

                    # Add count to dict
                    if not c in names:
                        names[c] = n
                        counts[c] = int(0)
                    counts[c] += int(b)
                    # remove these matched ip's from list (so at the end we have a list of non-matched ip's)
                    ip_fail.append([x for x in ip if x <= int(s)]) # is there a more efficient way?

                    # remove e ip's from main list to make it smaller
                    ip[:] = [x for x in ip if x >= int(e)] # is there a more efficient way?

    # Sort the failed list into single elements
    if ip_fail:
        for x in ip_fail:
            if len(x) > 1:
                for s in x:
                    ip.append(s)
            else:
                ip.append(x)

    # sort the failed list
    if ip:
        # Count the number of each failed ip
        failed_tmp = []
        for x in ip:
            c = ip.count(x)
            failed_tmp.append(str(x) + ", " + str(c))

        failed_tmp[:] = sorted(set(failed_tmp))

        # convert the ip numbers back to ip's for report of failed matches
        # failed = []
        # for x in failed_tmp:
        #     ipv4 = str(ipaddress.ip_address(x.split(',')[0]))
        #     c = str(x.split(',')[1])
        #     failed.append(str(x) + ", " + str(c))

        failed = failed_tmp

        # Sort the count highest first
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
