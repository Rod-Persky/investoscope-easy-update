import time
from datetime import date
import pickle
import copy

# Quote Providers
import investoscope
import qapi
import yahoo_json
import yahoo_csv
providers = [qapi, yahoo_json, yahoo_csv]

# Updater state
STATE_PICKLE_FILE = investoscope.BASE_PATH/'state.p'

def load_last_state():
  """Load last state (last update time for instruments)"""
  if (STATE_PICKLE_FILE).exists():
    return pickle.load(STATE_PICKLE_FILE.open("rb"))
  else:
    return dict()

def save_state(status):
  """ saves the current state """
  pickle.dump(status, STATE_PICKLE_FILE.open("wb"))

def get_quote(item):
  """ Get all quote data """
  provider_idx = 0
  while provider_idx < len(providers):
    provider = providers[provider_idx]
    try:
      # Permit the update scripts to modify the item
      item_copy = copy.deepcopy(item)
      data = provider.gen_historical_data_csv(item_copy)

    # Errors associated with other non-specific problems
    except IndexError:
      pass

    except Exception as ex:
      template = "An exception of type {0} occurred. Arguments:\n{1!r}"
      message = template.format(type(ex).__name__, ex.args)
      print(message)
    
    if data is not None:
      return data

    provider_idx += 1

  return None

def check_item_outdated(item, status):
  """ Check if the item is outdated """
  if item['code'] in status:
    # Update when the weekday has changed
    last_update = date.fromtimestamp(status[item['code']])
    if last_update.weekday() is not date.today().weekday():
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
  items = investoscope.get_tickers()
  progress = {'items': len(items), 'complete': 0}
  for item in items:
    progress_value = str(int(100*progress['complete']/progress['items']))
    print("PROGRESS:", progress_value, sep="")
    try:
      if check_item_outdated(item, status):
        print("Updating:", item['code'], item['name'])
        # ToDo: get_quote modifies item
        csv_text = get_quote(copy.deepcopy(item))

        if csv_text is None:
          continue

        investoscope.load_into_investoscope(item , csv_text)
        status = update_item_status(item, status)
        save_state(status)
      else:
        print("up to date:", item['code'], item['name'])
    except:
      print("Unable to get information for", item['name'], '('+item['code']+')')

    progress['complete'] += 1


main()
