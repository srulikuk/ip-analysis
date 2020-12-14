import os
import sys
import ipaddress
import time
import datetime
import operator
import urllib.request
from zipfile import ZipFile
import json
import ipsetpy
import _config


def get_time(t = " ", t2 = ":"):
    d_format = ("%Y-%m-%d" + t)
    t_format = "%H" + t2 + "%M" + t2 + "%S"
    time_n = datetime.datetime.now()
    time_n = time_n.strftime(d_format + t_format)
    return time_n

# Get IP ranges
def get_ranges():
    n = 0
    if (_config.download_range):
        csv_file = (_config.csv_file)
        download_dir = ("/tmp/ip2l_" + get_time("_", ".") + "/")
        download_file = "download.zip" # name the zip file when downloading
        download_zip = (download_dir + download_file)

        os.mkdir(download_dir)
        urllib.request.urlretrieve(_config.download_url, download_zip)
        try:
            with ZipFile(download_zip, 'r') as zip_archive:
                zip_archive.extract(csv_file, download_dir)

            n = 1
            range_source = download_dir + csv_file

        except:
            print("Download ZIP file failed")
            del_zip(n, download_zip, download_dir) # null, dir, file

    if n == 0:
        if (_config.alt_range_source):
            range_source = (_config.alt_range_source)
            print("Using alternate CSV file")
        else:
            print("No alternate range file found - QUIT")
            sys.exit(1)

    cidr_range = range_list(range_source)

    # delete downloaded file
    if n == 1:
        if (_config.delete_download):
            del_zip(range_source, download_zip, download_dir)

    return cidr_range

# Get the range file into list
def range_list(rs):
    cidr_range = []
    with open(rs, "r") as range_file:
        lines = range_file.readlines()
        for r in lines:
            try:
                r = r.replace('"', '')
                if '-' in r.split(',')[2]: # range is in list without country code/name
                    continue
                else:
                    cidr_range.append(r) #[
            except:
                continue
    return cidr_range

# Delete download files
def del_zip(r, z, d):
    if r != 0:
        os.remove(r)
    os.remove(z)
    os.rmdir(d)


# process ip list
def get_ip():
    ip_source = (_config.ip_source)
    ip = []
    ip_uniq = 0
    ip_skip_private = 0
    ip_skip_invalid = 0
    with open(ip_source, "r") as ips:
        lines = ips.read().split('\n')
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

    ip = sorted(ip)
    return ip, ip_skip_private, ip_skip_invalid, ip_uniq

# split the ip list into smaller chunks
def ip_split(l):
    m = (_config.max_arr)
    for i in range(0, len(l), m):
        yield l[i : i + m]

# Count matching ip's
def count_matches(i, s, e, c, n): # iplist, ip_fail list, start, end, code, name
    # Get the number of ip's matching the range by (by count of non matching)
    count_now = len(i)
    tmp_ip = []
    tmp_fail = []
    for x in i:
        if x < int(s):
            # add to fail list
            tmp_fail.append(x)
        if x > int(e):
            # return only larger ones for next iteration
            tmp_ip.append(x)
    # count matches
    b = count_now - (len(tmp_ip) + len(tmp_fail)) #(count_less + count_more)
    if b > 0 :
        add_to_dict(c, n, b) # code, name, count

    return tmp_ip, tmp_fail

# Add count to dict
def add_to_dict(c, n, b): # code, name, count
    if not c in NAMES:
        NAMES[c] = n
        COUNTS[c] = int(0)
    COUNTS[c] += int(b)

# proccess the fail_ip list
def proccess_failed(i):
    failed = []
    req = 0 # whoisip requests count
    suc = 0 # whoisip success count
    # Count the number of each failed ip
    ignore = []
    for x in i:
        if not x in ignore: # only process each unique ip once
            ignore.append(x)
            c = i.count(x)
            tmp = ipaddress.IPv4Address(int(x))
            conv_ip = str(tmp)
            req += 1
            try:
                code, name = ip_api_check(conv_ip)
                suc += 1
                add_to_dict(code, name, c)
            except:
            failed.append(str(conv_ip) + "," + str(c))

    return failed, req, suc

