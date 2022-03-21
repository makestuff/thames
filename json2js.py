#!/usr/bin/env python3

# The index.html has a couple of large inline 2D arrays for time offset in minutes, and depth. These
# are generated from the tide-tables using this script. Call it with any year 2017..2022, and it
# will produce valid Javascript array-initializers. For example:
#
#   $ grep -E "const (times|depths)" index.html > x
#   $ ./json2js.py 2022 > y
#   $ diff x y
#   $
#
# Clearly, they are the same
#
import urllib.request
import json
import datetime
import sys

# Parse the timestamps in the JSON file
def from_str(s):
  return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%MZ").replace(tzinfo=datetime.timezone.utc)

# Read tide times from JSON file for London Bridge (see https://github.com/makestuff/tides-ocr)
def get_tides(year):
  with open(f"{year}.json", "r") as f:
    all = json.load(f)
  year = all["year"]
  locations = []
  tides = []
  for data in all["data"]:
    locations.append(data["location"])
    tides.append([(from_str(i["ts"]), i["dst"], i["id"], i["h"]) for i in data["tides"]])
  return year, locations, tides

# Get the last item from a list
def last_of(lst):
  return lst[len(lst) - 1]

# Main entry point
if len(sys.argv) != 2:
  print(f"Synopsis: {sys.argv[0]} <year>")
  sys.exit(1)

year = int(sys.argv[1])
zerotime = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)

# First get the data for last year - we need the last tides
_, _, tides = get_tides(year - 1)
times = [[int((last_of(loc)[0] - zerotime).total_seconds()/60)] for loc in tides]
depths = [[last_of(loc)[3]] for loc in tides]

# Now extend with the data from this year
_, _, tides = get_tides(year)
num_results = min([len(r) for r in tides])
for j in range(len(tides)):
  times[j].extend([int((tides[j][i][0]-zerotime).total_seconds()/60) for i in range(num_results)])
  depths[j].extend([tides[j][i][3] for i in range(num_results)])

# And finally, print it
print(f"            const times = {times};");
print(f"            const depths = {depths};");
