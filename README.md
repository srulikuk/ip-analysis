# ip-analysis by country
### Analyse IP list and report count by country.

Expected format of the ip list is 1 ip per line, (duplicates are to be on separate lines).  
Expected format of the range list is like ip2location.com CSV file, (ip numbers).  
`"16777216","16777471","US","United States of America"`  

For IP's that the country is not identified in the range list it checks it online at ipwhois.app with a sleep of 0.5 seconds between each request not to abuse free account (be aware of free account limits).  

_Although the sample IP list in this repo is mostly a list of bad actor IP's it should NOT be be used as a blacklist as many listed are there through testing and randomly added IP's._  

Usage: Copy the config.py to _config.py and update the config as required, call the script without any arguments (python3 analyseV2.py)
