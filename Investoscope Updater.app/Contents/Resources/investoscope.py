import sqlite3
from pathlib import PosixPath
from subprocess import Popen, PIPE

INVESTOSCOPE_PATH = "~/.investoscope"
INVESTOSCOPE_DB = "data4.issqlite"
INVESTOSCOPE_ITEM_SQL = "SELECT "+\
                         "zsymbol AS symbol, "+\
                         "zname as name, "+\
                         "ZQUOTEFEEDIDENTIFIER as provider "+\
                         "FROM zquoteclient WHERE "+\
                         "ZQUOTEFEEDIDENTIFIER = \"com.investoscope.YahooFinance\" "+\
                         "and not symbol = \"Null\";" # yahoo equities

INVESTOSCOPE_APPLESCRIPT = """
tell first document of application "Investoscope 3"
	set anInstrument to first instrument whose symbol is "{item}"
	anInstrument import historical quotes with CSV "{csv_text}" with replace
end tell"""

BASE_PATH = PosixPath(INVESTOSCOPE_PATH).expanduser()
CSV_DOWNLOAD_PATH = BASE_PATH / 'csv_data'
CSV_DOWNLOAD_PATH.mkdir(exist_ok=True)

if not (BASE_PATH / INVESTOSCOPE_DB).exists():
  sys.exit(0)


def get_tickers():
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


def generate_applescript_command(item, csv_text):
  """ Generate the applescript command  """
  """Date,Open,High,Low,Close,Volume"""
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


def generate_csv_file_name(item, provider=""):
  """ Generate a file name replacing parts of name with valid
  filename bits """
  filename = item['code'].replace('.', '_')
  filename = filename.replace('^', 'idx_')

  if provider:
    provider = "_" + provider
    
  return CSV_DOWNLOAD_PATH / (filename + provider + '.csv')