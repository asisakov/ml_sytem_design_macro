import csv

import argparse
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument("filename")
args = parser.parse_args()

re_date = '(\d{4})M(\d+)'

def periodToDate(p):
    y, m = re.search(re_date, p).groups()
    return f"{y}-{m:0>2}-01"

commodities = []
with open(args.filename, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile)
    first = next(reader)

    for row in reader:
        commodity = {}
        for idx in range(0,4):
            field_name = first[idx].strip()
            commodity[field_name] = row[idx].strip()

        commodity['values'] = []
        for idx in (
          idx for
          idx in range(0, len(first)) if re.match(re_date, first[idx])):
            month_fmt = periodToDate(first[idx])
            value = row[idx]
            if not value == '':
                commodity['values'].append([month_fmt, value])

        commodities.append(commodity)

print(json.dumps(commodities))
