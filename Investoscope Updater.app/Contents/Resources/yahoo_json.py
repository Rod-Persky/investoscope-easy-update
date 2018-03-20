
import re
import time
import csv
import requests
import investoscope
from datetime import datetime

requests.packages.urllib3.disable_warnings()

OPT_WRITE_CSV = True
TIME_OFFSET_DAYS = lambda days: days*60*60*24

YAHOO_API_START    = "https://finance.yahoo.com/quote/{item}/chart"
YAHOO_API_ENDPOINT = "https://query1.finance.yahoo.com/v8/finance/chart/{item}"

YAHOO_HEADERS  = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_5 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) CriOS/64.0.3282.112 Mobile/15D60 Safari/604.1",
                  "Accept-Language": "en-au",
                  "Referer": "https://finance.yahoo.com",
                  "Origin":  "https://finance.yahoo.com"}

YAHOO_PARAMS = {"symbol": "{item}",
                    "period1": int(time.time())-(TIME_OFFSET_DAYS(3*365)),
                    "period2": int(time.time()),
                    "interval": "1d",
                    "includePrePost": "true",
                    "events": "div%7Csplit%7Cearn",
                    "lang": "en-US",
                    "region": "US",
                    "corsDomain": "finance.yahoo.com",
                    "crumb": "{yahoo_crumb}"}

YAPI_CRUMB_REGEX = r"CrumbStore\":{\"crumb\":\"([^\"]*)"


def get_yahoo_data_crumb(s, item):
  url = YAHOO_API_START.replace("{item}", item['code'])
  response = s.get(url, verify=False)

  yahoo_crumb_regex = re.search(YAPI_CRUMB_REGEX, response.text)
  yahoo_crumb = yahoo_crumb_regex.group(1)
  yahoo_crumb = yahoo_crumb.replace('\\u002F', '/')
  
  return yahoo_crumb


def get_yahoo_json_data(s, yahoo_crumb, item):
  url    = YAHOO_API_ENDPOINT.replace("{item}", item['code'])
  params = dict.copy(YAHOO_PARAMS)
  params['symbol'] = item['code']
  params['crumb']  = yahoo_crumb

  response = s.get(url, params=params, verify=False)
  return response.json()


def convert_json_to_csv(item, json_data):
  CSV_DATA = ["Date,Open,High,Low,Close,Volume"]
  try:
    data = json_data['chart']['result'][0]['indicators']['quote'][0]
    times = json_data['chart']['result'][0]['timestamp']
  except:
    return None

  for idx in range(0,len(data['close'])-1):
    date = datetime.fromtimestamp(times[idx]).strftime('%Y-%m-%d')
    CSV_DATA.append(
      ",".join(
        [
          date,
          str(data['open'][idx]),
          str(data['high'][idx]),
          str(data['low'][idx]),
          str(data['close'][idx]),
          str(data['volume'][idx])
        ]
      )
    )
  
  CSV_DATA = "\n".join(CSV_DATA)

  if OPT_WRITE_CSV:
    csv_path = investoscope.generate_csv_file_name(item, "yv2")
    with open(str(csv_path), 'w') as csv_file:
      csv_file.write(CSV_DATA)

  return CSV_DATA

def gen_historical_data_csv(item):
  """Get quote download crumb from yahoo"""
  with requests.Session() as s:
    s.headers.update(YAHOO_HEADERS)
    yahoo_crumb = get_yahoo_data_crumb(s, item)
    json_data = get_yahoo_json_data(s, yahoo_crumb, item)

  return convert_json_to_csv(item, json_data)


if __name__ == '__main__':
  OPT_WRITE_CSV = False
  gen_historical_data_csv({'code': 'CLH.AX'})