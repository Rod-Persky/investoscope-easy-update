# Investoscope Easy Update
# Copyright (C) 2017 Rodney Persky
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import time
import csv
import requests
import investoscope

requests.packages.urllib3.disable_warnings()

OPT_WRITE_CSV = True

TIME_OFFSET_DAYS = lambda days: days*60*60*24


YAHOO_HISTORY_PAGE = "https://finance.yahoo.com/quote/{item}/history"
YAHOO_CSV_URL = "https://query1.finance.yahoo.com/v7/finance/download/{item}"
YAHOO_CSV_PARAMS = {"period1": int(time.time())-(TIME_OFFSET_DAYS(3*365)),
                    "period2": int(time.time()),
                    "interval": "1d",
                    "events": "history",
                    "crumb": "{yahoo_crumb}"}
YAHOO_HEADERS = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/64.0.3282.112 Mobile/15D60 Safari/604.1",
                 "Accept-Language": "en-au",
                 "Referer": "https://finance.yahoo.com",
                 "Origin":  "https://finance.yahoo.com"}
YAHOO_CRUMB_REGEX = r"CrumbStore\":{\"crumb\":\"([^\"]*)"


def get_yahoo_data_crumb(s, item):
  url = YAHOO_HISTORY_PAGE.replace("{item}", item['code'])
  response = s.get(url, verify=False)

  # Get yahoo html
  yahoo_crumb_regex = re.search(YAHOO_CRUMB_REGEX, response.text)
  yahoo_crumb = yahoo_crumb_regex.group(1)
  yahoo_crumb = yahoo_crumb.replace('\\u002F', '/')
  return yahoo_crumb


def get_yahoo_csv_data(s, yahoo_crumb, item):
  url = YAHOO_CSV_URL.replace("{item}", item['code'])
  params = dict.copy(YAHOO_CSV_PARAMS)
  params['crumb'] = yahoo_crumb

  response = s.get(url, params=params, verify=False)
  csv_data = response.content

  if len(csv_data) < 1000:
    if b'Unauthorized' in csv_data:
      return None

  return csv_data


def tidy_yahoo_csv(csv_data):
  """ Generate investoscope / applescript csv string """
  csv_text = []
  csv_data = csv.reader(csv_data.split('\n'))
  for row in csv_data:
    # Ignore row with null values or is empty
    if "null" in row or not row:
      continue

    # Remove Adj Close
    row.pop(5)
    csv_text.append(",".join(row))
  csv_text = "\n".join(csv_text)
  return csv_text


def gen_historical_data_csv(item):
  """Get quote download crumb from yahoo"""
  with requests.Session() as s:
    s.headers.update(YAHOO_HEADERS)
    yahoo_crumb = get_yahoo_data_crumb(s, item)
    csv_data = get_yahoo_csv_data(s, yahoo_crumb, item)

  if OPT_WRITE_CSV:
    csv_path = investoscope.generate_csv_file_name(item)
    with open(str(csv_path), 'wb') as csv_file:
      csv_file.write(csv_data)

  return tidy_yahoo_csv(csv_data.decode('utf-8'))


if __name__ == '__main__':
  OPT_WRITE_CSV = False
  gen_historical_data_csv({'code': 'CSV.AX'})