# Try to retrieve data for the failed ip's from api
def ip_api_check(i):
    # see if we can get a result from whoisip
    time.sleep(0.5) # keep the api requests slow in a free account
    response = urllib.request.urlopen(_config.ip_api_url + i + _config.ip_api_request)
    data = json.load(response)

    try:
        code = data["country_code"]
        name = data["country"]
        return code, name
    except:
        return 0

# Write log file
def write_log(s, p, i, t, iu, tf, f, q, u, l, m): # Start time, Private ip count, Invalid ip count, Total_ip's, Ip_Uniq, Total ip_Fail, Failed., api reQuests, api sUccess, Line skips (range), Matched list
    report_path = (_config.report_path)
    file_time = get_time("_", ".")
    with open(report_path + file_time + '.log', "w") as log:
        log.write('------ IP GEO REPORT ------\n')
        log.write('Start time {}\nFinished at {}\n====\n\n'.format(s, get_time()))
        log.write('* Processed {} IP\'s\n'.format(t))
        log.write('* Matched {} IP\'s ({} unique IP\'s)\n'.format(t - tf, iu))
        if q > 0:
            log.write('* Made {} requests to whoisip, got {} successful results\n'.format(q, u))
        if i > 0:
            log.write('* {} lines were skipped from ip list as invalid\n'.format(i))
        if p > 0:
            log.write('* {} lines were skipped from ip list as they seem to be -\n'.format(p))
            log.write('  reserved (private) IP\'s (such as starting with 10./127./0.)\n')
        if l > 0:
            log.write('* {} lines were skipped from the range list as invalid\n'.format(l))
        if f:
            log.write('* Failed to match {} IP\'s ({} Unique IP\'s listed at the end)\n'.format(tf, len(f)))
        log.write('\n\nCOUNTRY NAME, TOTAL COUNT\n====\n')
        for x in m:
            log.write('{}, {}\n'.format(NAMES[x], str(COUNTS[x])))

        if f:
            log.write('\n\n====\nNo results found for the following IP\'s\n====\n')
            log.write('Total failed {}\n'.format(len(f)))
            log.write('====\nIP ADDR, COUNT\n')
            for x in f:
                log.write('{}\n'.format(x))
        else:
            log.write('\n====\nNo errors to report\n====\n')


# Global dicts
NAMES = dict()
COUNTS = dict()

def main():
    start_time = get_time()
    cidr = get_ranges()
    ip_l, ip_sp, ip_si, ip_uniq = get_ip()
    ip_fail = []
    line_skip = 0
    line_num = 0

    for ip_part in ip_split(ip_l):
        for r in cidr[line_num:]:
            s = r.split(',')[0] # Range start
            e = r.split(',')[1] # Range end
            c = r.split(',')[2] # iso code
            n = r.split(',')[3].strip() # full name

            # For efficiency - continue until first line (of range list) is in range of first ip in list
            if int(e) < ip_part[0]:
                line_num += 1
                continue

            # if range is larger than largest ip in slice add to fail and break
            if int(s) > ip_part[-1]:
                for x in ip_part:
                    if x:
                        ip_fail.append(x)
                line_num += 1
                break

            # else proccess the ip's in range
            tmp_ip_part, tmp_ip_fail = count_matches(ip_part, s, e, c, n) # iplist, start, end, code, name
            ip_part = tmp_ip_part
            ip_fail = [*ip_fail, *tmp_ip_fail]

            if len(ip_part) == 0:
                break

    # sort the failed list
    failed, req, suc = proccess_failed(ip_fail)

    # sort the COUNTS list
    matched = dict( sorted(COUNTS.items(), key=operator.itemgetter(1),reverse=True))
    # get the count of uniq ip's
    ip_uniq = len(set(ip_l))
    total_fail = len(failed)

    write_log(start_time, ip_sp, ip_si, len(ip_l), ip_uniq, total_fail, failed, req, suc, line_skip, matched)
    # Start time, Private ip count, Invalid ip count, Total_ip's, Ip_Uniq, Total Fail_ip, Failed, api reQuests, api sUccess, Line skips (range), Matched list

if __name__ == '__main__':
    main()
