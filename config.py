# path to ip list
ip_source = "sample_ip_list"

# where to save report, suffix is added from datetime
report_path = "/<path>/ip_report_"

# Download the range file
download_range = True

# alternative path to range file (will be used in case download fails
# or download_range = False, leave empty to ignore)
alt_range_source = "/<path>/IP2LOCATION-LITE-DB1.CSV"

# The following are based on ip2location.com free account (lite) ->
# download url
range_source_url = "https://www.ip2location.com/download/"

# download token
range_source_token = "<token>"

# download file code
range_source_file = "DB1LITE"

# download url built form above data
download_url = (range_source_url + "?token=" + range_source_token + "&file=" + range_source_file)

# name of list in downloaded zip file
csv_file = "IP2LOCATION-LITE-DB1.CSV"
# <- end of ip2location.com _config

# delete downloaded ip_range file when done
delete_download = True

# ip geo check api url / request
ip_api_url = "https://ipwhois.app/json/"
ip_api_request = "?objects=country_code,country"
# this is executed with the ip in between the _url and _request.

# max per ip list (explained below)
max_arr = 3000
# max_arr = explained;
# Test of 1 chunk of 557k ip's took 3660 seconds to process.
# Test results of > 550k ip's split into 3000 seemed the sweetest spot (total time ~24 seconds).
# Results from my tests of large lists (> 500k) showed 3000 is the sweetest spot.
# on lists of ~100k ip's it seems 1000 might be best.
