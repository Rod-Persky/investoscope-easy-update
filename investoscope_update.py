
import sqlite3
from pathlib import PosixPath
import sys
import re
import time
import csv
from subprocess import Popen, PIPE
import pickle
import requests

INVESTOSCOPE_PATH = "~/.investoscope"
INVESTOSCOPE_DB = "data4.issqlite"
INVESTOSCOPE_ITEM_SQL = "SELECT "+\
                         "zsymbol AS symbol, "+\
                         "zname as name, "+\
                         "ZQUOTEFEEDIDENTIFIER as provider "+\
                         "FROM zquoteclient WHERE "+\
                         "ZQUOTEFEEDIDENTIFIER = \"com.investoscope.YahooFinance\" "+\
                         "and not symbol = \"Null\";" # yahoo equities

TIME_OFFSET_DAYS = lambda days: days*60*60*24

YAHOO_HISTORY_PAGE = "https://finance.yahoo.com/quote/{item}/history"
YAHOO_CSV_URL = "https://query1.finance.yahoo.com/v7/finance/download/{item}"
YAHOO_CSV_PARAMS = {"period1": int(time.time())-(TIME_OFFSET_DAYS(2*365)),
                    "period2": int(time.time()),
                    "interval": "1d",
                    "events": "history",
                    "crumb": "{yahoo_crumb}"}

YAHOO_CRUMB_REGEX = r"CrumbStore\":{\"crumb\":\"([^\"]*)"

INVESTOSCOPE_APPLESCRIPT = """
tell first document of application "Investoscope 3"
	set anInstrument to first instrument whose symbol is "{item}"
	anInstrument import historical quotes with CSV "{csv_text}" with replace
end tell"""


BASE_PATH = PosixPath(INVESTOSCOPE_PATH).expanduser()
CSV_DOWNLOAD_PATH = BASE_PATH / 'csv_data'
CSV_DOWNLOAD_PATH.mkdir(exist_ok=True)

STATE_PICKLE_FILE = BASE_PATH/'state.p'

if not (BASE_PATH / INVESTOSCOPE_DB).exists():
  sys.exit(0)

def load_last_state():
  """Load last state (last update time for instruments)"""
  if (STATE_PICKLE_FILE).exists():
    return pickle.load(STATE_PICKLE_FILE.open("rb"))
  else:
    return dict()

def save_state(status):
  """ saves the current state """
  pickle.dump(status, STATE_PICKLE_FILE.open("wb"))

def generate_csv_file_name(item):
  """ Generate a file name replacing parts of name with valid
  filename bits """
  filename = item['code'].replace('.', '_')
  filename = filename.replace('^', 'idx_')
  return CSV_DOWNLOAD_PATH / (filename + '.csv')

def get_investoscope_items():
  """Return Investoscope Items"""
  with sqlite3.connect(str(BASE_PATH / INVESTOSCOPE_DB)) as conn:
    result = conn.execute(INVESTOSCOPE_ITEM_SQL)

  items = []
  for item in result:
    items.append({'code': item[0].strip(),
                  'internal code': item[0],
                  'name': item[1],
                  'provider': item[2]})

  return items


def tidy_yahoo_csv(csv_data):
  """ Generate investoscope / applescript csv string """
  csv_text = []
  csv_data = csv.reader(csv_data.split('\n'))
  for row in csv_data:
    # Ignore row with null values
    if "null" in row or len(row) == 0:
      continue

    # Remove Adj Close
    row.pop(5)
    csv_text.append(",".join(row))
  csv_text = "\n".join(csv_text)
  return csv_text

def download_yahoo_csv(item, yahoo_crumb, yahoo_cookie):
  """Get quote csv from yahoo"""
  url = YAHOO_CSV_URL.replace("{item}", item['code'])
  params = dict.copy(YAHOO_CSV_PARAMS)
  params['crumb'] = yahoo_crumb

  response = requests.get(url, params=params, cookies=yahoo_cookie)
  csv_data = response.content

  if len(csv_data) < 1000:
    if b'Unauthorized' in csv_data:
      print("retry")
      # Starts from the first yahoo call
      return get_yahoo_quote(item)

  csv_path = generate_csv_file_name(item)
  with open(str(csv_path), 'wb') as csv_file:
    csv_file.write(csv_data)

  return tidy_yahoo_csv(csv_data.decode('utf-8'))


def get_yahoo_quote(item):
  """Get quote download crumb from yahoo"""
  url = YAHOO_HISTORY_PAGE.replace("{item}", item['code'])
  response = requests.get(url)

  # Get yahoo cookie
  yahoo_cookie = {'B': response.cookies['B']}

  # Get yahoo html
  yahoo_crumb_regex = re.search(YAHOO_CRUMB_REGEX, response.text)
  yahoo_crumb = yahoo_crumb_regex.group(1)
  yahoo_crumb = yahoo_crumb.replace('\\u002F', '/')

  # get CSV (returns path to CSV)
  return download_yahoo_csv(item, yahoo_crumb, yahoo_cookie)


def get_quote(item):
  """ Get all quote data """
  if 'YahooFinance' in item['provider']:
    return get_yahoo_quote(item)


def generate_applescript_command(item, csv_text):
  """ Generate the applescript command  """
  applescript = INVESTOSCOPE_APPLESCRIPT
  applescript = applescript.replace('{item}', item['internal code'])
  applescript = applescript.replace('{csv_text}', csv_text)
  return applescript


def execute_applescript_command(applescript):
  """ Execute applescript command """
  process = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
  stdout, stderr = process.communicate(applescript.encode())
  if process.returncode is not 0:
    print(process.returncode, stdout, stderr)


def load_into_investoscope(item, csv_text):
  """ Load generated quotes into investoscope """
  applescript = generate_applescript_command(item, csv_text)
  execute_applescript_command(applescript)


def check_item_outdated(item, status):
  """ Check if the item is outdated """
  if item['code'] in status:
    state = status[item['code']]
    # If item is older than 1 day, then update
    if state < (int(time.time())-TIME_OFFSET_DAYS(1)):
      return True
    else:
      return False

  # If item not known, then it's outdated
  else:
    return True

def update_item_status(item, status):
  """ store that this has been updated """
  status[item['code']] = int(time.time())
  return status


def main():
  """Run Program"""
  status = load_last_state()
  items = get_investoscope_items()
  for item in items:
    try:
      if check_item_outdated(item, status):
        csv_text = get_quote(item)
        load_into_investoscope(item, csv_text)
        status = update_item_status(item, status)
        save_state(status)
    except:
      print("Unexpected error:", sys.exc_info()[0])


  print("done!")


main()
